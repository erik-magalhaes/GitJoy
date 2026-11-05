#!/usr/bin/env python3
"""Proposta "Noite de jogos no seu café" (3/nov/2026, pedido dele): parceria com cafés de Mauá, Santo André e Ribeirão
Pires. proposta.html (A4, 2 páginas, identidade da Jéssica) → out/proposta_jogos_no_cafe.pdf + out/pagina_N.png.
Ingresso em 2 opções: R$ 15 só os jogos (consumo 100% do café) ou R$ 30 com R$ 15 de consumação no café.

    /usr/bin/python3 gerar_pdf.py
"""
import os

import pymupdf
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")


# versão BAR (3/nov, ele: "e bar mais sossegado?"): mesmo texto, trocando café → bar
BAR = [("CAFÉ", "BAR"), ("café", "bar")]  # todas as menções são "o/do/no/seu café" (masculino), então troca direta

LUGARES = {"becas": "Becas Café", "democrata": "Democrata Café"}  # 3/nov: o Becas aceitou receber a proposta (sábado 13h–19h)


def render(html, final):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")  # Chromium do ambiente
        pg = b.new_page()
        pg.goto("file://" + html)
        pg.wait_for_timeout(500)
        pg.pdf(path=final, format="A4", print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    doc = pymupdf.open(final)
    base = os.path.splitext(final)[0]
    for k, page in enumerate(doc, 1):
        page.get_pixmap(dpi=90).save(f"{base}_p{k}.png")
        # JPEG para mandar no Direct do Instagram (não aceita PDF): 1440 px de largura
        page.get_pixmap(dpi=174).pil_save(f"{base}_pagina{k}.jpg", quality=92)
    print(final, len(doc), "páginas")


def main():
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(ROOT, "proposta.html")
    render(src, os.path.join(OUT, "proposta_jogos_no_cafe.pdf"))
    s = open(src, encoding="utf-8").read()
    for a, b in BAR:
        s = s.replace(a, b)
    tmp = os.path.join(ROOT, "_proposta_bar.html")  # na mesma pasta, para os caminhos relativos funcionarem
    open(tmp, "w", encoding="utf-8").write(s)
    try:
        render(tmp, os.path.join(OUT, "proposta_jogos_no_bar.pdf"))
    finally:
        os.remove(tmp)
    # versões com o nome do lugar (cafés que aceitaram receber a proposta)
    for arq, nome in LUGARES.items():
        s = open(src, encoding="utf-8").read()
        s = s.replace('<div class="tag">Proposta de parceria</div>',
                      f'<div class="tag">Proposta de parceria para o {nome}</div>', 1)
        s = s.replace("<h1>TARDE DE JOGOS<br>NO SEU CAFÉ</h1>", f"<h1>TARDE DE JOGOS<br>NO {nome.upper()}</h1>")
        curto = nome.split()[0]  # "Becas Café" → "o Becas" no corpo do texto
        for a in ("o seu café", "O seu café", "seu café"):
            s = s.replace(a, ("O " if a[0] == "O" else "o ") + curto if a != "seu café" else curto)
        for art in ("o", "O", "do", "no"):
            s = s.replace(f"{art} café", f"{art} {curto}")
        s = s.replace("o {0} {0}".format(curto), "o " + curto)
        tmp = os.path.join(ROOT, f"_proposta_{arq}.html")
        open(tmp, "w", encoding="utf-8").write(s)
        try:
            render(tmp, os.path.join(OUT, f"proposta_{arq}.pdf"))
        finally:
            os.remove(tmp)


if __name__ == "__main__":
    main()
