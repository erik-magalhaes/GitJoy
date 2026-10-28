#!/usr/bin/env python3
"""Carrossel 1080x1350 de Halloween "ESCOLHA SEU MEDO" (28/out/2026, pedido da Jéssica). Conceito próprio: A PRATELEIRA
DE TERROR DA LOCADORA. Cada jogo é uma FITA VHS de terror (estojo preto, capa com a caixa oficial, adesivo de gênero e o
adesivo de locadora "SEJA GENTIL: DEVOLVA EM 5 DIAS"), letreiro neon vermelho, prateleira escura com lombadas.
Adulto/retrô (ele achou a noite roxa do halloween.py "infantil"; os vídeos já usam o pôster de cinema). Caixas oficiais de
halloween-reels/assets/; fichas do site (comum/dados/acervo_site.json). Deluxe (Final Girl) = 7 dias.

    python3 halloween_carrossel.py      # out/halloween/01..09.png (+ out/halloween_folha.jpg)
"""
import json
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, cola,  # noqa
                    lilita, fig)

OUT = os.path.join(ROOT, "out", "halloween")
W, H = 1080, 1350
NEON, ESCURO, PRETO = (255, 46, 70), (16, 10, 20), (12, 12, 14)
HW = os.path.join(REPO, "halloween-reels", "assets")
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8"))
MEDOS = [  # (medo, gênero da fita, frase, nome no site, caixa, nome na tela, cor do adesivo)
    ("ASSASSINO\nMASCARADO", "SLASHER", "Você é a última sobrevivente contra o assassino. Jogo SOLO, pra jogar de luz apagada.",
     "Final Girl", "finalgirl.png", "Final Girl", (200, 30, 40)),
    ("ZUMBIS", "MORTOS-VIVOS", "O shopping foi tomado por zumbis: a turma se une pra sobreviver até o fim.",
     "Tiny Epic Zombies", "tiny_zombies.png", "Tiny Epic Zombies", (70, 150, 60)),
    ("VAMPIROS", "GÓTICO", "Duelo a dois: um é o Drácula, o outro é o caçador Van Helsing.",
     "Dracula vs Van Helsing", "dracula.png", "Drácula vs Van Helsing", (140, 20, 40)),
    ("FANTASMAS", "SOBRENATURAL", "Um fantasma precisa contar como morreu... sem poder falar. Os detetives que desvendem!",
     "Paranormal Detectives", "paranormal.png", "Paranormal Detectives", (60, 110, 200)),
    ("MONSTROS", "CRIATURAS", "Os monstros estão invadindo a cidade. Quem segura essa?",
     "O Vale dos Monstros II: A Invasão da Cidade", "vale_monstros.png", "O Vale dos Monstros II", (230, 120, 30)),
    ("PERDER A\nCABEÇA", "TERROR CÔMICO", "Pra rir de nervoso com a galera (e torcer pra não ser você).",
     "Por favor, não corte minha cabeça!", "nao_corte.png", "Por favor, não corte minha cabeça!", (120, 60, 170)),
    ("NADA?\nENTÃO É FAMÍLIA", "MISTÉRIO", "Pra família inteira: a turma do Scooby desmascarando o vilão.",
     "Scooby-Doo! The Board Game", "scooby.png", "Scooby-Doo!", (40, 160, 120)),
]


def ficha(nome):
    v = SITE[nome]
    a, b = v["jogadores"].split("–")
    jog = f"{a} jogador" if a == b == "1" else (f"{a} jogadores" if a == b else f"{a} a {b} jogadores")
    dias = 7 if v["preco"] == 60 else 5  # Deluxe = 7 dias
    return f"{jog} · {v['tempo'].replace('min', ' min')}", f"R$ {v['preco']} por {dias} dias", dias


