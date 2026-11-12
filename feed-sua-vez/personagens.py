#!/usr/bin/env python3
"""Carrosséis "QUE JOGO ESSE PERSONAGEM JOGARIA?" (12/nov/2026, ideia da Jéssica), cada um com conceito próprio:

  friends  A PORTA ROXA: fundo de porta de madeira roxa com a moldura amarela do olho mágico (com o NOSSO logo dentro),
           maçaneta dourada e um bilhete preso com fita: nome do personagem + emoji, "jogaria...", caixa, ficha e frase.
  series   APP DE STREAMING: tela escura, "Porque você assistiu [série]", miniatura do personagem (emoji), e o jogo
           como o título recomendado: "98% relevante", fichas em pílulas, frase, botões ALUGAR / MINHA LISTA.

Sem foto dos atores (direito de imagem de pessoa real em anúncio): personagem = nome + emoji.

    /usr/bin/python3 personagens.py friends --teste
    /usr/bin/python3 personagens.py series      # out/<nome>/NN.png + stories/ + previa.jpg
"""
import json
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
GR = os.path.join(REPO, "gravados-reels", "assets")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H = 1080, 1350
CREME = (255, 246, 228)
ROXO = (104, 66, 146)
AMARELO_PORTA = (246, 196, 52)
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json")))

# (personagem, emojis, jogo, nome no site, caixa, frase)
LISTAS = {
    "friends": [
        ("MONICA", "🖼️", "Art Society", "Art Society", f"{AC}/art_society.png",
         "Pendurar os quadros na parede, tudo certinho e alinhado. E ela PRECISA ganhar."),
        ("RACHEL", "🛍️", "High Society", "High Society", f"{AC}/high_society.png",
         "Leilão de luxo pra quem ama gastar... só não pode terminar com menos dinheiro que todo mundo."),
        ("ROSS", "🦖", "Draftosaurus", "Draftosaurus", f"{AC}/draftosaurus.png",
         "Dinossauros! Ele explicaria cada espécie. (E ainda diria que estava dando um tempo.)"),
        ("JOEY", "🎭", "Say my Name", "Say my Name", f"{AC}/say_my_name.png",
         "Ele é ator: interpreta até a mesa adivinhar. How you doin'?"),
        ("PHOEBE", "🐈", "Nekojima", "Nekojima", f"{AC}/nekojima.png",
         "Smelly cat, smelly cat... uma ilha inteira cheia de gatos."),
        ("CHANDLER", "😏", "Blablabel", "Blablabel", f"{AC}/blablabel.png",
         "Inventar nome pras coisas e fazer todo mundo rir. Could it BE any more perfeito?"),
    ],
    "joey": [
        ("JOEY", "🍕", "Taco Gato Cabra Queijo Pizza", "Taco Gato Cabra Queso Pizza: Carpincho promo",
         f"{REPO}/roleta-reels/assets/taco_gato.png",
         "Taco, queijo, PIZZA! Ele bate na pilha primeiro... só pra não ter que dividir."),
        ("JOEY", "🍗", "Critter Kitchen", "Critter Kitchen", f"{AC}/critter_kitchen.png",
         "Um jogo inteiro sobre comida. Joey doesn't share food!"),
        ("JOEY", "🎭", "Say my Name", "Say my Name", f"{AC}/say_my_name.png",
         "Ele é ator: interpreta até a mesa adivinhar. How you doin'?"),
    ],
    "series": [
        ("ELEVEN", "🧇", "Stranger Things", "The Mind", "The Mind", f"{REPO}/roleta-reels/assets/the_mind.png",
         "Um jogo de ler a mente: ninguém pode falar nada, só sentir a hora certa."),
        ("DUSTIN", "🧢", "Stranger Things", "Dungeon Fighter", "Dungeon Fighter", f"{AC}/dungeon_fighter.png",
         "Ele é do clube de RPG: masmorra, monstro e muita risada."),
        ("WANDINHA", "🖤", "Wandinha", "Paranormal Detectives", "Paranormal Detectives",
         f"{AC}/paranormal_detectives.png", "Conversar com fantasmas e descobrir como eles morreram."),
        ("TED MOSBY", "🏛️", "How I Met Your Mother", "Architectura", "Architectura", f"{AC}/architectura.png",
         "Ele é arquiteto: construir a cidade perfeita, prédio por prédio."),
        ("BARNEY", "🍸", "How I Met Your Mother", "Dungeons & Drinks", "Dungeons & Drinks", f"{AC}/dungeons_drinks.png",
         "Uma taverna, uma rodada e uma aventura. Challenge accepted!"),
        ("LORELAI", "☕", "Gilmore Girls", "Coffee Rush", "Coffee Rush", f"{GR}/top10/coffee_rush.png",
         "Café, café e mais café: atenda os pedidos antes que o cliente vá embora."),
    ],
}


