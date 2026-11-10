#!/usr/bin/env python3
"""Linha do tempo do diário do Tikal a partir da narração dele (narracao_diario/frase_NN.wav + palavras.json):
cada página = LEAD + fala + TAIL; a última ganha a tela final depois da fala. As palavras erradas do Whisper são
corrigidas em CORRIGE (o que ele FALOU). Gera narracao_diario/timeline.json, lido pelo diario.py.

    /usr/bin/python3 narracao_diario.py
"""
import json
import os
import wave

AQUI = os.path.dirname(os.path.abspath(__file__))
NAR = os.path.join(AQUI, "narracao_diario")
NOMES = ["gancho", "hexagono", "pa", "templo", "tesouro", "maioria", "guardiao", "vulcao", "cta"]
LEAD, TAIL, TELA_FINAL = 0.15, 0.15, 2.3
# 2ª gravação (10/nov): o que ELE falou (conferido com o Whisper medium). As palavras recebem os tempos do Whisper
# small; se a contagem não bate, os tempos são repartidos pelas letras entre a 1ª e a última palavra ouvida.
TEXTOS = [
    "Diário de expedição, dia 1. Cheguei a Tikal e dizem que tem templos perdidos nessa selva.",
    "A cada turno eu exploro um pedaço novo. Um templo, uma ruína com tesouro... acho que tem até uns vulcões.",
    "Tenho 10 pontos de ação por turno. Colocar um explorador no acampamento me custou um. E cada pedra que eu encontro "
    "no caminho me custa mais um.",
    "Dia 2 do diário de expedição: eu achei um templo! Com dois pontos, escavei mais um andar e ele passou a valer mais.",
    "Descobri que nas ruínas, se eu cavar um tesouro, custa 3 pontos. Se eu tiver 1, vale 1 ponto. 1 par vale 3. E se eu "
    "tiver 3 iguais no final, valem 6 pontos.",
    "Dia 3 do diário de expedição. Descobri que o templo só conta para quem tem mais exploradores nele. Ainda bem que os "
    "chefes valem por 3.",
    "Para me garantir, gastei cinco pontos e coloquei um guardião. O templo agora é meu até o final. E eu troquei um "
    "tesouro com o rival. Ele não pode recusar, mesmo!",
    "Eu sabia que tinha vulcões, e quando ele apareceu, foi hora de contar: os templos que eu domino e os tesouros que eu "
    "possuo. E no final, quem teve mais pontos venceu.",
    "Fim do diário de expedição, por enquanto. E você, escavaria templos ou roubaria tesouros? Comenta aqui! E aluga o "
    "Tikal na Sua Vez. O link tá na bio.",
]


def alinha(ouvidas, texto):
    """[(ini, fim, palavra)] do Whisper + texto certo → [(ini, fim, palavra certa)]."""
    certas = texto.split()
    if len(certas) == len(ouvidas):
        return [(a, b, w) for (a, b, _), w in zip(ouvidas, certas)]
    t0, t1 = ouvidas[0][0], ouvidas[-1][1]
    pesos = [len(w) + 2 for w in certas]
    tot, acc, out = sum(pesos), 0, []
    for w, p in zip(certas, pesos):
        a = t0 + (t1 - t0) * acc / tot
        acc += p
        out.append((a, t0 + (t1 - t0) * acc / tot, w))
    return out


def dur(n):
    with wave.open(os.path.join(NAR, f"frase_{n:02d}.wav")) as w:
        return w.getnframes() / w.getframerate()


def main():
    pal = json.load(open(os.path.join(NAR, "palavras.json"), encoding="utf-8"))
    t, tl = 0.0, []
    for k, nome in enumerate(NOMES):
        n = k + 1
        d = dur(n)
        ws = []
        for a, b, w in alinha(pal[f"{n:02d}"], TEXTOS[k]):
            ws.append({"w": w, "ini": round(t + LEAD + a, 2), "fim": round(t + LEAD + b, 2)})
        c = {"cena": nome, "ini": round(t, 3), "dur": round(LEAD + d + TAIL, 3), "fala": n, "voz_em": round(t + LEAD, 3),
             "palavras": ws}
        if nome == "cta":
            ia = next(p for p in ws if p["w"] == "aluga")
            c["t_comenta"] = round(ia["ini"] - t, 2)
            c["dur"] = round(LEAD + d + TELA_FINAL, 3)
        tl.append(c)
        t += c["dur"]
    json.dump(tl, open(os.path.join(NAR, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", round(t, 1))
    for c in tl:
        print(c["cena"], c["ini"], c["dur"], " ".join(p["w"] for p in c["palavras"]))


if __name__ == "__main__":
    main()
