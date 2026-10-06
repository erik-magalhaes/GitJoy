"""Desenho da tela do WhatsApp (tema claro) em 1080x1920.

Tudo em PIL. Os balões são imagens RGBA prontas (com cache); a tela é montada a cada quadro.
Área segura: mensagens entre x=36 e x=935 (os botões do TikTok ficam à direita) e acima de y~1480.
"""
import functools
import math
import os
import random
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(AQUI, "assets", "fonts")
W, H = 1080, 1920

# layout vertical
BANDA = 120                  # faixa com o nome da página
STATUS_Y = BANDA             # barra de status do celular
HEADER_Y = BANDA + 52
HEADER_H = 138
CHAT_Y0 = HEADER_Y + HEADER_H
CHAT_Y1 = 1470
INPUT_Y = CHAT_Y1
TECLADO_Y = INPUT_Y + 104
ESQ, DIR = 36, 935           # margens dos balões
MAXW = 690                   # largura máxima do texto do balão

# cores (tema claro do WhatsApp)
C = dict(
    fundo=(239, 234, 226), doodle=(226, 219, 207), header=(255, 255, 255), titulo=(17, 27, 33),
    sub=(102, 119, 129), verde=(0, 168, 132), in_=(255, 255, 255), out=(217, 253, 211),
    texto=(17, 27, 33), hora=(102, 119, 129), azul=(83, 189, 235), cinza_check=(140, 150, 156),
    chip=(255, 255, 255), teclado=(206, 210, 217), tecla=(255, 255, 255), amarelo=(255, 214, 0),
    preto=(18, 18, 18),
)

CORES_NOME = [(6, 147, 227), (229, 57, 53), (142, 36, 170), (0, 137, 123), (245, 124, 0), (57, 73, 171), (194, 24, 91)]


@functools.lru_cache(None)
def fonte(nome, tam, peso=None):
    f = ImageFont.truetype(os.path.join(FONTES, nome), tam)
    if peso is not None:
        try:
            f.set_variation_by_axes([32, peso] if nome.startswith("Inter") else [peso])
        except Exception:
            pass
    return f


def inter(tam, peso=450):
    return fonte("Inter.ttf", tam, peso)


# ------------------------------------------------------------------ texto com emoji
EMO_RE = re.compile(
    "((?:[\U0001F1E6-\U0001F1FF]{2})|(?:[\U0001F000-\U0001FAFF☀-➿⬀-⯿←-⇿⌀-⏿⤴⤵〰〽㊗㊙]"
    "️?[\U0001F3FB-\U0001F3FF]?(?:‍[\U0001F000-\U0001FAFF☀-➿]️?[\U0001F3FB-\U0001F3FF]?)*))")


@functools.lru_cache(None)
def emoji_img(e, tam):
    f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), e, font=f, embedded_color=True)
    bb = im.getbbox()
    if not bb:
        return Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    im = im.crop(bb)
    esc = tam / 128
    return im.resize((max(1, round(im.width * esc)), max(1, round(im.height * esc))), Image.LANCZOS)


def tokens(txt):
    """Divide em palavras (mantendo espaços) e emojis."""
    out = []
    for parte in EMO_RE.split(txt):
        if not parte:
            continue
        if EMO_RE.fullmatch(parte):
            out.append(("e", parte))
        else:
            for w in re.split(r"(\s+)", parte):
                if w:
                    out.append(("t", w))
    return out


def larg_tok(tok, f):
    k, s = tok
    if k == "e":
        return round(f.size * 1.18)
    return f.getlength(s)


def quebra(txt, f, maxw):
    """-> lista de linhas; cada linha é uma lista de tokens."""
    linhas = []
    for par in txt.split("\n"):
        atual, w = [], 0
        for tok in tokens(par):
            lw = larg_tok(tok, f)
            if tok[0] == "t" and tok[1].isspace():
                if atual:
                    atual.append(tok)
                    w += lw
                continue
            if w + lw > maxw and atual:
                while atual and atual[-1][0] == "t" and atual[-1][1].isspace():
                    w -= larg_tok(atual.pop(), f)
                linhas.append(atual)
                atual, w = [], 0
            atual.append(tok)
            w += lw
        while atual and atual[-1][0] == "t" and atual[-1][1].isspace():
            atual.pop()
        linhas.append(atual)
    return linhas


def larg_linha(linha, f):
    return sum(larg_tok(t, f) for t in linha)


