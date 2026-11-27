#!/usr/bin/env python3
"""Carrossel "VAI TER MAIS UM!" do Domingo de Jogos 13/12 (24/nov, ela: "para hoje um carrossel falando que vamos ter
mais um evento no dia 13/12, com todas as informações e um pouquinho de foto; pegue frames BONS, com as pessoas se
divertindo, sem fotos esquisitas").

Visual do kit de fim de ano (guarda-chuvinhas + pisca-pisca, `domingo.fundo`); as fotos ficam em POLAROIDES PENDURADAS
nos guarda-chuvas (como no vídeo `domingo_festa.py`). Quadros escolhidos no olho entre os nítidos (Laplaciano) do
repost do @becascafe (`brutos/nov24/festa.mp4`, recortado sem a moldura do story) + fotos deles de 20/11. O coraçãozinho
branco que o story pôs no meio da tela sai com inpaint (`sem_coracao`).

    /usr/bin/python3 domingo_carrossel.py      # out/domingo_carrossel/01..06.png + stories/ + previa.jpg
"""
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

import domingo as D
import domingo_mais as M
from tarde import E, TB, W, MAR, PET, LAR, AMA, BR, ROSA
from motor import ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(D.OUT, "domingo_carrossel")
FESTA = os.path.join(ROOT, "brutos", "nov24", "festa.mp4")
NOV20 = os.path.join(ROOT, "brutos", "nov20")
CW, CH = 1080, 1350
VERM = D.VERM


def sem_coracao(a):
    """O adesivo de coração do story fica sempre no mesmo lugar do quadro recortado (≈ 285, 415)."""
    x0, y0, x1, y1 = 240, 370, 335, 465
    r = a[y0:y1, x0:x1]
    g = cv2.cvtColor(r, cv2.COLOR_BGR2GRAY).astype(int)
    gb = cv2.cvtColor(cv2.medianBlur(r, 15), cv2.COLOR_BGR2GRAY).astype(int)
    m = ((g - gb > 18) & (g > 150)).astype(np.uint8) * 255
    M_ = np.zeros(a.shape[:2], np.uint8)
    M_[y0:y1, x0:x1] = cv2.dilate(m, np.ones((5, 5), np.uint8))
    return cv2.inpaint(a, M_, 6, cv2.INPAINT_TELEA)


def quadro_festa(t):
    dst = os.path.join(D.OUT, "_fotos", f"festa_{t:.2f}.png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(t), "-i", FESTA, "-frames:v", "1", "-vf",
                        "crop=576:770:72:215,hqdn3d=2:2:3:3,eq=contrast=1.04:saturation=1.06,unsharp=5:5:0.5", dst],
                       check=True)
        cv2.imwrite(dst, sem_coracao(cv2.imread(dst)))
    return Image.open(dst).convert("RGB")


def quadro_dia(t):
    dst = os.path.join(D.OUT, "_fotos", f"dia_{t:.2f}.png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(NOV20, "180822.mp4"),
                        "-frames:v", "1", "-vf", "hqdn3d=2:2:3:3,eq=contrast=1.04:saturation=1.06,unsharp=5:5:0.4", dst],
                       check=True)
    return Image.open(dst).convert("RGB")


def quadro_cafe(t):
    dst = os.path.join(D.OUT, "_fotos", f"cafe150333_{t:.2f}.png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(t), "-i",
                        os.path.join(ROOT, "brutos", "nov06", "20261106_150333.mp4"), "-frames:v", "1", "-vf",
                        "hqdn3d=2:2:3:3,eq=contrast=1.04:saturation=1.06,unsharp=5:5:0.4", dst], check=True)
    return Image.open(dst).convert("RGB")


def foto(nome):
    return ImageOps.exif_transpose(Image.open(os.path.join(NOV20, nome))).convert("RGB")


