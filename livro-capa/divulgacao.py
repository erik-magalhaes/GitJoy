#!/usr/bin/env python3
"""Materiais de divulgação de "Três Segredos e um CEO" (pseudônimo E.M. Valentine), no mesmo visual da capa:
noir quente (preto → vinho), brasas, título dourado em Cinzel/Playfair.

    python3 divulgacao.py   → out/divulgacao/
        perfil.png          1080x1080, monograma EM (Instagram/TikTok; tudo dentro do círculo)
        post_lancamento.png 1080x1350, capa + gancho
        story_em_breve.png  1080x1920, capa + "em breve" + espaço para o adesivo de link
        frase_1..4.png      1080x1350, carrossel de frases do livro
        tiktok_capa.png     1080x1920, capa de vídeo com o gancho grande

Precisa de out/capa.png (rode capa.py antes).
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(AQUI, "assets", "fonts")
OUT = os.path.join(AQUI, "out", "divulgacao")

CREME = (246, 232, 212)
VERMELHO = (235, 70, 62)
OURO = [(255, 236, 178), (226, 176, 92), (164, 110, 44), (240, 200, 120)]


def fonte(nome, tam, peso=None):
    f = ImageFont.truetype(os.path.join(FONTES, nome), tam)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def fundo(w, h, semente=1, luz=(0.15, 0.55)):
    """Preto com brilho vinho vindo de um ponto + brasas."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = luz[0] * w, luz[1] * h
    g = np.exp(-(((x - cx) / (0.75 * w)) ** 2 + ((y - cy) / (0.6 * h)) ** 2))
    a = np.zeros((h, w, 3), np.float32) + np.array([8, 3, 4])
    a += g[..., None] * np.array([120, 16, 22])
    vin = 1 - 0.5 * np.clip(np.sqrt(((x / w) - 0.5) ** 2 + ((y / h) - 0.5) ** 2) * 1.6 - 0.3, 0, 1)
    a *= vin[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return brasas(img, semente)


def brasas(img, semente=1, n=None):
    w, h = img.size
    rng = np.random.default_rng(semente)
    fa = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(fa)
    for _ in range(n or int(w * h / 18000)):
        px, py = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(1.2, 4.0)
        d.ellipse((px - r, py - r, px + r, py + r), fill=(255, int(rng.uniform(90, 170)), 60))
    fa = Image.blend(fa.filter(ImageFilter.GaussianBlur(4)), fa, 0.5)
    return Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(fa, np.int16) * 0.7, 0, 255).astype(np.uint8))


def _mascara(size, xy, txt, f, ancora, espaco, alinha="center", entrelinha=18):
    m = Image.new("L", size)
    d = ImageDraw.Draw(m)
    if espaco:
        larg = sum(d.textlength(c, font=f) for c in txt) + espaco * (len(txt) - 1)
        x0 = xy[0] - larg / 2 if ancora[0] == "m" else xy[0]
        for c in txt:
            d.text((x0, xy[1]), c, font=f, fill=255, anchor="l" + ancora[1])
            x0 += d.textlength(c, font=f) + espaco
    else:
        d.multiline_text(xy, txt, font=f, fill=255, anchor=ancora, spacing=entrelinha, align=alinha)
    return m


def texto(img, xy, txt, f, cor, ancora="mm", espaco=0, sombra=10, alinha="center", entrelinha=18):
    m = _mascara(img.size, xy, txt, f, ancora, espaco, alinha, entrelinha)
    if sombra:
        img.paste((0, 0, 0), (0, 0), m.filter(ImageFilter.GaussianBlur(sombra)))
    img.paste(cor, (0, 0), m)
    return m.getbbox()