def desenha_linha(im, x, y_base, linha, f, cor):
    """Desenha uma linha de tokens; y_base é a linha de base do texto."""
    d = ImageDraw.Draw(im)
    for tok in linha:
        if tok[0] == "e":
            e = emoji_img(tok[1], round(f.size * 1.08))
            im.alpha_composite(e, (round(x + (round(f.size * 1.18) - e.width) / 2), round(y_base - f.size * 0.92)))
        else:
            d.text((x, y_base), tok[1], font=f, fill=cor, anchor="ls")
        x += larg_tok(tok, f)
    return x


def texto_rico(im, x, y, txt, f, cor, maxw=10_000, entre=1.32, centro=False):
    linhas = quebra(txt, f, maxw)
    lh = round(f.size * entre)
    for i, ln in enumerate(linhas):
        xx = x - larg_linha(ln, f) / 2 if centro else x
        desenha_linha(im, xx, y + round(f.size * 0.95) + i * lh, ln, f, cor)
    return len(linhas) * lh


# ------------------------------------------------------------------ peças pequenas
def checks(d, x, y, cor, esc=1.0):
    """Dois tracinhos (lidos) de ~34x20 px."""
    w = max(2, round(2.6 * esc))
    for dx in (0, 9 * esc):
        pts = [(x + dx + 0 * esc, y + 11 * esc), (x + dx + 6 * esc, y + 17 * esc), (x + dx + 18 * esc, y + 3 * esc)]
        if dx:
            pts = [(x + dx + 4 * esc, y + 15 * esc), (x + dx + 6 * esc, y + 17 * esc), (x + dx + 18 * esc, y + 3 * esc)]
        d.line(pts, fill=cor, width=w, joint="curve")


def check1(d, x, y, cor, esc=1.0):
    w = max(2, round(2.6 * esc))
    d.line([(x, y + 11 * esc), (x + 6 * esc, y + 17 * esc), (x + 18 * esc, y + 3 * esc)], fill=cor, width=w, joint="curve")


@functools.lru_cache(None)
def avatar(nome, cor, tam, grupo=False):
    """Bolinha colorida com inicial (ou ícone de grupo)."""
    s = tam * 3
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=cor)
    if grupo:
        br = (255, 255, 255, 235)
        for cx, cy, r in ((0.36, 0.40, 0.13), (0.64, 0.40, 0.13), (0.5, 0.36, 0.15)):
            d.ellipse((s * (cx - r), s * (cy - r), s * (cx + r), s * (cy + r)), fill=br)
        d.chord((s * 0.18, s * 0.55, s * 0.82, s * 1.05), 180, 360, fill=br)
    else:
        f = inter(round(s * 0.46), 700)
        d.text((s / 2, s / 2 + s * 0.02), nome[:1].upper(), font=f, fill=(255, 255, 255), anchor="mm")
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=255)
    im.putalpha(m)
    return im.resize((tam, tam), Image.LANCZOS)


# ------------------------------------------------------------------ fundo, barras e teclado
@functools.lru_cache(None)
def papel_parede():
    im = Image.new("RGB", (W, H), C["fundo"])
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    cor = C["doodle"]
    for gy in range(0, H, 92):
        for gx in range(0, W, 92):
            x, y = gx + rnd.randint(8, 60), gy + rnd.randint(8, 60)
            k = rnd.randint(0, 5)
            s = rnd.randint(16, 26)
            if k == 0:
                d.ellipse((x, y, x + s, y + s), outline=cor, width=3)
            elif k == 1:  # coração
                d.ellipse((x, y, x + s / 2 + 2, y + s / 2 + 2), outline=cor, width=3)
                d.ellipse((x + s / 2 - 2, y, x + s + 0, y + s / 2 + 2), outline=cor, width=3)
                d.line([(x + 1, y + s / 3), (x + s / 2, y + s), (x + s - 1, y + s / 3)], fill=cor, width=3)
            elif k == 2:  # estrela
                pts = []
                for i in range(10):
                    r = s / 2 if i % 2 == 0 else s / 4.5
                    a = -math.pi / 2 + i * math.pi / 5
                    pts.append((x + s / 2 + r * math.cos(a), y + s / 2 + r * math.sin(a)))
                d.polygon(pts, outline=cor, width=3)
            elif k == 3:  # notinha musical
                d.ellipse((x, y + s * 0.6, x + s * 0.45, y + s), outline=cor, width=3)
                d.line([(x + s * 0.45, y + s * 0.8), (x + s * 0.45, y), (x + s * 0.8, y + s * 0.2)], fill=cor, width=3)
            elif k == 4:  # balãozinho
                d.rounded_rectangle((x, y, x + s * 1.2, y + s * 0.8), 6, outline=cor, width=3)
            else:  # onda
                d.line([(x + i * 4, y + s / 2 + 5 * math.sin(i)) for i in range(7)], fill=cor, width=3)
    return im


