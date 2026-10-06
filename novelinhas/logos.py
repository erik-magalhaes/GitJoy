"""Opções de nome + logo do perfil (1024x1024, pensado para o recorte redondo do TikTok).

python3 logos.py  ->  out/logo_<n>.png e out/logos_comparacao.jpg
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(AQUI, "assets", "fonts")
OUT = os.path.join(AQUI, "out")
S = 1024


def fonte(nome, tam, peso=None):
    f = ImageFont.truetype(os.path.join(FONTES, nome), tam)
    if peso is not None:
        try:
            f.set_variation_by_axes([peso] if "Inter" not in nome else [32, peso])
        except Exception:
            pass
    return f


def texto_centro(d, cx, cy, txt, f, fill, **kw):
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=f, **{k: v for k, v in kw.items() if k == "stroke_width"})
    d.text((cx - (x0 + x1) / 2, cy - (y0 + y1) / 2), txt, font=f, fill=fill, **kw)


def checks(d, x, y, esc, cor, larg=None):
    """Os dois tracinhos do WhatsApp (visto), com pontas arredondadas."""
    larg = larg or int(14 * esc)
    for dx in (0, 0.42):
        pts = [(x + (dx + 0.0) * 100 * esc, y + 0.52 * 100 * esc),
               (x + (dx + 0.28) * 100 * esc, y + 0.80 * 100 * esc),
               (x + (dx + 0.86) * 100 * esc, y + 0.18 * 100 * esc)]
        if dx > 0:  # o segundo tracinho só aparece na parte de cima, como no app
            pts[0] = (x + (dx + 0.18) * 100 * esc, y + 0.70 * 100 * esc)
            pts[1] = (x + (dx + 0.28) * 100 * esc, y + 0.80 * 100 * esc)
        d.line(pts, fill=cor, width=larg, joint="curve")
        for p in (pts[0], pts[-1]):
            r = larg / 2
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=cor)


def gradiente(w, h, c1, c2, radial=False):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for yy in range(h):
        for xx in range(0, w):
            if radial:
                t = min(1, math.hypot(xx - w / 2, yy - h * 0.42) / (w * 0.75))
            else:
                t = yy / (h - 1)
            px[xx, yy] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return im


def sombra(camada, raio=18, desloc=(0, 14), alfa=110):
    a = camada.split()[-1].filter(ImageFilter.GaussianBlur(raio))
    sh = Image.new("RGBA", camada.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: v * alfa // 255))
    out = Image.new("RGBA", camada.size, (0, 0, 0, 0))
    out.alpha_composite(sh, desloc)
    out.alpha_composite(camada)
    return out


def balao(w, h, cor, rabo="esq", r=70):
    im = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 40 + w, 40 + h), r, fill=cor)
    if rabo == "esq":
        d.polygon([(40 + 30, 40 + h - 60), (40 - 34, 40 + h + 26), (40 + 130, 40 + h - 6)], fill=cor)
    else:
        d.polygon([(40 + w - 30, 40 + h - 60), (40 + w + 34, 40 + h + 26), (40 + w - 130, 40 + h - 6)], fill=cor)
    return im


# ---------------------------------------------------------------- opção 1
def logo_novela_no_zap():
    """Balão verde do Zap com coroa de novela; texto em Pacifico."""
    im = gradiente(S, S, (18, 140, 126), (7, 74, 66), radial=True).convert("RGBA")
    b = balao(780, 520, (255, 255, 255, 255), "esq", r=110)
    d = ImageDraw.Draw(b)
    texto_centro(d, 430, 250, "Novela", fonte("Pacifico-Regular.ttf", 190), (7, 94, 84))
    f2 = fonte("Inter.ttf", 108, 900)
    texto_centro(d, 400, 455, "NO ZAP", f2, (37, 211, 102))
    checks(d, 640, 405, 1.05, (83, 189, 235), larg=17)
    im.alpha_composite(sombra(b), (72, 190))
    # coração dramático
    cor = Image.new("RGBA", (260, 240), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cor)
    dc.ellipse((10, 10, 130, 130), fill=(235, 64, 82))
    dc.ellipse((110, 10, 230, 130), fill=(235, 64, 82))
    dc.polygon([(16, 95), (224, 95), (120, 226)], fill=(235, 64, 82))
    dc.line([(110, 25), (95, 85), (140, 115), (118, 190)], fill=(255, 255, 255), width=12, joint="curve")
    cor = cor.rotate(-14, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(sombra(cor, 10, (0, 8)), (720, 110))
    return im.convert("RGB")


# ---------------------------------------------------------------- opção 2
def logo_visto_por_ultimo():
    """Clima de novela das nove: fundo vinho, dourado, letra cursiva."""
    im = gradiente(S, S, (110, 18, 40), (30, 4, 14), radial=True).convert("RGBA")
    d = ImageDraw.Draw(im)
    ouro = (236, 196, 112)
    d.ellipse((60, 60, S - 60, S - 60), outline=ouro, width=8)
    d.ellipse((86, 86, S - 86, S - 86), outline=(236, 196, 112, 120), width=3)
    texto_centro(d, S / 2, 400, "Visto", fonte("GreatVibes-Regular.ttf", 290), ouro)
    f = fonte("PlayfairDisplay.ttf", 92, 800)
    texto_centro(d, S / 2, 610, "POR ÚLTIMO", f, (255, 240, 225))
    checks(d, S / 2 - 70, 690, 1.4, (83, 189, 235), larg=22)
    f3 = fonte("Inter.ttf", 40, 600)
    texto_centro(d, S / 2, 880, "às 23:47", f3, (236, 196, 112, 255))
    return im.convert("RGB")


# ---------------------------------------------------------------- opção 3
def logo_tracinho_azul():
    """Os dois tracinhos azuis gigantes como símbolo; nome em tipografia forte."""
    im = gradiente(S, S, (17, 27, 33), (11, 20, 26)).convert("RGBA")
    d = ImageDraw.Draw(im)
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    checks(ImageDraw.Draw(lay), 250, 150, 4.6, (83, 189, 235), larg=78)
    glow = lay.filter(ImageFilter.GaussianBlur(40))
    im.alpha_composite(glow)
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    f = fonte("AbrilFatface-Regular.ts".replace(".ts", ".ttf"), 150)
    texto_centro(d, S / 2, 700, "Tracinho", f, (255, 255, 255))
    texto_centro(d, S / 2, 850, "AZUL", fonte("Inter.ttf", 130, 900), (83, 189, 235))
    return im.convert("RGB")


OPCOES = [("Novela no Zap", logo_novela_no_zap),
          ("Visto por Último", logo_visto_por_ultimo),
          ("Tracinho Azul", logo_tracinho_azul)]


def redondo(im, tam):
    im = im.resize((tam, tam), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (tam * 4, tam * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, tam * 4, tam * 4), fill=255)
    im.putalpha(m.resize((tam, tam), Image.LANCZOS))
    return im


def comparacao(logos):
    W, H = 1800, 980
    c = Image.new("RGB", (W, H), (245, 242, 238))
    d = ImageDraw.Draw(c)
    texto_centro(d, W / 2, 70, "Nome e logo do perfil: escolha 1, 2 ou 3", fonte("Inter.ttf", 54, 800), (30, 30, 30))
    for i, ((nome, _), im) in enumerate(zip(OPCOES, logos)):
        cx = 300 + i * 600
        c.paste(im.resize((480, 480), Image.LANCZOS), (cx - 240, 150))
        av = redondo(im, 170)
        c.paste(av, (cx - 200, 680), av)
        texto_centro(d, cx + 100, 730, f"@{nome.lower().replace(' ', '').replace('ú', 'u')}",
                     fonte("Inter.ttf", 30, 700), (30, 30, 30))
        texto_centro(d, cx + 100, 775, "assim no TikTok", fonte("Inter.ttf", 24, 500), (120, 120, 120))
        texto_centro(d, cx, 910, f"{i + 1}. {nome}", fonte("Inter.ttf", 50, 800), (30, 30, 30))
    return c


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    logos = []
    for i, (nome, fn) in enumerate(OPCOES, 1):
        im = fn()
        im.save(os.path.join(OUT, f"logo_{i}.png"))
        logos.append(im)
    comparacao(logos).save(os.path.join(OUT, "logos_comparacao.jpg"), quality=90)
    print("ok")
