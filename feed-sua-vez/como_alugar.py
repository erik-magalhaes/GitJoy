#!/usr/bin/env python3
"""Carrossel 1080x1350 "Como alugar no site" — conceito próprio: TUTORIAL DE CELULAR (14/out/2026).
Cada passo é um celular grande (saindo pela borda de baixo) com a tela do site redesenhada a partir das telas REAIS
(textos e botões copiados do site em 14/10: busca, "Alugar", carrinho, "Entrar para finalizar", login, Planos →
"Assinar pelo WhatsApp" com a mensagem pronta), um dedo tocando no botão certo e uma trilha pontilhada que passa de uma
tela para a outra. O checkout depois do login não foi visto (precisa de conta): o passo 5 não mostra tela, só o que o
site garante (retirada em Mauá ou entrega, frete combinado no pedido, Pix ou cartão). Fundo azul-petróleo pontilhado.
Identidade da Jéssica (fontes, marrom, contorno e sombra sólida) de assinatura-reels/estilo.py.

    python3 como_alugar.py      # out/como_alugar/01..09.png (+ out/como_alugar_folha.jpg)
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, jogo, dado,  # noqa
                    peao, cola, fig)

OUT = os.path.join(ROOT, "out", "como_alugar")
W, H = 1080, 1350
_R = lambda *p: os.path.join(REPO, *p)  # noqa: E731
# cores da interface do site (Acervo de Jogos)
UI_LAR = (249, 115, 22)
UI_TXT = (17, 24, 39)
UI_CINZA = (100, 116, 139)
UI_BORDA = (226, 232, 240)
UI_FOTO = (241, 245, 249)
UI_VERDE = (236, 253, 245), (110, 231, 183), (6, 95, 70)
ZAP = (37, 211, 102)
JOGOS = [  # (caixa oficial, nome, jogadores, tempo) — preços e dados do site em 14/10/2026 (todos R$ 30 / 5 dias)
    (os.path.join(ROOT, "assets", "site", "7_wonders_duel.jpg"), "7 Wonders Duel", "2", "30min"),
    (os.path.join(ROOT, "assets", "site", "azul_duel.jpg"), "Azul Duel", "2", "45min"),
    (os.path.join(ROOT, "assets", "site", "the_resistance.jpg"), "The Resistance", "5–10", "30min"),
    (os.path.join(ROOT, "assets", "site", "boop.jpg"), "boop.", "2", "30min"),
]
S = 1.45  # escala: 1 px da tela do celular (390 de largura) → px do carrossel
SW, SH = int(390 * S), int(760 * S)


def fundo_pontos(semente=0):
    """Azul-petróleo com grade de pontinhos (cara de tela de app)."""
    img = Image.new("RGBA", (W, H), PETROLEO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(30, H, 54):
        for x in range(30 + (27 if (y // 54) % 2 else 0), W, 54):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(40, 141, 168))
    return img


def trilha(img, y_esq, y_dir):
    """Trilha pontilhada que entra pela esquerda e sai pela direita (emenda de uma tela na outra)."""
    d = ImageDraw.Draw(img)
    pts = [(x, y_esq + (y_dir - y_esq) * x / W + 26 * math.sin(x / W * math.pi * 2)) for x in range(-20, W + 21, 4)]
    acc, desenha = 0.0, True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        acc += math.hypot(x1 - x0, y1 - y0)
        if acc > (34 if desenha else 22):
            acc, desenha = 0.0, not desenha
        if desenha:
            d.line((x0, y0, x1, y1), fill=AMARELO, width=12)


def u(v):
    return int(v * S)


def f(s, peso=600):
    return fig(s * S, peso)


def botao(d, x0, y0, x1, y1, txt, cor=UI_LAR, cor_txt=(255, 255, 255), s=15):
    d.rounded_rectangle((u(x0), u(y0), u(x1), u(y1)), radius=u((y1 - y0) / 2), fill=cor)
    d.text((u((x0 + x1) / 2), u((y0 + y1) / 2)), txt, font=f(s, 800), fill=cor_txt, anchor="mm")


def busca(d, txt="Tente 'Azul Duel'"):
    d.rectangle((0, 0, SW, u(62)), fill=(255, 255, 255))
    d.rounded_rectangle((u(16), u(12), u(374), u(50)), radius=u(19), fill=(255, 255, 255), outline=UI_BORDA, width=3)
    cx, cy = u(36), u(31)
    d.ellipse((cx - u(6), cy - u(6), cx + u(5), cy + u(5)), outline=UI_TXT, width=4)
    d.line((cx + u(4), cy + u(4), cx + u(9), cy + u(9)), fill=UI_TXT, width=4)
    d.text((u(58), u(31)), txt, font=f(13, 500), fill=UI_CINZA, anchor="lm")
    d.line((0, u(62), SW, u(62)), fill=UI_BORDA, width=2)


def recorte_foto(path, w, h, raio):
    """Foto do site (render da caixa no fundo laranja) INTEIRA dentro de w x h, cantos arredondados. Se a área não for
    quadrada, a foto não é cortada: as sobras são preenchidas com a própria foto ampliada e bem desfocada (o fundo
    laranja liso continua sem emenda)."""
    src = Image.open(path).convert("RGBA")
    s = max(w / src.width, h / src.height)
    im = src.resize((max(w, round(src.width * s)), max(h, round(src.height * s))), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((x0, y0, x0 + w, y0 + h))
    if abs(w - h) > 2:
        im = im.filter(ImageFilter.GaussianBlur(max(w, h) / 12))
        s = min(w / src.width, h / src.height)
        fr = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
        mk = Image.new("L", fr.size, 255)  # borda esfumada para a foto se misturar ao fundo
        for k in range(14):
            ImageDraw.Draw(mk).rectangle((k, k, fr.width - 1 - k, fr.height - 1 - k), outline=int(255 * k / 14))
        fr.putalpha(mk)
        im.alpha_composite(fr, ((w - fr.width) // 2, (h - fr.height) // 2))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=raio, fill=255)
    im.putalpha(m)
    return im


def foto_site(scr, path, x0, y0, x1, y1, raio):
    """Cola a foto do site no retângulo (coordenadas da tela do celular), como na loja de verdade."""
    scr.alpha_composite(recorte_foto(path, u(x1) - u(x0), u(y1) - u(y0), u(raio)), (u(x0), u(y0)))


def ficha_foto(path, lado):
    """Foto do site num cartão com contorno marrom e sombra sólida (capa e tela final)."""
    b = bloco(lado, lado, BRANCO, raio=34, ow=8, sombra=12)
    b.alpha_composite(recorte_foto(path, lado - 16, lado - 16, 28), (8, 8))
    ImageDraw.Draw(b).rounded_rectangle((0, 0, lado, lado), radius=34, outline=MARROM, width=8)
    return b


def tela_acervo():
    scr = Image.new("RGBA", (SW, SH), (255, 255, 255, 255))
    d = ImageDraw.Draw(scr)
    busca(d)
    d.text((u(16), u(92)), "Acervo", font=f(24, 800), fill=UI_TXT, anchor="lm")
    x = 16
    for t in ("Jogadores", "Categorias", "Complexidade"):
        tw = d.textlength(t, font=f(12, 600)) / S + 34
        d.rounded_rectangle((u(x), u(116), u(x + tw), u(144)), radius=u(14), fill=(255, 255, 255), outline=UI_BORDA,
                            width=3)
        d.text((u(x + 11), u(130)), t, font=f(12, 600), fill=UI_TXT, anchor="lm")
        d.polygon([(u(x + tw - 19), u(127)), (u(x + tw - 11), u(127)), (u(x + tw - 15), u(133))], fill=UI_TXT)
        x += tw + 8
    for k, (p, nome, jog, tempo) in enumerate(JOGOS):
        cx0, cy0 = 16 + (k % 2) * 183, 160 + (k // 2) * 290
        d.rounded_rectangle((u(cx0), u(cy0), u(cx0 + 175), u(cy0 + 278)), radius=u(14), fill=(255, 255, 255),
                            outline=UI_BORDA, width=3)
        foto_site(scr, p, cx0 + 8, cy0 + 8, cx0 + 167, cy0 + 140, 10)
        d.text((u(cx0 + 12), u(cy0 + 160)), nome, font=f(14, 700), fill=UI_TXT, anchor="lm")
        d.text((u(cx0 + 12), u(cy0 + 182)), f"{jog} jog. · {tempo}", font=f(12, 500), fill=UI_CINZA, anchor="lm")
        d.text((u(cx0 + 12), u(cy0 + 206)), "R$ 30", font=f(15, 800), fill=UI_LAR, anchor="lm")
        d.text((u(cx0 + 62), u(cy0 + 207)), "/ 5 dias", font=f(12, 500), fill=UI_CINZA, anchor="lm")
        botao(d, cx0 + 10, cy0 + 228, cx0 + 165, cy0 + 264, "Alugar", s=14)
    return scr


def tela_jogo():
    scr = Image.new("RGBA", (SW, SH), (255, 255, 255, 255))
    d = ImageDraw.Draw(scr)
    busca(d)
    d.text((u(16), u(88)), "Acervo  ›  ", font=f(13, 500), fill=UI_TXT, anchor="lm")
    d.text((u(16) + d.textlength("Acervo  ›  ", font=f(13, 500)), u(88)), "Azul Duel", font=f(13, 500), fill=UI_CINZA,
           anchor="lm")
    foto_site(scr, JOGOS[1][0], 16, 108, 374, 368, 16)
    d.text((u(16), u(404)), "Azul Duel", font=f(30, 800), fill=UI_TXT, anchor="lm")
    d.text((u(16), u(436)), "CATEGORIA FAMÍLIA", font=f(12, 500), fill=UI_CINZA, anchor="lm")
    d.text((u(16), u(468)), "2 jogadores   45 min   10+   Médio-leve", font=f(14, 500), fill=UI_TXT, anchor="lm")
    d.rounded_rectangle((u(16), u(494), u(374), u(626)), radius=u(16), fill=(255, 255, 255), outline=UI_BORDA, width=3)
    d.text((u(150), u(536)), "R$ 30", font=f(30, 800), fill=UI_LAR, anchor="mm")
    d.text((u(250), u(540)), "por 5 dias", font=f(14, 500), fill=UI_CINZA, anchor="mm")
    botao(d, 36, 568, 354, 608, "Alugar", s=16)
    return scr


def tela_carrinho():
    scr = Image.new("RGBA", (SW, SH), (255, 255, 255, 255))
    d = ImageDraw.Draw(scr)
    d.rectangle((0, 0, SW, u(62)), fill=(255, 255, 255))
    d.rounded_rectangle((u(14), u(10), u(376), u(54)), radius=u(12), fill=UI_VERDE[0], outline=UI_VERDE[1], width=3)
    d.ellipse((u(28), u(22), u(48), u(42)), fill=UI_VERDE[2])
    d.line((u(33), u(32), u(37), u(36), u(43), u(28)), fill=(255, 255, 255), width=4)
    d.text((u(58), u(32)), "Adicionado ao carrinho!", font=f(14, 500), fill=UI_VERDE[2], anchor="lm")
    d.text((u(16), u(96)), "Seu carrinho", font=f(26, 800), fill=UI_TXT, anchor="lm")
    d.rounded_rectangle((u(16), u(116), u(374), u(176)), radius=u(12), fill=UI_VERDE[0], outline=UI_VERDE[1], width=3)
    d.multiline_text((u(28), u(146)), BANNER_3, font=f(12.5, 600), fill=UI_VERDE[2], anchor="lm", spacing=u(3))
    for k, (p, nome, _, _) in enumerate([JOGOS[0], JOGOS[2], JOGOS[1]]):  # ordem do carrinho real
        y = 186 + k * 92
        d.rounded_rectangle((u(16), u(y), u(374), u(y + 82)), radius=u(14), fill=(255, 255, 255), outline=UI_BORDA,
                            width=3)
        foto_site(scr, p, 26, y + 9, 90, y + 73, 10)
        d.text((u(104), u(y + 26)), nome, font=f(15, 600), fill=UI_TXT, anchor="lm")
        d.text((u(104), u(y + 56)), "R$ 30 por 7 dias", font=f(12, 500), fill=UI_CINZA, anchor="lm")
        d.text((u(362), u(y + 56)), "R$ 30", font=f(15, 800), fill=UI_LAR, anchor="rm")
        d.text((u(362), u(y + 24)), "Remover", font=f(11, 500), fill=UI_CINZA, anchor="rm")
    d.text((u(16), u(474)), "←  Adicionar mais jogos", font=f(14, 800), fill=UI_LAR, anchor="lm")
    d.rounded_rectangle((u(16), u(498), u(374), u(700)), radius=u(16), fill=(255, 255, 255), outline=UI_BORDA, width=3)
    d.text((u(36), u(530)), "Resumo", font=f(18, 800), fill=UI_TXT, anchor="lm")
    d.text((u(36), u(574)), "Subtotal", font=f(16, 800), fill=UI_TXT, anchor="lm")
    d.text((u(354), u(574)), "R$ 90", font=f(20, 800), fill=UI_LAR, anchor="rm")
    botao(d, 36, 602, 354, 644, "Entrar para finalizar", s=16)
    d.text((u(195), u(668)), "Frete combinado na próxima etapa.", font=f(11, 500), fill=UI_CINZA, anchor="mm")
    return scr


def tela_login():
    scr = Image.new("RGBA", (SW, SH), (255, 255, 255, 255))
    d = ImageDraw.Draw(scr)
    busca(d)
    d.text((u(195), u(118)), "Login de clientes", font=f(24, 800), fill=UI_TXT, anchor="mm")
    for k, rot in enumerate(("Email", "Senha")):
        y = 160 + k * 86
        d.text((u(24), u(y)), rot, font=f(14, 600), fill=UI_TXT, anchor="lm")
        d.rounded_rectangle((u(24), u(y + 16), u(366), u(y + 58)), radius=u(10), fill=(255, 255, 255),
                            outline=UI_BORDA, width=3)
    d.rounded_rectangle((u(24), u(338), u(40), u(354)), radius=u(4), outline=UI_BORDA, width=3)
    d.text((u(50), u(346)), "Lembre-se de mim", font=f(13, 500), fill=UI_TXT, anchor="lm")
    botao(d, 24, 376, 366, 418, "Login", s=16)
    d.text((u(195), u(444)), "Esqueceu sua senha?", font=f(13, 500), fill=UI_CINZA, anchor="mm")
    d.line((u(24), u(478), u(366), u(478)), fill=UI_BORDA, width=2)
    d.text((u(195), u(512)), "Primeira vez por aqui?", font=f(15, 700), fill=UI_TXT, anchor="mm")
    d.rounded_rectangle((u(24), u(536), u(366), u(578)), radius=u(21), fill=(255, 255, 255), outline=UI_LAR, width=4)
    d.text((u(195), u(557)), "Criar conta", font=f(16, 800), fill=UI_LAR, anchor="mm")
    return scr


def tela_planos():
    scr = Image.new("RGBA", (SW, SH), (255, 255, 255, 255))
    d = ImageDraw.Draw(scr)
    busca(d)
    d.text((u(16), u(88)), "PLANOS", font=f(12, 700), fill=UI_LAR, anchor="lm")
    d.text((u(16), u(116)), "Planos", font=f(28, 800), fill=UI_TXT, anchor="lm")
    for k, (nome, preco, vez) in enumerate((("Silver", 49, "1 jogo"), ("Gold", 89, "2 jogos"),
                                            ("Platinum", 139, "3 jogos"))):
        y = 146 + k * 196
        d.rounded_rectangle((u(16), u(y), u(374), u(y + 184)), radius=u(16), fill=(255, 255, 255), outline=UI_BORDA,
                            width=3)
        d.text((u(36), u(y + 32)), f"Assinatura {nome}", font=f(18, 800), fill=UI_TXT, anchor="lm")
        d.text((u(36), u(y + 74)), f"R$ {preco}", font=f(30, 800), fill=UI_LAR, anchor="lm")
        d.text((u(36) + d.textlength(f"R$ {preco}", font=f(30, 800)) + u(6), u(y + 80)), "/mês", font=f(14, 500),
               fill=UI_CINZA, anchor="lm")
        d.text((u(36), u(y + 112)), f"Alugue até {vez} por vez", font=f(14, 500), fill=UI_TXT, anchor="lm")
        botao(d, 36, y + 132, 354, y + 170, "Assinar pelo WhatsApp", s=15)
    return scr


def tela_zap():
    scr = Image.new("RGBA", (SW, SH), (236, 229, 221, 255))
    d = ImageDraw.Draw(scr)
    for y in range(90, SH, 46):  # papel de parede discreto da conversa
        for x in range(20 + (23 if (y // 46) % 2 else 0), SW, 46):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(225, 216, 206))
    d.rectangle((0, 0, SW, u(70)), fill=(7, 94, 84))
    d.text((u(20), u(35)), "←", font=f(22, 700), fill=(255, 255, 255), anchor="lm")
    d.ellipse((u(48), u(13), u(92), u(57)), fill=(255, 255, 255))
    lg = Image.open(_R("voodoo-reels/assets/logo_suavez.png")).convert("RGBA")
    lg.thumbnail((u(38), u(38)), Image.LANCZOS)
    scr.alpha_composite(lg, (u(70) - lg.width // 2, u(35) - lg.height // 2))
    d.text((u(104), u(26)), "Sua vez!", font=f(17, 700), fill=(255, 255, 255), anchor="lm")
    d.text((u(104), u(48)), "(11) 97793-3910", font=f(12, 500), fill=(200, 230, 225), anchor="lm")
    d.rounded_rectangle((u(110), u(100), u(280), u(128)), radius=u(8), fill=(225, 245, 254))
    d.text((u(195), u(114)), "HOJE", font=f(11, 700), fill=UI_CINZA, anchor="mm")
    # mensagem já escrita pelo site, pronta pra enviar (teclado aberto embaixo)
    d.rounded_rectangle((u(10), u(412), u(320), u(492)), radius=u(26), fill=(255, 255, 255))
    d.multiline_text((u(28), u(452)), "Olá! Quero assinar o plano\nAssinatura Gold.", font=f(15, 500), fill=UI_TXT,
                     anchor="lm", spacing=u(4))
    d.ellipse((u(328), u(426), u(380), u(478)), fill=(0, 168, 132))
    cx, cy = u(354), u(452)
    d.polygon([(cx - u(10), cy - u(11)), (cx + u(13), cy), (cx - u(10), cy + u(11)), (cx - u(6), cy)],
              fill=(255, 255, 255))
    d.rectangle((0, u(504), SW, SH), fill=(210, 214, 220))
    for r, (n, x0) in enumerate(((10, 6), (9, 24), (7, 60))):
        for k in range(n):
            x = x0 + k * 38.4
            d.rounded_rectangle((u(x), u(516 + r * 54), u(x + 32), u(560 + r * 54)), radius=u(6), fill=(255, 255, 255))
    return scr


def celular(scr, corte=None):
    """Corpo do celular (contorno marrom, sombra sólida) com a tela dentro."""
    bw, bh = SW + 44, SH + 60
    im = bloco(bw, bh, (52, 38, 30), raio=70, ow=9, sombra=16)
    m = Image.new("L", scr.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, SW, SH + 80), radius=48, fill=255)
    im.paste(scr, (22, 34), m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((bw / 2 - 60, 12, bw / 2 + 60, 26), radius=7, fill=(30, 22, 18))
    return im


def dedo():
    """Mão tocando (desenhada simples, cor de pele + contorno marrom) com ondas de toque."""
    im = Image.new("RGBA", (260, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pele, ow = (255, 214, 170), 7
    for r, a in ((70, 120), (50, 190)):
        d.ellipse((60 - r, 60 - r, 60 + r, 60 + r), outline=BRANCO + (a,), width=8)
    # indicador + mão
    d.rounded_rectangle((40, 40, 96, 230), radius=28, fill=pele, outline=MARROM, width=ow)
    d.rounded_rectangle((60, 150, 230, 320), radius=60, fill=pele, outline=MARROM, width=ow)
    d.rounded_rectangle((47, 140, 89, 225), radius=20, fill=pele)
    for x in (110, 150, 190):
        d.rounded_rectangle((x - 6, 128, x + 34, 210), radius=20, fill=pele, outline=MARROM, width=ow)
    d.rectangle((70, 196, 222, 240), fill=pele)
    d.arc((54, 46, 82, 74), 200, 340, fill=(240, 180, 140), width=5)
    return im


def selo(n, cor=AMARELO, ct=MARROM, rot="PASSO"):
    """Selo redondo com o número do passo + pílula com o nome."""
    im = Image.new("RGBA", (220, 230), (0, 0, 0, 0))
    b = bloco(130, 130, cor, raio=65, ow=7, sombra=9)
    cola(b, titulo(str(n), 92, ct, contorno=MARROM, sw=0, sombra=0), 65, 70)
    cola(im, b, 110, 75, -6)
    cola(im, pilula(rot, 28, BRANCO, MARROM, pad=(18, 6), ow=4, sombra=5, fonte_titulo=True), 110, 190, 3)
    return im


def cabecalho(img, n, tit, sub, rot="PASSO", cor=AMARELO):
    cola(img, selo(n, cor, MARROM if cor == AMARELO else BRANCO, rot), 130, 140)
    t = titulo(tit, 86, BRANCO, larg_max=760)
    cola(img, t, 625, 40 + t.height / 2, -2)
    y = 40 + t.height + 10
    if sub:
        st = texto(sub, 34, BRANCO, 700, larg_max=760)
        cola(img, st, 625, y + st.height / 2)
        y += st.height
    return y


def passo(n, tit, sub, scr, toque, nota=None, nota_y=None, trilha_y=(1180, 1180), rot="PASSO", cor=AMARELO):
    img = fundo_pontos(n)
    trilha(img, *trilha_y)
    y = cabecalho(img, n, tit, sub, rot, cor)
    fone = celular(scr)
    fx, fy = 625, max(300, y + 25) + fone.height / 2
    cola(img, fone, fx, fy, 0)
    if toque:  # posição (na tela) do ponto tocado: a ponta do dedo cai exatamente ali
        tx = fx - fone.width / 2 + 22 + u(toque[0])
        ty = fy - fone.height / 2 + 34 + u(toque[1])
        e = 0.72
        cola(img, dedo(), tx + 70 * e, ty + 105 * e, 12, e)
    if nota:
        cola(img, nota, 165, nota_y, -4)
    return img


def nota(txt, cor=AMARELO, cor_txt=MARROM, w=290):
    w = min(w, 290)
    t = texto(txt, 31, cor_txt, 800, larg_max=w - 44)
    b = bloco(w, t.height + 50, cor, raio=30, ow=6, sombra=9)
    cola(b, t, w / 2, (t.height + 50) / 2)
    return b


def capa():
    img = fundo_pontos(0)
    trilha(img, 1250, 1180)
    cola(img, logo(260), 170, 120, -6)
    cola(img, pilula("PASSO A PASSO", 40, AMARELO, MARROM, pad=(28, 10), fonte_titulo=True), 800, 120, 4)
    cola(img, titulo("COMO ALUGAR\nNO SITE", 140, BRANCO, larg_max=960), W / 2, 365, -2)
    cola(img, texto("Do celular, em poucos toques.", 44, BRANCO, 800), W / 2, 560)
    fone = celular(tela_jogo())
    cola(img, fone, W / 2 + 150, 650 + fone.height / 2 * 0.86, -8, 0.86)
    cola(img, ficha_foto(JOGOS[0][0], 280), 200, 860, 7)
    cola(img, ficha_foto(JOGOS[2][0], 250), 205, 1105, -6)
    cola(img, pilula("arrasta pro lado  →", 28, BRANCO, MARROM, pad=(22, 8), ow=4, sombra=5), 215, 1290, -3)
    return img


def finalize():
    img = fundo_pontos(5)
    trilha(img, 1180, 1200)
    cabecalho(img, 5, "FINALIZE\nO PEDIDO", None)
    for k, (tit, desc, cor, ct) in enumerate((("RETIRE EM MAUÁ", "é só passar na loja", AMARELO, MARROM),
                                              ("OU RECEBA EM CASA", "o frete é combinado no pedido", LARANJA, BRANCO))):
        b = bloco(820, 210, cor, raio=36, ow=8, sombra=12)
        cola(b, titulo(tit, 66, BRANCO if cor == AMARELO else AMARELO, sw=6, sombra=6), 410, 78)
        cola(b, texto(desc, 36, ct, 800), 410, 158)
        cola(img, b, W / 2 + (-20, 25)[k], 430 + k * 255, (-1.5, 1.2)[k])
    cola(img, pilula("PAGUE NO PIX OU NO CARTÃO", 50, BRANCO, MARROM, pad=(36, 16), fonte_titulo=True), W / 2, 935, -2)
    cola(img, titulo("E BORA JOGAR!", 92, AMARELO), W / 2, 1075, 2)
    cola(img, peao(150, LARANJA), 120, 1230, -10)
    cola(img, dado(110, 6, BRANCO), 960, 1240, 12)
    return img


def final():
    """Tela final reta e centralizada: logo, título, as fotos do site em fileira e o link."""
    img = fundo_pontos(9)
    trilha(img, 1215, 1215)
    cola(img, logo(330), W / 2, 135)
    cola(img, titulo("PRONTO!\nAGORA É A SUA VEZ!", 104, BRANCO, larg_max=960), W / 2, 385)
    lado, passo_x = 230, 245
    for k, (p, *_r) in enumerate(JOGOS):
        cola(img, ficha_foto(p, lado), W / 2 + (k - 1.5) * passo_x, 690 + (0, -14, -14, 0)[k], (-4, -1.5, 1.5, 4)[k])
    cola(img, pilula("ALUGUE PELO LINK NA BIO", 56, AMARELO, MARROM, pad=(40, 18), fonte_titulo=True), W / 2, 935)
    cola(img, texto("suavez.acervodejogos.com.br", 40, BRANCO, 800), W / 2, 1050)
    cola(img, texto("@suavez_bg", 44, AMARELO, 900), W / 2, 1115)
    return img


# texto real do carrinho com 3 jogos (14/10/2026, sem o emoji 🎉 do começo)
BANNER_3 = "Com 3 jogos, você ganhou prazo extra: todos\nficam 7 dias sem pagar nada a mais."


def telas():
    return [
        capa(),
        passo(1, "ESCOLHA O JOGO", "Busque pelo nome ou use os filtros do acervo.", tela_acervo(), (165, 410),
              nota("Filtre por jogadores, categoria e complexidade!", w=330), 1100, (1180, 1200)),
        passo(2, "TOQUE EM\n“ALUGAR”", "Na página do jogo você vê jogadores, tempo e preço.", tela_jogo(), (300, 596),
              nota("R$ 15, 30, 45 ou 60 por 5 dias", w=320), 1080, (1200, 1180)),
        passo(3, "MONTE SEU\nCARRINHO", "Quanto mais jogos, mais dias pra todos:", tela_carrinho(), (330, 630),
              nota("3 jogos = 7 dias\n5 jogos = 10 dias\n7 jogos = 15 dias", w=320), 1060, (1180, 1180)),
        passo(4, "ENTRE NA\nSUA CONTA", "Primeira vez? Toque em “Criar conta” e preencha seus dados.", tela_login(),
              (320, 566), nota("Os dados e o endereço só na primeira vez.", w=320), 1080, (1180, 1180)),
        finalize(),
        passo(1, "QUER ASSINAR?", "No menu, toque em “Planos” e escolha o seu.", tela_planos(), (342, 498),
              nota("Trocas sem limite no mês!", w=310), 1100, (1200, 1180), "ASSINATURA", LARANJA),
        passo(2, "ABRE O\nWHATSAPP", "A mensagem já vem pronta: é só enviar que a gente combina tudo.", tela_zap(),
              (354, 452), nota("Silver R$ 49\nGold R$ 89\nPlatinum R$ 139", w=320), 1060, (1180, 1200), "ASSINATURA", LARANJA),
        final(),
    ]


def main():
    os.makedirs(OUT, exist_ok=True)
    ts = telas()
    for k, im in enumerate(ts):
        im.convert("RGB").save(os.path.join(OUT, f"{k + 1:02d}.png"))
    folha = Image.new("RGB", (5 * 324 + 60, 2 * 405 + 30), (255, 255, 255))
    for k, im in enumerate(ts):
        folha.paste(im.convert("RGB").resize((324, 405), Image.LANCZOS), (10 + (k % 5) * 334, 10 + (k // 5) * 415))
    folha.save(os.path.join(ROOT, "out", "como_alugar_folha.jpg"), quality=90)
    print("ok", len(ts))


if __name__ == "__main__":
    main()