def barra_status(im, hora, escuro=False):
    d = ImageDraw.Draw(im)
    bg = (11, 20, 26) if escuro else C["header"]
    fg = (255, 255, 255) if escuro else C["titulo"]
    d.rectangle((0, STATUS_Y, W, HEADER_Y), fill=bg)
    d.text((60, STATUS_Y + 27), hora, font=inter(30, 650), fill=fg, anchor="lm")
    x = W - 70
    d.rounded_rectangle((x - 50, STATUS_Y + 15, x, STATUS_Y + 39), 6, outline=fg, width=3)
    d.rectangle((x - 46, STATUS_Y + 19, x - 14, STATUS_Y + 35), fill=fg)
    d.rectangle((x + 3, STATUS_Y + 22, x + 6, STATUS_Y + 32), fill=fg)
    for i in range(4):  # sinal
        xx = x - 130 + i * 11
        d.rectangle((xx, STATUS_Y + 37 - 6 - i * 5, xx + 7, STATUS_Y + 37), fill=fg)
    cx, cy = x - 84, STATUS_Y + 38  # wi-fi
    for r in (22, 14, 6):
        d.arc((cx - r, cy - r, cx + r, cy + r), 225, 315, fill=fg, width=4)


def cabecalho(im, nome, sub, cor_av, grupo=False, sub_verde=False):
    d = ImageDraw.Draw(im)
    d.rectangle((0, HEADER_Y, W, CHAT_Y0), fill=C["header"])
    d.line([(0, CHAT_Y0 - 1), (W, CHAT_Y0 - 1)], fill=(225, 225, 225), width=2)
    cy = HEADER_Y + HEADER_H // 2
    g = C["titulo"]
    d.line([(58, cy), (34, cy), (46, cy - 13)], fill=g, width=5, joint="curve")
    d.line([(34, cy), (46, cy + 13)], fill=g, width=5)
    av = avatar(nome, cor_av, 92, grupo)
    im.paste(av, (78, cy - 46), av)
    tx = 192
    f1 = inter(40, 650)
    nome_v = nome
    while larg_linha(tokens(nome_v), f1) > 560 and len(nome_v) > 4:
        nome_v = nome_v[:-2] + "…"
    if sub:
        desenha_linha(im, tx, cy - 6, tokens(nome_v), f1, g)
        f2 = inter(29, 450)
        sub_v = sub
        while f2.getlength(sub_v) > 560 and len(sub_v) > 4:
            sub_v = sub_v[:-2] + "…"
        d.text((tx, cy + 38), sub_v, font=f2, fill=C["verde"] if sub_verde else C["sub"], anchor="ls")
    else:
        desenha_linha(im, tx, cy + 14, tokens(nome_v), f1, g)
    ic = (84, 101, 111)
    # câmera
    x = 790
    d.rounded_rectangle((x, cy - 15, x + 38, cy + 15), 6, outline=ic, width=4)
    d.polygon([(x + 40, cy - 3), (x + 54, cy - 12), (x + 54, cy + 12), (x + 40, cy + 3)], fill=ic)
    # telefone
    x = 892
    d.arc((x - 18, cy - 20, x + 22, cy + 20), 100, 260, fill=ic, width=8)
    d.ellipse((x - 14, cy - 22, x - 2, cy - 12), fill=ic)
    d.ellipse((x - 14, cy + 12, x - 2, cy + 22), fill=ic)
    # três pontinhos
    for k in (-14, 0, 14):
        d.ellipse((1016 - 4, cy + k - 4, 1016 + 4, cy + k + 4), fill=ic)


