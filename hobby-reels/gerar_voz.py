#!/usr/bin/env python3
"""Narração sintetizada (voz neural pt-BR Antonio, via edge-tts) para o Reels do hobby.

Cada fala é gerada separada, com velocidade e tom levemente diferentes, para não soar "certinha" demais.
A grafia em FALAS é a de pronúncia (ex.: "Uíngspan"); o texto das legendas fica no narracao.py.
    python3 gerar_voz.py      # narracao/raw/hobby_narracao_NN.mp3
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VOZ = "pt-BR-AntonioNeural"
FALAS = [  # (texto falado, velocidade, tom)
    ("Jogo de tabuleiro é só Banco Imobiliário e Detetive? Então senta aí, que você tá perdendo muita coisa!",
     "+16%", "-1Hz"),
    ("Os jogos modernos são outra coisa: regras simples, partidas rápidas, e ninguém fica eliminado esperando a vez.",
     "+14%", "-2Hz"),
    ("Tem jogo de festa pra dar risada, cooperativo pra jogar junto, e estratégia pra quem gosta de pensar.",
     "+15%", "-1Hz"),
    ("Tem até jogo pra dois, perfeito pro casal... e jogo pra jogar sozinho.", "+12%", "-2Hz"),
    ("Só que tem um porém: jogo bom é caro! Um Uíngspan sai por uns quatrocentos reais na loja.", "+13%", "-1Hz"),
    ("Na Sua Vez, você aluga ele por quarenta e cinco reais e joga cinco dias. Gostou? Aí compra sabendo que vale "
     "a pena.", "+15%", "-2Hz"),
    ("E quanto mais jogos, mais dias: três jogos, sete dias. Cinco, dez. E sete jogos, quinze dias, pelo mesmo "
     "preço!", "+14%", "-1Hz"),
    ("São mais de cento e sessenta jogos no acervo. E aí, qual desses você jogaria primeiro? Comenta aqui!",
     "+14%", "+0Hz"),
    ("Reserva online, retira em Mauá ou recebe em casa: aluga na Sua Vez, o link tá na bio!", "+12%", "-1Hz"),
]

if __name__ == "__main__":
    out = os.path.join(ROOT, "narracao", "raw")
    os.makedirs(out, exist_ok=True)
    for k, (txt, rate, pitch) in enumerate(FALAS, 1):
        dst = os.path.join(out, f"hobby_narracao_{k:02d}.mp3")
        subprocess.run([sys.executable, os.path.join(ROOT, "tts.py"), VOZ, txt, dst, rate, pitch], check=True)
        print("ok", dst)