def polaroide(im, w, h, legenda, ay=0.5):
    f = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, ay)).convert("RGBA")
    m = 22
    p = Image.new("RGBA", (w + 2 * m, h + m + 84), D.CREME + (255,))
    p.alpha_composite(f, (m, m))
    d = ImageDraw.Draw(p)
    d.rectangle((m, m, m + w - 1, m + h - 1), outline=MAR, width=3)
    d.rectangle((0, 0, p.width - 1, p.height - 1), outline=MAR, width=5)
    d.text((p.width / 2, h + m + 42), legenda, font=D.cabe(legenda, w, 40), fill=MAR, anchor="mm")
    sh = Image.new("RGBA", (p.width + 30, p.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((14, 16, p.width + 14, p.height + 16), fill=MAR + (150,))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(p, (0, 0))
    return sh


def pendura(img, pol, x, y_umb, cor, rot=0, w_umb=170):
    """Guarda-chuva no alto (com fio do teto) segurando a polaroide por 2 fios."""
    umb = guarda_hd(w_umb, cor, 3)
    hook = 14 + 0.75 * w_umb + 2
    S_ = int(max(pol.width, umb.width) + 80)
    alt = int(hook + 30 + pol.height + 40)
    sp = Image.new("RGBA", (S_, alt), (0, 0, 0, 0))
    cx = S_ / 2
    sp.alpha_composite(umb, (int(cx - umb.width / 2), 0))
    d = ImageDraw.Draw(sp)
    hx, hy = cx - 0.055 * w_umb, hook
    top = hy + 30
    px = int(hx - pol.width / 2 + 12)
    for ox in (0.25, 0.75):
        d.line([(hx, hy - 2), (px + ox * (pol.width - 30), top + 12)], fill=MAR, width=4)
    sp.alpha_composite(pol, (px, int(top)))
    d.ellipse((hx - 10, hy - 12, hx + 10, hy + 8), fill=BR, outline=MAR, width=4)
    r = sp.rotate(rot, resample=Image.BICUBIC, expand=True, center=(cx, 0))
    ImageDraw.Draw(img).line([(x, 0), (x, y_umb)], fill=(150, 120, 100), width=4)
    img.alpha_composite(r, (int(x - r.width / 2), int(y_umb - (r.height - alt) / 2 - 6)))


def guarda_hd(w, cor, seed=3):
    """Guarda-chuva desenhado em 3x e reduzido (bordas lisas, sem cara de print do vídeo)."""
    g = TB.guarda_chuva(w * 3, cor, seed)
    return g.resize((round(g.width / 3), round(g.height / 3)), Image.LANCZOS)


TEMA = "vermelho"   # "verde" | "vermelho" | "xadrez"


def floco(r, cor=(255, 255, 255), a=255):
    """Floco de neve desenhado (6 braços com galhinhos)."""
    import math
    S_ = int(r * 2 + 8)
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S_ / 2
    lw = max(2, int(r / 9))
    for k in range(6):
        ang = math.radians(60 * k + 90)
        ex, ey = c + r * math.cos(ang), c - r * math.sin(ang)
        d.line([(c, c), (ex, ey)], fill=cor + (a,), width=lw)
        for f in (0.45, 0.7):
            bx, by = c + r * f * math.cos(ang), c - r * f * math.sin(ang)
            for s_ in (-1, 1):
                a2 = ang + s_ * math.radians(40)
                L = r * 0.28
                d.line([(bx, by), (bx + L * math.cos(a2), by - L * math.sin(a2))], fill=cor + (a,), width=lw)
    d.ellipse((c - lw * 1.5, c - lw * 1.5, c + lw * 1.5, c + lw * 1.5), fill=cor + (a,))
    return im


def fundo_natal(tema):
    import random
    import sys
    if tema == "xadrez":
        sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "feed-sua-vez"))
        import natal_familia as NF
        img = NF.toalha(W, 1920)
    else:
        cor, cor2 = ((16, 82, 52), (34, 120, 76)) if tema == "verde" else ((168, 26, 34), (206, 48, 54))
        img = Image.new("RGBA", (W, 1920), cor + (255,))
        luz = Image.new("L", (W, 1920), 0)
        ImageDraw.Draw(luz).ellipse((-200, 150, W + 200, 1500), fill=255)
        luz = luz.filter(ImageFilter.GaussianBlur(220))
        img = Image.composite(Image.new("RGBA", (W, 1920), cor2 + (255,)), img, luz)
    rnd = random.Random(11)
    for _ in range(70):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 1920), rnd.uniform(10, 34)
        f = floco(r, a=int(rnd.uniform(70, 170)))
        f = f.rotate(rnd.uniform(0, 60), resample=Image.BICUBIC)
        img.alpha_composite(f, (int(x - f.width / 2), int(y - f.height / 2)))
    d = ImageDraw.Draw(img)
    for _ in range(160):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 1920), rnd.uniform(2, 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 214, 110, int(rnd.uniform(120, 230))))
    return img