def barra_entrada(im, rascunho="", cursor=False):
    d = ImageDraw.Draw(im)
    y = INPUT_Y + 14
    d.rectangle((0, INPUT_Y, W, TECLADO_Y), fill=C["fundo"])
    d.rounded_rectangle((18, y, 900, y + 78), 39, fill=(255, 255, 255))
    ic = (130, 140, 146)
    d.ellipse((42, y + 21, 78, y + 57), outline=ic, width=4)
    d.arc((52, y + 32, 68, y + 48), 20, 160, fill=ic, width=3)
    if rascunho:
        f = inter(38, 450)
        t = rascunho
        while larg_linha(tokens(t), f) > 640:
            t = t[1:]
        x = desenha_linha(im, 100, y + 53, tokens(t), f, C["texto"])
        if cursor:
            d.rectangle((x + 3, y + 18, x + 6, y + 62), fill=C["verde"])
    else:
        d.text((100, y + 53), "Mensagem", font=inter(38, 400), fill=ic, anchor="ls")
        d.line([(760, y + 52), (790, y + 24)], fill=ic, width=4)  # clipe (simplificado)
        d.rounded_rectangle((812, y + 26, 856, y + 58), 6, outline=ic, width=4)
    cx, cy = 980, y + 39
    d.ellipse((cx - 46, cy - 46, cx + 46, cy + 46), fill=C["verde"])
    if rascunho:
        d.polygon([(cx - 16, cy - 20), (cx + 22, cy), (cx - 16, cy + 20), (cx - 10, cy)], fill=(255, 255, 255))
    else:
        d.rounded_rectangle((cx - 9, cy - 24, cx + 9, cy + 6), 9, fill=(255, 255, 255))
        d.arc((cx - 17, cy - 12, cx + 17, cy + 16), 0, 180, fill=(255, 255, 255), width=4)
        d.line([(cx, cy + 16), (cx, cy + 24)], fill=(255, 255, 255), width=4)


@functools.lru_cache(None)
def _teclado():
    im = Image.new("RGB", (W, H - TECLADO_Y), C["teclado"])
    d = ImageDraw.Draw(im)
    linhas = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    kw, kh, gap = 96, 106, 12
    f = inter(46, 400)
    for i, ln in enumerate(linhas):
        tot = len(ln) * kw + (len(ln) - 1) * gap
        x0 = (W - tot) / 2
        y0 = 24 + i * (kh + 20)
        for j, ch in enumerate(ln):
            x = x0 + j * (kw + gap)
            d.rounded_rectangle((x, y0, x + kw, y0 + kh), 12, fill=C["tecla"])
            d.text((x + kw / 2, y0 + kh / 2 + 2), ch, font=f, fill=(30, 30, 30), anchor="mm")
    return im


def teclado(im, tecla=None):
    im.paste(_teclado(), (0, TECLADO_Y))


# ------------------------------------------------------------------ balões
def _meta(hora, saida, lido=True):
    """Imagem da hora + tracinhos."""
    f = inter(25, 450)
    w = round(f.getlength(hora)) + (40 if saida else 0) + 2
    im = Image.new("RGBA", (w, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((0, 24), hora, font=f, fill=C["hora"], anchor="ls")
    if saida:
        (checks if lido is not None else check1)(d, w - 33, 7, C["azul"] if lido else C["cinza_check"])
    return im


def _caixa(w, h, cor, saida, rabo):
    """Balão vazio com o rabinho no canto de cima."""
    pad = 16
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 2, pad + w, pad + h + 2), 22, fill=(0, 0, 0, 38))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.2)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((pad, pad, pad + w, pad + h), 22, fill=cor)
    if rabo:
        if saida:
            d.rectangle((pad + w - 24, pad, pad + w, pad + 24), fill=cor)
            d.polygon([(pad + w - 4, pad), (pad + w + 15, pad), (pad + w - 4, pad + 22)], fill=cor)
        else:
            d.rectangle((pad, pad, pad + 24, pad + 24), fill=cor)
            d.polygon([(pad + 4, pad), (pad - 15, pad), (pad + 4, pad + 22)], fill=cor)
    return im, pad


