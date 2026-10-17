#!/usr/bin/env python3
"""Reels "SEU SIGNO, SEU JOGO" (ideia 4, aprovada por ele em 17/out/2026). Sem narração, tudo escrito.
Céu de noite com estrelas piscando; cada signo = símbolo dourado brilhando + nome em Cinzel + a FOTO DO SITE do jogo num
cartão dourado + frase de zoeira (as frases foram aprovadas por ele; a do Splito confere com a regra: pontos da esquerda
× pontos da direita). Fecha com a grade dos 12 (pra pausar/printar), "marca o amigo" e o CTA.

    python3 signos.py --frame 1 3 5 ...   # out/frames.jpg
    python3 signos.py                     # out/signos_{com_trilha,para_musica}_final.mp4
"""
import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from base import W, H, FPS, REPO, OUT, texto, foto, folha, entrega  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "roleta-reels"))
from motor import seg, ease, lerp, logo_card, cola, sombra  # noqa: E402
import taro  # noqa: E402,F401  (registra a trilha "mistica" e o efeito "harpa")

OURO, OURO_ESC, CREME = (240, 198, 96), (120, 80, 20), (250, 240, 220)
NOITE = (10, 12, 38)
SIMB = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SIGNOS = [  # (símbolo, signo, jogo, foto do site, frase)
    ("♈", "ÁRIES", "1, 2, 3, Lucha!", "1_2_3_lucha", "Já chega querendo briga:\nluta livre, um contra um."),
    ("♉", "TOURO", "Bohnanza", "bohnanza", "Negocia tudo...\nmenos o feijão dele."),
    ("♊", "GÊMEOS", "Mascarade", "mascarade_second_edition", "Uma hora é rei, outra é bruxa:\nninguém sabe quem você é."),
    ("♋", "CÂNCER", "Quem do casal?", "quem_do_casal", "Ama descobrir o quanto\nconhece quem ama."),
    ("♌", "LEÃO", "Gravity Superstar", "gravity_superstar", "Nasceu pra ser estrela\n(literalmente)."),
    ("♍", "VIRGEM", "Architectura", "architectura", "Cada prédio no lugar certo,\nnada torto."),
    ("♎", "LIBRA", "Splito", "splito", "Seus pontos são a esquerda VEZES\na direita: tem que equilibrar."),
    ("♏", "ESCORPIÃO", "Coup", "coup_inquisition", "Blefa sem piscar, e se vingar\nfaz parte do jogo."),
    ("♐", "SAGITÁRIO", "Treasure Island", "treasure_island", "Caça ao tesouro,\ncom mapa e tudo."),
    ("♑", "CAPRICÓRNIO", "High Society", "high_society", "Gasta em luxo, mas quem fica\nmais pobre é eliminado."),
    ("♒", "AQUÁRIO", "Alieninjas", "alieninjas", "Um pouco alienígena,\num pouco ninja."),
    ("♓", "PEIXES", "Happy Salmon", "happy_salmon", "Sensível, mas topa\num high-five de peixe."),
]
GANCHO = 2.4
POR = 1.85
T_GRADE = GANCHO + POR * len(SIGNOS)
GRADE = 3.2
T_CTA = T_GRADE + GRADE
DUR = T_CTA + 3.4


# ---------------------------------------------------------------- céu
@lru_cache(None)
def ceu():
    yy = np.linspace(0, 1, H)[:, None]
    topo, meio, base = np.array([6, 8, 30]), np.array([24, 20, 70]), np.array([60, 30, 90])
    c = np.where(yy < 0.6, topo + (meio - topo) * (yy / 0.6), meio + (base - meio) * ((yy - 0.6) / 0.4))
    img = Image.fromarray((c[:, None, :] * np.ones((1, W, 1))).reshape(H, W, 3).astype(np.uint8)).convert("RGBA")
    neb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(neb)
    d.ellipse((-200, 300, 700, 1000), fill=(120, 60, 180, 60))
    d.ellipse((500, 1000, 1400, 1800), fill=(40, 90, 200, 50))
    img.alpha_composite(neb.filter(ImageFilter.GaussianBlur(160)))
    return img


rng = np.random.default_rng(7)
ESTRELAS = [(rng.random() * W, rng.random() * H, 0.6 + rng.random() * 2.4, rng.random() * 6.28, 0.6 + rng.random() * 1.6)
            for _ in range(240)]


def estrelas(img, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x, y, r, fase, vel in ESTRELAS:
        a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * vel * 2.2 + fase))
        rr = r * (0.8 + 0.4 * a)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 250, 230, int(255 * a)))
    img.alpha_composite(lay)


