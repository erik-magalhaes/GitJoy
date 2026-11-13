#!/usr/bin/env python3
"""TUDO PRA IMPRIMIR da Tarde de Jogos no Beca’s (13/nov/2026, pedido dele: "organizar tudo que eu preciso imprimir").
Junta os PDFs já gerados (rode antes tarde_becas.py, becas_chuva.py e cracha.py), cria a LISTA DE CONTROLE (Pix /
vale / chegou, 001–060) e um GUIA de impressão, e salva tudo numerado em out/becas/imprimir/ + um PDF único.

    /usr/bin/python3 imprimir_becas.py
"""
import os
import shutil

from PIL import Image, ImageDraw

import tarde_becas as TB
from tarde_becas import E

OUT = TB.OUT
DST = os.path.join(OUT, "imprimir")
DPI = 300
A4 = (2480, 3508)
MAR, PET, LAR = E.MARROM, E.PETROLEO, E.LARANJA

# (arquivo de saída, origem, páginas, como imprimir, quantas cópias)
ITENS = [  # 13/nov: ele tirou as plaquinhas; hoje imprime só estes 4
    ("01_vales_consumacao_001-060.pdf", "vales_A4_001-060.pdf", 3,
     "A4 sulfite (ou 120 g), colorido, tamanho real (100%). Cortar nas linhas cinza: 20 fichas de 5x5 cm por folha.",
     "3 folhas = 60 fichas numeradas. Ficam no CAIXA do Beca’s."),
    ("02_cupons_5off_BECAS5.pdf", "cupons_A4.pdf", 3,
     "A4, colorido, 100%. Cortar: 20 cupons de 5x5 cm por folha.",
     "3 folhas = 60 cupons. Cada pagante LEVA um. Criar o cupom BECAS5 (5%) no site antes!"),
    ("03_crachas_Erik_Jessica.pdf", "cracha_C_Erik_Jessica.pdf", 1,
     "A4, colorido, 100%, de preferência papel 180 g. Cortar cada crachá (10x14 cm) e pôr no porta-crachá.",
     "1 folha (Erik + Jéssica)."),
    ("04_flyer_2_por_A4.pdf", "flyer_2porA4.pdf", 1,
     "A4, colorido, 100%. Cortar ao meio: 2 flyers A5 por folha.", "Quantas quiser (cada folha = 2 flyers)."),
]

TIT = {"01_vales_consumacao_001-060.pdf": "FICHAS DE CONSUMAÇÃO R$ 15 (001 A 060)",
       "02_cupons_5off_BECAS5.pdf": "CUPONS 5% OFF (BECAS5)",
       "03_crachas_Erik_Jessica.pdf": "CRACHÁS ERIK E JÉSSICA",
       "04_flyer_2_por_A4.pdf": "FLYER TARDE DE JOGOS (2 POR A4)",
       "05_lista_de_controle.pdf": "LISTA DE CONTROLE (OPCIONAL)"}


def pagina():
    return Image.new("RGB", A4, (255, 255, 255))


def lista_controle():
    """2 folhas: nº do vale 001–060, nome, WhatsApp, Pix pago, chegou, recebeu cupom."""
    pags = []
    cols = [("Nº", 180), ("NOME", 760), ("WHATSAPP", 520), ("PIX", 200), ("CHEGOU", 220), ("CUPOM", 220)]
    x0, y0, lh = 190, 470, 98
    for p in range(2):
        img = pagina()
        d = ImageDraw.Draw(img)
        d.text((A4[0] / 2, 190), "TARDE DE JOGOS NO BECA’S · LISTA DE CONTROLE", font=E.lilita(84), fill=MAR, anchor="mm")
        d.text((A4[0] / 2, 300), "Sexta, 20/11 · 13h às 19h · R$ 30 (R$ 15 de consumação) · Pix = reserva confirmada",
               font=E.fig(46, 700), fill=PET, anchor="mm")
        d.text((A4[0] / 2, 370), f"Folha {p + 1} de 2", font=E.fig(40, 600), fill=(120, 110, 100), anchor="mm")
        x = x0
        for nome, w in cols:
            d.rectangle((x, y0, x + w, y0 + lh), fill=LAR, outline=MAR, width=4)
            d.text((x + w / 2, y0 + lh / 2), nome, font=E.lilita(44), fill=(255, 255, 255), anchor="mm")
            x += w
        for r in range(30):
            y = y0 + lh * (r + 1)
            x = x0
            for k, (nome, w) in enumerate(cols):
                d.rectangle((x, y, x + w, y + lh), fill=(255, 250, 240) if r % 2 else (255, 255, 255),
                            outline=MAR, width=3)
                if k == 0:
                    d.text((x + w / 2, y + lh / 2), f"{p * 30 + r + 1:03d}", font=E.lilita(46), fill=MAR,
                           anchor="mm")
                elif k >= 3:
                    s = 46
                    cx, cy = x + w / 2, y + lh / 2
                    d.rectangle((cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), outline=MAR, width=4)
                x += w
        pags.append(img)
    return pags