@functools.lru_cache(512)
def balao_texto(texto, hora, saida, rabo, nome=None, cor_nome=None, lido=True, encaminhada=False):
    f = inter(41, 430)
    linhas = quebra(texto, f, MAXW)
    lh = round(f.size * 1.30)
    meta = _meta(hora, saida, lido)
    px, py = 26, 14
    topo = 0
    if nome:
        topo += 44
    if encaminhada:
        topo += 40
    ws = [larg_linha(ln, f) for ln in linhas]
    w_txt = max(ws) if ws else 0
    so_emoji = len(linhas) == 1 and all(t[0] == "e" or t[1].isspace() for t in linhas[0]) and len(linhas[0]) <= 3
    if so_emoji:  # emoji sozinho fica grande e sem balão
        im = Image.new("RGBA", (300, 150), (0, 0, 0, 0))
        f2 = inter(100)
        x = desenha_linha(im, 10, 118, linhas[0], f2, (0, 0, 0))
        im = im.crop((0, 0, round(x) + 20, 150))
        return im, 0
    ultima = ws[-1] if ws else 0
    cabe = ultima + 18 + meta.width <= MAXW + 4
    w = max(w_txt, ultima + 18 + meta.width if cabe else meta.width) + 2 * px
    if nome:
        w = max(w, round(inter(31, 650).getlength(nome)) + 2 * px)
    h = topo + len(linhas) * lh + (0 if cabe else 32) + py * 2 + 4
    im, pad = _caixa(round(w), h, C["out"] if saida else C["in_"], saida, rabo)
    d = ImageDraw.Draw(im)
    y = pad + py
    if nome:
        d.text((pad + px, y + 30), nome, font=inter(31, 650), fill=cor_nome, anchor="ls")
        y += 44
    if encaminhada:
        fi = inter(29, 400)
        d.text((pad + px + 34, y + 28), "Encaminhada", font=fi, fill=C["hora"], anchor="ls")
        cx, cy = pad + px + 12, y + 18  # setinha
        d.arc((cx - 10, cy - 4, cx + 10, cy + 16), 180, 270, fill=C["hora"], width=3)
        d.polygon([(cx + 2, cy - 10), (cx + 14, cy - 4), (cx + 2, cy + 2)], fill=C["hora"])
        y += 40
    for i, ln in enumerate(linhas):
        desenha_linha(im, pad + px, y + round(f.size * 0.98) + i * lh, ln, f, C["texto"])
    im.alpha_composite(meta, (pad + round(w) - px - meta.width + 6, pad + h - py - 26))
    return im, pad


@functools.lru_cache(64)
def balao_apagada(hora, saida, rabo, nome=None, cor_nome=None):
    fi = fonte("Inter.ttf", 39, 400)
    txt = "Esta mensagem foi apagada" if not saida else "Você apagou esta mensagem"
    meta = _meta(hora, False)
    px, py = 26, 14
    topo = 44 if nome else 0
    w = 52 + fi.getlength(txt) + 18 + meta.width + 2 * px
    if nome:
        w = max(w, inter(31, 650).getlength(nome) + 2 * px)
    h = topo + 54 + py * 2
    im, pad = _caixa(round(w), h, C["out"] if saida else C["in_"], saida, rabo)
    d = ImageDraw.Draw(im)
    y = pad + py
    if nome:
        d.text((pad + px, y + 30), nome, font=inter(31, 650), fill=cor_nome, anchor="ls")
        y += topo
    cx, cy = pad + px + 18, y + 26
    cz = (140, 150, 156)
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), outline=cz, width=4)
    d.line([(cx - 11, cy + 11), (cx + 11, cy - 11)], fill=cz, width=4)
    # itálico "falso": desenha o texto numa camada e inclina
    camada = Image.new("RGBA", (round(fi.getlength(txt)) + 30, 60), (0, 0, 0, 0))
    ImageDraw.Draw(camada).text((10, 44), txt, font=fi, fill=cz, anchor="ls")
    camada = camada.transform(camada.size, Image.AFFINE, (1, 0.2, -6, 0, 1, 0), Image.BICUBIC)
    im.alpha_composite(camada, (pad + px + 40, y - 4))
    im.alpha_composite(meta, (pad + round(w) - px - meta.width + 6, pad + h - py - 26))
    return im, pad


def balao_digitando(t, saida=False):
    w, h = 130, 70
    im, pad = _caixa(w, h, C["out"] if saida else C["in_"], saida, True)
    d = ImageDraw.Draw(im)
    for i in range(3):
        fase = (t * 2.2 - i * 0.22) % 1.0
        dy = -8 * max(0, math.sin(fase * math.pi * 2)) if fase < 0.5 else 0
        cor = (150, 158, 164) if dy < -2 else (190, 196, 200)
        cx, cy = pad + 35 + i * 30, pad + h / 2 + dy
        d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=cor)
    return im, pad


def _onda(seed, n=38):
    rnd = random.Random(seed)
    v = [0.25 + 0.75 * abs(math.sin(i * 0.45 + rnd.random() * 2)) * rnd.random() ** 0.4 for i in range(n)]
    return [max(0.12, x) for x in v]