@lru_cache(None)
def _prateleira():
    """Parede escura da locadora com 2 prateleiras de lombadas de fita no fundo (desfocadas) e luz vermelha."""
    rng = np.random.default_rng(5)
    img = Image.new("RGBA", (W, H), ESCURO + (255,))
    d = ImageDraw.Draw(img)
    for y0 in (180, 1060):
        x = 40
        while x < W - 40:
            w = int(rng.integers(34, 48))
            c = tuple(int(v) for v in rng.choice([(40, 40, 46), (60, 20, 26), (26, 30, 50), (50, 44, 30), (30, 50, 40)]))
            d.rectangle((x, y0, x + w, y0 + 230), fill=c)
            d.rectangle((x + 6, y0 + 30, x + w - 6, y0 + 60), fill=tuple(min(255, v + 60) for v in c))
            x += w + 4
        d.rectangle((0, y0 + 230, W, y0 + 262), fill=(54, 34, 22))
    img = img.filter(ImageFilter.GaussianBlur(5))
    a = np.asarray(img).astype(float)  # escurece o meio (onde fica a fita) e põe a luz vermelha no alto
    yy, xx = np.mgrid[0:H, 0:W]
    vin = 1 - 0.62 * np.clip(1 - ((xx - W / 2) ** 2 / (W * 0.55) ** 2 + (yy - H / 2) ** 2 / (H * 0.42) ** 2), 0, 1)
    a[..., :3] *= vin[..., None]
    luz = np.clip(1 - ((xx - W / 2) ** 2 + (yy + 100) ** 2) / (700 ** 2), 0, 1)[..., None] * np.array([70, 6, 14])
    a[..., :3] += luz
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def fundo():
    return _prateleira().copy()


