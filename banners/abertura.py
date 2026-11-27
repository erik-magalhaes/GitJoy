#!/usr/bin/env python3
"""IMAGEM DE ABERTURA da página da loja na Rejoy (13/nov/2026): arte quadrada 1080x1080 (computador) e arte larga
1920x1080 (celular). Regra da Rejoy: SEM TEXTO na arte (a página já põe o nome da loja e pode cobrir as bordas) →
só fundo da identidade, caixas OFICIAIS do acervo e os mascotes (salsicha = Jéssica, coruja = Erik), tudo importante
longe das bordas.

    /usr/bin/python3 abertura.py   → out/abertura_quadrada.png + out/abertura_larga.png
"""
import os

from PIL import Image

import rejoy as R
E = R.E

L = lambda n: os.path.join(R.LISTA, n + ".png")  # noqa: E731
# só jogos que ESTÃO no site
CAIXAS = ["king_of_tokyo", "ticket_to_ride", "hitster", "dixit", "harmonies", "splendor_duel",
          "trio", "boop", "coup", "azul_duel", "the_resistance", "flip_7"]


def leque_caixas(img, nomes, cx, base, raio, h, abre=70):
    """caixas em arco (as das pontas giradas pra fora), de trás pra frente."""
    n = len(nomes)
    import math
    ordem = sorted(range(n), key=lambda i: -abs(i - (n - 1) / 2))  # pontas atrás, meio na frente
    for i in ordem:
        a = -abre + 2 * abre * i / (n - 1)
        x = cx + raio * math.sin(math.radians(a))
        y = base - raio * math.cos(math.radians(a))
        E.cola(img, R.caixa(L(nomes[i]), h), x, y, -a * 0.6)


def quadrada():
    W = H = 1080
    img = E.fundo(W, H, 4).copy()
    leque_caixas(img, CAIXAS[:7], 540, 860, 470, 245, abre=52)
    R.mascote(img, "salsicha_entregando", 560, 400, 975)
    R.mascote(img, "coruja_acenando", 515, 700, 975)
    return img


def larga():
    W, H = 1920, 1080
    img = E.fundo(W, H, 7).copy()
    leque_caixas(img, CAIXAS[:11], 960, 1250, 900, 265, abre=48)
    R.mascote(img, "salsicha_entregando", 600, 810, 985)
    R.mascote(img, "coruja_acenando", 555, 1120, 985)
    return img


if __name__ == "__main__":
    os.makedirs(R.OUT, exist_ok=True)
    q, l = quadrada(), larga()
    q.convert("RGB").save(os.path.join(R.OUT, "abertura_quadrada.png"))
    l.convert("RGB").save(os.path.join(R.OUT, "abertura_larga.png"))
    print("ok")
