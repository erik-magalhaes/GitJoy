#!/usr/bin/env python3
"""OBRIGADO da 1ª Tarde de Jogos (20/nov/2026). 2ª rodada (pedido dele): SEM número de pessoas, SEM "vai ter próxima?",
sem carrossel; destaques = 6 horas, 35 jogos diferentes, muita gente nova; agradece @becascafe e @espacofamilyheaven. Material DELES no Drive de
brutos → brutos/nov20/ (fora do git): 180822.mp4 (46 s, câmera passeando pelas mesas cheias e depois os jogos no
balcão), fotos 151849 Cores com Dicas, 151857 Dixit, 151917 Hot Streak, 151926 Marrakech, 112018 a mesa de jogos
montada, IMG_194900 = selfie Erik + Jéssica na porta do Beca’s (câmera da frente = ESPELHADA → flip).
O 144913 é o repost do story do @becascafe (com a interface do Instagram) e o IMG_194906 um print: não usados.

    /usr/bin/python3 obrigado.py --frame 1 4 11 15 20      # out/frames_obrigado.jpg
    /usr/bin/python3 obrigado.py --fotos                   # carrossel 1080x1350 + stories → out/obrigado/
    /usr/bin/python3 obrigado.py                           # Reels + Stories em vídeo
"""
import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import kit as K
import sons as S
import tarde as T
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA

from motor import FPS, out_back  # noqa: E402

OUT = T.OUT
BRUTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brutos", "nov20")
K.CLIPES["dia"] = (os.path.join(BRUTO, "180822.mp4"), "")
BEAT = 60 / 118
CORTE = 2 * BEAT
GANCHO = 2.6
# montagem: trechos do vídeo (início no bruto) ou fotos, um por corte
MONT = [("v", 3.0), ("v", 5.0), ("f", "20261120_151857.jpg"), ("v", 13.5), ("v", 15.5), ("f", "20261120_151917.jpg"),
        ("v", 27.6), ("f", "20261120_151926.jpg"), ("v", 17.6), ("f", "20261120_151849.jpg")]
ROTULOS = ["MESAS CHEIAS!", "MESAS CHEIAS!", "GENTE NOVA EM CADA MESA", "GENTE NOVA EM CADA MESA",
           "A GENTE ENSINOU TUDO", "A GENTE ENSINOU TUDO", "MUITA RISADA...", "...E COMPETIÇÃO!", "CAFÉ + JOGO",
           "CAFÉ + JOGO"]
# nome do jogo que aparece nas fotos (selo pequeno no alto)
NOME_FOTO = {"20261120_151857.jpg": "DIXIT", "20261120_151917.jpg": "HOT STREAK", "20261120_151926.jpg": "MARRAKECH",
             "20261120_151849.jpg": "CORES COM DICAS"}
T_MONT = GANCHO
T_JOGOS = T_MONT + len(MONT) * CORTE
D_JOGOS = 3.2
T_SELFIE = T_JOGOS + D_JOGOS
D_SELFIE = 4.2
T_FIM = T_SELFIE + D_SELFIE
DUR_BASE = T_FIM + 5.0
# 3ª rodada (21/nov): abertura com o vídeo do @becascafe (053620, repost do story deles com o adesivo "LET'S PLAY!":
# guarda-chuvinhas → entrando no salão vazio → mesa com os jogos arrumados), a 1,3x
K.CLIPES["intro"] = (os.path.join(BRUTO, "053620.mp4"), "")
D_INTRO = 6.6
VEL_INTRO = 1.3
DUR_TOTAL = DUR_BASE + D_INTRO
DUR = DUR_TOTAL
TRECHOS = [("intro", 0.0, D_INTRO, VEL_INTRO), ("dia", 0.8, GANCHO, 1.0), ("dia", 39.6, D_JOGOS, 1.0)] + \
    [("dia", s, CORTE, 1.0) for k, s in MONT if k == "v"]


@lru_cache(None)
def foto(nome, w=W, h=H):
    im = ImageOps.exif_transpose(Image.open(os.path.join(BRUTO, nome))).convert("RGB")
    if nome.startswith("IMG_194900"):
        im = ImageOps.mirror(im)
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h)).convert("RGBA")


