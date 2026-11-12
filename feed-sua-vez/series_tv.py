#!/usr/bin/env python3
"""Carrossel "QUE JOGO ESSE PERSONAGEM JOGARIA?" (12/nov/2026, ideia dele depois de rejeitar streaming, match, RG e
perfil): uma SALA com a TV mostrando a imagem OFICIAL da série (backdrop do TMDB em `assets/series/`) e, na mesinha
de centro, a caixa do jogo. A luz da TV tinge a parede; embaixo, um cartão com o nome do jogo, a ficha e a frase.

    /usr/bin/python3 series_tv.py --teste    # out/series_tv/teste.jpg
    /usr/bin/python3 series_tv.py            # out/series_tv/NN.png + stories/ + previa.jpg
"""
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import personagens as P  # noqa: E402

E = P.E
W, H = P.W, P.H
SER = os.path.join(ROOT, "assets", "series")
OUT = os.path.join(ROOT, "out", "series_tv")
CREME = P.CREME

# (personagem, artigo, série, imagem, jogo, nome no site, caixa, frase, cor da parede)
PARES = [
    ("ELEVEN", "a", "Stranger Things", "eleven", "The Mind", "The Mind", f"{P.REPO}/roleta-reels/assets/the_mind.png",
     "Um jogo de ler a mente: ninguém fala nada, só sente a hora certa.", (66, 78, 104)),
    ("DUSTIN", "o", "Stranger Things", "dustin", "Dungeon Fighter", "Dungeon Fighter", f"{P.AC}/dungeon_fighter.png",
     "Ele é do clube de RPG: masmorra, monstro e muita risada.", (92, 70, 60)),
    ("WANDINHA", "a", "Wandinha", "wandinha", "Paranormal Detectives", "Paranormal Detectives",
     f"{P.AC}/paranormal_detectives.png", "Conversar com fantasmas e descobrir como eles morreram.", (62, 58, 76)),
    ("TED", "o", "How I Met Your Mother", "ted", "Architectura", "Architectura", f"{P.AC}/architectura.png",
     "Ele é arquiteto: construir a cidade perfeita, prédio por prédio.", (70, 96, 104)),
    ("BARNEY", "o", "How I Met Your Mother", "barney", "Dungeons & Drinks", "Dungeons & Drinks",
     f"{P.AC}/dungeons_drinks.png", "Uma taverna, uma rodada e uma aventura. Challenge accepted!", (102, 66, 62)),
    ("LORELAI", "a", "Gilmore Girls", "lorelai", "Coffee Rush", "Coffee Rush", f"{P.GR}/top10/coffee_rush.png",
     "Café, café e mais café: atenda os pedidos antes que o cliente vá embora.", (84, 100, 76)),
]

TV = (190, 232, 890, 642)  # moldura da TV (x0, y0, x1, y1): tela 16:9 por dentro


@lru_cache(None)
def backdrop(nome, w, h):
    im = Image.open(os.path.join(SER, nome + ".jpg")).convert("RGB")
    r = w / h
    if im.width / im.height > r:
        nw = int(im.height * r)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / r)
        im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)


def sala(parede, img_tv, hh=H, dy=0):
    """Parede com a luz da TV, piso de madeira, tapete e a mesinha de centro (devolve a imagem e o topo da mesa)."""
    img = Image.new("RGBA", (W, hh), parede + (255,))
    a = np.zeros((hh, W, 3), np.float32)
    yy, xx = np.mgrid[0:hh, 0:W]
    base = np.array(parede, np.float32)
    a[:] = base
    # vinheta + brilho da TV na parede (cor média da imagem)
    media = np.array(img_tv.resize((1, 1)).getpixel((0, 0)), np.float32)
    cx, cy = W / 2, (TV[1] + TV[3]) / 2 + dy
    dist = np.sqrt(((xx - cx) / 620) ** 2 + ((yy - cy) / 520) ** 2)
    glow = np.clip(1.2 - dist, 0, 1)[..., None]
    a = a * (0.78 + 0.22 * np.clip(1.4 - dist * 0.7, 0, 1))[..., None] + glow * (media * 0.55 + 40) * 0.45
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    piso = 790 + dy
    rnd = random.Random(5)
    for k, y in enumerate(range(piso, hh, 34)):  # tábuas do piso
        tom = rnd.randint(-10, 10)
        d.rectangle((0, y, W, y + 33), fill=(150 + tom, 104 + tom, 68 + tom))
        d.line((0, y, W, y), fill=(118, 80, 50), width=2)
        for x in range(rnd.randint(-200, 0), W, rnd.randint(260, 420)):
            d.line((x, y, x, y + 33), fill=(118, 80, 50), width=2)
    d.rectangle((0, piso - 18, W, piso), fill=(236, 226, 210))  # rodapé
    d.ellipse((40, piso + 120, W - 40, piso + 420), fill=(226, 206, 170))  # tapete
    d.ellipse((70, piso + 140, W - 70, piso + 400), outline=(200, 176, 136), width=6)
    return img, piso


