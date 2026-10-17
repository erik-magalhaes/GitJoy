"""Cena do Santorini em "stop motion" com as peças OFICIAIS do manual Spin Master (renders 3D ampliados 4x por IA,
assets/pecas/): andar 1 (p1_768), 2 (p1_788), 3 (p1_804), cúpula (p1_820), construtor azul (p1_796) e cinza (p1_639).
A perspectiva foi medida no andar 1: lado esquerdo da base = A, lado direito = B (px na escala das peças ampliadas).
O empilhamento segue o diagrama "A Complete Tower" do manual (posições em pontos do PDF × 5,6 px/pt).

    img = cena({(x, y): "123c", ...}, peoes={(x, y): "azul"}, escala=0.6)   # RGBA
"""
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "assets", "pecas")
A = np.array([-125.0, -72.0])   # frente → esquerda (lado da base do andar 1)
B = np.array([220.0, -32.0])    # frente → direita
FOLGA = 1.10                    # a casa é um pouco maior que o bloco
FRENTE_L1 = np.array([140.0, 252.0])   # canto da frente da base no PNG do andar 1
PECA = {"1": "p1_768", "2": "p1_788", "3": "p1_804", "c": "p1_820", "azul": "p1_796", "cinza": "p1_639"}
# canto sup. esquerdo de cada peça relativo ao andar 1 (diagrama do manual, pt → px ampliado)
DESLOC = {"1": (0, 0), "2": ((323 - 315) * 5.6, (680 - 704) * 5.6), "3": ((321 - 315) * 5.6, (660 - 704) * 5.6),
          "c": ((330 - 315) * 5.6, (650 - 704) * 5.6)}
TOPO = {0: None, 1: (0.50, 0.24), 2: (0.52, 0.22), 3: (0.52, 0.20)}  # centro do topo (fração da peça)


@lru_cache(None)
def peca(n):
    return Image.open(os.path.join(P, PECA[n] + ".png")).convert("RGBA")


def casa(i, j, origem):
    """Centro da casa (i ao longo de A, j ao longo de B), a partir do canto da frente do tabuleiro."""
    return origem + (i + 0.5) * A * FOLGA + (j + 0.5) * B * FOLGA


def grama(w, h, seed=2):
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), np.float32)
    for esc, amp in [(64, 18), (24, 10), (8, 5)]:
        n = rng.random((h // esc + 2, w // esc + 2)).astype(np.float32)
        n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)) / 255 - 0.5
        base += n[..., None] * amp
    cor = np.array([118, 186, 74], np.float32) + base * np.array([1.0, 1.3, 0.6])
    return Image.fromarray(cor.clip(0, 255).astype(np.uint8), "RGB")


def tabuleiro(origem, tam):
    """Tampo 5x5 na perspectiva das peças, com grama, linhas brancas e borda grossa (como o tabuleiro do jogo)."""
    W, H = tam
    img = Image.new("RGBA", tam, (0, 0, 0, 0))
    c = [origem, origem + 5 * A * FOLGA, origem + 5 * (A + B) * FOLGA, origem + 5 * B * FOLGA]
    esp = 46
    lado = Image.new("RGBA", tam, (0, 0, 0, 0))
    d = ImageDraw.Draw(lado)
    d.polygon([tuple(c[1]), tuple(c[0]), tuple(c[0] + (0, esp)), tuple(c[1] + (0, esp))], fill=(98, 140, 60))
    d.polygon([tuple(c[0]), tuple(c[3]), tuple(c[3] + (0, esp)), tuple(c[0] + (0, esp))], fill=(80, 118, 50))
    img.alpha_composite(lado)
    m = Image.new("L", tam, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in c], fill=255)
    g = grama(W, H).convert("RGBA")
    g.putalpha(m)
    img.alpha_composite(g)
    d = ImageDraw.Draw(img)
    for k in range(6):
        p0, p1 = origem + k * A * FOLGA, origem + k * A * FOLGA + 5 * B * FOLGA
        d.line([tuple(p0), tuple(p1)], fill=(244, 240, 228), width=7)
        p0, p1 = origem + k * B * FOLGA, origem + k * B * FOLGA + 5 * A * FOLGA
        d.line([tuple(p0), tuple(p1)], fill=(244, 240, 228), width=7)
    return img


def poe_torre(img, centro, niveis, sombra=True):
    """Empilha os andares/cúpula numa casa. Retorna o ponto do topo (onde um construtor ficaria)."""
    frente = centro - 0.5 * (A + B)  # canto da frente do bloco
    ox, oy = frente - FRENTE_L1      # canto sup. esq. do andar 1
    if sombra and niveis:
        s = Image.new("RGBA", img.size, (0, 0, 0, 0))
        q = [frente + (0, 4), frente + A + (0, 4), frente + A + B + (0, 4), frente + B + (0, 4)]
        ImageDraw.Draw(s).polygon([tuple(p + (14, 10)) for p in q], fill=(0, 0, 0, 90))
        img.alpha_composite(s.filter(ImageFilter.GaussianBlur(10)))
    topo = centro.copy()
    for n in niveis:
        im = peca(n)
        dx, dy = DESLOC[n]
        if n == "c" and niveis.index("c") < 3:  # cúpula fora do 3º andar (Atlas): assenta no topo do andar de baixo
            m = str(niveis.index("c"))
            pm, p3, pc = peca(m), peca("3"), im
            frac = (DESLOC["c"][1] + pc.height - DESLOC["3"][1]) / p3.height  # onde a base da cúpula fica no 3º andar
            dx = DESLOC[m][0] + pm.width / 2 - pc.width / 2 + (DESLOC["c"][0] + pc.width / 2 - DESLOC["3"][0] - p3.width / 2)
            dy = DESLOC[m][1] + pm.height * frac - pc.height
        img.alpha_composite(im, (int(ox + dx), int(oy + dy)))
        if n != "c":
            fx, fy = TOPO[int(n)]
            topo = np.array([ox + dx + im.width * fx, oy + dy + im.height * fy])
    return topo


def poe_peao(img, base, cor):
    im = peca(cor)
    bb = im.getbbox()
    pe = np.array([(bb[0] + bb[2]) / 2, bb[3] - 18])
    s = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).ellipse((base[0] - 40, base[1] - 12, base[0] + 50, base[1] + 16), fill=(0, 0, 0, 80))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(im, (int(base[0] - pe[0]), int(base[1] - pe[1])))


def cena(torres, peoes=None, tam=(2200, 1700)):
    """torres = {(i, j): "123c"}, peoes = {(i, j): "azul"/"cinza"} (o peão fica no topo da torre da casa)."""
    peoes = peoes or {}
    origem = np.array([tam[0] * 0.40, tam[1] * 0.86])
    img = tabuleiro(origem, tam)
    casas = sorted({*torres, *peoes}, key=lambda k: -(k[0] + k[1]))  # de trás (longe) para a frente
    for k in casas:
        centro = casa(*k, origem)
        topo = poe_torre(img, centro, torres.get(k, ""))
        if k in peoes:
            poe_peao(img, topo, peoes[k])
    return img.crop(img.getbbox())