def zoom(im, u, z=0.06):
    """Aproximação lenta (Ken Burns)."""
    e = 1 + z * u
    w, h = im.size
    cw, ch = w / e, h / e
    return im.crop((int((w - cw) / 2), int((h - ch) / 2), int((w + cw) / 2), int((h + ch) / 2))).resize((w, h))


@lru_cache(None)
def numero(n, s=330):
    return E.titulo(str(n), s, AMA)


def gancho(img, t):
    img.alpha_composite(K.quadro_clip("dia", 0.8, GANCHO, 1.0, t))
    K.escurece(img, 280, 1200, 175)
    # 13:00 → 19:00 no relógio: "6 HORAS DE DIVERSÃO" (ele: não falar quantas pessoas foram)
    h = int(min(6, max(0, (t - 0.3) / 1.4 * 6)))
    K.poe(img, K.titulo("FORAM", 96, BR), W / 2, 420, t, 0.05, -2)
    if t > 0.3:
        bate = 1 + 0.12 * max(0, 1 - (t - 1.7) / 0.25) if t > 1.7 else 1
        E.cola(img, numero(h), W / 2, 680, -3, bate, 1)
    K.poe(img, K.titulo("HORAS DE\nDIVERSÃO!", 110, BR), W / 2, 965, t, 1.75, 2)
    K.poe(img, E.pilula("NA NOSSA TARDE DE JOGOS", 44, LAR, BR, fonte_titulo=True), W / 2, 1150, t, 1.95, -1)


def montagem(img, t):
    k = min(len(MONT) - 1, int((t - T_MONT) / CORTE))
    u = (t - T_MONT - k * CORTE)
    tipo, ref = MONT[k]
    if tipo == "v":
        img.alpha_composite(K.quadro_clip("dia", ref, CORTE, 1.0, u))
    else:
        img.alpha_composite(zoom(foto(ref), u / CORTE))
    K.escurece(img, 1180, 1560, 150)
    if tipo == "f" and ref in NOME_FOTO:
        E.cola(img, E.pilula(NOME_FOTO[ref], 40, AMA, MAR, fonte_titulo=True), W / 2, 300, 2, 1, 1)
    rot = ROTULOS[k]
    t0 = T_MONT + (k - (1 if k > 0 and ROTULOS[k - 1] == rot else 0)) * CORTE
    K.poe(img, K.etiqueta(rot, 64, AMA, MAR), W / 2, 1380, t, t0, -2 if k % 4 < 2 else 2)
    # contador fixo no canto
    E.cola(img, E.pilula("TARDE DE JOGOS", 34, PET, BR, fonte_titulo=True), 230, 150, -3, 1, 1)


def jogos(img, t):
    u = t - T_JOGOS
    img.alpha_composite(K.quadro_clip("dia", 39.6, D_JOGOS, 1.0, u))
    K.escurece(img, 1180, 1560, 150)
    K.poe(img, K.etiqueta("35 JOGOS DIFERENTES!", 62, LAR, BR), W / 2, 1380, t, T_JOGOS + 0.1, -2)


def selfie(img, t):
    u = (t - T_SELFIE) / D_SELFIE
    img.alpha_composite(zoom(foto("IMG_194900_261.jpg" if os.path.exists(os.path.join(BRUTO, "IMG_194900_261.jpg"))
                                  else "IMG_194900.jpg"), u, 0.05))
    K.escurece(img, 1150, 1620, 170)
    K.poe(img, K.titulo("FOI DEMAIS!", 150, AMA), W / 2, 1290, t, T_SELFIE + 0.3, -3)
    K.poe(img, E.pilula("uma tarde inteira de jogo, café e gente nova", 38, BR, MAR), W / 2, 1440, t,
          T_SELFIE + 0.7, 1)


