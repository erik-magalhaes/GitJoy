"""Camiseta de monitor da Sua Vez: arte para estampa + mockup nas costas da camiseta preta.

Uso: python3 mockup.py <print da loja (jpg)> <pasta de saída>
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = '/home/user/GitJoy'
LOGO = f'{RAIZ}/site/logo/logo_suavez_sem_frase.png'
FONTE = f'{RAIZ}/mlem-reels/assets/fonts/Poppins-Black.ttf'
FONTE_2 = f'{RAIZ}/mlem-reels/assets/fonts/Poppins-SemiBold.ttf'
BRANCO = (246, 243, 236)
LARANJA = (243, 146, 55)
AZUL = (47, 152, 182)


def fonte(caminho, tam):
    return ImageFont.truetype(caminho, tam)


def texto_espacado(d, cx, y, txt, f, cor, esp):
    larg = [d.textbbox((0, 0), c, font=f)[2] for c in txt]
    total = sum(larg) + esp * (len(txt) - 1)
    x = cx - total / 2
    for c, w in zip(txt, larg):
        d.text((x, y), c, font=f, fill=cor)
        x += w + esp


def arte(W=2400):
    """Arte das costas em fundo transparente (para a gráfica)."""
    H = int(W * 1.05)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lg = Image.open(LOGO).convert('RGBA')
    lw = int(W * 0.78)
    lg = lg.resize((lw, round(lg.height * lw / lg.width)), Image.LANCZOS)
    img.alpha_composite(lg, ((W - lw) // 2, 0))
    d = ImageDraw.Draw(img)
    y = lg.height + int(W * 0.08)
    # linha fina laranja
    d.rounded_rectangle((W * 0.30, y, W * 0.70, y + W * 0.012), radius=W * 0.006, fill=LARANJA)
    y += int(W * 0.06)
    f = fonte(FONTE, int(W * 0.165))
    texto_espacado(d, W / 2, y, 'MONITOR', f, BRANCO, int(W * 0.012))
    y += int(W * 0.21)
    f2 = fonte(FONTE_2, int(W * 0.062))
    texto_espacado(d, W / 2, y, '@suavez_bg', f2, LARANJA, int(W * 0.006))
    return img.crop(img.getbbox())


def aplica(foto, estampa, cx, topo, largura):
    """Estampa na camiseta, escurecendo junto com as sombras do tecido."""
    base = np.asarray(foto.convert('RGB')).astype(float)
    e = estampa.resize((largura, round(estampa.height * largura / estampa.width)), Image.LANCZOS)
    x0, y0 = int(cx - e.width / 2), int(topo)
    reg = base[y0:y0 + e.height, x0:x0 + e.width]
    lum = reg.mean(2)
    lum_s = np.asarray(Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(float)
    ea = np.asarray(e).astype(float)
    # sombra do tecido: mais claro nas partes iluminadas, mais escuro nas dobras
    m = lum_s.mean()
    sombra = np.clip(0.92 + (lum_s - m) / max(m, 1) * 0.6, 0.72, 1.08)[..., None]
    cor = np.clip(ea[..., :3] * sombra * 0.94, 0, 255)
    a = ea[..., 3:4] / 255.0 * 0.97
    reg[:] = reg * (1 - a) + cor * a
    return Image.fromarray(base.round().astype(np.uint8))


if __name__ == '__main__':
    src, saida = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert('RGB')
    costas = im.crop((140, 760, 1075, 1790))
    est = arte()
    est.save(f'{saida}/arte_costas_monitor.png')
    m = aplica(costas, est, cx=468, topo=370, largura=345)
    m.save(f'{saida}/mockup_costas_monitor.jpg', quality=95)
    print(est.size, m.size)
