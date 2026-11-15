#!/usr/bin/env python3
"""SPOILER da Tarde de Jogos no Beca’s (15/nov/2026, pedido dele): "uma foto e um vídeo, tipo um spoiler do que vai ter no
evento, e pra lembrar as pessoas de fazerem a reserva". Os 12 jogos que ELE listou: Santorini, Hot Streak, Código Secreto
(Imagens), Flip 7 (A Vingança), UNO No Mercy, Drácula vs Van Helsing, Hive, Dixit Disney, Hitster, Hitster Verão,
Marrakech e UNO Stacko. Caixas OFICIAIS (UNO No Mercy da Ri Happy/Mattel; Hitster Verão HIT002 e Dixit Disney DIX631 da
API da Galápagos → promo/assets/spoiler/).
Visual das guarda-chuvinhas (o preferido deles para o Beca’s): fita amarela de "SPOILER" + grade de 12 cartas "?" que
viram as caixas uma a uma, no ritmo da batida, com o nome do jogo; depois data, endereço e a reserva.

    /usr/bin/python3 spoiler.py --fotos                 # out/spoiler/post.png (1080x1350) + story.png (1080x1920)
    /usr/bin/python3 spoiler.py --frame 0.8 4 9 14      # out/frames_spoiler.jpg (versão stories)
    /usr/bin/python3 spoiler.py --reels | --stories     # out/spoiler_{reels,stories}_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
import tarde as T
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA
from motor import FPS, out_back  # noqa: E402

REPO = os.path.dirname(T.ROOT)
OUT = T.OUT
A = lambda p: os.path.join(REPO, p)  # noqa: E731
SP = "promo/assets/spoiler/"
# (nome na tela, caixa) — ordem da revelação = ordem da grade (4 colunas x 3 linhas)
JOGOS = [
    ("SANTORINI", A("hobby-reels/assets/caixas/santorini.png")),
    ("HITSTER", A("gravados-reels/assets/lista/hitster.png")),
    ("UNO NO MERCY", A(SP + "uno_no_mercy.png")),
    ("DIXIT DISNEY", A(SP + "dixit_disney.png")),
    ("CÓDIGO SECRETO", A("hobby-reels/assets/caixas/c_digo_secreto_imagens.png")),
    ("HOT STREAK", A("hobby-reels/assets/caixas/hot_streak.png")),
    ("HIVE", A("hobby-reels/assets/caixas/hive.png")),
    ("FLIP 7", A("gravados-reels/assets/top10/flip_7_a_vinganca.png")),
    ("DRÁCULA VS VAN HELSING", A("halloween-reels/assets/dracula.png")),
    ("UNO STACKO", A("promo/assets/criancas/uno_stacko.png")),
    ("MARRAKECH", A("gravados-reels/assets/perguntas/marrakech.png")),
    ("HITSTER VERÃO", A(SP + "hitster_verao.png")),
]
BPM = 118
BEAT = 60 / BPM
T_REV0 = 4 * BEAT  # 1ª revelação (2,03 s)
T_REV = [T_REV0 + k * BEAT for k in range(len(JOGOS))]
T_FIM_REV = T_REV[-1] + BEAT
DUR = 15.0

# layouts: y de cada peça (vídeo/story 1080x1920 e post 1080x1350)
LAY = {
    "story": dict(fita=500, tit=500, sub=622, linhas=(745, 920, 1095), cel=(240, 168), nome=1222, data=1300, end=1362,
                  extra="link"),
    "reels": dict(fita=500, tit=500, sub=622, linhas=(745, 920, 1095), cel=(240, 168), nome=1222, data=1300, end=1362,
                  extra="whats"),
    "post": dict(fita=300, tit=300, sub=410, linhas=(540, 712, 884), cel=(232, 160), nome=990, data=1062, end=1120,
                 extra="post"),
}
XS = (165, 405, 645, 885)


# ---------------------------------------------------------------- peças
@lru_cache(None)
def fita(w, h=96, txt="SPOILER  •  SPOILER  •  SPOILER  •  SPOILER  •  SPOILER  •  SPOILER  •  SPOILER"):
    """Fita amarela de aviso com listras pretas nas bordas e SPOILER repetido."""
    im = Image.new("RGBA", (w, h), AMA + (255,))
    d = ImageDraw.Draw(im)
    for y0 in (0, h - 14):
        for x in range(-30, w + 30, 34):
            d.polygon([(x, y0), (x + 17, y0), (x + 31, y0 + 14), (x + 14, y0 + 14)], fill=MAR)
    d.text((w / 2, h / 2 + 2), txt, font=E.lilita(int(h * 0.42)), fill=MAR, anchor="mm")
    sh = Image.new("RGBA", (w, h + 10), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 70), (0, 8), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    sh.alpha_composite(im)
    return sh


@lru_cache(None)
def caixa(k, w, h):
    """Caixa oficial cabendo em w x h, com sombra marrom suave."""
    im = Image.open(JOGOS[k][1]).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 24, im.height + 24), (0, 0, 0, 0))
    sh.paste(MAR + (120,), (12, 16), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    sh.alpha_composite(im, (2, 2))
    return sh


@lru_cache(None)
def carta(w, h, k):
    """Carta virada: petróleo listrado com "?" amarelo."""
    c = E.bloco(w, h, PET, raio=22, ow=6, sombra=8).copy()
    d = ImageDraw.Draw(c)
    for x in range(-h, w, 26):
        d.line((x, h - 8, x + h, 8), fill=(40, 140, 166), width=8)
    d.rounded_rectangle((0, 0, w, h), radius=22, outline=MAR, width=6)
    d.text((w / 2, h / 2 + 4), "?", font=E.lilita(int(h * 0.62)), fill=AMA, anchor="mm", stroke_width=5,
           stroke_fill=MAR)
    return c.rotate(random.Random(k).uniform(-4, 4), expand=True, resample=Image.BICUBIC)


@lru_cache(None)
def titulo(txt, s, cor=LAR, larg=980):
    return E.titulo(txt, s, cor, larg_max=larg)


@lru_cache(None)
def pil(txt, s, cor, fg=MAR, ft=True):
    return E.pilula(txt, s, cor, fg, fonte_titulo=ft)


def mais():
    return pil("+ E TEM MUITO MAIS NA MESA!", 46, ROSA, BR)


def seta_baixo():
    im = Image.new("RGBA", (90, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((45, 5, 45, 80), fill=MAR, width=12)
    d.polygon([(10, 62), (80, 62), (45, 105)], fill=MAR)
    return im


# ---------------------------------------------------------------- cena
def grade(img, t, L):
    cw, ch = L["cel"]
    for k in range(len(JOGOS)):
        x, y = XS[k % 4], L["linhas"][k // 4]
        tr = T_REV[k]
        entra = T.surge(t, 0.9 + 0.04 * k, 0.3)
        if t < tr:  # carta "?" (treme um pouquinho logo antes de virar)
            tremor = 3 * math.sin(t * 60) if tr - t < 0.2 else 0
            E.cola(img, carta(cw - 20, ch - 10, k), x + tremor, y, 0, entra[1], entra[0])
            continue
        u = (t - tr) / 0.32
        if u < 1:  # a carta encolhe e a caixa estoura no lugar
            E.cola(img, carta(cw - 20, ch - 10, k), x, y, 0, max(0.0, 1 - 2.2 * u), 1)
        s = out_back(min(1.0, u), 1.8)
        E.cola(img, caixa(k, cw - 16, ch), x, y, (-1) ** k * 3, s, min(1.0, u * 2))


def topo(img, t, L):
    T.guarda_chuvas(img, t)
    a, s = T.surge(t, 0.25, 0.35)
    E.cola(img, fita(1400), W / 2, L["fita"] + 8, -5, 1.0 if s > 0 else 0, a)
    T.poe(img, titulo("ALERTA DE SPOILER!", 116), W / 2, L["tit"], t, 0.45, 2)
    T.poe(img, pil("O QUE VAI TER NA MESA DA TARDE DE JOGOS", 34, BR, PET), W / 2, L["sub"], t, 0.75, -1)


def quadro(t, modo="story", img=None):
    L = LAY[modo]
    if img is None:
        img = T.fundo().copy()
    topo(img, t, L)
    grade(img, t, L)
    # nome do jogo que acabou de virar
    if T_REV0 <= t < T_FIM_REV + 0.1:
        k = min(len(JOGOS) - 1, int((t - T_REV0) / BEAT))
        lt = t - T_REV[k]
        E.cola(img, pil(JOGOS[k][0], 54, AMA), W / 2, L["nome"], (-1) ** k * 2, out_back(min(1, lt / 0.2), 2))
    if t >= T_FIM_REV:
        T.poe(img, mais(), W / 2, L["nome"], t, T_FIM_REV, 2)
        t1 = T_FIM_REV + 0.6
        T.poe(img, TB.selo_data(38), W / 2, L["data"], t, t1, -1)
        T.poe(img, TB.selo_endereco(30), W / 2, L["end"], t, t1 + 0.2, 1)
        if L["extra"] == "link":  # Stories: área y≈1480–1640 LIVRE para o adesivo de link
            if t > t1 + 0.5:
                al = min(1, (t - t1 - 0.5) / 0.3)
                bob = 8 * math.sin(2 * math.pi * (t - t1) / 1.2)
                tx = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
                ImageDraw.Draw(tx).text((W / 2 - 60, 45), "garanta sua mesa aqui:", font=E.fig(42, 900), fill=MAR,
                                        anchor="mm")
                tx.alpha_composite(seta_baixo(), (int(W / 2 + 205), int(bob)))
                tx.putalpha(tx.getchannel("A").point(lambda v: int(v * al)))
                img.alpha_composite(tx, (0, 1390))
            T.poe(img, pil("ou no WhatsApp " + TB.WHATS, 36, BR, MAR, False), W / 2, 1700, t, t1 + 0.8, 0)
        elif L["extra"] == "whats":  # Reels: reserva + comenta, tudo acima de y≈1590
            T.poe(img, pil("R$ 30 · R$ 15 VIRAM CONSUMAÇÃO", 34, AMA), W / 2, 1425, t, t1 + 0.4, -1)
            T.poe(img, pil("GARANTA SUA MESA: WHATSAPP " + TB.WHATS, 36, PET, BR), W / 2, 1495, t, t1 + 0.6, 1)
            T.poe(img, pil("Comenta: qual você joga primeiro?", 36, BR, MAR, False), W / 2, 1572, t, t1 + 0.9, -1)
    return img


def post():
    img = TB.fundo(1080, 1350, [40, 95, 30, 85, 40, 90], 120)
    L = LAY["post"]
    E.cola(img, fita(1400, 84), W / 2, L["fita"] + 6, -5)
    E.cola(img, titulo("ALERTA DE SPOILER!", 104), W / 2, L["tit"], 2)
    E.cola(img, pil("O QUE VAI TER NA MESA DA TARDE DE JOGOS", 32, BR, PET), W / 2, L["sub"], -1)
    grade(img, 99, L)
    E.cola(img, pil("+ E TEM MUITO MAIS NA MESA!", 40, ROSA, BR), W / 2, L["nome"], 2)
    E.cola(img, TB.selo_data(34), W / 2, L["data"], -1)
    E.cola(img, TB.selo_endereco(27), W / 2, L["end"], 1)
    E.cola(img, pil("R$ 30 · R$ 15 VIRAM CONSUMAÇÃO", 30, AMA), W / 2, 1178, -1)
    E.cola(img, pil("GARANTA SUA MESA: WHATSAPP " + TB.WHATS, 34, PET, BR), W / 2, 1255, 1)
    return img.convert("RGB")


# ---------------------------------------------------------------- som
def audio(nome):
    ev = [(0.08 * k + 0.05, S.sino() * 0.25, 0.25) for k in range(len(T.CHUVAS))]
    ev += [(0.25, S.fita(), 0.6), (0.45, S.estouro(), 0.35), (0.75, S.cartao(), 0.35)]
    for k, tr in enumerate(T_REV):
        ev.append((tr, S.cartao(), 0.55))
        ev.append((tr + 0.02, S.plim() if k % 2 else S.sino(), 0.3))
    ev += [(T_FIM_REV, S.estouro(), 0.5), (T_FIM_REV + 0.6, S.cartao(), 0.35), (T_FIM_REV + 0.8, S.cartao(), 0.35),
           (T_FIM_REV + 1.2, S.sino(), 0.4)]
    mus = S.musica_pop(DUR + 0.5, 0.0, BPM)
    com, sem = (os.path.join(OUT, f"{nome}_{x}.wav") for x in ("com", "sem"))
    S.grava(com, DUR, ev, mus, musica_ganho=0.42, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


def render_story(fi):
    return quadro(fi / FPS, "story").convert("RGB").tobytes()


def render_reels(fi):
    return quadro(fi / FPS, "reels").convert("RGB").tobytes()


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--fotos" in sys.argv:
        d = os.path.join(OUT, "spoiler")
        os.makedirs(d, exist_ok=True)
        post().save(os.path.join(d, "post.png"))
        quadro(DUR, "story").convert("RGB").save(os.path.join(d, "story.png"))
        print("ok", d)
        return
    modo = "reels" if "--reels" in sys.argv else "story"
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x, modo).convert("RGB") for x in ts], os.path.join(OUT, "frames_spoiler.jpg"))
        print("ok")
        return
    nome = "spoiler_reels" if modo == "reels" else "spoiler_stories"
    com, sem = audio(nome)
    K.entrega(nome, DUR, render_reels if modo == "reels" else render_story, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
