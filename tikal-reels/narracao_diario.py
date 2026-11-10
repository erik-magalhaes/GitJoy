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
LEAD, TAIL, TELA_FINAL = 0.25, 0.35, 3.2
CORRIGE = {"ticar": "Tikal", "tempos": "templos", "tempo.": "templo!", "ruída": "ruína", "campamento,": "acampamento,",
           "Por": "Pôr", "alugue": "aluga", "-te": "o", "calma": "Tikal na", "a": "a"}


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
        for a, b, w in pal[f"{n:02d}"]:
            w2 = CORRIGE.get(w, w)
            if nome == "cta" and w == "a" and ws and ws[-1]["w"] == "Tikal na":
                w2 = "Sua"  # "...Tikal na Sua Vez"
                continue
            ws.append({"w": w2, "ini": round(t + LEAD + a, 2), "fim": round(t + LEAD + b, 2)})
        c = {"cena": nome, "ini": round(t, 3), "dur": round(LEAD + d + TAIL, 3), "fala": n, "voz_em": round(t + LEAD, 3),
             "palavras": ws}
        if nome == "cta":
            ia = next(i for i, p in enumerate(pal["09"]) if p[2].startswith("alugue"))
            c["t_comenta"] = round(LEAD + pal["09"][ia][0], 2)
            c["dur"] = round(LEAD + d + TELA_FINAL, 3)
        tl.append(c)
        t += c["dur"]
    json.dump(tl, open(os.path.join(NAR, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", round(t, 1))
    for c in tl:
        print(c["cena"], c["ini"], c["dur"], " ".join(p["w"] for p in c["palavras"]))


if __name__ == "__main__":
    main()
