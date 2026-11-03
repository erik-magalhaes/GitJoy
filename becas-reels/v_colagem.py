#!/usr/bin/env python3
"""Reels A do Becas: COLAGEM (referência "GAME NIGHT!" do Pinterest que ele mandou, 3/nov/2026). Papel branco amassado
rasgado sobre azul royal; título de letras recortadas de revista batendo uma a uma; as cenas REAIS de jogo deles aparecem
dentro de rasgos do papel com o nome em letras recortadas e a ficha em máquina de escrever; informações datilografadas,
placa escrita à mão e estrela vermelha. Som: tesoura, rasgo, fita, teclas de máquina e batida de pisão e palma.

    /usr/bin/python3 v_colagem.py --frame 1.5 3.5 6 10 18 22 25
    /usr/bin/python3 v_colagem.py         # out/colagem_{com_som,para_musica}_final.mp4
"""
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
import estilos as ST
from kit import W, H, FPS, ease

JOGOS = [("critter", 0.6, "CRITTER KITCHEN", "1 a 5 jogadores · 60 min"),
         ("sushi", 0.4, "SUSHI GO!", "2 a 5 jogadores · 15 min"),
         ("canvas", 1.4, "CANVAS", "1 a 5 jogadores · 30 min"),
         ("art", 0.5, "ART SOCIETY", "2 a 4 jogadores · 60 min"),
         ("passaporte", 0.8, "PASSAPORTE MUNDO", "1 a 6 jogadores · 45 min"),
         ("sky_dados", 3.5, "SKY TEAM", "2 jogadores · 20 min")]
GANCHO = 3.4
PJ = 2.3                      # tempo de cada jogo
INI_J = GANCHO
INFO = INI_J + len(JOGOS) * PJ
CTA = INFO + 4.6
DUR = CTA + 5.0
LETRAS = "TARDE\nDE JOGOS!"
N_LETRAS = len(LETRAS.replace("\n", "").replace(" ", ""))


@lru_cache(None)
def fundo():
    return ST.fundo_colagem()


@lru_cache(None)
def moldura_rasgada(w, h, seed):
    pts = ST.borda_rasgada([(0, 0), (w, 0), (w, h), (0, h), (0, 0)], seed, 10)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    mb = Image.new("L", (w + 40, h + 40), 0)
    mb.paste(m.filter(ImageFilter.MaxFilter(15)), (20, 20))
    base = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    base.paste((250, 249, 245, 255), (0, 0), mb)
    sh = ST.sombra(base, 12, (8, 12), 120)
    return sh, m


def janela(img, frame, cx, cy, w, h, seed, rot, esc=1.0):
    sh, m = moldura_rasgada(w, h, seed)
    peca = sh.copy()
    fr = ST.cobre(frame, w, h).convert("RGBA")
    fr.putalpha(m)
    peca.alpha_composite(fr, (2 * 12 + 20, 2 * 12 + 20))
    if esc != 1.0:
        peca = peca.resize((max(1, int(peca.width * esc)), max(1, int(peca.height * esc))), Image.BILINEAR)
    ST.cola(img, peca, cx, cy, rot)


def titulo_parcial(img, txt, cx, cy, s, n_visiveis, larg=980, seed=0):
    """Como ST.titulo_recortado, mas só as n primeiras letras (cada uma 'bate' com um pulo)."""
    linhas = txt.split("\n")
    y = cy - (len(linhas) - 1) * s * 0.62
    cont = 0
    for li, linha in enumerate(linhas):
        pecas = [ST.letra_recortada(ch, seed + li * 40 + k, s) if ch != " " else None for k, ch in enumerate(linha)]
        tot = sum((p.width - 28 if p else s * 0.35) for p in pecas)
        e = min(1.0, larg / tot)
        x = cx - tot * e / 2
        for p in pecas:
            if p is None:
                x += s * 0.35 * e
                continue
            if cont < n_visiveis:
                q = p.resize((int(p.width * e), int(p.height * e)), Image.LANCZOS) if e < 1 else p
                img.alpha_composite(q, (int(x - 14 * e), int(y - q.height / 2)))
            x += (p.width - 28) * e
            cont += 1
        y += s * 1.24


def maquina_parcial(img, x, y, linhas, n_chars, s=50):
    d = ImageDraw.Draw(img)
    resto = n_chars
    for k, l in enumerate(linhas):
        if resto <= 0:
            break
        d.text((x, y + k * s * 1.4), l[:resto], font=ST.F("SpecialElite-Regular.ttf", s), fill=ST.PRETO)
        resto -= len(l)


def tremor(t, k=0):
    """Tremidinho de stop motion (troca a 8 quadros/s)."""
    r = random.Random(int(t * 8) * 31 + k)
    return r.uniform(-1.2, 1.2), r.uniform(-4, 4), r.uniform(-4, 4)


def cena_gancho(img, t):
    n = min(N_LETRAS, int(t / 0.17) + 1)
    titulo_parcial(img, LETRAS, W / 2, 720, 235, n)
    if t > 2.2:
        a, s = K.surge(t, 2.2, 0.3)
        ST.cola(img, ST.placa("VEM JOGAR\nCOM A GENTE!", 500, 260).resize(
            (max(1, int(500 * s) + 60), max(1, int(260 * s) + 60))), 760, 1290, 6)


