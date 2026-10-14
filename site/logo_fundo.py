"""Logo da Sua Vez sobre o fundo escuro do site (#0d0c10 com brilho laranja)."""
import sys
import numpy as np
from PIL import Image, ImageFilter

LOGO = '/home/user/GitJoy/mlem-reels/assets/logo_suavez.png'
FUNDO = (13, 12, 16)
LARANJA = np.array([249, 115, 22], float)
CREME = (245, 239, 228)
SAIDA = '/home/user/GitJoy/site/logo'


def fundo(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(float)
    # brilho laranja suave no meio, como o topo da página inicial
    d = ((x - w / 2) / (w * 0.55)) ** 2 + ((y - h * 0.42) / (h * 0.6)) ** 2
    g = np.clip(1 - d, 0, 1) ** 2 * 0.20
    img = np.array(FUNDO, float)[None, None] * (1 - g[..., None]) + LARANJA * g[..., None]
    return Image.fromarray(img.round().astype(np.uint8)).convert('RGBA')


def tagline_creme(logo):
    """Troca o marrom da frase de baixo por creme (fica legível no escuro)."""
    a = np.array(logo).astype(float)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    h = a.shape[0]
    zona = np.zeros(al.shape, bool)
    zona[int(h * 0.86):] = True
    marrom = zona & (al > 0) & (r > g) & (g >= b - 10) & (r < 200)
    lum = np.clip((r + g + b) / 3 / 140, 0, 1)
    for i, c in enumerate(CREME):
        a[..., i] = np.where(marrom, c * (0.75 + 0.25 * lum), a[..., i])
    return Image.fromarray(a.round().astype(np.uint8))


def contorno(logo, raio=4):
    al = logo.split()[3].filter(ImageFilter.MaxFilter(raio * 2 + 1))
    base = Image.new('RGBA', logo.size, CREME + (0,))
    base.putalpha(al)
    base.alpha_composite(logo)
    return base


def monta(logo, w, h, escala):
    bg = fundo(w, h)
    lw = int(w * escala)
    lg = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    bg.alpha_composite(lg, ((w - lg.width) // 2, (h - lg.height) // 2))
    return bg.convert('RGB')


if __name__ == '__main__':
    L = Image.open(LOGO).convert('RGBA')
    pad = Image.new('RGBA', (L.width + 40, L.height + 40), (0, 0, 0, 0))
    pad.alpha_composite(L, (20, 20))
    A = contorno(pad)                 # igual ao site (contorno creme)
    B = tagline_creme(pad)            # frase em creme, sem contorno
    for nome, lg in (('contorno', A), ('creme', B)):
        monta(lg, 1600, 900, 0.72).save(f'{SAIDA}/logo_fundo_site_{nome}.png')
        monta(lg, 1080, 1080, 0.80).save(f'{SAIDA}/logo_fundo_site_{nome}_quadrado.png')
    print('ok')
