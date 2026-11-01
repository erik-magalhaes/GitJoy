#!/usr/bin/env python3
"""Carrossel "SEU MÊS, SEU JOGO" (31/out/2026), na trend "Seu mês, seu bichinho" que ele mandou (@hippieartesanatos):
capa com os 12 jogos em volta do título, uma tela por mês (papel pastel, letra de mão em caixa alta, a caixa do jogo no
meio e uma frase com o "personagem" do jogo no clima do mês) e uma tela final pra comentar.
Caixas recortadas do site (hobby-reels/assets/acervo/); letra = Patrick Hand engrossada (como em taco-reels).
1080x1350.

    python3 seu_mes.py            # out/seu_mes/01..14.png + out/seu_mes_previa.jpg + out/carrossel_seu_mes.zip
    python3 seu_mes.py --previa   # só capa + 3 meses na folha de prévia
"""
import os
import random
import sys
import zipfile
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

W, H = 1080, 1350
OUT = os.path.join(ROOT, "out")
ACERVO = os.path.join(REPO, "hobby-reels", "assets", "acervo")
MAO = os.path.join(REPO, "taco-reels", "assets", "fonts", "PatrickHand-Regular.ttf")
# os 12 bichinhos que ELES fizeram no Gemini (folha 4x3, na ordem dos meses), a partir dos textos que eu mandei
GEMINI = os.path.join(ROOT, "assets", "seu_mes", "gemini_12.jpg")
FUNDO_GEMINI = np.array([248, 244, 232], float)
TINTA = (34, 30, 30)
MESES = [  # (mês, frase, jogo, recorte, fundo pastel)
    ("JANEIRO", "GATO ASTRONAUTA\nDE FÉRIAS NA LUA", "MLEM: Agência Espacial", "mlem_space_agency", (198, 214, 240)),
    ("FEVEREIRO", "UNICÓRNIO QUE SÓ\nPENSA EM CARNAVAL", "Unicorn Fever", "unicorn_fever", (246, 204, 222)),
    ("MARÇO", "BICHINHO DA FLORESTA\nFAZENDO PLANILHA DO ANO", "Everdell Duo", "everdell_duo", (214, 234, 200)),
    ("ABRIL", "XERIFE QUE FINGE\nQUE ACREDITA", "Sheriff of Nottingham", "sheriff_of_nottingham_2nd_edition",
     (250, 226, 190)),
    ("MAIO", "CHEF ESTRESSADO\nNO DIA DAS MÃES", "Critter Kitchen", "critter_kitchen", (228, 214, 244)),
    ("JUNHO", "FAZENDEIRO\nDE QUADRILHA", "La Granja", "la_granja", (252, 214, 196)),
    ("JULHO", "TURISTA PERDIDO\nNO METRÔ DE LONDRES", "Next Station London", "next_station_london",
     (204, 230, 236)),
    ("AGOSTO", "CHEFÃO DE MASMORRA\nNO MÊS DO DESGOSTO", "Boss Monster", "boss_monster_the_dungeon_building_card_game",
     (236, 220, 206)),
    ("SETEMBRO", "PASSARINHO\nESPERANDO A PRIMAVERA", "Wingspan", "wingspan", (220, 238, 214)),
    ("OUTUBRO", "SUPER-HERÓI ZUMBI\nBATENDO PONTO", "DCeased", "dceased_gotham_city_outbreak", (214, 206, 232)),
    ("NOVEMBRO", "BANDIDO\nDE BLACK FRIDAY", "Bad Company", "bad_company", (244, 232, 204)),
    ("DEZEMBRO", "DRAGÃO CONFEITEIRO\nNO TURNO DO NATAL", "Flamecraft", "flamecraft", (250, 210, 210)),
]


@lru_cache(None)
def mao(s):
    return ImageFont.truetype(MAO, int(s))


