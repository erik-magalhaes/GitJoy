#!/usr/bin/env python3
"""NOVAS OPÇÕES do Beca’s (7/nov/2026, pedido dele: "não mexe no que já está feito, cria novas opções", intercalando as
gravações do Beca’s com os vídeos dos JOGOS na mesa que eles já têm; usar o vídeo da PAREDE do café que a Jéssica fez
quando ele chegar no Drive → `brutos/nov06/parede.mp4`, entra sozinho no gancho e num par se o arquivo existir).

    combo   "CAFÉ + JOGO = COMBO PERFEITO" (~20 s): corte seco alternando um plano do café e um plano de jogo, com
            "+" estourando no corte; fecha com "= TARDE DE JOGOS NO BECA’S" + convite.
    metade  "METADE CAFÉ, METADE JOGO" (~16 s): tela dividida, café em cima e jogo embaixo, os dois andando juntos,
            pílula "+" na emenda; fecha com o convite.

Cada um em Reels (padrão) e Stories (`--stories`: espaço do adesivo de link no meio, y≈1350–1580).

    /usr/bin/python3 cafe_e_jogo.py combo --frame 1 3 5 9 18
    /usr/bin/python3 cafe_e_jogo.py metade [--stories]
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

import no_becas as NB
from no_becas import K, S, E, TB, W, H, FPS, MAR, PET, LAR, AMA, BR, ROSA, Plano, etq, tit, out_back

OUT = K.OUT
PAREDE = os.path.join(NB.NOV, "parede.mp4")
TEM_PAREDE = os.path.exists(PAREDE)
if TEM_PAREDE:
    K.CLIPES["parede"] = (PAREDE, "BECA’S")

FMT = "reels"


def gancho_plano(d):
    if TEM_PAREDE:
        return Plano("parede", 0.5, d, 1.0, z=(1.0, 1.08))
    return Plano("jardim", 5.0, d, 0.9, z=(1.25, 1.38), ay=0.15)


# pares (plano do café, texto do café, plano do jogo, texto do jogo)
def pares(dc, dj):
    p = [(Plano("jardim", 11.4, dc, 0.9, z=(1.05, 1.1), ay=0.3), "UM CANTINHO LINDO",
          Plano("art", 0.6, dj, 1.0), "ART SOCIETY"),
         (Plano("vitrine", 2.4, dc, 1.0, z=(1.0, 1.05)), "UMA VITRINE DESSAS",
          Plano("critter", 0.3, dj, 1.0), "CRITTER KITCHEN"),
         (Plano("brownie", 0.0, dc, 1.0, z=(1.0, 1.06)), "UM BOLO NUVEM",
          Plano("sushi", 0.3, dj, 1.0), "SUSHI GO!"),
         (Plano("jardim", 7.3, dc, 1.0, z=(1.2, 1.28), ay=0.12), "UM TETO COLORIDO",
          Plano("canvas", 1.4, dj, 1.0), "CANVAS")]
    if TEM_PAREDE:
        p.insert(1, (Plano("parede", 3.0, dc, 1.0, z=(1.04, 1.0)), "UMA PAREDE DESSAS",
                     Plano("passaporte", 1.0, dj, 1.0), "PASSAPORTE MUNDO"))
    return p


# ======================================================================== COMBO (corte alternado)
A_GANCHO = 2.4
A_DC, A_DJ = 1.5, 1.5
A_PARES = pares(A_DC, A_DJ)
A_PL = [gancho_plano(A_GANCHO)] + [x for c, _, j, _ in A_PARES for x in (c, j)]
A_INI = NB.inicios(A_PL)
A_VID = sum(p.d for p in A_PL)
A_DUR = A_VID + 5.6



def mais(img, t, t0, cx=W / 2, cy=900, s=1.0):
    """'+' amarelo estourando no corte."""
    if t < t0 or t > t0 + 0.6:
        return
    u = (t - t0) / 0.6
    esc = out_back(min(1, u * 2.2)) * s * (1 - 0.15 * u)
    a = 1.0 if u < 0.7 else max(0.0, 1 - (u - 0.7) / 0.3)
    E.cola(img, tit("+", 300, AMA), cx, cy, -8 + 16 * u, esc, a)


def final(img, t, t0, comenta):
    u = t - t0
    NB.escuro(img, min(140, u * 400))
    NB.balanco(img, t)
    if FMT == "stories":
        K.poe(img, tit("= TARDE DE JOGOS\nNO BECA’S!", 92, AMA), W / 2, 400, t, t0 + 0.1, -2)
        K.poe(img, NB.card_convite(), W / 2, 880, t, t0 + 0.35, 1)
        NB.linha_link(img, t, t0 + 0.9, 1200)
        K.poe(img, etq("MANDA PRA QUEM VAI COM VOCÊ!", 40, BR, MAR), W / 2, 1660, t, t0 + 1.1, -1.5)
    else:
        K.poe(img, tit("= TARDE DE JOGOS\nNO BECA’S!", 92, AMA), W / 2, 520, t, t0 + 0.1, -2)
        K.poe(img, NB.card_convite(), W / 2, 1020, t, t0 + 0.35, 1)
        K.poe(img, etq(comenta, 38, BR, MAR), W / 2, 1440, t, t0 + 1.0, -1.5)


def a_quadro(t):
    if t < A_VID:
        img, k, u = NB.sequencia(A_PL, t, dis=0.0)
        K.marca(img)
        if k == 0:
            K.escurece(img, 1250, 1750, 130)
            K.poe(img, tit("TEM COMBO MELHOR\nQUE CAFÉ + JOGO?", 96, AMA), W / 2, 1480, t, 0.15, -2)
        else:
            par = (k - 1) // 2
            cafe = (k - 1) % 2 == 0
            _, tc, _, tj = A_PARES[par]
            K.escurece(img, 1300, 1720, 120)
            if cafe:
                K.poe(img, etq(tc + "...", 60, BR, MAR), W / 2, 1500, t, A_INI[k] + 0.05, -2)
            else:
                K.poe(img, etq("+ " + tj, 66, AMA, MAR), W / 2, 1500, t, A_INI[k], 2)
                mais(img, t, A_INI[k])
        return img.convert("RGB")
    img = A_PL[0].quadro(A_PL[0].d - 0.01).filter(ImageFilter.GaussianBlur(12))
    final(img, t, A_VID, "COMENTA: QUAL COMBO VOCÊ PEDIA?")
    return img.convert("RGB")


def a_audio():
    ev = [(0.15, S.cartao(), 0.4)]
    for k in range(1, len(A_PL)):
        cafe = (k - 1) % 2 == 0
        ev.append((A_INI[k], S.cartao() if cafe else S.plim(), 0.35 if cafe else 0.45))
        if not cafe:
            ev.append((A_INI[k], S.dado(), 0.25))
    ev += [(A_VID, S.sino(), 0.45), (A_VID + 0.35, S.cartao(), 0.4), (A_VID + 1.0, S.cartao(), 0.3)]
    return ev, S.musica_pop(A_DUR + 0.5, 0.0), 0.42


# ======================================================================== METADE (tela dividida)
B_GANCHO = 2.2
B_D = 2.3
B_PARES = pares(B_D, B_D)
B_CAFE = [gancho_plano(B_GANCHO)] + [c for c, _, _, _ in B_PARES]
B_JOGO = [Plano("taketime", 0.5, B_GANCHO, 1.0)] + [j for _, _, j, _ in B_PARES]
B_INI = NB.inicios(B_CAFE)
B_VID = sum(p.d for p in B_CAFE)
B_DUR = B_VID + 5.6
HM = H // 2


def metade(im, ay=0.5):
    """Faixa de 1080x960 do quadro (corte no meio, um pouco acima)."""
    y0 = int((H - HM) * ay)
    return im.crop((0, y0, W, y0 + HM))


def b_quadro(t):
    if t < B_VID:
        a, k, u = NB.sequencia(B_CAFE, t, dis=0.0)
        b, _, _ = NB.sequencia(B_JOGO, t, dis=0.0)
        img = Image.new("RGBA", (W, H))
        img.paste(metade(a, 0.45), (0, 0))
        img.paste(metade(b, 0.5), (0, HM))
        d = ImageDraw.Draw(img)
        d.rectangle((0, HM - 7, W, HM + 7), fill=MAR)
        K.marca(img)
        if k == 0:
            K.poe(img, etq("METADE CAFÉ...", 60, BR, MAR), W / 2, 760, t, 0.1, -2)
            K.poe(img, etq("...METADE JOGO!", 60, AMA, MAR), W / 2, 1160, t, 0.6, 2)
        else:
            _, tc, _, tj = B_PARES[k - 1]
            K.poe(img, etq(tc, 48, BR, MAR), W / 2, 830, t, B_INI[k] + 0.05, -1.5)
            K.poe(img, etq(tj, 52, AMA, MAR), W / 2, 1090, t, B_INI[k] + 0.2, 1.5)
        E.cola(img, NB.tit("+", 150, AMA), W / 2, HM, 6 * math.sin(t * 3), 1.0 + 0.06 * math.sin(t * 6))
        return img.convert("RGB")
    img = B_CAFE[-1].quadro(B_CAFE[-1].d - 0.01).filter(ImageFilter.GaussianBlur(12))
    final(img, t, B_VID, "COMENTA: CAFÉ OU JOGO, O QUE VEM PRIMEIRO?")
    return img.convert("RGB")


def b_audio():
    ev = [(0.1, S.cartao(), 0.4), (0.6, S.cartao(), 0.4)]
    for k in range(1, len(B_CAFE)):
        ev += [(B_INI[k], S.sopro(0.3), 0.3), (B_INI[k] + 0.2, S.cartao(), 0.3)]
    ev += [(B_VID, S.sino(), 0.45), (B_VID + 0.35, S.cartao(), 0.4), (B_VID + 1.0, S.cartao(), 0.3)]
    return ev, S.musica_cafe(B_DUR + 0.5), 0.45


# ======================================================================== main
PECAS = {"combo": (a_quadro, A_DUR, A_PL, a_audio), "metade": (b_quadro, B_DUR, B_CAFE + B_JOGO, b_audio)}
_QF = None


def render(fi):
    return _QF(fi / FPS).tobytes()


def main():
    global _QF, FMT
    peca = sys.argv[1]
    FMT = "stories" if "--stories" in sys.argv else "reels"
    nome = f"{peca}_stories" if FMT == "stories" else peca
    qf, dur, planos, audiof = PECAS[peca]
    _QF = qf
    K.prepara([p.trecho() for p in planos])
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        K.folha([qf(x) for x in ts], os.path.join(OUT, f"frames_{nome}.jpg"))
        print("ok", dur)
        return
    ev, mus, mg = audiof()
    com, sem = os.path.join(OUT, f"{nome}_com.wav"), os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, dur, ev, mus, musica_ganho=mg, fx_ganho=0.8)
    S.grava(sem, dur, ev, None, fx_ganho=0.8)
    K.entrega(nome, dur, render, com, sem)
    print("ok", nome, dur)


if __name__ == "__main__":
    main()