def balao_audio(hora, saida, rabo, dur, prog, quem, cor_av, transcricao=None, nome=None, cor_nome=None,
                encaminhada=False, tocando=False):
    """Mensagem de voz: avatar, play/pausa, onda que vai sendo preenchida, duração e transcrição."""
    w = 640
    topo = (44 if nome else 0) + (40 if encaminhada else 0)
    f_tr = inter(35, 420)
    linhas_tr = quebra(transcricao, f_tr, w - 60) if transcricao else []
    lh = round(f_tr.size * 1.3)
    h_tr = (len(linhas_tr) * lh + 30) if transcricao is not None else 0
    h = topo + 120 + h_tr
    im, pad = _caixa(w, h, C["out"] if saida else C["in_"], saida, rabo)
    d = ImageDraw.Draw(im)
    y = pad + 12
    if nome:
        d.text((pad + 26, y + 30), nome, font=inter(31, 650), fill=cor_nome, anchor="ls")
        y += 44
    if encaminhada:
        d.text((pad + 60, y + 28), "Encaminhada", font=inter(29, 400), fill=C["hora"], anchor="ls")
        cx, cy = pad + 38, y + 18
        d.arc((cx - 10, cy - 4, cx + 10, cy + 16), 180, 270, fill=C["hora"], width=3)
        d.polygon([(cx + 2, cy - 10), (cx + 14, cy - 4), (cx + 2, cy + 2)], fill=C["hora"])
        y += 40
    av = avatar(quem, cor_av, 86)
    ax = pad + w - 110 if not saida else pad + 18
    im.paste(av, (ax, y + 8), av)
    mic = (0, 168, 132) if not saida else (83, 189, 235)
    d.ellipse((ax + 58, y + 62, ax + 92, y + 96), fill=mic)
    d.rounded_rectangle((ax + 70, y + 68, ax + 80, y + 84), 5, fill=(255, 255, 255))
    x0 = pad + (30 if not saida else 128)
    cy = y + 52
    if tocando:
        d.rectangle((x0, cy - 20, x0 + 10, cy + 20), fill=(84, 101, 111))
        d.rectangle((x0 + 20, cy - 20, x0 + 30, cy + 20), fill=(84, 101, 111))
    else:
        d.polygon([(x0, cy - 22), (x0 + 34, cy), (x0, cy + 22)], fill=(84, 101, 111))
    ox = x0 + 58
    barras = _onda(hash(quem + hora) % 1000)
    larg_onda = 380
    passo = larg_onda / len(barras)
    for i, a in enumerate(barras):
        bx = ox + i * passo
        bh = 6 + a * 46
        feito = i / len(barras) < prog
        cor = (0, 168, 132) if (feito and not saida) else (83, 189, 235) if feito else (180, 188, 193)
        d.rounded_rectangle((bx, cy - bh / 2, bx + passo * 0.55, cy + bh / 2), 2, fill=cor)
    bolinha = ox + prog * larg_onda
    d.ellipse((bolinha - 11, cy - 11, bolinha + 11, cy + 11), fill=(0, 168, 132) if not saida else (83, 189, 235))
    s = dur * (prog if tocando or prog > 0 else 1)
    d.text((x0, y + 108), f"{int(s // 60)}:{int(s % 60):02d}", font=inter(25, 450), fill=C["hora"], anchor="ls")
    meta = _meta(hora, saida)
    im.alpha_composite(meta, (pad + w - meta.width - (130 if not saida else 18), y + 86))
    if transcricao is not None:
        yt = y + 128
        d.line([(pad + 26, yt - 4), (pad + w - 26, yt - 4)], fill=(230, 230, 230), width=2)
        for i, ln in enumerate(linhas_tr):
            desenha_linha(im, pad + 28, yt + round(f_tr.size * 1.0) + i * lh, ln, f_tr, (70, 82, 90))
    return im, pad


@functools.lru_cache(16)
def _foto_recortada(caminho, w, h_max):
    ft = caminho() if callable(caminho) else Image.open(caminho).convert("RGB")
    esc = w / ft.width
    h = min(h_max, round(ft.height * esc))
    ft = ft.resize((w, round(ft.height * esc)), Image.LANCZOS)
    top = (ft.height - h) // 2
    return ft.crop((0, top, w, top + h))