def tv(img, nome, dy=0):
    x0, y0, x1, y1 = TV[0], TV[1] + dy, TV[2], TV[3] + dy
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=18, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=(20, 20, 22), outline=E.MARROM, width=6)
    m = 18
    sw, sh = x1 - x0 - 2 * m, y1 - y0 - 2 * m
    img.paste(backdrop(nome, sw, sh), (x0 + m, y0 + m))
    brilho = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))  # reflexo
    ImageDraw.Draw(brilho).polygon([(0, 0), (int(sw * 0.35), 0), (int(sw * 0.15), sh), (0, sh)],
                                   fill=(255, 255, 255, 18))
    img.alpha_composite(brilho, (x0 + m, y0 + m))
    return (x0 + m, y0 + m, sw, sh)


def rack(img, dy=0):
    """Rack de madeira embaixo da TV."""
    d = ImageDraw.Draw(img)
    y = TV[3] + dy + 50
    d.rectangle((70, y, W - 70, y + 120), fill=(122, 82, 52), outline=E.MARROM, width=5)
    d.rectangle((70, y, W - 70, y + 16), fill=(146, 100, 64))
    for x in (W // 2 - 200, W // 2 + 200):
        d.rectangle((x - 150, y + 30, x + 150, y + 106), outline=(96, 62, 38), width=4)
        d.ellipse((x - 8, y + 62, x + 8, y + 78), fill=(214, 170, 90))
    return y + 120


def mesinha(img, topo):
    """Mesinha de centro em leve perspectiva; devolve o y do tampo (onde a caixa pousa)."""
    d = ImageDraw.Draw(img)
    y = topo
    d.polygon([(220, y), (W - 220, y), (W - 150, y + 70), (150, y + 70)], fill=(164, 112, 72), outline=E.MARROM)
    d.rectangle((150, y + 70, W - 150, y + 100), fill=(120, 80, 50), outline=E.MARROM, width=4)
    for x in (180, W - 200):
        d.rectangle((x, y + 100, x + 22, y + 190), fill=(110, 72, 44), outline=E.MARROM, width=3)
    return y + 40


def tela(k, story_h=None):
    nome, art, serie, imgn, jogo, site, caixa, frase, parede = PARES[k]
    hh = story_h or H
    dy = 285 if story_h else 0
    btv = backdrop(imgn, 100, 56)
    img, piso = sala(parede, btv, hh, dy)
    tv(img, imgn, dy)
    d = ImageDraw.Draw(img)
    # título na parede
    t = E.titulo(f"O QUE {'A' if art == 'a' else 'O'} {nome}\nJOGARIA?", 74, cor=(255, 255, 255), larg_max=760)
    P.centro(img, t, W / 2 - 70, 34 + dy)
    # selo da série no canto da tela
    sx, sy, sw, sh = TV[0] + 18, TV[1] + 18 + dy, TV[2] - TV[0] - 36, TV[3] - TV[1] - 36
    pl = E.pilula(serie.upper(), 26, (20, 20, 22), (255, 255, 255), fonte_titulo=True, ow=3, sombra=0)
    img.alpha_composite(pl, (sx + 18, sy + sh - pl.height - 18))
    # mesinha com a caixa
    tampo = mesinha(img, piso + 150)
    cx = E.jogo(caixa, 330, larg=400)
    halo = Image.new("L", (cx.width + 260, cx.height + 200), 0)
    ImageDraw.Draw(halo).ellipse((70, 70, halo.width - 70, halo.height - 70), fill=140)
    halo = halo.filter(ImageFilter.GaussianBlur(50))
    luz = Image.new("RGBA", halo.size, (255, 236, 190, 0))
    luz.putalpha(halo)
    img.alpha_composite(luz, ((W - luz.width) // 2, tampo - cx.height - 90))
    sh_ = Image.new("RGBA", (cx.width + 60, 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh_).ellipse((0, 0, cx.width + 60, 40), fill=(0, 0, 0, 90))
    sh_ = sh_.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(sh_, ((W - sh_.width) // 2, tampo - 20))
    img.alpha_composite(cx, ((W - cx.width) // 2, tampo - cx.height + 6))
    # cartão com o jogo
    cw = 940
    tn = E.titulo(jogo, 60, cor=E.LARANJA, larg_max=cw - 60)
    fi = E.texto("  ·  ".join(P.ficha_partes(site)), 26, cor=E.PETROLEO, peso=800, larg_max=cw - 60)
    fr = E.texto(frase, 28, cor=E.MARROM, peso=600, larg_max=cw - 80, entre=1.25)
    ch = tn.height + fi.height + fr.height + 30
    yc = tampo + 130
    if story_h is None:
        yc = min(yc, H - ch - 20)
    img.alpha_composite(E.bloco(cw, ch, CREME, raio=30, ow=6, sombra=10), ((W - cw) // 2, yc))
    P.centro(img, tn, W / 2, yc + 6)
    P.centro(img, fi, W / 2, yc + 6 + tn.height)
    P.centro(img, fr, W / 2, yc + 10 + tn.height + fi.height)
    lg = E.logo(140)
    img.alpha_composite(lg, (W - lg.width - 26, TV[1] + dy - lg.height - 6 if False else 26 + dy))
    return img


def mosaico(w, h):
    im = Image.new("RGB", (w, h))
    cw, ch = w // 3, h // 2
    for i, p in enumerate(PARES):
        im.paste(backdrop(p[3], cw, ch), ((i % 3) * cw, (i // 3) * ch))
    return im


def tela_tv_custom(conteudo, titulo, cor_parede, hh=H):
    dy = (hh - H) // 2 if hh != H else 0
    img, piso = sala(cor_parede, conteudo.resize((100, 56)), hh, dy)
    x0, y0, x1, y1 = TV[0], TV[1] + dy, TV[2], TV[3] + dy
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), radius=18, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=(20, 20, 22), outline=E.MARROM, width=6)
    m = 18
    img.paste(conteudo.resize((x1 - x0 - 2 * m, y1 - y0 - 2 * m), Image.LANCZOS), (x0 + m, y0 + m))
    t = E.titulo(titulo, 74, cor=(255, 255, 255), larg_max=760)
    P.centro(img, t, W / 2 - 70, 34 + dy)
    lg = E.logo(140)
    img.alpha_composite(lg, (W - lg.width - 26, 26 + dy))
    tampo = mesinha(img, piso + 150)
    return img, tampo, dy


def capa():
    img, tampo, _ = tela_tv_custom(mosaico(1200, 676), "QUE JOGO ESSE\nPERSONAGEM JOGARIA?", (70, 66, 92))
    lq = E.leque([p[6] for p in PARES], 250, passo=0.5)
    if lq.width > W - 120:
        lq = lq.resize((W - 120, int(lq.height * (W - 120) / lq.width)), Image.LANCZOS)
    img.alpha_composite(lq, ((W - lq.width) // 2, tampo - lq.height + 40))
    cw = 940
    t1 = E.titulo("ELEVEN · DUSTIN · WANDINHA", 44, cor=E.LARANJA, larg_max=cw - 60)
    t2 = E.titulo("TED · BARNEY · LORELAI", 44, cor=E.LARANJA, larg_max=cw - 60)
    ch = t1.height + t2.height + 30
    yc = H - ch - 30
    img.alpha_composite(E.bloco(cw, ch, CREME, raio=30, ow=6, sombra=10), ((W - cw) // 2, yc))
    P.centro(img, t1, W / 2, yc + 12)
    P.centro(img, t2, W / 2, yc + 12 + t1.height)
    return img


def final(story=False):
    hh = 1920 if story else H
    tela_txt = Image.new("RGB", (1200, 676), (24, 24, 30))
    dt = ImageDraw.Draw(tela_txt)
    dt.text((600, 250), "E VOCÊ?", font=E.lilita(170), fill=(255, 255, 255), anchor="mm")
    dt.text((600, 430), "qual personagem você é na mesa?", font=E.fig(52, 700), fill=(255, 214, 102), anchor="mm")
    img, tampo, dy = tela_tv_custom(tela_txt, "E VOCÊ,\nJOGARIA QUAL?", (84, 70, 96), hh)
    lq = E.leque([p[6] for p in PARES], 230, passo=0.5)
    if lq.width > W - 140:
        lq = lq.resize((W - 140, int(lq.height * (W - 140) / lq.width)), Image.LANCZOS)
    img.alpha_composite(lq, ((W - lq.width) // 2, tampo - lq.height + 40))
    cw = 940
    linhas = [E.texto("Aluga na Sua Vez: retire em Mauá ou receba em casa", 30, cor=E.MARROM, peso=800),
              E.texto("3 jogos = 7 dias pelo mesmo preço!", 30, cor=E.PETROLEO, peso=800),
              E.pilula("LINK NA BIO · @SUAVEZ_BG", 30, E.AMARELO, E.MARROM, fonte_titulo=True),
              E.titulo("MARCA O AMIGO QUE É A WANDINHA DO GRUPO!", 38, cor=E.LARANJA, larg_max=cw - 60)]
    ch = sum(l.height for l in linhas) + 40
    yc = tampo + 120
    if not story:
        yc = H - ch - 24
    img.alpha_composite(E.bloco(cw, ch, CREME, raio=30, ow=6, sombra=10), ((W - cw) // 2, yc))
    y = yc + 14
    for l in linhas:
        P.centro(img, l, W / 2, y)
        y += l.height + 4
    if story:
        tt = E.texto("aluga aqui:", 42, cor=(255, 255, 255), peso=900)
        y = yc + ch + 40
        P.centro(img, tt, W / 2, y)
        d = ImageDraw.Draw(img)
        cx, yy = W // 2, y + tt.height + 10
        d.polygon([(cx - 34, yy), (cx + 34, yy), (cx, yy + 46)], fill=E.LARANJA, outline=E.MARROM, width=5)
    return img


def main():
    os.makedirs(os.path.join(OUT, "stories"), exist_ok=True)
    if "--teste" in sys.argv:
        a, b = tela(0), tela(2)
        f = Image.new("RGB", (W * 2 + 40, H), (255, 255, 255))
        f.paste(a.convert("RGB"), (0, 0))
        f.paste(b.convert("RGB"), (W + 40, 0))
        f.save(os.path.join(OUT, "teste.jpg"), quality=90)
        print("ok teste")
        return
    telas = [capa()] + [tela(k) for k in range(len(PARES))] + [final()]
    stories = [None] + [tela(k, story_h=1920) for k in range(len(PARES))] + [final(story=True)]
    for i, (t, st) in enumerate(zip(telas, stories), 1):
        t.convert("RGB").save(os.path.join(OUT, f"{i:02d}.png"))
        if st is None:
            st = t.resize((W, 1920)).filter(ImageFilter.GaussianBlur(40))
            st = Image.blend(st.convert("RGB"), Image.new("RGB", (W, 1920), (30, 28, 40)), 0.35).convert("RGBA")
            st.alpha_composite(t, (0, 285))
        st.convert("RGB").save(os.path.join(OUT, "stories", f"story_{i:02d}.png"))
    folha = Image.new("RGB", (4 * 370 + 10, 2 * 460 + 10), (255, 255, 255))
    for i, t in enumerate(telas):
        folha.paste(t.convert("RGB").resize((360, 450)), (10 + (i % 4) * 370, 10 + (i // 4) * 460))
    folha.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