def fundo_parado(livres=()):
    """Fundo PARADO: guarda-chuvinhas retos (sem o balanço do vídeo) + pisca-pisca. `livres` = x das polaroides
    penduradas (o guarda-chuva do fundo ali sai, pra não embolar)."""
    import tarde as T
    img = fundo_natal(TEMA)
    d = ImageDraw.Draw(img)
    for k, (x, L, w, cor, _) in enumerate(T.CHUVAS):
        if any(abs(x - lx) < 120 for lx in livres):
            continue
        d.line([(x, -5), (x, L)], fill=(150, 120, 100), width=3)
        g = guarda_hd(w, cor, k)
        img.alpha_composite(g, (int(x - g.width / 2), int(L - 6)))
    img.alpha_composite(D._luzes(0), (0, 0))
    return img


def base(seed=0, livres=()):
    return fundo_parado(livres).crop((0, 0, CW, CH))


def story_de(tela, ultima=False):
    st = fundo_parado()
    st.alpha_composite(tela.convert("RGBA"), (0, 285 if not ultima else 160))
    if ultima:
        E.cola(st, E.pilula("garanta sua vaga aqui:", 40, BR, MAR), W / 2, 1560, 0, 1, 1)
        E.cola(st, D.seta(), W / 2, 1660, 0, 0.5, 1)
    return st.convert("RGB")


# ---------------------------------------------------------------- telas
def t_capa():
    img = base(livres=(290, 790))
    pendura(img, polaroide(quadro_cafe(6.5), 330, 410, "no Beca’s Café", 0.35), 290, 150, ROSA, 4, 150)
    pendura(img, polaroide(ImageOps.mirror(foto("IMG_194900.jpg")), 330, 410, "com monitoria!", 0.3), 790, 130, AMA, -4,
            150)
    E.cola(img, E.titulo("VAI TER\nMAIS UM!", 120, LAR), 540, 1000, -2, 1, 1)
    E.cola(img, E.pilula("ESPECIAL DE NATAL", 42, (24, 110, 66), BR, fonte_titulo=True), 540, 1150, 1, 1, 1)
    E.cola(img, E.pilula("DOMINGO DE JOGOS · 13/12", 48, PET, BR, fonte_titulo=True), 540, 1235, -1, 1, 1)
    E.cola(img, E.pilula("ARRASTA PRO LADO!", 30, AMA, MAR, fonte_titulo=True), 540, 1310, 1, 1, 1)
    return img.convert("RGB")


def t_lembra():
    img = base(livres=(290, 800))
    pendura(img, polaroide(quadro_festa(49.5), 390, 500, "gente nova em cada mesa"), 290, 440, PET, -3)
    pendura(img, polaroide(quadro_dia(13.5), 390, 500, "jogo novo pra aprender", 0.6), 800, 470, ROSA, 3)
    E.cola(img, E.titulo("LEMBRA DA NOSSA\nTARDE DE JOGOS?", 92, LAR), 540, 300, -2, 1, 1)
    E.cola(img, E.pilula("6 horas de jogo, 35 jogos e muita risada!", 38, BR, MAR), 540, 1270, 1, 1, 1)
    return img.convert("RGB")


def t_como():
    img = base(livres=(540,))
    pendura(img, polaroide(foto("20261120_112018.jpg").crop((1500, 860, 3360, 1560)), 660, 290, "os jogos esperando por você"), 540, 410, AMA, -2, 150)
    E.cola(img, E.titulo("COMO\nFUNCIONA?", 100, LAR), 540, 270, -2, 1, 1)
    y = 1095
    for k, (txt, cor) in enumerate((("Você chega, senta e escolhe o jogo", LAR),
                                    ("A gente leva os jogos e ENSINA tudo", PET),
                                    ("Vem sozinho, em dupla ou com a turma", ROSA))):
        E.cola(img, E.pilula(txt, 38, cor, BR, fonte_titulo=False), 540, y + k * 85, (-1, 1, -1)[k], 1, 1)
    return img.convert("RGB")