def guia():
    img = pagina()
    d = ImageDraw.Draw(img)
    d.text((A4[0] / 2, 200), "O QUE IMPRIMIR · TARDE DE JOGOS NO BECA’S", font=E.lilita(88), fill=MAR, anchor="mm")
    d.text((A4[0] / 2, 310), "Sexta, 20/11 · imprimir tudo em TAMANHO REAL (100%, sem \"ajustar à página\")",
           font=E.fig(46, 700), fill=PET, anchor="mm")
    y = 430
    for k, (arq, _, n, como, qtd) in enumerate(ITENS + [("05_lista_de_controle.pdf", None, 2,
                                                          "A4 preto e branco. Na prancheta, na entrada.",
                                                          "2 folhas (001 a 060).")]):
        d.rounded_rectangle((170, y, A4[0] - 170, y + 380), 30, fill=(255, 247, 233), outline=MAR, width=5)
        d.ellipse((210, y + 40, 330, y + 160), fill=LAR, outline=MAR, width=5)
        d.text((270, y + 100), str(k + 1), font=E.lilita(70), fill=(255, 255, 255), anchor="mm")
        d.text((370, y + 70), TIT.get(arq, arq[3:-4].replace("_", " ").upper()), font=E.lilita(58), fill=MAR, anchor="lm")
        d.text((370, y + 140), f"{n} página(s)", font=E.fig(40, 700), fill=PET, anchor="lm")
        yy = y + 200
        for txt, cor in ((como, MAR), (qtd, (150, 70, 20))):
            linhas, cur = [], ""
            for p in txt.split():
                if d.textlength(cur + " " + p, font=E.fig(40, 600)) > A4[0] - 620 and cur:
                    linhas.append(cur)
                    cur = p
                else:
                    cur = (cur + " " + p).strip()
            linhas.append(cur)
            for l in linhas:
                d.text((370, yy), l, font=E.fig(40, 600), fill=cor, anchor="lm")
                yy += 52
        y += 410
    return img


def main():
    os.makedirs(DST, exist_ok=True)
    for f in os.listdir(DST):
        os.remove(os.path.join(DST, f))
    # flyer A5 duas vezes numa A4 em pé (cada um girado 90°)
    fl = Image.open(os.path.join(OUT, "flyer_A5.png")).convert("RGB")
    a4 = pagina()
    f2 = fl.rotate(90, expand=True).resize((A4[0], A4[1] // 2), Image.LANCZOS)
    a4.paste(f2, (0, 0))
    a4.paste(f2, (0, A4[1] // 2))
    ImageDraw.Draw(a4).line((0, A4[1] // 2, A4[0], A4[1] // 2), fill=(170, 170, 170), width=3)
    a4.save(os.path.join(OUT, "flyer_2porA4.pdf"), resolution=DPI)
    for arq, orig, _, _, _ in ITENS:
        shutil.copy(os.path.join(OUT, orig), os.path.join(DST, arq))
    lc = lista_controle()
    lc[0].save(os.path.join(DST, "05_lista_de_controle.pdf"), resolution=DPI, save_all=True, append_images=lc[1:])
    g = guia()
    g.save(os.path.join(DST, "00_GUIA_o_que_imprimir.pdf"), resolution=DPI)
    # PDF único com tudo, na ordem
    import fitz
    tudo = fitz.open()
    for f in sorted(os.listdir(DST)):
        if f.endswith(".pdf") and not f.startswith(("TUDO", "00_", "05_")):
            tudo.insert_pdf(fitz.open(os.path.join(DST, f)))
    tudo.save(os.path.join(DST, "TUDO_para_imprimir.pdf"), deflate=True)
    print("ok", len(tudo), "páginas")


if __name__ == "__main__":
    main()