def balao_foto(caminho, hora, saida, rabo, legenda=None, nome=None, cor_nome=None, h_max=560, w=600):
    ft = _foto_recortada(caminho, w, h_max)
    topo = 44 if nome else 0
    f = inter(41, 430)
    linhas = quebra(legenda, f, w - 40) if legenda else []
    lh = round(f.size * 1.3)
    h_leg = len(linhas) * lh + 46 if legenda else 0
    bw, bh = w + 12, topo + ft.height + 12 + h_leg
    im, pad = _caixa(bw, bh, C["out"] if saida else C["in_"], saida, rabo)
    d = ImageDraw.Draw(im)
    if nome:
        d.text((pad + 22, pad + 38), nome, font=inter(31, 650), fill=cor_nome, anchor="ls")
    m = Image.new("L", ft.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, ft.width - 1, ft.height - 1), 16, fill=255)
    im.paste(ft, (pad + 6, pad + 6 + topo), m)
    meta = _meta(hora, saida)
    if legenda:
        for i, ln in enumerate(linhas):
            desenha_linha(im, pad + 22, pad + topo + ft.height + 12 + round(f.size * 1.0) + i * lh, ln, f, C["texto"])
        im.alpha_composite(meta, (pad + bw - meta.width - 14, pad + bh - 38))
    else:
        sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle((pad + bw - meta.width - 34, pad + bh - 50, pad + bw - 10, pad + bh - 12),
                                                  14, fill=(0, 0, 0, 90))
        im.alpha_composite(sombra)
        im.alpha_composite(meta, (pad + bw - meta.width - 22, pad + bh - 46))
    return im, pad


@functools.lru_cache(32)
def chip_data(txt):
    f = inter(29, 550)
    w = round(f.getlength(txt)) + 44
    im = Image.new("RGBA", (w + 8, 56), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w + 4, 52), 14, fill=(255, 255, 255, 235))
    d.text((w / 2 + 4, 29), txt, font=f, fill=(84, 101, 111), anchor="mm")
    return im


@functools.lru_cache(32)
def chip_sistema(txt):
    """Aviso amarelado do sistema (ex.: 'Dona Neide saiu')."""
    f = inter(29, 450)
    w = min(860, round(f.getlength(txt)) + 44)
    im = Image.new("RGBA", (w + 8, 58), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w + 4, 54), 14, fill=(255, 245, 196, 245))
    d.text((w / 2 + 4, 30), txt, font=f, fill=(84, 101, 111), anchor="mm")
    return im


# ------------------------------------------------------------------ peças da marca
def banda_marca(im, titulo, parte):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, BANDA), fill=C["preto"])
    d.rectangle((0, BANDA - 8, W, BANDA), fill=C["amarelo"])
    f = inter(44, 900)
    import marca
    d.text((40, 62), marca.NOME, font=f, fill=C["amarelo"], anchor="lm")
    x = 40 + f.getlength(marca.NOME) + 26
    d.text((x, 62), f"{titulo} · {parte}", font=inter(30, 600), fill=(235, 235, 235), anchor="lm")


def tarja(txt, tam=64, cor_txt=None, cor_fundo=None, maxw=900, destaque=None, ang=0.0):
    """Faixa preta com texto (o visual do logo). destaque = índice de palavra em amarelo (legenda karaokê)."""
    cor_txt = cor_txt or (255, 255, 255)
    cor_fundo = cor_fundo or C["preto"]
    f = inter(tam, 850)
    linhas = quebra(txt, f, maxw)
    lh = round(tam * 1.22)
    larg = max(larg_linha(l, f) for l in linhas)
    im = Image.new("RGBA", (round(larg) + 70, len(linhas) * lh + 46), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, im.width, im.height), fill=cor_fundo)
    k = 0
    for i, ln in enumerate(linhas):
        x = (im.width - larg_linha(ln, f)) / 2
        yb = 23 + i * lh + round(tam * 0.98)
        for tok in ln:
            if tok[0] == "t" and not tok[1].isspace():
                cor = C["amarelo"] if (destaque is not None and k <= destaque) else cor_txt
                d.text((x, yb), tok[1], font=f, fill=cor, anchor="ls")
                k += 1
            elif tok[0] == "e":
                e = emoji_img(tok[1], round(tam * 1.0))
                im.alpha_composite(e, (round(x), round(yb - tam * 0.9)))
            x += larg_tok(tok, f)
    if ang:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    return im