def t_jogos():
    img = base(livres=(190, 540, 890))
    pendura(img, polaroide(foto("20261120_151849.jpg"), 270, 360, "Cores com Dicas"), 190, 470, ROSA, 3, 130)
    pendura(img, polaroide(foto("20261120_151917.jpg"), 270, 360, "Hot Streak"), 540, 530, PET, -2, 130)
    pendura(img, polaroide(foto("20261120_151857.jpg"), 270, 360, "Dixit Disney"), 890, 470, AMA, 3, 130)
    E.cola(img, E.titulo("35 JOGOS\nNA MESA", 110, LAR), 540, 300, -2, 1, 1)
    E.cola(img, E.pilula("Do jogo rapidinho ao jogão: a gente indica o seu!", 34, BR, MAR), 540, 1270, 1, 1, 1)
    return img.convert("RGB")


def t_desafio():
    import desafio_hitster as DH
    img = base(3.3)
    E.cola(img, E.titulo("E TEM\nDESAFIO HITSTER!", 104, LAR), 540, 290, -2, 1, 1)
    E.cola(img, DH.caixa(430), 300, 720, -6, 1, 1)
    for x, y, sz, c, r in ((150, 520, 70, VERM, -12), (930, 470, 60, PET, 10), (950, 960, 66, AMA, 8)):
        E.cola(img, DH.nota(sz, c), x, y, r, 1, 1)
    passos = E.bloco(500, 330, BR, raio=30, ow=6, sombra=10).copy()
    d = ImageDraw.Draw(passos)
    for k, txt in enumerate(("toca a música", "cada mesa chuta o ano", "chegou perto? pontua!")):
        y = 62 + k * 100
        d.ellipse((30, y - 30, 90, y + 30), fill=(LAR, PET, AMA)[k], outline=MAR, width=4)
        d.text((60, y + 1), str(k + 1), font=E.lilita(40), fill=BR if k < 2 else MAR, anchor="mm")
        d.text((110, y), txt, font=E.fig(34, 900), fill=MAR, anchor="lm")
    E.cola(img, passos, 770, 730, 2, 1, 1)
    E.cola(img, E.pilula("TODAS AS MESAS JOGAM JUNTAS", 42, PET, BR, fonte_titulo=True), 540, 1080, -1, 1, 1)
    E.cola(img, E.titulo("VALENDO PRÊMIO!", 92, AMA), 540, 1200, 2, 1, 1)
    return img.convert("RGB")


def t_vagas():
    img = base(3.6)
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 120, AMA), 540, 300, 2, 1, 1)
    E.cola(img, D.painel(0), 540, 760, 0, 0.92, 1)
    E.cola(img, E.pilula("VAGAS LIMITADAS!", 44, PET, BR, fonte_titulo=True), 540, 1180, -1, 1, 1)
    E.cola(img, E.pilula("Faça sua reserva pelo link na bio", 38, AMA, MAR, fonte_titulo=False), 540, 1270, 1, 1, 1)
    return img.convert("RGB")


def t_final():
    img = base(4.0)
    E.cola(img, TB.parceria(90), 540, 230, 0, 1, 1)
    E.cola(img, E.pilula("ESPECIAL DE NATAL", 40, (24, 110, 66), BR, fonte_titulo=True), 540, 345, -1, 1, 1)
    E.cola(img, D.card(), 540, 690, 0, 0.95, 1)
    E.cola(img, E.pilula("RESERVE PELO LINK NA BIO", 40, PET, BR, fonte_titulo=True), 540, 1050, -1, 1, 1)
    E.cola(img, E.pilula("Marca aqui quem vem com você!", 36, BR, MAR), 540, 1145, 1, 1, 1)
    E.cola(img, E.pilula("@suavez_bg  ×  @becascafe", 32, AMA, MAR, fonte_titulo=True), 540, 1250, 0, 1, 1)
    return img.convert("RGB")


TELAS = [t_capa, t_lembra, t_como, t_jogos, t_desafio, t_vagas, t_final]


def main():
    os.makedirs(os.path.join(PASTA, "stories"), exist_ok=True)
    ims = [f() for f in TELAS]
    for k, im in enumerate(ims):
        im.save(os.path.join(PASTA, f"{k + 1:02d}.png"))
        story_de(im, k == len(ims) - 1).save(os.path.join(PASTA, "stories", f"story_{k + 1:02d}.png"))
    sh = Image.new("RGB", (len(ims) * 360, 450), "white")
    for k, im in enumerate(ims):
        sh.paste(im.resize((360, 450)), (k * 360, 0))
    sh.save(os.path.join(PASTA, "previa.jpg"), quality=90)
    print("ok", PASTA)


if __name__ == "__main__":
    main()
