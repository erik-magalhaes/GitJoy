#!/usr/bin/env python3
"""Post-jogo "ACHE OS 5 ERROS" (19/nov/2026, ele escolheu da lista: post que seja um jogo no feed). Foto OFICIAL das
cartas do Dixit (Galápagos, ccstore DIX001_02.jpg, 1715x2000 → assets/orig/dixit_cartas.jpg). As 5 diferenças são
feitas aqui (cv2.inpaint e troca de cor só nos pixels da peça):
  1 a tesoura entre as formigas some · 2 o olho da menina fica castanho · 3 some uma bolha de sabão no céu ·
  4 some uma das luas do cachorro de folhas · 5 o peixinho laranja some.
Carrossel 1080x1350: 1 a foto original ("ACHE OS 5 ERROS / arrasta e compara"), 2 a alterada ("achou? comenta
quantos!"), 3 a resposta circulada + aluga o Dixit. Mais as mesmas telas como Stories 1080x1920.

    /usr/bin/python3 erros.py      # out/erros/01..03.png + stories/ + conferencia.jpg
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
for p in ("comum", "assinatura-reels", "promo"):
    sys.path.insert(0, os.path.join(REPO, p))
import estilo as E  # noqa: E402

OUT = os.path.join(ROOT, "out", "erros")
W, H = 1080, 1350
MAR, PET, LAR, AMA, BR = E.MARROM, E.PETROLEO, E.LARANJA, E.AMARELO, E.BRANCO
VERM = (214, 48, 40)
FUNDO = (255, 214, 92)

# (nome, caixa x0 y0 x1 y1 na foto original, círculo da resposta cx cy r)
ERROS = [("tesoura", (1082, 265, 1195, 410), (1110, 335, 95)),
         ("olho", (38, 905, 112, 990), (75, 948, 70)),
         ("bolha", (88, 308, 168, 374), (128, 341, 62)),
         ("lua", (1410, 615, 1485, 690), (1447, 652, 60)),
         ("peixe", (820, 1860, 925, 1950), (872, 1903, 70))]


def altera(im):
    a = np.array(im.convert("RGB"))
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    out = a.copy()
    mask_in = np.zeros(a.shape[:2], np.uint8)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]

    def caixa(b):
        x0, y0, x1, y1 = b
        return (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)

    # 1 tesoura: prata (pouca saturação, clara) + cabo amarelo, dentro da caixa
    b = caixa(ERROS[0][1])
    fundo_verm = ((h < 8) | (h > 168)) & (s > 110)
    m1 = b & ~fundo_verm & (v > 72)
    mask_in |= m1.astype(np.uint8)
    mask_in |= (caixa((1035, 300, 1100, 420)) & (h > 15) & (h < 40) & (s > 90) & (v > 120)).astype(np.uint8)
    # 3 bolha: some inteira (fundo liso em degradê)
    x0, y0, x1, y1 = ERROS[2][1]
    mask_in |= ((((xx - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2 + ((yy - (y0 + y1) / 2) / ((y1 - y0) / 2)) ** 2) < 1
                ).astype(np.uint8)
    # 4 lua: amarelo no fundo escuro
    b = caixa(ERROS[3][1])
    mask_in |= (b & (v > 90) & (h > 10) & (h < 40)).astype(np.uint8)
    # 5 peixe: laranja no azul
    b = caixa(ERROS[4][1])
    mask_in |= (b & (h < 30) & (s > 45)).astype(np.uint8)
    mk = cv2.dilate(mask_in * 255, np.ones((9, 9), np.uint8))
    out = cv2.inpaint(out, mk, 15, cv2.INPAINT_TELEA)
    # grão do papel por cima da área refeita (senão fica lisa demais)
    grao = np.random.default_rng(5).normal(0, 7, out.shape)
    m3 = (cv2.GaussianBlur(mk, (9, 9), 0)[..., None] / 255.0)
    out = np.clip(out + grao * m3, 0, 255).astype(np.uint8)
    # 2 olho: íris azul/verde-água → castanho
    hsv2 = cv2.cvtColor(out, cv2.COLOR_RGB2HSV).astype(int)
    b = caixa(ERROS[1][1]) & (hsv2[..., 0] > 70) & (hsv2[..., 0] < 115) & (hsv2[..., 1] > 40)
    hsv2[..., 0] = np.where(b, 12, hsv2[..., 0])
    hsv2[..., 1] = np.where(b, np.minimum(255, hsv2[..., 1] + 60), hsv2[..., 1])
    hsv2[..., 2] = np.where(b, (hsv2[..., 2] * 0.8).astype(int), hsv2[..., 2])
    out = cv2.cvtColor(hsv2.astype(np.uint8), cv2.COLOR_HSV2RGB)
    # suaviza a emenda das trocas de cor
    return Image.fromarray(out)


def cola(img, im, cx, cy, rot=0.0):
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def fundo(h):
    img = Image.new("RGBA", (W, h), FUNDO + (255,))
    d = ImageDraw.Draw(img)
    for x in range(-h, W, 70):
        d.polygon([(x, 0), (x + 30, 0), (x + 30 + h, h), (x + h, h)], fill=(255, 205, 70, 255))
    return img


def moldura(foto, larg, alt):
    s = min(larg / foto.width, alt / foto.height)
    f = foto.resize((int(foto.width * s), int(foto.height * s)), Image.LANCZOS).convert("RGBA")
    m = 16
    bl = E.bloco(f.width + 2 * m, f.height + 2 * m, BR, raio=26, ow=7, sombra=12)
    bl.alpha_composite(f, (m + 7 - 7 + 0, m))
    return bl, s


def selo(n):
    s = 120
    im = Image.new("RGBA", (s + 12, s + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((12, 12, s + 12, s + 12), fill=MAR)
    d.ellipse((0, 0, s, s), fill=LAR, outline=MAR, width=7)
    d.text((s / 2, s / 2 + 2), str(n), font=E.lilita(78), fill=BR, anchor="mm", stroke_width=4, stroke_fill=MAR)
    return im


def tela(foto, topo, sub, n=None, circulos=None, rodape=None, h=H, y_foto=None):
    img = fundo(h)
    oy = (h - H) // 2
    cola(img, E.titulo(topo, 92, BR, larg_max=960), W / 2, oy + 110, -1.5)
    cola(img, E.pilula(sub, 34, PET, BR), W / 2, oy + 215, 1)
    bl, s = moldura(foto, 920, 900)
    yf = oy + (y_foto or 755)
    x0, y0 = int(W / 2 - bl.width / 2), int(yf - bl.height / 2)
    img.alpha_composite(bl, (x0, y0))
    if circulos:
        d = ImageDraw.Draw(img)
        for k, (cx, cy, r) in enumerate(circulos):
            X, Y, R = x0 + 16 + cx * s, y0 + 16 + cy * s, max(34, r * s)
            d.ellipse((X - R, Y - R, X + R, Y + R), outline=VERM, width=9)
            num = E.pilula(str(k + 1), 30, VERM, BR, fonte_titulo=True)
            img.alpha_composite(num, (int(X + R * 0.6), int(Y - R * 0.95 - num.height / 2)))
    if n:
        cola(img, selo(n), 110, oy + 330, -8)
    if rodape:
        rodape(img, oy)
    E.cola(img, E.logo(150), W - 110, oy + H - 70, 0, 1.0, 1.0) if hasattr(E, "cola") else None
    return img.convert("RGB")


def rod1(img, oy):
    cola(img, E.pilula("Arrasta pro lado e compara as duas!  →", 36, BR, MAR), W / 2 - 60, oy + 1275, 0)


def rod2(img, oy):
    cola(img, E.pilula("Achou? Comenta quantos erros você viu!", 36, BR, MAR), W / 2 - 60, oy + 1275, 0)


def rod3(img, oy):
    cola(img, E.pilula("É o DIXIT: tem na Sua Vez! Link na bio", 36, LAR, BR, fonte_titulo=True), W / 2 - 60,
         oy + 1275, 0)


def main():
    os.makedirs(os.path.join(OUT, "stories"), exist_ok=True)
    orig = Image.open(os.path.join(ROOT, "assets", "orig", "dixit_cartas.jpg")).convert("RGB")
    alt = altera(orig)
    alt.save(os.path.join(OUT, "dixit_alterada.jpg"), quality=95)
    circ = [c for _, _, c in ERROS]
    telas = [tela(orig, "ACHE OS 5 ERROS!", "Essa é a imagem original", 1, rodape=rod1),
             tela(alt, "ACHE OS 5 ERROS!", "Agora com 5 diferenças", 2, rodape=rod2),
             tela(alt, "ACHOU TODOS?", "A resposta tá aqui!", None, circ, rodape=rod3)]
    for k, im in enumerate(telas):
        im.save(os.path.join(OUT, f"{k + 1:02d}.png"))
        st = tela(*[orig if k == 0 else alt], "ACHE OS 5 ERROS!" if k < 2 else "ACHOU TODOS?",
                  ["Essa é a imagem original", "Agora com 5 diferenças", "A resposta tá aqui!"][k],
                  [1, 2, None][k], circ if k == 2 else None, [rod1, rod2, rod3][k], h=1920)
        st.save(os.path.join(OUT, "stories", f"story_{k + 1:02d}.png"))
    # conferência: zoom em cada erro, antes e depois
    sh = Image.new("RGB", (5 * 260, 520), "white")
    for k, (_, (x0, y0, x1, y1), _) in enumerate(ERROS):
        pad = 40
        bb = (max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad)
        for j, im in enumerate((orig, alt)):
            c = im.crop(bb)
            c.thumbnail((250, 250))
            sh.paste(c, (k * 260, j * 260))
    sh.save(os.path.join(OUT, "conferencia.jpg"))
    print("ok")


if __name__ == "__main__":
    main()