def ficha_partes(nome):
    d = SITE[nome]
    a, _, b = d["jogadores"].partition("–")
    jog = f"{a} jogadores" if a == b else f"{a} a {b} jogadores"
    dias = 7 if d["preco"] == 60 else 5
    return [jog, d["tempo"].replace("min", " min"), f"R$ {d['preco']} / {dias} dias"]


@lru_cache(None)
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(size), max(2, int(im.height * size / im.width))), Image.LANCZOS)


def centro(img, im, cx, y):
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


# ------------------------------------------------------------------------------------------------- FRIENDS: porta roxa
@lru_cache(None)
def _porta(hh):
    img = Image.new("RGBA", (W, hh), ROXO + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for x in range(0, W, 135):  # tábuas
        tom = rnd.randint(-8, 8)
        d.rectangle((x, 0, x + 133, hh), fill=(ROXO[0] + tom, ROXO[1] + tom, ROXO[2] + tom))
        d.line((x, 0, x, hh), fill=(78, 46, 112), width=4)
        for _ in range(26):  # veios
            y = rnd.randint(0, hh)
            d.line((x + rnd.randint(8, 40), y, x + rnd.randint(60, 125), y + rnd.randint(-3, 3)),
                   fill=(ROXO[0] + 10, ROXO[1] + 8, ROXO[2] + 12), width=2)
    # maçaneta dourada à direita
    cx, cy = W - 70, int(hh * 0.62)
    d.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill=E.MARROM)
    d.ellipse((cx - 38, cy - 38, cx + 34, cy + 34), fill=(222, 170, 60))
    d.ellipse((cx - 22, cy - 26, cx + 2, cy - 4), fill=(255, 226, 140))
    return img


def olho_magico(img, cx, cy, w=330, h=170):
    """A moldura amarela do olho mágico, com o logo da Sua Vez no meio."""
    d = ImageDraw.Draw(img)
    for k, cor in [(16, E.MARROM), (8, AMARELO_PORTA)]:
        pass
    d.ellipse((cx - w // 2 + 10, cy - h // 2 + 12, cx + w // 2 + 10, cy + h // 2 + 12), fill=E.MARROM)  # sombra
    d.ellipse((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2), fill=AMARELO_PORTA, outline=E.MARROM, width=7)
    d.ellipse((cx - w // 2 + 34, cy - h // 2 + 30, cx + w // 2 - 34, cy + h // 2 - 30), fill=(255, 255, 255),
              outline=E.MARROM, width=5)
    lg = Image.open(E.LOGO).convert("RGBA")
    lw = w - 140
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    if lg.height > h - 90:
        lg = lg.resize((int(lg.width * (h - 90) / lg.height), h - 90), Image.LANCZOS)
    img.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))


def fita(img, cx, cy, w=170, ang=-8):
    t = Image.new("RGBA", (w, 48), (250, 238, 200, 210))
    ImageDraw.Draw(t).rectangle((0, 0, w - 1, 47), outline=(220, 205, 160, 220), width=2)
    t = t.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))


