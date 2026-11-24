#!/usr/bin/env python3
"""Imagem do Domingo de Jogos 13/12 para mandar no WHATSAPP (24/nov). Visual do post do feed (vermelho natalino,
guarda-chuvinhas), mas com 4 polaroides pequenas (gente se divertindo, jogos, comida) no lugar da foto + quadro de
vagas, e sem "link na bio": endereço do Beca’s e reserva pelo WhatsApp. 1080x1500 → out/domingo/whatsapp.png
"""
import os
import subprocess

from PIL import Image

import domingo as D
import domingo_carrossel as DC
from motor import ffmpeg
from tarde import E, TB, MAR, PET, LAR, AMA, BR, ROSA


def quadro_nov06(arq, t):
    dst = os.path.join(D.OUT, "_fotos", f"{arq}_{t:.2f}.png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(t), "-i",
                        os.path.join(DC.ROOT, "brutos", "nov06", f"20261106_{arq}.mp4"), "-frames:v", "1", "-vf",
                        "hqdn3d=2:2:3:3,eq=contrast=1.04:saturation=1.06,unsharp=5:5:0.4", dst], check=True)
    return Image.open(dst).convert("RGB")


FOTOS = [  # (imagem, legenda, ay, giro, y)
    (lambda: DC.quadro_festa(49.5), "gente nova", 0.45, -6, 0),
    (lambda: DC.foto("20261120_151857.jpg"), "jogo bom", 0.5, 4, 25),
    (lambda: quadro_nov06("151311", 0.5), "bolo nuvem", 0.5, -3, 5),
    (lambda: DC.quadro_festa(12.6), "muita risada", 0.4, 5, 20),
]


def whatsapp():
    img = Image.new("RGBA", (1080, 1500))
    img.alpha_composite(D.fundo(3.0).crop((0, 0, 1080, 1500)))
    E.cola(img, E.titulo("DOMINGO\nDE JOGOS", 135, LAR), 540, 405, -2, 1, 1)
    E.cola(img, D.selo_fim_de_ano(36), 540, 575, 1, 1, 1)
    for k, (f, leg, ay, rot, dy) in enumerate(FOTOS):
        E.cola(img, DC.polaroide(f(), 210, 270, leg, ay), 140 + k * 267, 815 + dy, rot, 1, 1)
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 96, D.COR_VAGAS), 540, 1065, -2, 1, 1)
    E.cola(img, E.pilula(f"{D.DATA} · {D.HORA}", 42, AMA, MAR, fonte_titulo=True), 540, 1170, 1, 1, 1)
    E.cola(img, E.pilula(f"{D.PRECO} · R$ 25 viram consumação no café", 30, BR, MAR), 540, 1240, -1, 1, 1)
    E.cola(img, E.pilula("BECA’S CAFÉ · RUA SOROCABA, 35 · MAUÁ", 32, BR, MAR, fonte_titulo=True), 540, 1310, 1, 1, 1)
    E.cola(img, E.pilula("TEM DESAFIO HITSTER VALENDO PRÊMIO!", 32, AMA, MAR, fonte_titulo=True), 540, 1375, -1, 1, 1)
    E.cola(img, E.pilula(f"RESERVE PELO WHATSAPP {TB.WHATS}", 36, PET, BR, fonte_titulo=True), 540, 1445, 0, 1, 1)
    return img.convert("RGB")


if __name__ == "__main__":
    os.makedirs(os.path.join(D.OUT, "domingo"), exist_ok=True)
    p = os.path.join(D.OUT, "domingo", "whatsapp.png")
    whatsapp().save(p)
    print(p)
