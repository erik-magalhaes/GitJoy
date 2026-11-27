#!/usr/bin/env python3
"""CONVITE da Tarde de Jogos no Beca’s com os MASCOTES (12/nov/2026, pedido dele): a salsicha (Jéssica; até 13/nov era uma capivara) e a coruja (Erik)
em 3D, recortadas das folhas do Gemini (`mascote/assets/poses/`), no visual das guarda-chuvinhas.

10 s: guarda-chuvinhas caem; a salsicha passa de patinete trazendo os jogos; a coruja aponta para o calendário pendurado
(NOVEMBRO / 20, caneta circula); a salsicha acena; "VEM JOGAR COM A GENTE!", data/horário, endereço e preço; no fim os
dois trocam de pose (joinha). Stories: "garanta sua mesa aqui:" + seta e y≈1440–1600 LIVRE para o adesivo de link.
Reels: "Comenta: qual jogo você quer aprender?" + WhatsApp no lugar do espaço do link.

    /usr/bin/python3 convite_mascotes.py --frame 1.5 4 9      # out/frames_convite_mascotes.jpg
    /usr/bin/python3 convite_mascotes.py [--reels]            # out/convite_mascotes_{stories|reels}_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
import story_becas as SB
import tarde as T
import lembrete_becas as LB
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA, out_back

from motor import FPS  # noqa: E402

OUT = T.OUT
POSES = os.path.join(T.REPO, "mascote", "assets", "poses")
REELS = "--reels" in sys.argv
DUR = 10.0
LB.KC, LB.W_UMB, LB.FIO = 0.68, 220, 150   # calendário menor, mais alto
T_CIRC = (2.2, 2.9)


@lru_cache(None)
def pose(nome, h, espelha=False):
    im = Image.open(os.path.join(POSES, nome + ".png")).convert("RGBA")
    im = im.resize((int(im.width * h / im.height), int(h)), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if espelha else im


@lru_cache(None)
def sombra(w):
    im = Image.new("RGBA", (int(w * 1.4), 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((w * 0.2, 20, w * 1.2, 60), fill=MAR + (70,))
    return im.filter(ImageFilter.GaussianBlur(10))


def mascote(img, nome, h, cx, base, t, t0, espelha=False, fase=0.0):
    """Personagem com os pés em `base`: entra pulando (escala out_back) e depois respira/balança de leve."""
    if t < t0:
        return
    u = min(1.0, (t - t0) / 0.45)
    s = out_back(u, 1.6)
    p = pose(nome, h, espelha)
    bob = 6 * math.sin(2 * math.pi * (t - t0) / 1.6 + fase)
    sq = 1 + 0.015 * math.sin(2 * math.pi * (t - t0) / 0.8 + fase)
    w2, h2 = max(1, int(p.width * s / sq)), max(1, int(p.height * s * sq))
    q = p.resize((w2, h2), Image.BICUBIC)
    sh = sombra(p.width * 0.8)
    img.alpha_composite(sh, (int(cx - sh.width / 2), int(base - 45)))
    img.alpha_composite(q, (int(cx - w2 / 2), int(base - h2 + bob * 0.4)))


def patinete(img, t):
    """A salsicha de patinete atravessa a tela trazendo os jogos (0,6–3,0 s)."""
    t0, t1 = 0.6, 3.0
    if not t0 <= t <= t1:
        return
    u = (t - t0) / (t1 - t0)
    p = pose("salsicha_patinete", 420)
    x = -p.width + u * (W + 2 * p.width)
    y = 1590 - p.height + 6 * math.sin(2 * math.pi * t * 4)
    for k in range(3):  # linhas de velocidade
        d = ImageDraw.Draw(img)
        yy = 1590 - 90 - k * 55
        d.line((x - 40 - k * 30, yy, x - 160 - k * 30, yy), fill=MAR + (120,), width=6)
    img.alpha_composite(p, (int(x), int(y)))


@lru_cache(None)
def seta():
    return LB.seta_baixo()


def quadro(t):
    img = T.fundo().copy()
    T.guarda_chuvas(img, t)
    # calendário pendurado (entra caindo)
    ang = SB.balanco(t, 2.4, 2.5)
    u = min(1, max(0, (t - T_CIRC[0]) / (T_CIRC[1] - T_CIRC[0])))
    entra = min(1.0, max(0.0, (t - 0.3) / 0.6))
    if entra > 0:
        cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        SB.pendulo(cam, W / 2 + 40, ang, LB.W_UMB, ROSA, LB.FIO, "cal_lembrete", LB.circulo(u) if u > 0 else None)
        img.alpha_composite(cam, (0, int(-(1 - out_back(entra, 1.2)) * 900)))
    # a dupla dos dois lados do calendário; no fim trocam para o joinha
    fim = t >= 6.2
    mascote(img, "coruja_joinha" if fim else "coruja_apontando", 490, 215, 915, t, 1.6, fase=0.5)
    mascote(img, "salsicha_joinha" if fim else "salsicha_acenando", 490, 870, 915, t, 1.9, espelha=not fim, fase=1.7)
    patinete(img, t)
    T.poe(img, T.titulo("VEM JOGAR\nCOM A GENTE!", 104, LAR), W / 2, 1015, t, 3.0, -2)
    T.poe(img, E.pilula("TARDE DE JOGOS NO BECA’S CAFÉ", 44, PET, BR, fonte_titulo=True), W / 2, 1150, t, 3.4, 1)
    T.poe(img, TB.selo_data(36), W / 2, 1222, t, 3.6, -1)
    T.poe(img, TB.selo_endereco(29), W / 2, 1286, t, 3.8, 1)
    T.poe(img, E.pilula("R$ 30 · R$ 15 VIRAM CONSUMAÇÃO", 32, AMA, MAR, fonte_titulo=True), W / 2, 1346, t, 4.0, -1)
    if REELS:
        T.poe(img, E.pilula("Comenta: qual jogo você quer aprender?", 38, BR, MAR), W / 2, 1450, t, 4.4, 1)
        T.poe(img, E.pilula("RESERVE NO WHATSAPP " + TB.WHATS, 36, PET, BR, fonte_titulo=True), W / 2, 1530, t, 4.7, -1)
    else:
        if t > 4.4:  # área y≈1450–1600 livre para o adesivo de link
            a = min(1, (t - 4.4) / 0.3)
            bob = 8 * math.sin(2 * math.pi * (t - 4.4) / 1.2)
            txt = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
            ImageDraw.Draw(txt).text((W / 2 - 60, 40), "garanta sua mesa aqui:", font=E.fig(40, 900), fill=MAR,
                                     anchor="mm")
            txt.alpha_composite(seta(), (int(W / 2 + 195), int(bob - 8)))
            if a < 1:
                txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
            img.alpha_composite(txt, (0, 1360))
        T.poe(img, E.pilula("ou no WhatsApp " + TB.WHATS, 34, BR, MAR), W / 2, 1665, t, 4.7, 0)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(nome):
    ev = [(0.08 * k + 0.4, S.sino() * 0.25, 0.25) for k in range(len(T.CHUVAS))]
    ev += [(0.6, S.sopro(0.6), 0.45), (0.5, S.sino(), 0.3), (1.6, S.plim(), 0.4), (1.9, S.plim(), 0.4),
           (T_CIRC[0], S.arrasta(T_CIRC[1] - T_CIRC[0]), 0.45), (3.0, S.cartao(), 0.4), (3.4, S.cartao(), 0.3),
           (3.6, S.cartao(), 0.3), (3.8, S.cartao(), 0.3), (4.0, S.cartao(), 0.3), (4.4, S.sino(), 0.35),
           (6.2, S.plim(), 0.45)]
    mus = S.musica_cafe(DUR + 0.5)
    com = os.path.join(OUT, nome + "_com.wav")
    sem = os.path.join(OUT, nome + "_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


def main():
    os.makedirs(OUT, exist_ok=True)
    nome = "convite_mascotes_" + ("reels" if REELS else "stories")
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if x[0].isdigit()]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_convite_mascotes.jpg"))
        print("ok")
        return
    com, sem = audio(nome)
    K.entrega(nome, DUR, render, com, sem)
    print("ok")


if __name__ == "__main__":
    main()