def cena_jogo(img, t):
    k = min(len(JOGOS) - 1, int((t - INI_J) / PJ))
    u = t - INI_J - k * PJ
    nome, t0, titulo, ficha = JOGOS[k]
    rot, dx, dy = tremor(t, k)
    entra = ease(min(1.0, u / 0.25))
    frame = K.quadro_clip(nome, *ST.FULL[nome], 1.0, t0 + u).convert("RGB")
    janela(img, frame, W / 2 + dx + (1 - entra) * (-W if k % 2 else W), 860 + dy, 880, 1000, 20 + k,
           (-3 if k % 2 else 3) + rot)
    n = int(max(0, u - 0.3) / 0.06) + 1
    titulo_parcial(img, titulo, W / 2, 1490, 92, n, 960, seed=100 + k * 10)
    maquina_parcial(img, 120, 1600, ["> " + ficha], int(max(0, u - 0.8) / 0.03), 42)
    if k == 0 and u < 1.6:
        ST.cola(img, ST.placa("olha isso:", 360, 160), 260, 330, -8)


INFO_LINHAS = ["# tarde de jogos no Becas Café", "# R$ 30, e R$ 15 viram café", "# a gente ensina todos os jogos",
               "# venha sozinho ou com a galera", "# data em breve"]


def cena_info(img, t):
    u = t - INFO
    titulo_parcial(img, "ANOTA AÍ:", W / 2, 440, 150, int(u / 0.1) + 1, seed=300)
    maquina_parcial(img, 60, 640, INFO_LINHAS, int(max(0, u - 0.8) / 0.022), 54)
    if u > 3.2:
        ST.cola(img, ST.estrela(230, 140, 14, ST.VERM + (255,)), 760, 1350, 8)
        ST.cola(img, ST.placa("RESERVE NO\nWHATSAPP!", 470, 250), 740, 1340, 5)


def cena_cta(img, t):
    u = t - CTA
    img.alpha_composite(K.logo(220), (int(W / 2 - 110), 300))
    titulo_parcial(img, "COMENTA:", W / 2, 640, 150, int(u / 0.1) + 1, seed=500)
    ST.cola(img, ST.placa("qual jogo você\nquer aprender?", 640, 300), W / 2, 920, -3)
    if u > 1.2:
        d = ImageDraw.Draw(img)
        d.text((W / 2, 1250), "(11) 97793-3910", font=ST.F("Anton-Regular.ttf", 120), fill=ST.AZUL, anchor="mm")
        d.text((W / 2, 1360), "reserve sua mesa · ou chegue no dia", font=ST.F("SpecialElite-Regular.ttf", 44),
               fill=ST.PRETO, anchor="mm")


def quadro(t):
    img = fundo().copy()
    if t < INI_J:
        cena_gancho(img, t)
    elif t < INFO:
        cena_jogo(img, t)
    elif t < CTA:
        cena_info(img, t)
    else:
        cena_cta(img, t)
    if t < CTA:
        img.alpha_composite(K.logo(150), (W - 180, 40))
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(com, sem):
    ev = [(k * 0.17, S.tesoura(), 0.7) for k in range(N_LETRAS)]
    ev += [(2.2, S.fita(), 0.7)]
    for k, (_, _, titulo, ficha) in enumerate(JOGOS):
        t0 = INI_J + k * PJ
        ev += [(t0, S.rasgo(), 0.8)]
        ev += [(t0 + 0.3 + j * 0.06, S.tesoura(), 0.35) for j in range(len(titulo.replace(" ", "")))]
        ev += [(t0 + 0.8 + j * 0.06, S.tecla(), 0.25) for j in range(0, len(ficha), 2)]
    ev += [(INFO + j * 0.1, S.tesoura(), 0.5) for j in range(8)]
    tot = sum(len(l) for l in INFO_LINHAS)
    ev += [(INFO + 0.8 + j * 0.022 * 2, S.tecla(), 0.3) for j in range(tot // 2)]
    ev += [(INFO + 0.8 + tot * 0.022, S.sininho_maquina(), 0.6), (INFO + 3.2, S.fita(), 0.6)]
    ev += [(CTA + j * 0.1, S.tesoura(), 0.5) for j in range(8)] + [(CTA + 1.2, S.cartao(), 0.6)]
    mus = S.musica_stomp(DUR, 0.0)
    S.grava(com, DUR, ev, mus, musica_ganho=0.5, fx_ganho=0.85)
    S.grava(sem, DUR, ev, None, fx_ganho=0.85)


def main():
    os.makedirs(K.OUT, exist_ok=True)
    K.prepara([(n, t0, d, 1.0) for n, (t0, d) in ST.FULL.items()])
    print("duração", round(DUR, 1))
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(K.OUT, "frames_colagem.jpg"))
        return
    com, sem = os.path.join(K.OUT, "colagem_com.wav"), os.path.join(K.OUT, "colagem_sem.wav")
    audio(com, sem)
    K.entrega("colagem", DUR, render, com, sem)


if __name__ == "__main__":
    main()