@lru_cache(None)
def neon(txt, s, cor=NEON):
    """Letreiro de neon: tubo claro com brilho colorido em volta."""
    f = lilita(s)
    tw = ImageDraw.Draw(Image.new("L", (1, 1))).multiline_textbbox((0, 0), txt, font=f, align="center", spacing=8)
    w, h = int(tw[2]) + 120, int(tw[3]) + 120
    base = Image.new("L", (w, h), 0)
    ImageDraw.Draw(base).multiline_text((w / 2, h / 2), txt, font=f, fill=255, anchor="mm", align="center", spacing=8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for r, a in ((26, 0.55), (12, 0.8), (4, 1.0)):
        g = base.filter(ImageFilter.GaussianBlur(r)).point(lambda v, a=a: int(min(255, v * a * 1.6)))
        lay = Image.new("RGBA", (w, h), cor + (0,))
        lay.putalpha(g)
        im.alpha_composite(lay)
    nucleo = Image.new("RGBA", (w, h), (255, 225, 230, 0))
    nucleo.putalpha(base.filter(ImageFilter.GaussianBlur(1)))
    im.alpha_composite(nucleo)
    return im


def adesivo_redondo(txt, r, cor, fg=BRANCO, s=None):
    im = Image.new("RGBA", (2 * r + 16, 2 * r + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((10, 12, 2 * r + 10, 2 * r + 12), fill=(0, 0, 0, 140))
    d.ellipse((2, 2, 2 * r + 2, 2 * r + 2), fill=cor, outline=BRANCO, width=5)
    tx = texto(txt, s or int(r * 0.3), fg, 900, larg_max=r * 1.5, entre=1.05)
    im.alpha_composite(tx, (r + 2 - tx.width // 2, r + 2 - tx.height // 2))
    return im


def fita(caixa, genero, cor, w=620, h=900):
    """Estojo de VHS preto com a capa: faixa do topo com o gênero, a caixa oficial do jogo e a faixa 'VHS' embaixo."""
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((18, 22, w + 18, h + 22), radius=26, fill=(0, 0, 0, 160))
    d.rounded_rectangle((0, 0, w, h), radius=26, fill=PRETO, outline=(60, 60, 66), width=4)
    m = 34
    capa = Image.new("RGBA", (w - 2 * m, h - 2 * m), (0, 0, 0, 255))
    cd = ImageDraw.Draw(capa)
    for y in range(capa.height):  # degradê escuro com a cor do gênero
        u = y / capa.height
        cd.line((0, y, capa.width, y), fill=tuple(int(c * (0.18 + 0.32 * (1 - u))) for c in cor))
    cola(capa, jogo(os.path.join(HW, caixa), 560, capa.width - 90), capa.width / 2, capa.height / 2 + 10)
    cd.rectangle((0, 0, capa.width, 86), fill=cor)
    cd.text((capa.width / 2, 45), genero, font=lilita(52), fill=BRANCO, anchor="mm")
    cd.rectangle((0, capa.height - 80, capa.width, capa.height), fill=(20, 20, 22))
    cd.text((34, capa.height - 40), "VHS", font=lilita(50 if w >= 500 else 30), fill=BRANCO, anchor="lm")
    if w >= 500:
        cd.text((capa.width - 30, capa.height - 40), "HI-FI · STEREO", font=fig(26, 800), fill=(170, 170, 176), anchor="rm")
    im.alpha_composite(capa, (m, m))
    brilho = Image.new("RGBA", (w, h), (0, 0, 0, 0))  # reflexo do plástico
    ImageDraw.Draw(brilho).polygon([(w * 0.55, 0), (w * 0.78, 0), (w * 0.3, h), (w * 0.08, h)], fill=(255, 255, 255, 22))
    im.alpha_composite(brilho)
    return im


def etiqueta_locadora(linha1, linha2, w=420):
    """Etiqueta branca de locadora (preço e prazo), como as coladas nas fitas."""
    im = bloco(w, 150, (250, 248, 240), raio=14, ow=5, sombra=8, contorno=(30, 30, 30))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 40), fill=NEON)
    d.text((w / 2, 21), "LOCADORA SUA VEZ", font=fig(24, 900), fill=BRANCO, anchor="mm")
    d.text((w / 2, 78), linha1, font=fig(28, 800), fill=(40, 40, 40), anchor="mm")
    d.text((w / 2, 118), linha2, font=fig(32, 900), fill=NEON, anchor="mm")
    return im


def tela_medo(k, medo, genero, frase, nome_site, caixa, nome, cor):
    img = fundo()
    cola(img, texto("se você tem medo de...", 40, (230, 200, 205), 800), W / 2, 92)
    cola(img, neon(medo, 104 if "\n" not in medo else 88), W / 2, 230 if "\n" not in medo else 250)
    cola(img, fita(caixa, genero, cor, h=830), 390, 760, -4)
    l1, l2, dias = ficha(nome_site)
    cola(img, etiqueta_locadora(l1, l2), 820, 640, 7)
    cola(img, adesivo_redondo(f"SEJA GENTIL: DEVOLVA EM {dias} DIAS", 110, AMARELO, MARROM, 27), 850, 900, -10)
    cola(img, pilula(nome, 40, BRANCO, PRETO, pad=(26, 10), fonte_titulo=True), W / 2, 1200, -2)
    cola(img, texto(frase, 34, (235, 225, 228), 700, larg_max=900, entre=1.25), W / 2, 1278)
    return img


def capa():
    img = fundo()
    cola(img, logo(230), W - 165, 105, 3)
    cola(img, neon("TERROR", 200), W / 2, 330)
    cola(img, titulo("ESCOLHA\nSEU MEDO", 140, BRANCO, PRETO), W / 2, 660, -3)
    for j, (caixa, cor) in enumerate([("finalgirl.png", (200, 30, 40)), ("dracula.png", (140, 20, 40)),
                                      ("paranormal.png", (60, 110, 200))]):
        f = fita(caixa, "", cor, w=300, h=430)
        cola(img, f, 220 + j * 320, 1060, (-8, 0, 8)[j])
    cola(img, pilula("a prateleira de terror da locadora  →", 34, NEON, BRANCO, pad=(26, 10)), W / 2, H - 60, -1)
    return img


def final():
    img = fundo()
    cola(img, neon("QUAL É O\nSEU MEDO?", 120), W / 2, 330)
    cola(img, pilula("Comenta aqui!", 54, AMARELO, MARROM, pad=(30, 12), fonte_titulo=True), W / 2, 580, 3)
    c = bloco(820, 470, (250, 248, 240), raio=18, ow=6, sombra=12, contorno=(30, 30, 30))
    ImageDraw.Draw(c).rectangle((0, 0, 820, 60), fill=NEON)
    cola(c, texto("SESSÃO DE TERROR EM CASA", 34, BRANCO, 900), 410, 32)
    cola(c, logo(320), 410, 180, -2)
    cola(c, texto("Retire em Mauá ou receba em casa.\nAlugue 3 e os 3 ficam 7 dias!", 36, (40, 40, 40), 800, entre=1.3),
         410, 360)
    cola(img, c, W / 2, 900, -1)
    cola(img, pilula("LINK NA BIO · @SUAVEZ_BG", 42, NEON, BRANCO, pad=(30, 14), fonte_titulo=True), W / 2, 1230, -2)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    telas = [capa()] + [tela_medo(k + 1, *m) for k, m in enumerate(MEDOS)] + [final()]
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (5 * 405 + 60, 2 * 506 + 30), (255, 255, 255))
    for k, im in enumerate(telas):
        folha.paste(im.convert("RGB").resize((405, 506), Image.LANCZOS), (10 + (k % 5) * 415, 10 + (k // 5) * 516))
    folha.save(os.path.join(ROOT, "out", "halloween_folha.jpg"), quality=90)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
