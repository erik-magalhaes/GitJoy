"""Stories "QUE JOGO É ESSE?" (estilo "qual é esse Pokémon?"): sombra da caixa + categoria + dicas + 3 opções.
Para cada jogo sai a pergunta (NN_pergunta.png) e a resposta (NN_resposta.png), 1080x1920.
Uso: /usr/bin/python3 promo/quiz_sombra.py"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

W, H = 1080, 1920
OUT = os.path.join(REPO, "promo", "out", "quiz_sombra")
AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
VERDE = (64, 168, 82)
ESCURO = (22, 34, 52)

# (arquivo da caixa, nome, categoria, jogadores, tempo, dicas, opções, índice da certa)
JOGOS = [
    ("hive", "Hive", "POCKET", "2 jogadores", "20 min",
     ["Não tem tabuleiro", "As peças são insetos", "Cerque a abelha rainha do outro!"],
     ["Azul Duel", "Hive", "7 Wonders Duel"], 1),
    ("ticket_to_ride", "Ticket to Ride", "FAMÍLIA", "2 a 5 jogadores", "60 min",
     ["Tem trem", "Junte cartas da mesma cor", "Ligue as cidades do seu bilhete"],
     ["Next Station London", "Metro", "Ticket to Ride"], 2),
    ("dixit", "Dixit", "FAMÍLIA", "3 a 6 jogadores", "30 min",
     ["Cartas com desenhos de sonho", "Dê uma dica sobre a sua carta", "Fácil demais? Ninguém pontua!"],
     ["Dixit", "Telma", "Say my Name"], 0),
    ("draftosaurus", "Draftosaurus", "FAMÍLIA", "2 a 5 jogadores", "15 min",
     ["Monte o seu parque", "Os bichos são de madeira", "Pega um e passa o resto pro lado"],
     ["Dinosaur Island", "Draftosaurus", "Dinosaur World"], 1),
    ("wingspan", "Wingspan", "ESTRATÉGICO", "1 a 5 jogadores", "70 min",
     ["Mais de 170 cartas diferentes", "Tem ovinhos e comedouro de dados", "Floresta, campo e área alagada"],
     ["Harmonies", "Everdell Duo", "Wingspan"], 2),
    ("flamecraft", "Flamecraft", "DELUXE", "1 a 5 jogadores", "60 min",
     ["Dragõezinhos fofos", "Eles trabalham em lojinhas", "Encante as lojas da cidade"],
     ["Flamecraft", "Tesouro do Dragão", "Wonderland's War"], 0),
    ("coup_inquisition", "Coup", "FAMÍLIA", "2 a 6 jogadores", "15 min",
     ["Só 2 cartas na mão", "Duque, Assassino, Capitão...", "Duvida, se tiver coragem!"],
     ["The Resistance", "Coup", "Mascarade"], 1),
]


def fundo(semente):
    """Explosão de raios (amarelo × laranja) no meio, petróleo nas bordas, como na brincadeira do Pokémon."""
    img = Image.new("RGBA", (W, H), E.PETROLEO + (255,))
    d = ImageDraw.Draw(img)
    cx, cy, n = W / 2, 760, 28
    for k in range(n):
        a0 = 2 * math.pi * k / n + semente * 0.07
        a1 = a0 + math.pi / n
        r = 2000
        d.polygon([(cx, cy), (cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))],
                  fill=(36, 140, 168))
    # miolo claro
    brilho = Image.new("L", (W, H), 0)
    ImageDraw.Draw(brilho).ellipse((cx - 470, cy - 470, cx + 470, cy + 470), fill=255)
    brilho = brilho.filter(ImageFilter.GaussianBlur(120))
    raios = Image.new("RGBA", (W, H), E.AMARELO + (255,))
    d2 = ImageDraw.Draw(raios)
    for k in range(n):
        a0 = 2 * math.pi * k / n + semente * 0.07
        a1 = a0 + math.pi / n
        d2.polygon([(cx, cy), (cx + 2000 * math.cos(a0), cy + 2000 * math.sin(a0)),
                    (cx + 2000 * math.cos(a1), cy + 2000 * math.sin(a1))], fill=(255, 222, 110))
    img = Image.composite(raios, img, brilho)
    return img


def caixa(nome, h, larg):
    im = Image.open(os.path.join(AC, nome + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def sombra(cx):
    """A 'sombra' do jogo: caixa escura (só o volume e manchas bem borradas da arte, sem dar pra ler o nome)
    com um contorno claro fino."""
    a = cx.getchannel("A")
    L = np.array(cx.convert("L").filter(ImageFilter.GaussianBlur(9))).astype(float) / 255
    base, hi = np.array(ESCURO, float), np.array([70, 100, 140], float)
    rgb = base + (hi - base) * (L[..., None] ** 1.5) * 0.55
    sil = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.array(a)]).astype(np.uint8), "RGBA")
    pad = 14
    out = Image.new("RGBA", (cx.width + 2 * pad, cx.height + 2 * pad), (0, 0, 0, 0))
    borda = Image.new("RGBA", out.size, E.BRANCO + (0,))
    am = Image.new("L", out.size, 0)
    am.paste(a, (pad, pad))
    borda.putalpha(am.filter(ImageFilter.MaxFilter(13)))
    out.alpha_composite(borda)
    out.alpha_composite(sil, (pad, pad))
    return out


def com_borda(cx):
    pad = 14
    a = Image.new("L", (cx.width + 2 * pad, cx.height + 2 * pad), 0)
    a.paste(cx.getchannel("A"), (pad, pad))
    out = Image.new("RGBA", a.size, E.BRANCO + (0,))
    out.putalpha(a.filter(ImageFilter.MaxFilter(13)))
    out.alpha_composite(cx, (pad, pad))
    return out


def interrogacao(img):
    E.cola(img, E.titulo("?", 230, E.AMARELO), 880, 820, 12)


def opcao(letra, txt, estado):
    """estado: None (pergunta), True (certa), False (errada)."""
    cor, cor_t = E.BRANCO, E.MARROM
    if estado is True:
        cor, cor_t = VERDE, E.BRANCO
    elif estado is False:
        cor, cor_t = (214, 222, 226), (130, 120, 112)
    w, h = 760, 104
    im = E.bloco(w, h, cor, raio=h // 2, ow=6, sombra=8)
    d = ImageDraw.Draw(im)
    d.ellipse((14, 12, 14 + 80, 12 + 80), fill=E.AMARELO if estado is None else (E.BRANCO if estado else (190, 198, 202)),
              outline=E.MARROM, width=5)
    d.text((54, 54), letra, font=E.lilita(52), fill=E.MARROM, anchor="mm")
    d.text((w / 2 + 40, h / 2 + 2), txt, font=E.fig(46, 900), fill=cor_t, anchor="mm")
    if estado is True:  # visto desenhado (a fonte não tem ✓)
        d.line([(w - 92, 52), (w - 72, 72), (w - 40, 32)], fill=E.BRANCO, width=11, joint="curve")
    return im


def tela(k, j, resposta):
    nome, titulo_jogo, cat, jog, tempo, dicas, opcoes, certa = j
    img = fundo(k)
    E.cola(img, E.logo(230), W / 2, 170)
    E.cola(img, E.titulo("QUE JOGO\nÉ ESSE?" if not resposta else "É O...", 120, E.AMARELO, larg_max=980),
           W / 2, 365 if not resposta else 320, -2)
    cx = caixa(nome, 430, 540)
    if resposta:
        E.cola(img, com_borda(cx), W / 2, 715, -4)
        E.cola(img, E.titulo(titulo_jogo.upper() + "!", 92, E.BRANCO, larg_max=960), W / 2, 990, 2)
    else:
        E.cola(img, sombra(cx), W / 2, 730, -4)
        interrogacao(img)
    # categoria + ficha
    cor, cor_t = E.CAT[cat]
    y = 1110 if resposta else 1015
    selos = [E.pilula(cat, 40, cor, cor_t, fonte_titulo=True), E.pilula(jog, 34, E.BRANCO), E.pilula(tempo, 34, E.BRANCO)]
    tot = sum(s.width for s in selos) + 18 * 2
    x = W / 2 - tot / 2
    for s in selos:
        E.cola(img, s, x + s.width / 2, y, 0)
        x += s.width + 18
    if not resposta:
        # dicas
        bl = E.bloco(900, 250, E.BRANCO, raio=34, ow=7, sombra=11)
        d = ImageDraw.Draw(bl)
        d.text((40, 42), "DICAS", font=E.lilita(40), fill=E.LARANJA, anchor="lm")
        for i, t in enumerate(dicas):
            yy = 100 + i * 56
            d.ellipse((42, yy - 9, 60, yy + 9), fill=E.PETROLEO)
            d.text((80, yy), t, font=E.fig(38, 800), fill=E.MARROM, anchor="lm")
        E.cola(img, bl, W / 2, 1215, 0)
    y0 = 1435 if not resposta else 1260
    for i, t in enumerate(opcoes):
        est = None if not resposta else (i == certa)
        E.cola(img, opcao("ABC"[i], t, est), W / 2, y0 + i * 117, (-1, 1, -1)[i])
    if resposta:
        E.cola(img, E.pilula("Tem no nosso acervo! Aluga pelo link na bio", 36, E.AMARELO), W / 2, 1650, -1)
    return img.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    miniaturas = []
    for k, j in enumerate(JOGOS, 1):
        for resp in (False, True):
            im = tela(k, j, resp)
            nome = f"{k:02d}_{'resposta' if resp else 'pergunta'}.png"
            im.save(os.path.join(OUT, nome))
            miniaturas.append(im.resize((270, 480)))
    folha = Image.new("RGB", (270 * 7, 480 * 2), "white")
    for i, m in enumerate(miniaturas):
        folha.paste(m, ((i // 2) * 270, (i % 2) * 480))
    folha.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok", OUT)


if __name__ == "__main__":
    main()