def papel(cor, semente=1):
    """Papel pastel com grão e fibra leve."""
    rng = np.random.default_rng(semente)
    a = np.ones((H, W, 3)) * np.array(cor, float)
    g = rng.normal(0, 1, (H // 3, W // 3))
    g = np.asarray(Image.fromarray(((g + 4) * 30).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                   float) / 30 - 4
    a += g[..., None] * 2.2
    a += rng.normal(0, 2.0, (H, W, 1))
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")


def letra(img, txt, s, cx, cy, cor=TINTA, sw=None, entre=1.12, semente=0):
    """Letra de mão em caixa alta: cada letra com tamanho/altura/giro levemente diferentes, traço engrossado."""
    rnd = random.Random(semente)
    sw = max(1, int(s * 0.045)) if sw is None else sw
    f = mao(s)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    linhas = txt.split("\n")
    lh = s * entre
    y0 = cy - lh * (len(linhas) - 1) / 2
    for k, l in enumerate(linhas):
        larg = [d0.textlength(c, font=f) * 1.04 for c in l]
        x = cx - sum(larg) / 2
        for c, lw in zip(l, larg):
            if c != " ":
                ss = s * rnd.uniform(0.95, 1.05)
                g = Image.new("RGBA", (int(ss * 1.6), int(ss * 1.6)), (0, 0, 0, 0))
                ImageDraw.Draw(g).text((g.width / 2, g.height / 2), c, font=mao(ss), fill=cor, anchor="mm",
                                       stroke_width=sw, stroke_fill=cor)
                g = g.rotate(rnd.uniform(-3.5, 3.5), resample=Image.BICUBIC)
                img.alpha_composite(g, (int(x + lw / 2 - g.width / 2), int(y0 + k * lh - g.height / 2 +
                                                                              rnd.uniform(-3, 3))))
            x += lw


@lru_cache(None)
def caixa(nome, h, larg=None):
    im = Image.open(os.path.join(ACERVO, nome + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = h / im.height
    if larg and im.width * s > larg:
        s = larg / im.width
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    m = Image.new("RGBA", im.size, (40, 30, 30, 255))
    m.putalpha(im.getchannel("A").point(lambda v: int(v * 0.32)))
    sh.alpha_composite(m, (52, 58))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh.alpha_composite(im, (40, 40))
    return sh


@lru_cache(None)
def _rembg(k):
    """Máscara do rembg (isnet) para a célula k, guardada em assets/seu_mes/rembg_NN.png (só serve de juiz)."""
    cache = os.path.join(ROOT, "assets", "seu_mes", f"rembg_{k:02d}.png")
    cel = _celula(k)
    if not os.path.exists(cache):
        from rembg import new_session, remove
        remove(Image.fromarray(cel), session=new_session("isnet-general-use")).getchannel("A").save(cache)
    return np.asarray(Image.open(cache), float) / 255


def _celula(k):
    im = np.asarray(Image.open(GEMINI).convert("RGB"))
    ch, cw = im.shape[0] / 3, im.shape[1] / 4
    r, c = divmod(k, 4)
    return im[int(r * ch):int((r + 1) * ch), int(c * cw):int((c + 1) * cw)].copy()


@lru_cache(None)
def bicho(k, h):
    """Recorta o bichinho do mês k da folha do Gemini.
    1) fundo = creme/cinza claro LIGADO À BORDA (inclui a sombra do chão, que é cinza claro sem cor);
    2) "buracos" de fundo presos dentro do desenho (entre as pernas, dentro da cadeira) saem quando o rembg também
       diz que é fundo; 3) a franja clara do contorno vira meio transparente (sem halo branco no fundo colorido)."""
    import cv2
    cel = _celula(k)
    f = cel.astype(float)
    borda_px = np.r_[cel[0], cel[-1], cel[:, 0], cel[:, -1]].astype(float)
    fundo_cor = np.median(borda_px, 0)  # o creme muda de uma folha do Gemini para outra
    dist = np.sqrt(((f - fundo_cor) ** 2).sum(-1))
    sat = f.max(-1) - f.min(-1)
    lum = f.mean(-1)
    rb = _rembg(k)
    # parecido com o fundo: perto do creme, ou cinza bem claro e sem cor (sombra de chão), com o rembg concordando
    chao = np.arange(cel.shape[0])[:, None] > 0.72 * cel.shape[0]  # sombra/chão cinza no pé do desenho
    claro = (dist < 30) | ((lum > 165) & (sat < 26) & (rb < 0.5)) | (chao & (lum > 110) & (sat < 30) & (rb < 0.6))
    n, lab, st, _ = cv2.connectedComponentsWithStats(claro.astype(np.uint8), connectivity=4)
    borda = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fundo = np.isin(lab, list(borda))
    for i in range(1, n):  # buracos internos
        if i in borda or not 150 <= st[i, cv2.CC_STAT_AREA] < 0.015 * cel.shape[0] * cel.shape[1]:
            continue
        m = lab == i
        if rb[m].mean() < 0.3:
            fundo |= m
    alfa = (~fundo).astype(np.uint8) * 255
    # pedacinhos da célula vizinha que encostam na borda (ponta de bandeirinha, papel) saem
    n, lab, st, _ = cv2.connectedComponentsWithStats((alfa > 0).astype(np.uint8), connectivity=8)
    tot = st[1:, cv2.CC_STAT_AREA].sum()
    H_, W_ = alfa.shape
    for i in range(1, n):
        x, y, w, hh, a = st[i]
        tira = ((y == 0 or y + hh >= H_) and hh < 0.15 * H_) or ((x == 0 or x + w >= W_) and w < 0.15 * W_)
        if (x == 0 or y == 0 or x + w >= W_ or y + hh >= H_) and (a < 0.04 * tot or tira):
            alfa[lab == i] = 0
        elif (a < 40 and rb[lab == i].mean() < 0.2) or \
                (a < 0.005 * tot and (y + hh < 0.07 * H_ or y > 0.85 * H_)):  # sujeira do papel / resto do vizinho
            alfa[lab == i] = 0
    alfa = cv2.erode(alfa, np.ones((3, 3), np.uint8))
    # franja: perto da borda do recorte, quanto mais parecido com o creme, mais transparente
    perto = cv2.dilate(255 - alfa, np.ones((7, 7), np.uint8)) > 0
    suave = np.clip((dist - 12) / 45, 0, 1)
    a = alfa.astype(float) / 255
    a = np.where(perto, np.minimum(a, suave), a)
    a = cv2.GaussianBlur(a, (0, 0), 0.7)
    out = Image.fromarray(np.dstack([cel, (a * 255).astype(np.uint8)]))
    out = out.crop(out.getbbox())
    s = h / out.height
    out = out.resize((int(out.width * s), int(h)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 60, 2))
    return out


def selo(img, x, y, w=170):
    lg = E.logo(w)
    img.alpha_composite(lg, (int(x), int(y)))


ESTILO = "A"  # escolha dele (1/nov)  # como a caixa aparece: A fundo desfocado, B caixa maior com etiqueta, C polaroide


def etiqueta(txt, semente=0):
    """Etiqueta kraft com furinho e barbante, escrita à mão."""
    w = int(60 + 22 * len(txt))
    im = Image.new("RGBA", (w + 20, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(30, 10), (w + 10, 10), (w + 10, 100), (30, 100), (8, 55)], fill=(214, 182, 140), outline=(120, 90, 60))
    d.ellipse((24, 47, 40, 63), fill=(250, 245, 235), outline=(120, 90, 60), width=2)
    letra(im, txt, 40, (w + 40) / 2, 57, (60, 40, 25), sw=1, semente=semente)
    return im


@lru_cache(None)
def fundo_caixa(rec, cor):
    """A arte da caixa enorme, bem desfocada e clareada com a cor do mês."""
    im = Image.open(os.path.join(ACERVO, rec + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = max(W / im.width, H / im.height) * 1.15
    im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
    base = Image.new("RGBA", (W, H), cor + (255,))
    base.alpha_composite(im, (int(W / 2 - im.width / 2), int(H / 2 - im.height / 2)))
    base = base.filter(ImageFilter.GaussianBlur(28))
    veu = Image.new("RGBA", (W, H), cor + (165,))
    base.alpha_composite(veu)
    return base


def tela_mes(k, estilo=None):
    estilo = estilo or ESTILO
    mes, frase, jogo, rec, cor = MESES[k]
    img = papel(cor, k + 3)
    if estilo == "A":
        img = fundo_caixa(rec, cor).copy()
    letra(img, mes, 110, W / 2, 165, semente=k)
    if estilo == "A":
        b = bicho(k, 560)
        if b.width > 880:
            b = b.resize((880, int(b.height * 880 / b.width)), Image.LANCZOS)
        img.alpha_composite(b, (int(W / 2 - b.width / 2), int(570 - b.height / 2)))
        letra(img, frase, 70, W / 2, 950, semente=k + 50)
        cx = caixa(rec, 255, 280)
        img.alpha_composite(cx, (int(W - 25 - cx.width), int(H - 10 - cx.height)))
        letra(img, "jogo: " + jogo, 42, (200 + W - 25 - cx.width) / 2, 1200, (60, 50, 50), sw=1, semente=k + 90)
    elif estilo == "B":  # bichinho à esquerda, caixa grande à direita com etiqueta
        b = bicho(k, 520)
        if b.width > 640:
            b = b.resize((640, int(b.height * 640 / b.width)), Image.LANCZOS)
        img.alpha_composite(b, (int(370 - b.width / 2), int(560 - b.height / 2)))
        cx = caixa(rec, 400, 380).rotate(-6, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(cx, (int(820 - cx.width / 2), int(700 - cx.height / 2)))
        et = etiqueta(jogo, k).rotate(4, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(et, (int(min(W - 20 - et.width, 820 - et.width / 2)), 905))
        letra(img, frase, 74, W / 2, 1110, semente=k + 50)
    else:  # C: polaroide com a caixa presa com fita, bichinho em cima
        b = bicho(k, 480)
        if b.width > 760:
            b = b.resize((760, int(b.height * 760 / b.width)), Image.LANCZOS)
        img.alpha_composite(b, (int(W / 2 - b.width / 2), int(470 - b.height / 2)))
        letra(img, frase, 64, W / 2, 805, semente=k + 50)
        pol = Image.new("RGBA", (400, 470), (252, 250, 245, 255))
        cx = caixa(rec, 300, 320)
        pol.alpha_composite(cx, (int(200 - cx.width / 2), int(185 - cx.height / 2)))
        letra(pol, jogo if len(jogo) < 18 else jogo.split(":")[0], 34, 200, 425, (60, 50, 50), sw=1, semente=k)
        pol = pol.rotate(-5, expand=True, resample=Image.BICUBIC)
        sh = Image.new("RGBA", (pol.width + 40, pol.height + 40), (0, 0, 0, 0))
        m = Image.new("RGBA", pol.size, (40, 30, 30, 255))
        m.putalpha(pol.getchannel("A").point(lambda v: int(v * 0.3)))
        sh.alpha_composite(m, (28, 32))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        sh.alpha_composite(pol, (20, 20))
        img.alpha_composite(sh, (int(W / 2 - sh.width / 2), 880))
        fita = Image.new("RGBA", (150, 46), (240, 226, 170, 200)).rotate(8, expand=True)
        img.alpha_composite(fita, (int(W / 2 - 75), 880))
    selo(img, 34, H - 128, 150)
    return img


def comparar():
    telas = [tela_mes(k, e) for k in (0, 11) for e in "ABC"]
    sh = Image.new("RGB", (3 * 440 + 20, 2 * 600 + 60), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for j, e in enumerate(("A · FUNDO DESFOCADO", "B · CAIXA GRANDE + ETIQUETA", "C · POLAROIDE")):
        d.text((20 + j * 440 + 215, 25), e, font=mao(34), fill=TINTA, anchor="mm")
    for i, im in enumerate(telas):
        r, c = divmod(i, 3)
        sh.paste(im.convert("RGB").resize((430, 537), Image.LANCZOS), (15 + c * 440, 55 + r * 600))
    sh.save(os.path.join(OUT, "seu_mes_opcoes.jpg"), quality=90)


def tela_capa():
    img = papel((246, 206, 196), 99)
    letra(img, "SEU MÊS,\nSEU JOGO", 128, W / 2, 610, semente=7)
    letra(img, "(qual é o seu?)", 60, W / 2, 800, (90, 70, 70), sw=2, semente=8)
    # as 12 caixas em volta do título (sentido horário, começando em janeiro no alto à esquerda)
    pos = [(170, 175), (430, 150), (690, 160), (930, 230), (950, 520), (960, 820), (900, 1120), (640, 1180),
           (380, 1190), (140, 1110), (120, 820), (130, 500)]
    for k, ((x, y), m) in enumerate(zip(pos, MESES)):
        cx = bicho(k, 210)
        if cx.width > 250:
            cx = cx.resize((250, int(cx.height * 250 / cx.width)), Image.LANCZOS)
        cx = cx.rotate(random.Random(k).uniform(-6, 6), expand=True, resample=Image.BICUBIC)
        img.alpha_composite(cx, (int(x - cx.width / 2), int(y - cx.height / 2)))
    selo(img, W / 2 - 85, 905, 170)
    return img


def tela_final():
    img = papel((210, 228, 240), 77)
    letra(img, "E AÍ,\nQUAL É O SEU MÊS?", 100, W / 2, 380, semente=3)
    letra(img, "comenta aqui\ne marca quem é do seu mês!", 58, W / 2, 640, (90, 70, 70), sw=2, semente=4)
    lg = E.logo(330)
    img.alpha_composite(lg, (int(W / 2 - lg.width / 2), 820))
    letra(img, "ALUGA O SEU NA SUA VEZ\nO LINK TÁ NA BIO", 56, W / 2, 1150, semente=5)
    return img


def main():
    d = os.path.join(OUT, "seu_mes")
    os.makedirs(d, exist_ok=True)
    if "--opcoes" in sys.argv:
        comparar()
        print("ok opcoes")
        return
    previa = "--previa" in sys.argv
    telas = [tela_capa()] + [tela_mes(k) for k in (range(12) if not previa else (0, 3, 11))]
    if not previa:
        telas.append(tela_final())
    for k, im in enumerate(telas, 1):
        im.convert("RGB").save(os.path.join(d, f"{k:02d}.png"))
    cols = min(len(telas), 7)
    rows = (len(telas) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 330 + 10, rows * 420 + 10), (255, 255, 255))
    for k, im in enumerate(telas):
        sh.paste(im.convert("RGB").resize((320, 400), Image.LANCZOS), (10 + (k % cols) * 330, 10 + (k // cols) * 420))
    sh.save(os.path.join(OUT, "seu_mes_previa.jpg"), quality=90)
    if not previa:
        with zipfile.ZipFile(os.path.join(OUT, "carrossel_seu_mes.zip"), "w") as z:
            for k in range(1, len(telas) + 1):
                z.write(os.path.join(d, f"{k:02d}.png"), f"seu_mes_{k:02d}.png")
    print("ok", len(telas))


if __name__ == "__main__":
    main()
