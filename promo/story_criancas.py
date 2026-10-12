#!/usr/bin/env python3
"""Story do Dia das Crianças (12/out) da Sua Vez, 1080x1920, no VISUAL DA LOJA (mesmo das artes de promoção:
creme com listras laranja, cartão do logo, Poppins azul-marinho, faixa laranja). A 1ª versão (céu azul com meeples
desenhados) foi REJEITADA: "não tem nada com o visual da loja" e "meeples mal feitos". Agora só caixas OFICIAIS: os 4
jogos do Reels das crianças (gravados-reels/assets/oficial), com jogadores e tempo do site.

    python3 story_criancas.py      # out/story_criancas.png
"""
import json
import os

from PIL import Image, ImageDraw

from promo_3jogos import ORANGE, NAVY, GREEN, GREEN_L, BLUE, WHITE, BLACK, XB, SB, LOGO, OUT, f, fundo, paste_c, \
    shadowed, text_c

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OF = os.path.join(REPO, "gravados-reels", "assets", "oficial")
SITE = json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8"))
ROXO = (124, 58, 237)
JOGOS = [  # (arquivo, nome, chave no site, cor do cartão)
    ("go_cuckoo.png", "Go Cuckoo!", "Go Cuckoo", ORANGE),
    ("gravity_superstar.png", "Gravity Superstar", "Gravity Superstar", BLUE),
    ("draftosaurus.png", "Draftosaurus", "Draftosaurus", GREEN),
    ("scooby_doo.png", "Scooby-Doo", "Scooby-Doo!", ROXO),
]


def info(chave):
    for k, v in SITE.items():
        if k.lower().startswith(chave.lower()):
            a, b = v["jogadores"].split("–")
            return f"{a} a {b} jogadores · {v['tempo'].replace('min', ' min')}"
    raise KeyError(chave)


def caixa(nome, h, larg):
    im = Image.open(os.path.join(OF, nome)).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    if nome == "scooby_doo.png":  # capa reta: cantinho arredondado
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.width // 30, fill=255)
        im.putalpha(m)
    return im


def cartao(arq, nome, chave, cor, w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=34, fill=WHITE)
    d.rounded_rectangle((0, h - 110, w - 1, h - 1), radius=34, fill=cor)
    d.rectangle((0, h - 110, w - 1, h - 80), fill=cor)
    bx = shadowed(caixa(arq, h - 140, w - 60), 12, (5, 10), 0.28)
    paste_c(im, bx, w / 2, (h - 110) / 2 + 4)
    text_c(d, (w / 2, h - 72), nome, f(BLACK, 34), WHITE)
    text_c(d, (w / 2, h - 32), info(chave), f(SB, 25), WHITE)
    return shadowed(im, 14, (6, 12), 0.22)


def main():
    W, H = 1080, 1920
    img = fundo(W, H)
    d = ImageDraw.Draw(img)
    y = 210
    lg = Image.open(LOGO).convert("RGBA")
    lw = 280
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lg.width + 40, lg.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=26, fill=WHITE)
    card.alpha_composite(lg, (20, 15))
    paste_c(img, shadowed(card, 12, (4, 8), 0.2), W / 2, y + card.height / 2)
    y += card.height + 50
    text_c(d, (W / 2, y + 40), "FELIZ DIA DAS", f(BLACK, 92), NAVY)
    y += 110
    d.rounded_rectangle((90, y, W - 90, y + 150), radius=40, fill=ORANGE)
    text_c(d, (W / 2, y + 80), "CRIANÇAS!", f(BLACK, 110), WHITE)
    y += 150 + 55
    text_c(d, (W / 2, y), "4 jogos pra brincar junto com a criançada:", f(SB, 38), NAVY)
    y += 45
    cw, ch, gap = 450, 370, 24
    for k, (arq, nome, chave, cor) in enumerate(JOGOS):
        cx = W / 2 + (k % 2 - 0.5) * (cw + gap)
        cy = y + ch / 2 + (k // 2) * (ch + gap) + 20
        paste_c(img, cartao(arq, nome, chave, cor, cw, ch), cx, cy)
    y += 2 * ch + gap + 42
    box = (70, y, W - 70, y + 100)
    d.rounded_rectangle(box, radius=26, fill=GREEN_L, outline=(134, 239, 172), width=3)
    text_c(d, (W / 2, y + 50), "Alugue 3 jogos e fique 7 dias com eles!", f(XB, 36), (21, 101, 52))
    y += 140
    text_c(d, (W / 2, y), "RETIRE EM MAUÁ OU RECEBA EM CASA", f(XB, 36), NAVY)
    text_c(d, (W / 2, y + 50), "suavez.acervodejogos.com.br  ·  @suavez_bg", f(SB, 32), ORANGE)
    os.makedirs(OUT, exist_ok=True)
    img.convert("RGB").save(os.path.join(OUT, "story_criancas.png"))
    print("ok", y + 50)


if __name__ == "__main__":
    main()
