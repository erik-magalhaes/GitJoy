#!/usr/bin/env python3
"""Proposta "Confraternização com jogos de tabuleiro" (16/nov/2026, 1º pedido de evento: Rodrigo, ~30 pessoas).
Pacote do Erik: R$ 1.200 = até 30 pessoas, 4 h, 2 monitores; hora extra R$ 250. proposta.html (A4, 2 págs, identidade da
Jéssica, mesmo visual de proposta-cafe/) → out/proposta_confraternizacao.pdf + JPEGs por página (pro WhatsApp).

    /usr/bin/python3 gerar_pdf.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "proposta-cafe"))
from gerar_pdf import render  # noqa: E402

if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    render(os.path.join(ROOT, "proposta.html"), os.path.join(ROOT, "out", "proposta_confraternizacao.pdf"))
