"""Estudo preliminar: casa térrea em lote de condomínio de 600 m² (20 x 30 m).

Gera out/planta.png e out/planta.pdf (planta humanizada com implantação e quadro de áreas).
Medidas em metros; y = 0 é a frente do lote (rua embaixo do desenho).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Arc, Polygon
from matplotlib.backends.backend_pdf import PdfPages

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "out")
os.makedirs(OUT, exist_ok=True)

LOTE = (20.0, 30.0)
RECUO = dict(frente=5.0, lateral=1.5, fundo=3.0)   # premissa: conferir no regulamento do condomínio

COR = dict(social="#F6E7C8", intimo="#DCE9F5", servico="#E6E6E6", jogos="#E9DDF3",
           trabalho="#E2F0DA", varanda="#F3D9C4", grama="#CFE8B8", piso="#ECE6DA",
           deck="#D9B98C", areia="#F2E2A8", parede="#2B2B2B", movel="#7A7A7A")

# nome, x0, y0, x1, y1, zona
AMBIENTES = [
    ("Garagem\n2 carros",          1.5,  5.0,  7.5, 10.5, "servico"),
    ("Lavanderia\n+ ducha pet",    1.5, 10.5,  5.6, 13.0, "servico"),
    ("Lavabo",                     5.6, 10.5,  7.5, 13.0, "servico"),
    ("Cozinha",                    1.5, 13.0,  7.5, 17.0, "social"),
    ("Varanda gourmet",            1.5, 17.0,  7.5, 22.0, "varanda"),
    ("Sala de estar",              7.5,  5.0, 14.5,  9.0, "social"),
    ("Galeria",                    7.5,  9.0,  9.0, 14.0, "social"),
    ("Sala de jogos",              9.0,  9.0, 13.3, 14.0, "jogos"),
    ("Jantar / TV",                7.5, 14.0, 13.3, 22.0, "social"),
    ("Home office\n(+ hóspedes)", 14.5,  5.0, 18.5,  9.0, "trabalho"),
    ("",                          13.3,  9.0, 14.5, 17.5, "intimo"),   # corredor íntimo
    ("Banho",                     14.5,  9.0, 18.5, 11.0, "servico"),
    ("Quarto da filha",           14.5, 11.0, 18.5, 14.4, "intimo"),
    ("Closet",                    14.5, 14.4, 16.2, 17.5, "intimo"),
    ("Banho suíte",               16.2, 14.4, 18.5, 17.5, "servico"),
    ("Suíte do casal",            13.3, 17.5, 18.5, 22.0, "intimo"),
]


def area(a):
    _, x0, y0, x1, y1, _ = a
    return (x1 - x0) * (y1 - y0)


def areas():
    d = {}
    for a in AMBIENTES:
        nome = a[0].replace("\n", " ") or "Circulação íntima"
        d[nome] = area(a)
    return d


def desenha(ax):
    W, H = LOTE
    ax.set_xlim(-1.2, W + 1.2)
    ax.set_ylim(-3.2, H + 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    # rua, calçada e lote
    ax.add_patch(Rectangle((-1.2, -3.2), W + 2.4, 1.6, fc="#BDBDBD", ec="none"))
    ax.text(W / 2, -2.4, "RUA DO CONDOMÍNIO", ha="center", va="center", fontsize=9, color="#555", weight="bold")
    ax.add_patch(Rectangle((-1.2, -1.6), W + 2.4, 1.6, fc="#E3E3E3", ec="none"))
    ax.add_patch(Rectangle((0, 0), W, H, fc=COR["grama"], ec="#6B8E4E", lw=1.2, ls=(0, (6, 3))))

    # pisos externos
    ax.add_patch(Rectangle((1.5, -1.6), 6.0, 6.6, fc=COR["piso"], ec="#B9AE98", lw=0.6))     # entrada de carros
    ax.text(4.5, 2.2, "entrada de carros\n(piso drenante)", ha="center", fontsize=6.5, color="#7A6E57")
    ax.add_patch(Rectangle((9.4, -1.6), 1.3, 6.6, fc=COR["piso"], ec="#B9AE98", lw=0.6))     # caminho
    ax.add_patch(Rectangle((8.6, 3.8), 3.2, 1.2, fc=COR["deck"], ec="#9C7A4C", lw=0.6))     # marquise
    ax.text(10.2, 4.4, "marquise", ha="center", va="center", fontsize=6, color="#5E4626")
    ax.add_patch(Rectangle((0, 10.5), 1.5, 11.5, fc=COR["piso"], ec="#B9AE98", lw=0.6))     # corredor pet
    ax.text(0.75, 16.2, "corredor do pet", rotation=90, ha="center", va="center", fontsize=6.5, color="#7A6E57")
    ax.add_patch(Rectangle((1.5, 22.0), 17.0, 2.2, fc=COR["deck"], ec="#9C7A4C", lw=0.6))  # deck
    for x in [i * 0.5 + 1.5 for i in range(35)]:
        ax.plot([x, x], [22.0, 24.2], color="#B8945F", lw=0.3)
    ax.text(10, 23.1, "DECK DE MADEIRA", ha="center", va="center", fontsize=7, color="#5E4626", weight="bold")

    # playground
    ax.add_patch(FancyBboxPatch((8.2, 25.2), 6.4, 3.8, boxstyle="round,pad=0,rounding_size=0.8",
                                fc=COR["areia"], ec="#C9A93F", lw=0.8))
    ax.add_patch(Rectangle((8.8, 26.6), 1.8, 1.8, fc="#F28B82", ec="#B5544B", lw=0.6))
    ax.add_patch(Polygon([(8.6, 28.4), (9.7, 29.2), (10.8, 28.4)], fc="#C0504D", ec="#8E3532", lw=0.6))
    ax.text(9.7, 27.4, "casinha", ha="center", va="center", fontsize=5.5)
    ax.plot([11.6, 14.0], [28.3, 28.3], color="#6B4E2E", lw=1.6)
    for x in (12.2, 13.4):
        ax.add_patch(Rectangle((x - 0.25, 27.6), 0.5, 0.2, fc="#4F81BD", ec="none"))
        ax.plot([x - 0.2, x - 0.2], [27.8, 28.3], color="#555", lw=0.4)
        ax.plot([x + 0.2, x + 0.2], [27.8, 28.3], color="#555", lw=0.4)
    ax.text(12.8, 27.2, "balanço", ha="center", fontsize=5.5)
    ax.add_patch(Rectangle((11.4, 25.6), 2.6, 1.0, fc="#FFF3C4", ec="#C9A93F", lw=0.5))
    ax.text(12.7, 26.1, "tanque de areia", ha="center", va="center", fontsize=5.5)
    ax.text(11.4, 29.45, "ESPAÇO DE BRINCAR", ha="center", fontsize=7, weight="bold", color="#7A5E00")

    # espaço pet
    ax.add_patch(FancyBboxPatch((0.4, 24.9), 5.6, 4.4, boxstyle="round,pad=0,rounding_size=0.5",
                                fc="#DDEFC9", ec="#7FA35B", lw=0.8, ls="--"))
    ax.add_patch(Rectangle((0.7, 26.9), 2.0, 2.0, fc="#D9C3A3", ec="#8A6E45", lw=0.7))
    ax.text(1.7, 27.9, "casinha\ncoberta", ha="center", va="center", fontsize=5.5)
    ax.add_patch(Circle((4.6, 28.2), 0.35, fc="#9FC5E8", ec="#3D7CB8", lw=0.6))
    ax.text(4.6, 27.5, "ducha /\nbebedouro", ha="center", va="top", fontsize=5)
    ax.text(3.2, 25.4, "ESPAÇO DO CACHORRO", ha="center", fontsize=7, weight="bold", color="#3E5F22")

    # horta e árvores
    for i in range(3):
        ax.add_patch(Rectangle((16.0, 25.4 + i * 1.3), 3.2, 0.8, fc="#A9763E", ec="#6E4A22", lw=0.5))
    ax.text(17.6, 29.4, "HORTA", ha="center", fontsize=7, weight="bold", color="#5A3B18")
    for (x, y, r) in [(15.2, 2.5, 1.4), (18.2, 1.6, 1.0), (19.0, 20.0, 0.9), (7.0, 28.6, 1.0), (0.8, 6.5, 0.7), (19.2, 13.0, 0.6)]:
        ax.add_patch(Circle((x, y), r, fc="#8DBF6A", ec="#4E7A2E", lw=0.7, alpha=0.85))

    # portões que fecham o fundo para o cachorro
    for (x0, y0, x1, y1) in [(0, 10.5, 1.5, 10.5), (18.5, 8.5, 20, 8.5)]:
        ax.plot([x0, x1], [y0, y1], color="#C0504D", lw=2.4)
    ax.text(0.75, 10.0, "portão", ha="center", fontsize=5.5, color="#C0504D")
    ax.text(19.25, 8.0, "portão", ha="center", fontsize=5.5, color="#C0504D")

    # ambientes
    for nome, x0, y0, x1, y1, zona in AMBIENTES:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=COR[zona], ec=COR["parede"], lw=1.6))

    # moveis
    mobilia(ax)

    # rótulos
    ar = areas()
    for a in AMBIENTES:
        nome, x0, y0, x1, y1, _ = a
        if not nome:
            continue
        chave = nome.replace("\n", " ")
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        pos = ROTULO.get(chave, (cx, cy))
        ax.text(pos[0], pos[1], f"{nome.upper()}\n{ar[chave]:.1f} m²", ha="center", va="center",
                fontsize=6.6 if (x1 - x0) * (y1 - y0) > 8 else 5.4, weight="bold", color="#222",
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.2))

    # paredes externas grossas
    contorno = [(1.5, 5), (18.5, 5), (18.5, 22), (1.5, 22), (1.5, 5)]
    ax.plot(*zip(*contorno), color=COR["parede"], lw=3.2, solid_joinstyle="miter")

    portas(ax)
    janelas(ax)
    cotas(ax)



ROTULO = {
    "Garagem 2 carros": (4.5, 9.6), "Lavanderia + ducha pet": (2.6, 11.5), "Lavabo": (6.9, 11.0),
    "Cozinha": (4.6, 16.55), "Varanda gourmet": (4.5, 21.2), "Sala de estar": (9.6, 8.1), "Galeria": (8.25, 11.6),
    "Sala de jogos": (11.0, 13.0), "Jantar / TV": (8.8, 19.4), "Home office (+ hóspedes)": (16.2, 7.6),
    "Banho": (15.6, 10.4), "Quarto da filha": (15.9, 12.8), "Closet": (15.35, 16.4), "Banho suíte": (17.4, 16.7),
    "Suíte do casal": (15.0, 21.2),
}


def r(ax, x, y, w, h, fc="white", ec=None, lw=0.6, round_=0.0, **k):
    if round_:
        p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={round_}", fc=fc,
                           ec=ec or COR["movel"], lw=lw, **k)
    else:
        p = Rectangle((x, y), w, h, fc=fc, ec=ec or COR["movel"], lw=lw, **k)
    ax.add_patch(p)


def cadeiras(ax, x0, y0, w, h, n_lado, cab=True):
    for i in range(n_lado):
        cx = x0 + w * (i + 0.5) / n_lado
        r(ax, cx - 0.22, y0 - 0.5, 0.44, 0.4, round_=0.08)
        r(ax, cx - 0.22, y0 + h + 0.1, 0.44, 0.4, round_=0.08)
    if cab:
        cy = y0 + h / 2
        r(ax, x0 - 0.5, cy - 0.22, 0.4, 0.44, round_=0.08)
        r(ax, x0 + w + 0.1, cy - 0.22, 0.4, 0.44, round_=0.08)


def vaso(ax, x, y, ang=0):
    ax.add_patch(FancyBboxPatch((x - 0.2, y - 0.25), 0.4, 0.5, boxstyle="round,pad=0,rounding_size=0.18",
                                fc="white", ec=COR["movel"], lw=0.6))
    r(ax, x - 0.22, y + 0.25, 0.44, 0.15)


def pia(ax, x, y, w=0.5, h=0.4):
    r(ax, x, y, w, h, round_=0.1)


def mobilia(ax):
    # garagem: 2 carros
    for x in (2.1, 4.9):
        r(ax, x, 5.4, 1.9, 4.4, fc="#F4F4F4", round_=0.4, lw=0.8)
        r(ax, x + 0.25, 7.6, 1.4, 1.0, fc="#DCE6EE", round_=0.2, lw=0.4)
    # lavanderia: lava e seca, tanque, ducha pet
    for x in (1.6, 2.3):
        r(ax, x, 12.3, 0.65, 0.65, round_=0.05)
        ax.add_patch(Circle((x + 0.32, 12.62), 0.22, fc="none", ec=COR["movel"], lw=0.5))
    r(ax, 3.1, 12.4, 0.8, 0.55); r(ax, 3.2, 12.48, 0.6, 0.38, round_=0.1)
    r(ax, 3.4, 10.6, 1.1, 0.9, fc="#D6E8F5", ec="#3D7CB8")
    ax.text(3.95, 11.05, "ducha\npet", ha="center", va="center", fontsize=4.8, color="#235A8C")
    # lavabo
    vaso(ax, 6.0, 10.85); pia(ax, 5.7, 12.2, 0.45, 0.55)
    # cozinha
    r(ax, 1.6, 13.75, 0.6, 3.15, fc="#F7F7F7")
    pia(ax, 1.65, 14.3, 0.5, 0.7)
    for y in (15.7, 16.2):
        ax.add_patch(Circle((1.9, y + 0.2), 0.15, fc="none", ec=COR["movel"], lw=0.5))
    r(ax, 1.6, 13.1, 2.4, 0.6, fc="#F7F7F7")
    ax.text(2.8, 13.4, "torre + geladeira", ha="center", va="center", fontsize=4.3)
    r(ax, 3.3, 14.6, 2.6, 1.0, fc="#FFFFFF", lw=0.9)
    for x in (3.6, 4.4, 5.2):
        ax.add_patch(Circle((x + 0.15, 16.0), 0.2, fc="white", ec=COR["movel"], lw=0.5))
    ax.text(4.6, 15.1, "ilha", ha="center", va="center", fontsize=5)
    # varanda gourmet
    r(ax, 1.6, 17.1, 3.6, 0.6, fc="#F7F7F7")
    r(ax, 1.6, 17.1, 1.0, 0.6, fc="#C9B8A6")
    ax.text(2.1, 17.4, "churrasq.", ha="center", va="center", fontsize=4.5)
    pia(ax, 3.4, 17.15, 0.6, 0.45)
    r(ax, 2.8, 18.9, 1.0, 2.2, fc="#F2E3CF", lw=0.8)
    cadeiras(ax, 2.8, 18.9, 1.0, 2.2, 1, cab=False)
    for y in (19.1, 19.75, 20.4):
        r(ax, 2.3, y, 0.4, 0.44, round_=0.08); r(ax, 3.9, y, 0.4, 0.44, round_=0.08)
    # sala de estar (a porta da frente abre direto aqui)
    r(ax, 7.6, 5.1, 0.4, 3.0, fc="#E9DDF3", ec="#7D5BA6")
    ax.text(7.8, 6.6, "vitrine", rotation=90, ha="center", va="center", fontsize=4.5, color="#5A3E80")
    r(ax, 11.0, 5.15, 2.8, 0.9, fc="#C9D7E3", round_=0.15)          # sofá
    r(ax, 11.7, 6.45, 1.4, 0.7, fc="#F2E3CF", round_=0.1)           # centro
    r(ax, 11.2, 7.55, 0.75, 0.75, fc="#C9D7E3", round_=0.2)         # poltronas
    r(ax, 12.85, 7.55, 0.75, 0.75, fc="#C9D7E3", round_=0.2)
    # galeria: estante de jogos ao longo da parede
    r(ax, 7.55, 9.1, 0.35, 2.6, fc="#D3C0E8", ec="#7D5BA6")
    r(ax, 7.55, 12.6, 0.35, 1.3, fc="#D3C0E8", ec="#7D5BA6")
    # sala de jogos
    r(ax, 9.1, 13.55, 4.1, 0.4, fc="#D3C0E8", ec="#7D5BA6")
    r(ax, 12.85, 9.1, 0.4, 4.4, fc="#D3C0E8", ec="#7D5BA6")
    ax.text(11.0, 13.75, "estantes da coleção (~300 caixas)", ha="center", va="center", fontsize=4.6, color="#5A3E80")
    r(ax, 9.9, 10.85, 2.2, 1.2, fc="#5E8C61", ec="#3A5A3C", lw=0.9)
    r(ax, 10.05, 11.0, 1.9, 0.9, fc="#7FB083", ec="none")
    cadeiras(ax, 9.9, 10.85, 2.2, 1.2, 2)
    # estar / jantar
    r(ax, 9.4, 15.0, 2.2, 1.0, fc="#F2E3CF", lw=0.8)
    cadeiras(ax, 9.4, 15.0, 2.2, 1.0, 3)
    r(ax, 10.0, 18.3, 0.9, 3.0, fc="#C9D7E3", round_=0.15)          # sofá virado para a TV
    r(ax, 10.0, 20.4, 1.9, 0.9, fc="#C9D7E3", round_=0.15)          # chaise
    r(ax, 11.25, 18.9, 0.8, 1.2, fc="#F2E3CF", round_=0.1)
    r(ax, 11.4, 17.2, 0.7, 0.7, fc="#C9D7E3", round_=0.2)           # poltrona
    r(ax, 12.85, 18.2, 0.35, 2.6, fc="#555555")
    # home office
    r(ax, 15.0, 5.1, 2.4, 0.7, fc="#F2E3CF")
    r(ax, 15.9, 5.95, 0.6, 0.55, round_=0.2)
    r(ax, 17.7, 5.6, 0.7, 2.7, fc="#C9D7E3", round_=0.15)
    ax.text(18.05, 6.95, "sofá-cama", rotation=90, ha="center", va="center", fontsize=4.5)
    r(ax, 15.2, 8.55, 2.0, 0.4, fc="#E2F0DA")
    # banho social
    pia(ax, 15.7, 9.1, 0.6, 0.42); pia(ax, 16.4, 9.1, 0.6, 0.42)
    vaso(ax, 18.1, 9.5)
    r(ax, 17.0, 9.9, 1.4, 1.0, fc="#D6E8F5", ec="#3D7CB8")
    # quarto da filha
    r(ax, 17.4, 11.8, 1.0, 2.0, fc="white", lw=0.8); r(ax, 17.5, 13.35, 0.8, 0.35, round_=0.1)
    r(ax, 14.7, 13.8, 2.2, 0.55, fc="#F7F7F7")
    r(ax, 15.8, 11.1, 1.4, 0.55, fc="#F2E3CF")
    ax.add_patch(Circle((15.6, 12.7), 0.55, fc="#FCE4EC", ec="#D48BA4", lw=0.6))
    # closet
    r(ax, 14.55, 14.5, 0.45, 2.9, fc="#F7F7F7"); r(ax, 15.75, 14.5, 0.4, 2.1, fc="#F7F7F7")
    # banho suíte
    pia(ax, 16.3, 14.5, 0.42, 0.6); pia(ax, 16.3, 15.2, 0.42, 0.6)
    r(ax, 17.3, 14.5, 1.1, 1.5, fc="#D6E8F5", ec="#3D7CB8")
    vaso(ax, 18.05, 16.7)
    # suíte do casal
    r(ax, 16.4, 18.7, 2.0, 2.0, fc="white", lw=0.9)
    r(ax, 17.95, 18.85, 0.35, 0.75, round_=0.1); r(ax, 17.95, 19.8, 0.35, 0.75, round_=0.1)
    r(ax, 17.9, 18.15, 0.45, 0.45); r(ax, 17.9, 20.8, 0.45, 0.45)
    r(ax, 13.5, 20.0, 1.0, 1.0, fc="#C9D7E3", round_=0.15)



def porta(ax, x, y, w, orient, abre=1, giro=1):
    """orient 'h' = porta em parede horizontal, 'v' = parede vertical. abre = lado (+1/-1)."""
    if orient == "h":
        ax.plot([x, x + w], [y, y], color="white", lw=3.6, solid_capstyle="butt", zorder=5)
        hx = x if giro > 0 else x + w
        ax.plot([hx, hx], [y, y + abre * w], color="#333", lw=0.8, zorder=6)
        t1, t2 = (0, 90) if (giro > 0 and abre > 0) else (90, 180) if (giro < 0 and abre > 0) else (270, 360) if giro > 0 else (180, 270)
        ax.add_patch(Arc((hx, y), 2 * w, 2 * w, theta1=t1, theta2=t2, color="#333", lw=0.5, zorder=6))
    else:
        ax.plot([x, x], [y, y + w], color="white", lw=3.6, solid_capstyle="butt", zorder=5)
        hy = y if giro > 0 else y + w
        ax.plot([x, x + abre * w], [hy, hy], color="#333", lw=0.8, zorder=6)
        t1, t2 = (0, 90) if (giro > 0 and abre > 0) else (270, 360) if (giro < 0 and abre > 0) else (90, 180) if giro > 0 else (180, 270)
        ax.add_patch(Arc((x, hy), 2 * w, 2 * w, theta1=t1, theta2=t2, color="#333", lw=0.5, zorder=6))


def vao(ax, x0, y0, x1, y1, correr=False):
    ax.plot([x0, x1], [y0, y1], color="white", lw=3.8, solid_capstyle="butt", zorder=5)
    if correr:
        dx, dy = (0, 0.06) if y0 == y1 else (0.06, 0)
        ax.plot([x0, (x0 + x1) / 2 + 0.2 * (x1 != x0)], [y0 - dy, (y0 + y1) / 2 - dy + 0.2 * (y1 != y0)], color="#3D7CB8", lw=1.0, zorder=6)
        ax.plot([(x0 + x1) / 2 - 0.2 * (x1 != x0), x1], [(y0 + y1) / 2 + dy - 0.2 * (y1 != y0), y1 + dy], color="#3D7CB8", lw=1.0, zorder=6)


def portas(ax):
    porta(ax, 9.6, 5.0, 1.2, "h", abre=1)                  # entrada social (pivotante)
    vao(ax, 2.0, 5.0, 7.0, 5.0)                            # portão garagem
    ax.plot([2.0, 7.0], [5.0, 5.0], color="#888", lw=0.8, ls="--", zorder=6)
    porta(ax, 4.6, 10.5, 0.8, "h", abre=1)                 # garagem -> lavanderia
    porta(ax, 1.5, 10.8, 0.9, "v", abre=1)                 # lavanderia -> corredor pet
    porta(ax, 4.6, 13.0, 0.8, "h", abre=1)                 # lavanderia -> cozinha
    porta(ax, 7.5, 11.8, 0.7, "v", abre=-1)                # lavabo (abre da galeria)
    vao(ax, 7.6, 9.0, 8.9, 9.0)                            # sala de estar -> galeria
    vao(ax, 9.2, 9.0, 13.1, 9.0, correr=True)              # vidro fixo sala de estar | sala de jogos
    vao(ax, 9.0, 10.0, 9.0, 13.4, correr=True)             # galeria -> sala de jogos (correr)
    vao(ax, 7.6, 14.0, 8.9, 14.0)                          # galeria -> estar/jantar
    vao(ax, 7.5, 14.1, 7.5, 16.9)                          # cozinha aberta p/ jantar
    vao(ax, 4.0, 17.0, 7.0, 17.0)                          # passa-pratos cozinha -> gourmet
    vao(ax, 7.5, 17.4, 7.5, 21.6, correr=True)             # estar -> gourmet
    porta(ax, 14.5, 7.9, 0.9, "v", abre=1)                 # office (porta no canto da sala)
    vao(ax, 13.35, 9.0, 14.45, 9.0)                        # sala de estar -> corredor íntimo
    porta(ax, 14.5, 9.3, 0.7, "v", abre=1)                 # banho social
    porta(ax, 14.5, 11.3, 0.8, "v", abre=1)                # quarto da filha
    porta(ax, 13.4, 17.5, 0.85, "h", abre=1)               # SUÍTE: corredor -> quarto
    porta(ax, 15.0, 17.5, 0.75, "h", abre=-1)              # quarto -> closet
    porta(ax, 16.4, 17.5, 0.7, "h", abre=-1, giro=-1)      # quarto -> banho suíte
    # fundo: aberto para o deck
    vao(ax, 1.6, 22.0, 7.4, 22.0)
    for x in (1.5, 4.5, 7.5):
        ax.add_patch(Rectangle((x - 0.15, 21.85), 0.3, 0.3, fc="#2B2B2B", zorder=7))
    vao(ax, 8.0, 22.0, 12.8, 22.0, correr=True)            # estar -> deck
    vao(ax, 13.8, 22.0, 17.8, 22.0, correr=True)           # suíte -> deck



def janela(ax, x0, y0, x1, y1):
    ax.plot([x0, x1], [y0, y1], color="white", lw=3.8, solid_capstyle="butt", zorder=5)
    off = 0.07
    if y0 == y1:
        for d in (-off, off):
            ax.plot([x0, x1], [y0 + d, y1 + d], color="#3D7CB8", lw=0.7, zorder=6)
    else:
        for d in (-off, off):
            ax.plot([x0 + d, x1 + d], [y0, y1], color="#3D7CB8", lw=0.7, zorder=6)


def janelas(ax):
    janela(ax, 14.9, 5.0, 18.0, 5.0)      # office frente
    janela(ax, 11.2, 5.0, 12.2, 5.0)      # sala de estar
    janela(ax, 13.0, 5.0, 14.0, 5.0)      # sala de estar
    janela(ax, 18.5, 5.8, 18.5, 7.6)      # office lateral
    janela(ax, 18.5, 9.0, 18.5, 10.2)     # banho
    janela(ax, 18.5, 11.4, 18.5, 13.8)    # quarto filha
    janela(ax, 18.5, 14.9, 18.5, 15.9)    # banho suíte
    janela(ax, 18.5, 18.2, 18.5, 21.2)    # suíte lateral
    janela(ax, 1.5, 13.6, 1.5, 15.9)      # cozinha
    janela(ax, 1.5, 7.0, 1.5, 9.0)        # garagem ventilação
    ax.add_patch(Rectangle((9.7, 10.0), 2.8, 2.8, fc="none", ec="#3D7CB8", lw=0.6, ls=":", zorder=6))
    ax.text(11.1, 12.55, "claraboia", ha="center", fontsize=4.6, color="#235A8C", zorder=7)



def cota(ax, x0, y0, x1, y1, txt, off=0.0):
    ax.annotate("", xy=(x0, y0), xytext=(x1, y1), arrowprops=dict(arrowstyle="<->", lw=0.6, color="#444"))
    ax.text((x0 + x1) / 2 + (off if x0 == x1 else 0), (y0 + y1) / 2 + (0.25 if y0 == y1 else 0), txt,
            ha="center", va="center", fontsize=6.5, color="#333", rotation=90 if x0 == x1 else 0,
            bbox=dict(fc="white", ec="none", pad=0.5))


def cotas(ax):
    W, H = LOTE
    cota(ax, 0, H + 0.5, W, H + 0.5, "20,00 m (lote)")
    cota(ax, -0.7, 0, -0.7, H, "30,00 m (lote)")
    cota(ax, 20.6, 0, 20.6, 5, "recuo 5,0", off=0)
    cota(ax, 20.6, 5, 20.6, 22, "casa 17,0 m")
    cota(ax, 20.6, 22, 20.6, 30, "quintal 8,0 m")
    cota(ax, 1.5, 24.5, 18.5, 24.5, "17,0 m")


def quadro(ax):
    ax.axis("off")
    ar = areas()
    total = sum(ar.values())
    gourmet = ar["Varanda gourmet"]
    ordem = ["Sala de estar", "Galeria", "Lavabo", "Jantar / TV", "Cozinha", "Varanda gourmet", "Sala de jogos",
             "Home office (+ hóspedes)", "Circulação íntima", "Banho", "Quarto da filha", "Closet",
             "Banho suíte", "Suíte do casal", "Garagem 2 carros", "Lavanderia + ducha pet"]
    linhas = [(n, f"{ar[n]:.1f}") for n in ordem]
    y = 0.97
    ax.text(0, y, "QUADRO DE ÁREAS", fontsize=11, weight="bold"); y -= 0.045
    for n, a in linhas:
        ax.text(0.0, y, n, fontsize=8.5); ax.text(0.95, y, a + " m²", fontsize=8.5, ha="right"); y -= 0.027
    ax.plot([0, 0.95], [y + 0.015, y + 0.015], color="#333", lw=0.6)
    ax.text(0.0, y - 0.01, "Área construída (sem paredes)", fontsize=8.5, weight="bold")
    ax.text(0.95, y - 0.01, f"{total:.0f} m²", fontsize=8.5, ha="right", weight="bold"); y -= 0.035
    ax.text(0.0, y - 0.01, "Com paredes (~ +8%)", fontsize=8.5)
    ax.text(0.95, y - 0.01, f"~{total * 1.08:.0f} m²", fontsize=8.5, ha="right"); y -= 0.035
    ax.text(0.0, y - 0.01, "Taxa de ocupação do lote", fontsize=8.5)
    ax.text(0.95, y - 0.01, f"{17 * 17 / 600 * 100:.0f}%", fontsize=8.5, ha="right"); y -= 0.06
    ax.text(0, y, "LEGENDA", fontsize=10, weight="bold"); y -= 0.04
    for z, nome in [("social", "Social / receber"), ("jogos", "Sala de jogos"), ("trabalho", "Trabalho"),
                    ("intimo", "Íntimo"), ("servico", "Serviço / banhos"), ("varanda", "Varanda gourmet")]:
        ax.add_patch(Rectangle((0, y - 0.008), 0.06, 0.022, fc=COR[z], ec="#333", lw=0.5, transform=ax.transAxes))
        ax.text(0.09, y, nome, fontsize=8.5, va="bottom"); y -= 0.026
    y -= 0.03
    ax.text(0, y, "PREMISSAS (a confirmar)", fontsize=10, weight="bold"); y -= 0.035
    for t in ["Lote 20 x 30 m, plano", "Recuos: frente 5 m, laterais 1,5 m,", "   fundo 3 m (ver regulamento)",
              "Casa térrea, pé-direito 3,0 m", "Norte ainda desconhecido", "Estudo de layout, não é projeto", "   legal nem executivo"]:
        ax.text(0, y, t, fontsize=8); y -= 0.024
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)


def main():
    fig = plt.figure(figsize=(16.54, 11.69))   # A3 deitado
    ax = fig.add_axes([0.02, 0.03, 0.70, 0.90])
    desenha(ax)
    fig.text(0.02, 0.955, "CASA TÉRREA EM CONDOMÍNIO  ·  LOTE 600 m²", fontsize=17, weight="bold")
    fig.text(0.02, 0.935, "Estudo preliminar de layout — suíte do casal, quarto da filha, home office, sala de jogos, "
             "área de receber, espaço de brincar e espaço do cachorro", fontsize=9.5, color="#444")
    q = fig.add_axes([0.74, 0.05, 0.24, 0.85])
    quadro(q)
    fig.savefig(os.path.join(OUT, "planta.png"), dpi=170)
    with PdfPages(os.path.join(OUT, "planta.pdf")) as pdf:
        pdf.savefig(fig)
    print({k: round(v, 1) for k, v in areas().items()}, round(sum(areas().values()), 1))


if __name__ == "__main__":
    main()
