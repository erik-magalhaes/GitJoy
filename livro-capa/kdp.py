#!/usr/bin/env python3
"""Arquivos do livro para a Amazon KDP, a partir do markdown exportado do Claude Doc do manuscrito.

    python3 kdp.py <manuscrito.md>   → out/kdp/tres_segredos_e_um_ceo.{epub,docx} + out/kdp/capa_kindle.jpg

Tira tudo antes do "## Capítulo 1" (notas de trabalho e linha de autoria), põe a página de direitos autorais,
gera o EPUB (capa embutida, sumário) e o DOCX (Georgia 12, cada capítulo em página nova) com pandoc.
Precisa de out/capa.jpg (rode capa.py antes).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "out", "kdp")
NOME = "tres_segredos_e_um_ceo"

FRENTE = """---
title: "Três Segredos e um CEO"
author: "E.M. Valentine"
lang: pt-BR
rights: "Copyright © 2026 E.M. Valentine. Todos os direitos reservados."
---

# Direitos autorais {.unnumbered .unlisted}

*Três Segredos e um CEO*

Copyright © 2026 E.M. Valentine.
Todos os direitos reservados.

Nenhuma parte desta obra pode ser reproduzida sem a autorização da autora.

Esta é uma obra de ficção. Nomes, personagens, empresas, lugares e acontecimentos são fruto da imaginação da autora. Qualquer semelhança com pessoas reais, vivas ou mortas, ou com fatos reais é mera coincidência.

"""


def estiliza(base, destino):
    d = docx.Document(base)
    s = {x.name: x for x in d.styles}
    for nome in ("Normal", "Body Text", "First Paragraph"):
        st = s[nome]
        st.font.name, st.font.size = "Georgia", Pt(12)
        pf = st.paragraph_format
        pf.space_after = pf.space_before = Pt(0)
        pf.line_spacing = 1.2
        pf.first_line_indent = Cm(0) if nome == "First Paragraph" else Cm(0.75)
    h = s["Heading 1"]
    h.font.size, h.font.name = Pt(20), "Georgia"
    h.paragraph_format.page_break_before = True
    h.paragraph_format.space_after = Pt(24)
    h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for p in d.paragraphs:
        if p.style.name in ("Title", "Author"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p.text.strip() in ("* * *", "FIM"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Cm(0)
    d.save(destino)


def main():
    texto = open(sys.argv[1], encoding="utf-8").read()
    corpo = re.sub(r"^## ", "# ", texto[texto.index("## Capítulo 1"):], flags=re.M)
    os.makedirs(OUT, exist_ok=True)
    capa = os.path.join(AQUI, "out", "capa.jpg")
    with tempfile.TemporaryDirectory() as tmp:
        md = os.path.join(tmp, "livro.md")
        open(md, "w", encoding="utf-8").write(FRENTE + corpo)
        subprocess.run(["pandoc", md, "-o", os.path.join(OUT, NOME + ".epub"), "--epub-cover-image=" + capa,
                        "--toc", "--toc-depth=1", "--split-level=1", "-M", "toc-title=Sumário"], check=True)
        base = os.path.join(tmp, "base.docx")
        subprocess.run(["pandoc", md, "-o", base], check=True)
        estiliza(base, os.path.join(OUT, NOME + ".docx"))
    shutil.copy(capa, os.path.join(OUT, "capa_kindle.jpg"))
    print("ok", OUT, len(corpo.split()), "palavras")


if __name__ == "__main__":
    main()
