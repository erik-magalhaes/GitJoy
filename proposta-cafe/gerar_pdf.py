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


def main():
    os.makedirs(OUT, exist_ok=True)
    final = os.path.join(OUT, "proposta_jogos_no_cafe.pdf")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")  # Chromium do ambiente
        pg = b.new_page()
        pg.goto("file://" + os.path.join(ROOT, "proposta.html"))
        pg.wait_for_timeout(500)
        pg.pdf(path=final, format="A4", print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    doc = pymupdf.open(final)
    for k, page in enumerate(doc, 1):
        page.get_pixmap(dpi=90).save(os.path.join(OUT, f"pagina_{k}.png"))
    print(final, len(doc), "páginas")


if __name__ == "__main__":
    main()