def texto_ouro(img, xy, txt, f, ancora="mm", espaco=0, brilho=True):
    w, h = img.size
    m = _mascara(img.size, xy, txt, f, ancora, espaco)
    bb = m.getbbox()
    img.paste((0, 0, 0), (0, 0), m.filter(ImageFilter.GaussianBlur(12)).point(lambda v: min(255, v * 2)))
    if brilho:
        img.paste((230, 120, 60), (0, 0), m.filter(ImageFilter.GaussianBlur(24)).point(lambda v: v // 3))
    t = np.clip((np.arange(h) - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)
    pts = np.linspace(0, 1, len(OURO))
    grad = np.zeros((h, w, 3), np.uint8)
    for c in range(3):
        grad[..., c] = np.interp(t, pts, [o[c] for o in OURO]).astype(np.uint8)[:, None]
    img.paste(Image.fromarray(grad), (0, 0), m)
    return bb


def filete(img, cx, y, meia=260):
    d = ImageDraw.Draw(img)
    d.line((cx - meia, y, cx - 30, y), fill=(200, 150, 80), width=3)
    d.line((cx + 30, y, cx + meia, y), fill=(200, 150, 80), width=3)
    d.ellipse((cx - 8, y - 8, cx + 8, y + 8), fill=(196, 30, 42))


def livro(capa, altura):
    """Capa como livro: lombada escura à esquerda, brilho e sombra no chão."""
    c = capa.resize((round(capa.width * altura / capa.height), altura), Image.LANCZOS)
    w, h = c.size
    a = np.asarray(c).astype(np.float32)
    x = np.arange(w, dtype=np.float32)
    lomb = 1 - 0.55 * np.exp(-((x - w * 0.012) / (w * 0.01)) ** 2) + 0.12 * np.exp(-((x - w * 0.035) / (w * 0.012)) ** 2)
    a *= lomb[None, :, None]
    c = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    pad = 80
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sombra = Image.new("L", out.size, 0)
    ImageDraw.Draw(sombra).rectangle((pad + 18, pad + 24, pad + w + 18, pad + h + 24), fill=210)
    out.putalpha(sombra.filter(ImageFilter.GaussianBlur(30)))
    out.paste(c, (pad, pad))
    return out


def perfil():
    W = H = 1080
    img = fundo(W, H, semente=3, luz=(0.5, 0.45))
    # tudo dentro do círculo central (as redes cortam em círculo)
    texto_ouro(img, (W / 2 - 4, 500), "EM", fonte("PlayfairDisplay.ttf", 420, 900), espaco=-10)
    filete(img, W / 2, 735, meia=200)
    texto(img, (W / 2, 810), "E.M. VALENTINE", fonte("Cinzel.ttf", 58, 700), CREME, espaco=10)
    return img


def post_lancamento(capa):
    W, H = 1080, 1350
    img = fundo(W, H, semente=5, luz=(0.5, 0.4))
    texto(img, (W / 2, 95), "E.M. VALENTINE APRESENTA", fonte("Cinzel.ttf", 36, 700), CREME, espaco=8)
    lv = livro(capa, 820)
    img.paste(lv, ((W - lv.width) // 2, 140), lv)
    fi = fonte("PlayfairDisplay-Italic.ttf", 48, 500)
    texto(img, (W / 2, 1125), "Uma noite. Nove meses. Três filhos.", fi, CREME)
    texto(img, (W / 2, 1190), "E agora ele é o meu chefe.", fonte("PlayfairDisplay-Italic.ttf", 50, 800), VERMELHO)
    filete(img, W / 2, 1262, meia=220)
    texto(img, (W / 2, 1305), "EM BREVE", fonte("Cinzel.ttf", 40, 900), (240, 200, 120), espaco=14)
    return img


def story(capa):
    W, H = 1080, 1920
    img = fundo(W, H, semente=7, luz=(0.5, 0.35))
    texto(img, (W / 2, 210), "ELE SUMIU DEPOIS DE UMA NOITE.", fonte("Cinzel.ttf", 40, 700), CREME, espaco=4)
    texto(img, (W / 2, 270), "VOLTOU COMO O MEU CHEFE.", fonte("Cinzel.ttf", 40, 700), VERMELHO, espaco=4)
    lv = livro(capa, 1020)
    img.paste(lv, ((W - lv.width) // 2, 330), lv)
    texto_ouro(img, (W / 2, 1500), "EM BREVE", fonte("PlayfairDisplay.ttf", 130, 900), espaco=10)
    texto(img, (W / 2, 1610), "Toque no link e entre na lista de espera", fonte("PlayfairDisplay-Italic.ttf", 44, 500), CREME)
    # espaço livre para o adesivo de link do Instagram (y ~1680–1800)
    return img


FRASES = [
    ("— Isso...\n— Isso não foi de mentira.", "Capítulo 9 · A festa de noivado"),
    ("Regra número um:\nnada de beijos fora das fotos.", "Capítulo 7 · Regras do acordo"),
    ("— Você é o nosso pai?\n— Sou.\n— Por que você demorou tanto?", "Capítulo 5 · Exame de DNA"),
    ("— Eu chutei a máscara\ne saí pelo elevador de serviço\ncom o sapato na mão.", "Capítulo 10 · Regra quebrada"),
]


def frase(i, txt, cap):
    W, H = 1080, 1350
    img = fundo(W, H, semente=11 + i, luz=((0.15, 0.85, 0.2, 0.8)[i % 4], 0.5))
    texto_ouro(img, (W / 2, 250), "“", fonte("PlayfairDisplay.ttf", 260, 900))
    texto(img, (W / 2, 680), txt, fonte("PlayfairDisplay-Italic.ttf", 64, 600), CREME, sombra=12, entrelinha=30)
    filete(img, W / 2, 1050, meia=200)
    texto(img, (W / 2, 1110), cap.upper(), fonte("Cinzel.ttf", 30, 700), (240, 200, 120), espaco=4)
    texto(img, (W / 2, 1250), "TRÊS SEGREDOS E UM CEO · E.M. VALENTINE", fonte("Cinzel.ttf", 28, 700), CREME, espaco=4)
    return img


def tiktok(capa):
    W, H = 1080, 1920
    img = fundo(W, H, semente=13, luz=(0.5, 0.6))
    big = fonte("PlayfairDisplay.ttf", 92, 900)
    texto(img, (W / 2, 330), "ELE NÃO SABIA\nQUE TINHA\nTRÊS FILHOS", big, CREME, sombra=14, entrelinha=10)
    texto_ouro(img, (W / 2, 640), "ATÉ VIRAR O MEU CHEFE", fonte("Cinzel.ttf", 62, 900), espaco=4)
    lv = livro(capa, 900)
    img.paste(lv, ((W - lv.width) // 2, 720), lv)
    # pé livre (legenda/botões do TikTok ficam embaixo e à direita)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    capa = Image.open(os.path.join(AQUI, "out", "capa.png")).convert("RGB")
    perfil().save(os.path.join(OUT, "perfil.png"))
    post_lancamento(capa).save(os.path.join(OUT, "post_lancamento.png"))
    story(capa).save(os.path.join(OUT, "story_em_breve.png"))
    for i, (t, c) in enumerate(FRASES):
        frase(i, t, c).save(os.path.join(OUT, f"frase_{i + 1}.png"))
    tiktok(capa).save(os.path.join(OUT, "tiktok_capa.png"))
    print("ok", OUT)


if __name__ == "__main__":
    main()