def final(img, t, modo):
    """Divulgação do evento (21/nov, ele: "não é só agradecimento, é sobre o evento"): convite pra levar a experiência
    pro evento da pessoa + agradecimento no pé (sem o "vai ter próxima?")."""
    base = T.fundo().copy()
    T.guarda_chuvas(base, t - T_FIM + 3)
    img.alpha_composite(base)
    K.poe(img, E.logo(300), W / 2, 540, t, T_FIM + 0.05)
    K.poe(img, K.titulo("QUER UMA TARDE\nASSIM NO SEU\nEVENTO?", 112, LAR), W / 2, 830, t, T_FIM + 0.3, -2)
    K.poe(img, E.pilula("A gente leva os jogos e ensina todo mundo!", 40, PET, BR, fonte_titulo=True), W / 2, 1060, t,
          T_FIM + 0.6, 1)
    K.poe(img, E.pilula(f"WHATSAPP {TB.WHATS}", 44, LAR, BR, fonte_titulo=True), W / 2, 1150, t, T_FIM + 0.8, -1)
    K.poe(img, E.pilula("Obrigado a todo mundo que veio jogar com a gente,", 32, BR, MAR), W / 2, 1290, t, T_FIM + 1.1, 1)
    K.poe(img, E.pilula("ao @becascafe e ao @espacofamilyheaven!", 32, AMA, MAR), W / 2, 1365, t, T_FIM + 1.25, -1)
    K.poe(img, E.pilula("@suavez_bg", 34, AMA, MAR, fonte_titulo=True), W / 2, 1650, t, T_FIM + 1.4, 0)


def intro(t):
    img = K.quadro_clip("intro", 0.0, D_INTRO, VEL_INTRO, t)
    K.escurece(img, 180, 520, 150)
    K.poe(img, K.titulo("ANTES DE\nABRIR AS PORTAS...", 92, BR), W / 2, 340, t, 0.1, -2)
    if t > 4.2:
        K.escurece(img, 1180, 1460, 150)
        K.poe(img, K.etiqueta("TUDO PRONTO PRA JOGAR!", 62, AMA, MAR), W / 2, 1320, t, 4.3, 2)
    K.marca(img)
    return img.convert("RGB")


def quadro(t, modo="reels"):
    if t < D_INTRO:
        return intro(t)
    t -= D_INTRO
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < T_MONT:
        gancho(img, t)
    elif t < T_JOGOS:
        montagem(img, t)
    elif t < T_SELFIE:
        jogos(img, t)
    elif t < T_FIM:
        selfie(img, t)
    else:
        final(img, t, modo)
    # flash rápido nas viradas de bloco
    for tb in (0.0, T_MONT, T_JOGOS, T_SELFIE, T_FIM):
        dd = t - tb
        if 0 <= dd < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - dd / 0.12)))))
    if t < T_FIM:
        K.marca(img)
    return img.convert("RGB")


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def audio(nome):
    ev = [(0.3 + j * 1.4 / 6, S.tic(), 0.35) for j in range(6)] + [(1.72, S.estouro(), 0.6), (1.75, S.plim(), 0.5)]
    ev += [(T_MONT + k * CORTE, S.sopro(0.25), 0.3) for k in range(len(MONT))]
    ev += [(T_JOGOS, S.sopro(0.4), 0.4), (T_SELFIE, S.sino(), 0.45), (T_SELFIE + 0.3, S.estouro(), 0.5),
           (T_FIM, S.sopro(0.5, False), 0.4), (T_FIM + 0.3, S.plim(), 0.5)]
    ev = [(t0 + D_INTRO, x, g) for t0, x, g in ev] + [(0.1, S.sopro(0.4), 0.3), (4.3, S.plim(), 0.4)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.42, fx_ganho=0.75)
    S.grava(sem, DUR, ev, None, fx_ganho=0.75)
    return com, sem


# ------------------------------------------------------------------------------------------------ carrossel
CW, CH = 1080, 1350
LEG = {"20261120_151849.jpg": "Cores com Dicas", "20261120_151857.jpg": "Dixit",
       "20261120_151917.jpg": "Hot Streak", "20261120_151926.jpg": "Marrakech"}


def fundo_c(seed=0):
    base = T.fundo().copy().crop((0, 0, CW, CH))
    T.guarda_chuvas(base, 2.0 + seed)
    return base


