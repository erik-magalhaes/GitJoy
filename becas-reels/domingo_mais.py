#!/usr/bin/env python3
"""Mais divulgação do DOMINGO DE JOGOS NO BECA’S (22/nov/2026, pedido dele: "usa vídeos e fotos de jogos").
Tudo com material REAL deles: cenas de jogo na mesa (gravados-reels/brutos/mesa e nov01), a tarde de 20/11
(brutos/nov20) e o Beca’s (brutos/nov06). Reaproveita as peças do `domingo.py` (quadro de vagas, convite, seta).

1. Reels/Stories "DOMINGO É DIA DE..." (~21 s): gancho "O QUE FAZER NO DOMINGO EM MAUÁ?" na parede do Beca’s →
   cortes na batida alternando café e jogo, cada um com o complemento da frase → DOMINGO DE JOGOS + 30 vagas → convite.
2. Carrossel "O QUE ROLA NO DOMINGO DE JOGOS" (6 telas 1080x1350 + stories): polaroides grandes com quadros reais.

    /usr/bin/python3 domingo_mais.py --frame 1 3 6 10 15 19
    /usr/bin/python3 domingo_mais.py --fotos
    /usr/bin/python3 domingo_mais.py
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageOps

import domingo as D
import kit as K
import sons as S
import tarde as T
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA

from motor import FPS, ffmpeg  # noqa: E402

OUT = T.OUT
PASTA = os.path.join(OUT, "domingo_mais")
NOV06 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brutos", "nov06")
for _n, _a in {"parede": "20261106_150726.mp4", "vitrine": "20261106_150657.mp4", "bolo2": "20261106_151311.mp4",
               "jardim": "20261106_150333.mp4"}.items():
    K.CLIPES[_n] = (os.path.join(NOV06, _a), "BECA’S")

BEAT = 60 / 118
CORTE = 2 * BEAT
GANCHO = 2.4
# (clipe, início no bruto, velocidade, complemento de "DOMINGO É DIA DE...")
CORTES = [("art", 0.6, 1.0, "...APRENDER JOGO NOVO"),
          ("vitrine", 2.4, 1.0, "...CAFÉ COM DOCE"),
          ("dia", 13.5, 1.0, "...RIR COM OS AMIGOS"),
          ("sushi", 2.0, 1.0, "...GANHAR (OU NÃO)"),
          ("bolo2", 1.0, 1.2, "...BOLO NUVEM"),
          ("unlock", 2.6, 1.0, "...DESVENDAR MISTÉRIO"),
          ("dia", 3.0, 1.0, "...CONHECER GENTE NOVA"),
          ("sky_dados", 4.0, 1.5, "...PILOTAR UM AVIÃO"),
          ("canvas", 2.0, 1.2, "...PINTAR UM QUADRO")]
T_MONT = GANCHO
T_TIT = T_MONT + len(CORTES) * CORTE
T_CTA = T_TIT + 4.2
DUR = T_CTA + 5.8
TRECHOS = [("parede", 0.2, GANCHO, 1.0)] + [(c, s, CORTE, v) for c, s, v, _ in CORTES]


# ---------------------------------------------------------------- vídeo
def gancho(img, t):
    img.alpha_composite(K.quadro_clip("parede", 0.2, GANCHO, 1.0, t))
    K.escurece(img, 300, 1000, 170)
    K.poe(img, K.titulo("O QUE FAZER\nNO DOMINGO\nEM MAUÁ?", 128, BR), W / 2, 650, t, 0.05, -2)


def montagem(img, t):
    k = min(len(CORTES) - 1, int((t - T_MONT) / CORTE))
    u = t - T_MONT - k * CORTE
    c, s, v, txt = CORTES[k]
    img.alpha_composite(K.quadro_clip(c, s, CORTE, v, u))
    K.escurece(img, 160, 420, 150)
    K.escurece(img, 1220, 1540, 150)
    E.cola(img, E.pilula("DOMINGO É DIA DE...", 50, PET, BR, fonte_titulo=True), W / 2, 290, -2, 1, 1)
    K.poe(img, K.etiqueta(txt, 62, AMA if k % 2 == 0 else BR, MAR), W / 2, 1380, t, T_MONT + k * CORTE,
          2 if k % 2 else -2, d=0.18)


def titulo(img, t):
    img.alpha_composite(D.fundo(t - T_TIT))
    K.poe(img, K.titulo("...JOGO NO\nBECA’S CAFÉ!", 132, LAR), W / 2, 560, t, T_TIT + 0.05, -2)
    K.poe(img, E.pilula(f"DOMINGO DE JOGOS · {D.DATA.split(', ')[-1]}", 46, PET, BR, fonte_titulo=True), W / 2, 760,
          t, T_TIT + 0.35, 1)
    if t > T_TIT + 0.6:
        E.cola(img, D.painel_anim(t, T_TIT + 0.6), W / 2, 1150, 0, 0.82, 1)
    K.poe(img, K.titulo("SÓ 30 VAGAS!", 110, D.VERM), W / 2, 1560, t, T_TIT + 2.4, 2)


def cta(img, t, modo):
    D.cta(img, t - T_CTA + D.T_CTA, modo)


def quadro(t, modo="reels"):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < T_MONT:
        gancho(img, t)
    elif t < T_TIT:
        montagem(img, t)
    elif t < T_CTA:
        titulo(img, t)
    else:
        cta(img, t, modo)
    for tb in (T_MONT, T_TIT, T_CTA):
        dd = t - tb
        if 0 <= dd < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - dd / 0.12)))))
    if t < T_TIT:
        K.marca(img)
    return img.convert("RGB")


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def audio(nome):
    ev = [(0.05, S.sopro(0.4), 0.3), (T_MONT, S.estouro(), 0.4)]
    ev += [(T_MONT + k * CORTE, S.tic(k % 2 == 0), 0.35) for k in range(len(CORTES))]
    ev += [(T_TIT, S.sino(), 0.45), (T_TIT + 0.05, S.estouro(), 0.5)]
    ev += [(T_TIT + 0.85 + k * 0.045, S.tic(k % 2 == 0), 0.15) for k in range(D.VAGAS)]
    ev += [(T_TIT + 2.4, S.plim(), 0.5), (T_CTA, S.sopro(0.5, False), 0.4), (T_CTA + 0.35, S.carta_vira(), 0.5)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.75)
    S.grava(sem, DUR, ev, None, fx_ganho=0.75)
    return com, sem


# ---------------------------------------------------------------- carrossel
CW, CH = 1080, 1350


def quadro_de(arq, seg, w, h, ay=0.5):
    """Quadro real de um vídeo (ou foto) recortado em w x h."""
    if arq.lower().endswith(".jpg"):
        im = ImageOps.exif_transpose(Image.open(arq)).convert("RGB")
    else:
        dst = os.path.join(OUT, "_fotos", f"dm_{os.path.basename(arq)}_{seg:.1f}.jpg")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(seg), "-i", arq, "-frames:v", "1", "-vf",
                            "hqdn3d=3:3:4:4,eq=contrast=1.03:saturation=1.05,unsharp=5:5:0.3", "-q:v", "2", dst],
                           check=True)
        im = Image.open(dst).convert("RGB")
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, ay))


def polaroide(arq, seg, w, h, legenda, ay=0.5):
    f = quadro_de(arq, seg, w, h, ay).convert("RGBA")
    m = 24
    p = Image.new("RGBA", (w + 2 * m, h + m + 96), D.CREME + (255,))
    p.alpha_composite(f, (m, m))
    d = ImageDraw.Draw(p)
    d.rectangle((0, 0, p.width - 1, p.height - 1), outline=MAR, width=5)
    d.text((p.width / 2, h + m + 48), legenda, font=D.cabe(legenda, w, 46), fill=MAR, anchor="mm")
    sh = Image.new("RGBA", (p.width + 18, p.height + 18), (0, 0, 0, 0))
    sh.paste(MAR + (255,), (16, 16, p.width + 16, p.height + 16))
    sh.alpha_composite(p, (0, 0))
    return sh


def fita(img, x, y, rot):
    f = Image.new("RGBA", (190, 54), (250, 224, 150, 210))
    E.cola(img, f, x, y, rot, 1, 1)


DIA = os.path.join(D.BRUTO, "180822.mp4")
MESA = os.path.join(K.BR_, "mesa")
FOTO = lambda n: os.path.join(D.BRUTO, n)  # noqa: E731


def base_c(seed=3.0):
    img = T.fundo().copy().crop((0, 0, CW, CH))
    T.guarda_chuvas(img, seed)
    return img


def tela_capa():
    img = base_c(2.2)
    E.cola(img, polaroide(DIA, 13.5, 330, 430, "rindo"), 245, 880, -7, 1, 1)
    E.cola(img, polaroide(os.path.join(MESA, "sushi.mp4"), 2.4, 330, 430, "jogando"), 835, 880, 6, 1, 1)
    E.cola(img, polaroide(os.path.join(NOV06, "20261106_151311.mp4"), 1.6, 330, 430, "e comendo!"), 540, 940, -1, 1, 1)
    E.cola(img, E.titulo("O QUE ROLA NO\nDOMINGO DE JOGOS?", 88, LAR), 540, 440, -2, 1, 1)
    E.cola(img, E.pilula("ARRASTA PRO LADO!", 38, PET, BR, fonte_titulo=True), 540, 1280, 1, 1, 1)
    return img.convert("RGB")


def tela(arq, seg, leg, titulo, texto, ay=0.5, rot=-3, seed=3.0):
    img = base_c(seed)
    E.cola(img, E.titulo(titulo, 96, LAR), 540, 420, -2, 1, 1)
    p = polaroide(arq, seg, 760, 560, leg, ay)
    E.cola(img, p, 540, 870, rot, 1, 1)
    fita(img, 540, 870 - p.height / 2 + 8, rot + 4)
    E.cola(img, E.pilula(texto, 32, BR, MAR), 540, 1250, 1, 1, 1)
    return img.convert("RGB")


def tela_final(link=False):
    img = base_c(4.0)
    E.cola(img, TB.parceria(90), 540, 330, 0, 1, 1)
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 110, D.VERM), 540, 500, -2, 1, 1)
    E.cola(img, D.card(), 540, 880, 0, 0.92, 1)
    E.cola(img, E.pilula(f"RESERVE NO WHATSAPP {TB.WHATS}", 38, PET, BR, fonte_titulo=True), 540, 1200, -1, 1, 1)
    E.cola(img, E.pilula("Comenta: com quem você vem?", 36, BR, MAR), 540, 1280, 1, 1, 1)
    return img.convert("RGB")


TELAS = [
    tela_capa,
    lambda: tela(os.path.join(MESA, "art_society.mp4"), 1.0, "Art Society", "A GENTE ENSINA",
                 "Nunca jogou? Melhor ainda: a gente explica tudo na mesa.", seed=2.6),
    lambda: tela(DIA, 39.6, "a mesa de 20/11", "35 JOGOS NA MESA",
                 "Do jogo rapidinho de cartas ao de estratégia.", rot=3, seed=3.4),
    lambda: tela(os.path.join(NOV06, "20261106_150657.mp4"), 2.6, "a vitrine do Beca’s", "CAFÉ + JOGO",
                 "Dos seus R$ 40, R$ 25 viram consumação no café.", seed=2.9),
    lambda: tela(DIA, 3.0, "gente nova em cada mesa", "VEM DO SEU JEITO",
                 "Sozinho, em dupla ou com a galera: tem mesa pra todo mundo.", ay=0.08, rot=2, seed=3.8),
    tela_final,
]


def story_de(tela_img, ultima=False):
    st = D.fundo(3.0)
    st.alpha_composite(tela_img.convert("RGBA"), (0, 285 if not ultima else 160))
    if ultima:
        E.cola(st, E.pilula("garanta sua vaga aqui:", 40, BR, MAR), W / 2, 1560, 0, 1, 1)
        E.cola(st, D.seta(), W / 2, 1660, 0, 0.5, 1)
    return st.convert("RGB")


def fotos():
    os.makedirs(os.path.join(PASTA, "stories"), exist_ok=True)
    ims = [f() for f in TELAS]
    for k, im in enumerate(ims):
        im.save(os.path.join(PASTA, f"{k + 1:02d}.png"))
        story_de(im, k == len(ims) - 1).save(os.path.join(PASTA, "stories", f"story_{k + 1:02d}.png"))
    sh = Image.new("RGB", (len(ims) * 360, 450), "white")
    for k, im in enumerate(ims):
        sh.paste(im.resize((360, 450)), (k * 360, 0))
    sh.save(os.path.join(PASTA, "previa.jpg"), quality=88)
    print("ok", PASTA)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--fotos" in sys.argv:
        fotos()
        return
    K.prepara(TRECHOS)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        md = "stories" if "--stories" in sys.argv else "reels"
        K.folha([quadro(x, md) for x in ts], os.path.join(OUT, "frames_domingo_mais.jpg"))
        print("ok", DUR)
        return
    for nome, rnd in (("dia_de_reels", render_reels), ("dia_de_stories", render_stories)):
        com, sem = audio(nome)
        K.entrega(nome, DUR, rnd, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