def tela_friends(k, pares):
    nome, emj, jogo, site, caixa, frase = pares[k]
    img = _porta(H).copy()
    olho_magico(img, W // 2, 125)
    bw, bh = 880, 1050
    b = Image.new("RGBA", (bw + 16, bh + 16), (0, 0, 0, 0))
    b.alpha_composite(E.bloco(bw, bh, CREME, raio=14, ow=6, sombra=12))
    yy = 40
    e = emoji(emj, 120)
    t = E.titulo(nome, 120, cor=E.LARANJA, larg_max=bw - 220)
    xx = (bw - (t.width + e.width + 20)) // 2
    b.alpha_composite(t, (xx, yy))
    b.alpha_composite(e, (xx + t.width + 20, yy + (t.height - e.height) // 2 - 6))
    yy += t.height
    jt = E.texto("jogaria...", 44, cor=E.PETROLEO, peso=900)
    centro(b, jt, bw / 2, yy - 6)
    yy += jt.height + 6
    cx = E.jogo(caixa, 400, larg=470)
    centro(b, cx, bw / 2, yy)
    yy += cx.height + 6
    tn = E.titulo(jogo, 62, cor=E.MARROM, contorno=E.MARROM, larg_max=bw - 80) if False else \
        E.titulo(jogo, 62, cor=(255, 255, 255), larg_max=bw - 80)
    centro(b, tn, bw / 2, yy)
    yy += tn.height
    fi = E.texto("  ·  ".join(ficha_partes(site)), 27, cor=E.PETROLEO, peso=800, larg_max=bw - 80)
    centro(b, fi, bw / 2, yy)
    yy += fi.height + 4
    fr = E.texto(frase, 31, cor=E.MARROM, peso=600, larg_max=bw - 120, entre=1.28)
    centro(b, fr, bw / 2, yy)
    b = b.rotate([-1.6, 1.4][k % 2], expand=True, resample=Image.BICUBIC)
    img.alpha_composite(b, ((W - b.width) // 2, 225))
    fita(img, W // 2 - 300, 252, ang=-12)
    fita(img, W // 2 + 300, 252, ang=10)
    return img


def capa_friends(pares):
    img = _porta(H).copy()
    olho_magico(img, W // 2, 140, 380, 196)
    t = E.titulo("QUE JOGO CADA\nAMIGO JOGARIA?", 108, cor=AMARELO_PORTA, larg_max=1000)
    centro(img, t, W / 2, 270)
    y = 270 + t.height + 10
    for i, (nome, emj, *_r) in enumerate(pares):
        c = E.pilula(f"{nome}", 42, CREME, E.MARROM, fonte_titulo=True)
        e = emoji(emj, 58)
        x = 150 if i % 2 == 0 else 570
        yy = y + (i // 2) * 120
        img.alpha_composite(e, (x, yy + 4))
        img.alpha_composite(c, (x + 72, yy))
    lq = E.leque([p[4] for p in pares], 230, passo=0.55)
    if lq.width > W - 100:
        lq = lq.resize((W - 100, int(lq.height * (W - 100) / lq.width)), Image.LANCZOS)
    centro(img, lq, W / 2, H - lq.height - 30)
    return img


# --------------------------------------------------------------------------------------------- SÉRIES: app de streaming
FUNDO_APP = (18, 18, 24)


@lru_cache(None)
def _app(hh):
    img = Image.new("RGBA", (W, hh), FUNDO_APP + (255,))
    d = ImageDraw.Draw(img)
    for y in range(hh):  # leve degradê
        v = int(8 * y / hh)
        d.line((0, y, W, y), fill=(18 + v, 18 + v, 26 + v))
    return img


def barra_app(img, y=40):
    lg = E.logo(150)
    img.alpha_composite(lg, (40, y))
    d = ImageDraw.Draw(img)
    f = E.fig(30, 800)
    x = 40 + lg.width + 40
    for i, t in enumerate(["Início", "Séries", "Jogos", "Minha lista"]):
        d.text((x, y + lg.height // 2), t, font=f, fill=(255, 255, 255) if i == 2 else (150, 150, 160), anchor="lm")
        x += d.textlength(t, font=f) + 34


def tela_series(k, pares):
    nome, emj, serie, jogo, site, caixa, frase = pares[k]
    img = _app(H).copy()
    barra_app(img)
    d = ImageDraw.Draw(img)
    y = 170
    d.text((60, y), "Porque você assistiu", font=E.fig(34, 600), fill=(170, 170, 180))
    d.text((60, y + 44), serie, font=E.lilita(62), fill=(255, 255, 255))
    y += 140
    # miniatura do personagem
    mw, mh = 300, 300
    m = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
    dm = ImageDraw.Draw(m)
    dm.rounded_rectangle((0, 0, mw - 1, mh - 1), radius=22, fill=(44, 44, 56))
    e = emoji(emj, 150)
    m.alpha_composite(e, ((mw - e.width) // 2, 40))
    dm.text((mw // 2, mh - 52), nome, font=E.lilita(44), fill=(255, 255, 255), anchor="mm")
    img.alpha_composite(m, (60, y))
    # destaque: o jogo recomendado
    hx, hw, hh_ = 390, 630, 300
    cx = E.jogo(caixa, 260, larg=300)
    bg = Image.open(caixa).convert("RGBA").resize((hw, hh_)).filter(ImageFilter.GaussianBlur(26))
    escuro = Image.new("RGBA", (hw, hh_), (0, 0, 0, 120))
    bg.alpha_composite(escuro)
    msk = Image.new("L", (hw, hh_), 0)
    ImageDraw.Draw(msk).rounded_rectangle((0, 0, hw - 1, hh_ - 1), radius=22, fill=255)
    tile = Image.new("RGBA", (hw, hh_), (0, 0, 0, 0))
    tile.paste(bg, (0, 0), msk)
    tile.alpha_composite(cx, ((hw - cx.width) // 2, (hh_ - cx.height) // 2))
    img.alpha_composite(tile, (hx, y))
    d.text((hx + 18, y + 16), "RECOMENDADO", font=E.fig(24, 900), fill=E.AMARELO)
    y += mh + 50
    d.text((60, y), f"{nome.title() if nome != 'TED MOSBY' else 'Ted Mosby'} jogaria:", font=E.fig(36, 700),
           fill=(170, 170, 180))
    y += 50
    tn = E.titulo(jogo, 88, cor=(255, 255, 255), contorno=(0, 0, 0), sw=0, sombra=0, larg_max=W - 120)
    img.alpha_composite(tn, (50, y))
    y += tn.height
    d.text((60, y), "98% relevante", font=E.fig(34, 900), fill=(90, 210, 120))
    x = 60 + d.textlength("98% relevante", font=E.fig(34, 900)) + 24
    for p in ficha_partes(site):
        f = E.fig(28, 700)
        tw = d.textlength(p, font=f)
        d.rounded_rectangle((x, y + 2, x + tw + 28, y + 42), radius=8, outline=(150, 150, 160), width=2)
        d.text((x + 14, y + 22), p, font=f, fill=(220, 220, 228), anchor="lm")
        x += tw + 44
    y += 70
    fr = E.texto(frase, 33, cor=(230, 230, 236), peso=500, larg_max=W - 140, alinha="lm", entre=1.3)
    img.alpha_composite(fr, (55, y))
    y += fr.height + 30
    # botões
    d.rounded_rectangle((60, y, 460, y + 92), radius=14, fill=(255, 255, 255))
    d.polygon([(110, y + 26), (110, y + 66), (146, y + 46)], fill=(0, 0, 0))
    d.text((170, y + 46), "ALUGAR", font=E.lilita(46), fill=(0, 0, 0), anchor="lm")
    d.rounded_rectangle((490, y, 1020, y + 92), radius=14, fill=(70, 70, 82))
    d.text((530, y + 46), "+  Minha lista", font=E.fig(40, 800), fill=(255, 255, 255), anchor="lm")
    y += 130
    # barra de progresso do "episódio"
    d.rounded_rectangle((60, y, W - 60, y + 10), radius=5, fill=(70, 70, 82))
    d.rounded_rectangle((60, y, 60 + (W - 120) * (k + 1) // len(pares), y + 10), radius=5, fill=E.LARANJA)
    d.text((W - 60, y + 28), f"Ep. {k + 1} de {len(pares)}", font=E.fig(26, 700), fill=(150, 150, 160), anchor="ra")
    return img


def capa_series(pares):
    img = _app(H).copy()
    barra_app(img)
    d = ImageDraw.Draw(img)
    t = E.titulo("QUE JOGO ESSE\nPERSONAGEM\nJOGARIA?", 112, cor=(255, 255, 255), contorno=(0, 0, 0), sw=0,
                 sombra=0, larg_max=980)
    centro(img, t, W / 2, 170)
    d.text((W // 2, 170 + t.height + 10), "Uma seleção baseada no que você assiste", font=E.fig(34, 600),
           fill=(170, 170, 180), anchor="ma")
    y = 170 + t.height + 90
    tw, th = 300, 300
    for i, (nome, emj, *_r) in enumerate(pares):
        x = 60 + (i % 3) * (tw + 30)
        yy = y + (i // 3) * (th + 30)
        m = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        dm = ImageDraw.Draw(m)
        dm.rounded_rectangle((0, 0, tw - 1, th - 1), radius=22, fill=(44, 44, 56))
        e = emoji(emj, 130)
        m.alpha_composite(e, ((tw - e.width) // 2, 40))
        dm.text((tw // 2, th - 52), nome, font=E.lilita(40), fill=(255, 255, 255), anchor="mm")
        img.alpha_composite(m, (x, yy))
    return img


# --------------------------------------------------------------------------------------------- final + stories
def tela_final(modo, pares, story=False):
    hh = 1920 if story else H
    if modo == "friends":
        img = _porta(hh).copy()
        olho_magico(img, W // 2, 150, 380, 196)
        y = 290
        cor_t, cor_c = AMARELO_PORTA, (255, 255, 255)
    else:
        img = _app(hh).copy()
        barra_app(img)
        y = 190
        cor_t, cor_c = (255, 255, 255), E.AMARELO
    t = E.titulo("E VOCÊ, JOGARIA\nQUAL DESSES?", 90, cor=cor_t, larg_max=980,
                 **({} if modo == "friends" else {"contorno": (0, 0, 0), "sw": 0, "sombra": 0}))
    centro(img, t, W / 2, y)
    y += t.height + 20
    cw, ch = 900, 470
    img.alpha_composite(E.bloco(cw, ch, CREME, raio=36, ow=8, sombra=14), ((W - cw) // 2, y))
    cx_i = 5 if modo == "series" else 4
    lq = E.leque([p[cx_i] for p in pares], 200, passo=0.5)
    if lq.width > cw - 60:
        lq = lq.resize((cw - 60, int(lq.height * (cw - 60) / lq.width)), Image.LANCZOS)
    centro(img, lq, W / 2, y + 24)
    yy = y + 24 + lq.height - 6
    for txt, cor in [("Aluga na Sua Vez: retire em Mauá ou receba em casa", E.MARROM),
                     ("3 jogos = 7 dias pelo mesmo preço!", E.PETROLEO)]:
        tt = E.texto(txt, 31, cor=cor, peso=800, larg_max=820)
        centro(img, tt, W / 2, yy)
        yy += tt.height
    pl = E.pilula("LINK NA BIO · @SUAVEZ_BG", 32, E.AMARELO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, yy + 8)
    y += ch + 40
    c = E.titulo("MARCA AQUELE AMIGO QUE É\n" + ("O ROSS DO GRUPO!" if modo == "friends" else "A WANDINHA DO GRUPO!"),
                 52, cor=cor_c, larg_max=980)
    centro(img, c, W / 2, y)
    if story:
        y += c.height + 40
        tt = E.texto("aluga aqui:", 42, cor=(255, 255, 255), peso=900)
        centro(img, tt, W / 2, y)
        d = ImageDraw.Draw(img)
        cx, yy = W // 2, y + tt.height + 10
        d.polygon([(cx - 34, yy), (cx + 34, yy), (cx, yy + 46)], fill=E.LARANJA, outline=E.MARROM, width=5)
    return img


def story_de(modo, tela):
    st = (_porta(1920) if modo == "friends" else _app(1920)).copy()
    st.alpha_composite(tela, (0, 285))
    return st


def main():
    modo = sys.argv[1]
    pares = LISTAS[modo]
    out = os.path.join(ROOT, "out", "personagens_" + modo)
    os.makedirs(os.path.join(out, "stories"), exist_ok=True)
    capa = capa_friends if modo == "friends" else capa_series
    tela = tela_friends if modo == "friends" else tela_series
    if modo == "joey":
        ts = [tela_friends(k, pares) for k in range(3)]
        f = Image.new("RGB", (W * 3 + 80, H), (255, 255, 255))
        for i, t in enumerate(ts):
            f.paste(t.convert("RGB"), (i * (W + 40), 0))
        f.resize((f.width // 2, f.height // 2)).save(os.path.join(ROOT, "out", "joey_opcoes.jpg"), quality=90)
        print("ok joey")
        return
    if "--teste" in sys.argv:
        a, b = capa(pares), tela(0, pares)
        f = Image.new("RGB", (W * 2 + 40, H), (255, 255, 255))
        f.paste(a.convert("RGB"), (0, 0))
        f.paste(b.convert("RGB"), (W + 40, 0))
        f.save(os.path.join(out, "teste.jpg"), quality=90)
        print("ok teste")
        return
    telas = [capa(pares)] + [tela(k, pares) for k in range(len(pares))] + [tela_final(modo, pares)]
    for i, t in enumerate(telas, 1):
        t.convert("RGB").save(os.path.join(out, f"{i:02d}.png"))
        st = tela_final(modo, pares, story=True) if i == len(telas) else story_de(modo, t)
        st.convert("RGB").save(os.path.join(out, "stories", f"story_{i:02d}.png"))
    folha = Image.new("RGB", (4 * 370 + 10, 2 * 460 + 10), (255, 255, 255))
    for i, t in enumerate(telas):
        folha.paste(t.convert("RGB").resize((360, 450)), (10 + (i % 4) * 370, 10 + (i // 4) * 460))
    folha.save(os.path.join(out, "previa.jpg"), quality=88)
    print("ok", len(telas))


if __name__ == "__main__":
    main()
