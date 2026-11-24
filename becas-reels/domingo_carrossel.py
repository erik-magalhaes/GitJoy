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
    umb = TB.guarda_chuva(w_umb, cor, 3)
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


def base(seed):
    return D.fundo(seed).crop((0, 0, CW, CH))


# ---------------------------------------------------------------- telas
def t_capa():
    img = base(2.2)
    pendura(img, polaroide(quadro_festa(14.0), 330, 410, "mesa cheia!"), 290, 150, ROSA, 4, 150)
    pendura(img, polaroide(foto("20261120_151926.jpg"), 330, 410, "Marrakech", 0.35), 790, 130, AMA, -4, 150)
    E.cola(img, E.titulo("VAI TER\nMAIS UM!", 120, LAR), 540, 1000, -2, 1, 1)
    E.cola(img, D.selo_fim_de_ano(42), 540, 1150, 1, 1, 1)
    E.cola(img, E.pilula("DOMINGO DE JOGOS · 13/12", 48, PET, BR, fonte_titulo=True), 540, 1235, -1, 1, 1)
    E.cola(img, E.pilula("ARRASTA PRO LADO!", 30, AMA, MAR, fonte_titulo=True), 540, 1310, 1, 1, 1)
    return img.convert("RGB")


def t_lembra():
    img = base(2.6)
    E.cola(img, E.titulo("LEMBRA DA NOSSA\nTARDE DE JOGOS?", 92, LAR), 540, 300, -2, 1, 1)
    pendura(img, polaroide(quadro_festa(49.5), 390, 500, "gente nova em cada mesa"), 290, 440, PET, -3)
    pendura(img, polaroide(quadro_dia(13.5), 390, 500, "jogo novo pra aprender", 0.6), 800, 470, ROSA, 3)
    E.cola(img, E.pilula("6 horas de jogo, 35 jogos e muita risada!", 38, BR, MAR), 540, 1270, 1, 1, 1)
    return img.convert("RGB")


def t_como():
    img = base(3.1)
    E.cola(img, E.titulo("COMO\nFUNCIONA?", 100, LAR), 540, 270, -2, 1, 1)
    pendura(img, polaroide(foto("20261120_112018.jpg"), 560, 380, "os jogos esperando por você", 0.55), 540, 410, AMA, -2, 150)
    y = 1095
    for k, (txt, cor) in enumerate((("Você chega, senta e escolhe o jogo", LAR),
                                    ("A gente leva os jogos e ENSINA tudo", PET),
                                    ("Vem sozinho, em dupla ou com a turma", ROSA))):
        E.cola(img, E.pilula(txt, 38, cor, BR, fonte_titulo=False), 540, y + k * 85, (-1, 1, -1)[k], 1, 1)
    return img.convert("RGB")


def t_jogos():
    img = base(3.4)
    E.cola(img, E.titulo("35 JOGOS\nNA MESA", 110, LAR), 540, 300, -2, 1, 1)
    pendura(img, polaroide(foto("20261120_151849.jpg"), 270, 360, "Cores com Dicas"), 190, 470, ROSA, 3, 130)
    pendura(img, polaroide(foto("20261120_151917.jpg"), 270, 360, "Hot Streak"), 540, 530, PET, -2, 130)
    pendura(img, polaroide(foto("20261120_151857.jpg"), 270, 360, "Dixit Disney"), 890, 470, AMA, 3, 130)
    E.cola(img, E.pilula("Do jogo rapidinho ao jogão: a gente indica o seu!", 34, BR, MAR), 540, 1270, 1, 1, 1)
    return img.convert("RGB")


def t_vagas():
    img = base(3.6)
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 120, VERM), 540, 300, 2, 1, 1)
    E.cola(img, D.painel(0), 540, 760, 0, 0.92, 1)
    E.cola(img, E.pilula("VAGAS LIMITADAS!", 44, PET, BR, fonte_titulo=True), 540, 1180, -1, 1, 1)
    E.cola(img, E.pilula("Faça sua reserva pelo WhatsApp", 38, AMA, MAR, fonte_titulo=False), 540, 1270, 1, 1, 1)
    return img.convert("RGB")


def t_final():
    img = base(4.0)
    E.cola(img, TB.parceria(90), 540, 230, 0, 1, 1)
    E.cola(img, D.selo_fim_de_ano(40), 540, 345, -1, 1, 1)
    E.cola(img, D.card(), 540, 690, 0, 0.95, 1)
    E.cola(img, E.pilula(f"RESERVE NO WHATSAPP {TB.WHATS}", 40, PET, BR, fonte_titulo=True), 540, 1050, -1, 1, 1)
    E.cola(img, E.pilula("Marca aqui quem vem com você!", 36, BR, MAR), 540, 1145, 1, 1, 1)
    E.cola(img, E.pilula("@suavez_bg  ×  @becascafe", 32, AMA, MAR, fonte_titulo=True), 540, 1250, 0, 1, 1)
    return img.convert("RGB")


TELAS = [t_capa, t_lembra, t_como, t_jogos, t_vagas, t_final]


def main():
    os.makedirs(os.path.join(PASTA, "stories"), exist_ok=True)
    ims = [f() for f in TELAS]
    for k, im in enumerate(ims):
        im.save(os.path.join(PASTA, f"{k + 1:02d}.png"))
        M.story_de(im, k == len(ims) - 1).save(os.path.join(PASTA, "stories", f"story_{k + 1:02d}.png"))
    sh = Image.new("RGB", (len(ims) * 360, 450), "white")
    for k, im in enumerate(ims):
        sh.paste(im.resize((360, 450)), (k * 360, 0))
    sh.save(os.path.join(PASTA, "previa.jpg"), quality=90)
    print("ok", PASTA)


if __name__ == "__main__":
    main()