@lru_cache(None)
def simbolo(ch, s):
    f = ImageFont.truetype(SIMB, s)
    im = Image.new("RGBA", (int(s * 1.6), int(s * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((im.width / 2, im.height / 2), ch, font=f, fill=OURO, anchor="mm")
    glow = im.filter(ImageFilter.GaussianBlur(s / 9))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for _ in range(2):
        out.alpha_composite(glow)
    out.alpha_composite(im)
    return out


@lru_cache(None)
def cartao(nome, w):
    """Foto do site em cartão com moldura dourada."""
    return foto(nome, w, borda=12, cor_borda=OURO, raio=30, sombra_a=0.6)


def halo(img, x, y, r, a):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse((x - r, y - r, x + r, y + r), fill=(255, 210, 120, int(a)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r / 2.5)))


# ---------------------------------------------------------------- cenas
def cena_gancho(img, t):
    u = ease(seg(t, 0.0, 0.5))
    for k, (ch, *_r) in enumerate(SIGNOS):  # anel girando com os 12 símbolos
        ang = 2 * math.pi * k / 12 + t * 0.35
        cola(img, simbolo(ch, 70), W / 2 + 380 * math.cos(ang) * 1.25, 1000 + 400 * math.sin(ang) * 1.45, alpha=0.85 * u)
    halo(img, W / 2, 1000, 260, 70 * u)
    cola(img, texto("SEU SIGNO,", "cinzel", 112, CREME, OURO_ESC, 3, 4, OURO_ESC), W / 2, 880, sc=lerp(0.85, 1, u), alpha=u)
    cola(img, texto("SEU JOGO", "cinzel", 132, OURO, OURO_ESC, 4, 5, OURO_ESC), W / 2, 1040, sc=lerp(0.85, 1, u), alpha=u)
    v = ease(seg(t, 0.5, 0.9))
    cola(img, texto("pausa no seu e marca o amigo", "figtree", 46, CREME), W / 2, 1720, alpha=v)


def cena_signo(img, t, k):
    ch, signo, jogo, arq, frase = SIGNOS[k]
    t0 = GANCHO + k * POR
    lt = t - t0
    ent = ease(seg(lt, 0.0, 0.25))
    sai = ease(seg(lt, POR - 0.15, POR))
    alpha = ent * (1 - sai)
    dy = lerp(60, 0, ent) - 40 * sai
    halo(img, W / 2, 420, 150, 110 * alpha * (0.8 + 0.2 * math.sin(lt * 6)))
    cola(img, simbolo(ch, 150), W / 2, 420 + dy * 0.5, alpha=alpha, sc=lerp(0.6, 1, ent))
    cola(img, texto(signo, "cinzel", 92, OURO, OURO_ESC, 3, 4, OURO_ESC), W / 2, 590 + dy * 0.5, alpha=alpha)
    c = ease(seg(lt, 0.04, 0.34))
    cola(img, cartao(arq, 620), W / 2, 1000 + lerp(140, 0, c) - 40 * sai, rot=lerp(-6, 0, c), alpha=c * (1 - sai))
    d = ease(seg(lt, 0.18, 0.45)) * (1 - sai)
    cola(img, texto(jogo, "lilita", 76, (255, 255, 255), (40, 24, 60), 6, 5, (40, 24, 60)), W / 2, 1390, alpha=d)
    cola(img, texto(frase, "figtree", 46, CREME, None, 0, 3, (10, 8, 30), entre=1.25), W / 2, 1530, alpha=d)


@lru_cache(None)
def grade():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cw, x0, y0, dx, dy = 230, W / 2 - 1.5 * 250, 420, 250, 350
    for k, (ch, signo, jogo, arq, _f) in enumerate(SIGNOS):
        x, y = x0 + (k % 4) * dx, y0 + (k // 4) * dy
        cola(lay, simbolo(ch, 44), x, y - 18)
        cola(lay, texto(signo, "cinzel", 30, OURO), x, y + 22)
        cola(lay, foto(arq, cw, borda=6, cor_borda=OURO, raio=18, sombra_a=0.5), x, y + 168)
    return lay


def cena_grade(img, t):
    lt = t - T_GRADE
    u = ease(seg(lt, 0.0, 0.4))
    cola(img, texto("QUAL É O SEU?", "cinzel", 84, OURO, OURO_ESC, 3, 4, OURO_ESC), W / 2, 250, alpha=u)
    cola(img, grade(), W / 2, H / 2, sc=lerp(0.92, 1, u), alpha=u)
    v = ease(seg(lt, 0.5, 0.9))
    cola(img, texto("Comenta o seu signo\ne marca o amigo!", "lilita", 64, (255, 255, 255),
                    (40, 24, 60), 6, 5, (40, 24, 60)), W / 2, 1530, alpha=v)


def cena_cta(img, t):
    lt = t - T_CTA
    u = ease(seg(lt, 0.0, 0.4))
    halo(img, W / 2, 520, 260, 90 * u)
    cola(img, logo_card(430), W / 2, 520, sc=lerp(0.8, 1, u), alpha=u)
    v = ease(seg(lt, 0.25, 0.65))
    cola(img, texto("O SEU JOGO TÁ\nNA SUA VEZ", "cinzel", 86, OURO, OURO_ESC, 3, 4, OURO_ESC), W / 2, 880, alpha=v)
    w = ease(seg(lt, 0.5, 0.9))
    for k, (txt, cor) in enumerate([("3 JOGOS = 7 DIAS", OURO), ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", CREME),
                                     ("LINK NA BIO · @SUAVEZ_BG", (255, 255, 255))]):
        cola(img, texto(txt, "figtree", 48 if k != 1 else 42, cor, None, 0, 3, (10, 8, 30), entre=1.25), W / 2,
             1140 + k * 150, alpha=w)


def frame(t):
    img = ceu().copy()
    estrelas(img, t)
    if t < GANCHO:
        cena_gancho(img, t)
    elif t < T_GRADE:
        cena_signo(img, t, min(len(SIGNOS) - 1, int((t - GANCHO) / POR)))
    elif t < T_CTA:
        cena_grade(img, t)
    else:
        cena_cta(img, t)
    if t < T_CTA:
        img.alpha_composite(logo_card(150), (W - 186, 46))
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.05, "brilho", 0.7), (0.4, "reveal", 0.5)]
    for k in range(len(SIGNOS)):
        t0 = GANCHO + k * POR
        c += [(t0 + 0.02, "whoosh", 0.35), (t0 + 0.12, "harpa", 0.55)]
    c += [(T_GRADE, "reveal", 0.6), (T_CTA, "ding", 0.6)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    print(f"duração {DUR:.1f} s")
    if a.frame:
        os.makedirs(OUT, exist_ok=True)
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    entrega("signos", DUR, render_frame, cues(), "mistica", musica_ganho=0.34)


if __name__ == "__main__":
    main()