def polaroide(nome, w=640):
    f = ImageOps.exif_transpose(Image.open(os.path.join(BRUTO, nome))).convert("RGBA")
    f = f.resize((w, int(f.height * w / f.width)), Image.LANCZOS)
    m = 26
    p = Image.new("RGBA", (w + 2 * m, f.height + m + 110), TB.CREME + (255,))
    p.alpha_composite(f, (m, m))
    d = ImageDraw.Draw(p)
    d.rectangle((0, 0, p.width - 1, p.height - 1), outline=MAR, width=5)
    d.text((p.width / 2, f.height + m + 55), LEG.get(nome, ""), font=E.lilita(54), fill=MAR, anchor="mm")
    sh = Image.new("RGBA", (p.width + 24, p.height + 24), (0, 0, 0, 0))
    sh.paste(MAR + (255,), (16, 16, p.width + 16, p.height + 16))
    sh.alpha_composite(p, (0, 0))
    return sh


def capa_c():
    img = foto("IMG_194900.jpg", CW, CH).copy()
    K.escurece(img, 760, 1350, 210) if False else None
    g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for y in range(700, CH):
        gd.line((0, y, CW, y), fill=(25, 14, 6, int(220 * min(1, (y - 700) / 420))))
    img.alpha_composite(g)
    E.cola(img, E.titulo("23 PESSOAS!", 150, AMA), CW / 2, 1010, -3, 1, 1)
    E.cola(img, E.pilula("NA NOSSA 1ª TARDE DE JOGOS · OBRIGADO!", 38, LAR, BR, fonte_titulo=True), CW / 2, 1160, 1, 1, 1)
    E.cola(img, E.logo(170), CW - 120, 90, 0, 1, 1)
    return img.convert("RGB")


def tela_foto(nome, k):
    img = fundo_c(k)
    p = polaroide(nome, 600 if nome != "20261120_112018.jpg" else 820)
    s = min(1.0, 1080 / p.height)
    E.cola(img, p, CW / 2, 760, [-3, 2, -2, 3][k % 4], s, 1)
    return img.convert("RGB")


def tela_fim():
    img = fundo_c(9)
    E.cola(img, TB.parceria(120), CW / 2, 420, 0, 1, 1)
    E.cola(img, E.titulo("VAI TER\nPRÓXIMA?", 150, LAR), CW / 2, 700, -2, 1, 1)
    E.cola(img, E.pilula("Comenta EU VOU que a gente te avisa!", 42, PET, BR, fonte_titulo=True), CW / 2, 960, 1, 1, 1)
    E.cola(img, E.pilula("Obrigado a todo mundo que veio e ao Beca’s Café!", 32, BR, MAR), CW / 2, 1050, -1, 1, 1)
    E.cola(img, E.logo(200), CW / 2, 1210, 0, 1, 1)
    return img.convert("RGB")


def story_de(tela):
    st = T.fundo().copy()
    T.guarda_chuvas(st, 3.0)
    st.alpha_composite(tela.convert("RGBA"), (0, 285))
    return st.convert("RGB")


def fotos():
    d = os.path.join(OUT, "obrigado")
    os.makedirs(os.path.join(d, "stories"), exist_ok=True)
    telas = [capa_c()] + [tela_foto(n, k) for k, n in enumerate(["20261120_151857.jpg", "20261120_151917.jpg",
                                                                 "20261120_151926.jpg", "20261120_151849.jpg"])]
    telas.append(tela_fim())
    for k, im in enumerate(telas):
        im.save(os.path.join(d, f"{k + 1:02d}.png"))
        story_de(im).save(os.path.join(d, "stories", f"story_{k + 1:02d}.png"))
    sh = Image.new("RGB", (len(telas) * 360, 450), "white")
    for k, im in enumerate(telas):
        sh.paste(im.resize((360, 450)), (k * 360, 0))
    sh.save(os.path.join(d, "previa.jpg"), quality=88)
    print("ok", d)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--fotos" in sys.argv:
        fotos()
        return
    K.prepara(TRECHOS)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_obrigado.jpg"))
        print("ok", DUR)
        return
    for nome, rnd in (("obrigado_reels", render_reels),):
        com, sem = audio(nome)
        K.entrega(nome, DUR, rnd, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
