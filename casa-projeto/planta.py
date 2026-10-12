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
    ("Lavanderia\n+ ducha pet",    1.5, 10.5,  5.5, 13.0, "servico"),
    ("Lavabo",                     5.5, 10.5,  7.5, 13.0, "servico"),
    ("Cozinha",                    1.5, 13.0,  7.5, 18.0, "social"),
    ("Sala de estar",              7.5,  5.0, 13.0, 10.5, "social"),
    ("Jantar + jogos",             7.5, 10.5, 13.0, 18.0, "social"),
    ("Varanda gourmet",            1.5, 18.0, 13.0, 22.0, "varanda"),
    ("Home office\n(+ hóspedes)", 13.0,  5.0, 18.5,  9.0, "trabalho"),
    ("",                          13.0,  9.0, 14.2, 18.0, "intimo"),   # corredor íntimo
    ("Banho",                     14.2,  9.0, 18.5, 11.3, "servico"),
    ("Quarto da filha",           14.2, 11.3, 18.5, 14.7, "intimo"),
    ("Closet",                    14.2, 14.7, 16.0, 18.0, "intimo"),
    ("Banho suíte",               16.0, 14.7, 18.5, 18.0, "servico"),
    ("Suíte do casal",            13.0, 18.0, 18.5, 22.0, "intimo"),
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
    ax.add_patch(Rectangle((11.5, -1.6), 1.3, 6.6, fc=COR["piso"], ec="#B9AE98", lw=0.6))    # caminho
    ax.add_patch(Rectangle((7.5, 3.3), 5.5, 1.7, fc=COR["deck"], ec="#9C7A4C", lw=0.6))     # varanda de entrada
    ax.text(9.6, 4.15, "varanda de entrada", ha="center", va="center", fontsize=6, color="#5E4626")
    ax.add_patch(Rectangle((0, 10.5), 1.5, 11.5, fc=COR["piso"], ec="#B9AE98", lw=0.6))     # corredor pet
    for xx in (0.35, 0.65, 0.95, 1.25):                                                          # varal
        ax.plot([xx, xx], [12.4, 21.4], color="#8A8A8A", lw=0.6, ls=(0, (3, 2)))
    for yy in (12.4, 21.4):
        ax.plot([0.2, 1.4], [yy, yy], color="#6E4A22", lw=1.6)
    ax.text(0.75, 16.9, "VARAL / SERVIÇO", rotation=90, ha="center", va="center", fontsize=6.3, color="#555",
            weight="bold", bbox=dict(fc=COR["piso"], ec="none", pad=0.8))
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
    for (x0, y0, x1, y1) in [(0, 10.5, 1.5, 10.5), (18.5, 8.5, 20, 8.5), (0, 22.0, 1.5, 22.0)]:
        ax.plot([x0, x1], [y0, y1], color="#C0504D", lw=2.4)
    ax.text(0.75, 10.0, "portão", ha="center", fontsize=5.5, color="#C0504D")
    ax.text(0.75, 22.25, "portão", ha="center", fontsize=5.5, color="#C0504D")
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
    L = [(7.6, 5.1), (12.9, 5.1), (12.9, 17.9), (1.6, 17.9), (1.6, 13.1), (7.6, 13.1), (7.6, 5.1)]
    ax.plot(*zip(*L), color="#C2702E", lw=1.3, ls=(0, (6, 3)), zorder=8)
    ar = areas()
    tot_L = ar["Sala de estar"] + ar["Jantar + jogos"] + ar["Cozinha"]
    ax.text(10.6, 11.3, f"SALA INTEGRADA EM L\n{tot_L:.0f} m² sem paredes", ha="center", va="center", fontsize=6.8,
            weight="bold", color="#9A4F14", zorder=9, bbox=dict(fc="#FFF6EA", ec="#C2702E", lw=0.8, pad=1.5))
    ax.annotate("", xy=(6.6, 14.2), xytext=(8.15, 9.9), zorder=9,
                arrowprops=dict(arrowstyle="-|>", color="#C2702E", lw=1.1, ls="--",
                                connectionstyle="angle,angleA=90,angleB=0,rad=0.6"))
    ax.text(8.25, 12.4, "circulação livre\nsala → cozinha", rotation=90, ha="center", va="center", fontsize=4.8,
            color="#9A4F14", zorder=9)
    cotas(ax)



ROTULO = {
    "Garagem 2 carros": (4.5, 9.6), "Lavanderia + ducha pet": (3.5, 11.9), "Lavabo": (6.6, 11.5),
    "Cozinha": (3.6, 17.3), "Sala de estar": (11.6, 9.6), "Jantar + jogos": (10.8, 17.3),
    "Varanda gourmet": (5.6, 21.3), "Home office (+ hóspedes)": (15.4, 7.6), "Banho": (15.4, 10.4),
    "Quarto da filha": (15.8, 12.7), "Closet": (15.1, 16.8), "Banho suíte": (17.4, 17.4),
    "Suíte do casal": (15.0, 21.3),
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
    for x in (2.7, 3.4):
        r(ax, x, 12.3, 0.65, 0.65, round_=0.05)
        ax.add_patch(Circle((x + 0.32, 12.62), 0.22, fc="none", ec=COR["movel"], lw=0.5))
    r(ax, 4.15, 12.4, 0.8, 0.55); r(ax, 4.25, 12.48, 0.6, 0.38, round_=0.1)
    r(ax, 2.6, 10.6, 1.1, 0.9, fc="#D6E8F5", ec="#3D7CB8")
    ax.text(3.15, 11.05, "ducha\npet", ha="center", va="center", fontsize=4.8, color="#235A8C")
    # lavabo
    vaso(ax, 6.0, 12.55); pia(ax, 6.85, 10.6, 0.55, 0.45)
    # cozinha: bancada na parede, torre + geladeira, ilha virada para o jantar
    r(ax, 1.6, 13.8, 0.6, 4.1, fc="#F7F7F7")
    pia(ax, 1.65, 14.5, 0.5, 0.7)
    for y in (16.0, 16.5):
        ax.add_patch(Circle((1.9, y + 0.2), 0.15, fc="none", ec=COR["movel"], lw=0.5))
    r(ax, 2.7, 13.1, 2.4, 0.6, fc="#F7F7F7")
    ax.text(3.9, 13.4, "torre + geladeira", ha="center", va="center", fontsize=4.3)
    r(ax, 4.9, 14.4, 1.0, 2.6, fc="#FFFFFF", lw=0.9)
    ax.text(5.4, 15.7, "ilha", ha="center", va="center", fontsize=5, rotation=90)
    for y in (14.7, 15.5, 16.3):
        ax.add_patch(Circle((6.3, y + 0.15), 0.2, fc="white", ec=COR["movel"], lw=0.5))
    # sala de estar: TV na parede da garagem, sofá em L
    r(ax, 7.55, 6.4, 0.35, 2.6, fc="#555555")
    r(ax, 9.9, 6.0, 0.9, 3.4, fc="#C9D7E3", round_=0.15)
    r(ax, 8.4, 8.5, 1.5, 0.9, fc="#C9D7E3", round_=0.15)
    r(ax, 8.55, 6.7, 0.9, 1.2, fc="#F2E3CF", round_=0.1)
    # jantar + jogos: UMA mesa grande (jantar e jogatina) e a parede de jogos
    r(ax, 12.55, 10.6, 0.4, 7.3, fc="#D3C0E8", ec="#7D5BA6")
    ax.text(12.75, 14.25, "estante da coleção (~350 jogos)", rotation=90, ha="center", va="center", fontsize=4.6,
            color="#5A3E80")
    r(ax, 10.1, 12.4, 1.2, 3.0, fc="#5E8C61", ec="#3A5A3C", lw=0.9)
    r(ax, 10.2, 12.5, 1.0, 2.8, fc="#C9A57A", ec="none")
    for k in range(4):
        y = 12.55 + k * 0.75
        r(ax, 9.6, y, 0.4, 0.44, round_=0.08); r(ax, 11.4, y, 0.4, 0.44, round_=0.08)
    r(ax, 10.48, 11.9, 0.44, 0.4, round_=0.08); r(ax, 10.48, 15.5, 0.44, 0.4, round_=0.08)
    ax.text(10.7, 13.9, "mesa 10 lugares\n(jantar e jogos)", ha="center", va="center", fontsize=4.6, color="white",
            rotation=90)
    # varanda gourmet: churrasqueira, pia, balcão com banquetas (sem mesa) e sofá externo
    r(ax, 1.6, 18.2, 0.7, 1.4, fc="#C9B8A6")
    ax.text(1.95, 18.9, "churrasq.", rotation=90, ha="center", va="center", fontsize=4.5)
    r(ax, 1.6, 19.7, 0.6, 2.1, fc="#F7F7F7"); pia(ax, 1.65, 20.4, 0.5, 0.6)
    r(ax, 3.5, 18.05, 3.8, 0.45, fc="#F7F7F7")
    ax.text(5.4, 18.27, "balcão (passa-pratos)", ha="center", va="center", fontsize=4.3)
    for x in (3.8, 4.6, 5.4, 6.2, 7.0):
        ax.add_patch(Circle((x, 18.85), 0.19, fc="white", ec=COR["movel"], lw=0.5))
    r(ax, 12.0, 18.6, 0.9, 2.9, fc="#C9D7E3", round_=0.15)
    r(ax, 9.6, 19.0, 0.8, 0.8, fc="#C9D7E3", round_=0.2); r(ax, 9.6, 20.4, 0.8, 0.8, fc="#C9D7E3", round_=0.2)
    # home office
    r(ax, 14.8, 5.1, 2.4, 0.7, fc="#F2E3CF")
    r(ax, 15.7, 5.95, 0.6, 0.55, round_=0.2)
    r(ax, 17.7, 5.6, 0.7, 2.8, fc="#C9D7E3", round_=0.15)
    ax.text(18.05, 7.0, "sofá-cama", rotation=90, ha="center", va="center", fontsize=4.5)
    r(ax, 14.4, 8.55, 2.0, 0.4, fc="#E2F0DA")
    # banho social
    pia(ax, 15.4, 9.1, 0.6, 0.42); pia(ax, 16.1, 9.1, 0.6, 0.42)
    vaso(ax, 18.1, 9.5)
    r(ax, 17.0, 10.1, 1.4, 1.1, fc="#D6E8F5", ec="#3D7CB8")
    # quarto da filha: cama, guarda-roupa, cantinho de brincar (sem escrivaninha)
    r(ax, 17.4, 12.0, 1.0, 2.0, fc="white", lw=0.8); r(ax, 17.5, 13.55, 0.8, 0.35, round_=0.1)
    r(ax, 14.4, 14.1, 2.2, 0.55, fc="#F7F7F7")
    ax.add_patch(Circle((15.6, 12.6), 0.65, fc="#FCE4EC", ec="#D48BA4", lw=0.6))
    ax.text(15.6, 12.6, "brincar", ha="center", va="center", fontsize=4.6)
    # closet
    r(ax, 14.25, 14.8, 0.45, 3.1, fc="#F7F7F7"); r(ax, 15.55, 14.8, 0.4, 2.2, fc="#F7F7F7")
    # banho suíte
    pia(ax, 16.05, 14.8, 0.42, 0.6); pia(ax, 16.05, 15.55, 0.42, 0.6)
    r(ax, 17.3, 14.8, 1.1, 1.5, fc="#D6E8F5", ec="#3D7CB8")
    vaso(ax, 18.05, 17.2)
    # suíte do casal
    r(ax, 16.4, 19.0, 2.0, 2.0, fc="white", lw=0.9)
    r(ax, 17.95, 19.15, 0.35, 0.75, round_=0.1); r(ax, 17.95, 20.1, 0.35, 0.75, round_=0.1)
    r(ax, 17.9, 18.45, 0.45, 0.45); r(ax, 17.9, 21.1, 0.45, 0.45)
    r(ax, 13.4, 20.6, 0.9, 0.9, fc="#C9D7E3", round_=0.15)



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
    porta(ax, 11.6, 5.0, 1.1, "h", abre=1, giro=-1)        # entrada: abre direto na sala de estar
    vao(ax, 2.0, 5.0, 7.0, 5.0)                            # portão garagem
    ax.plot([2.0, 7.0], [5.0, 5.0], color="#888", lw=0.8, ls="--", zorder=6)
    porta(ax, 4.4, 10.5, 0.8, "h", abre=1)                 # garagem -> lavanderia
    porta(ax, 1.5, 10.7, 0.9, "v", abre=1)                 # lavanderia -> corredor pet
    porta(ax, 1.7, 13.0, 0.8, "h", abre=1)                 # lavanderia -> cozinha
    porta(ax, 7.5, 11.2, 0.7, "v", abre=-1)                # lavabo (abre do jantar)
    vao(ax, 7.6, 10.5, 12.9, 10.5)                         # sala de estar aberta para o jantar (L integrado)
    vao(ax, 7.5, 13.1, 7.5, 17.9)                          # cozinha aberta para o jantar
    vao(ax, 3.5, 18.0, 7.4, 18.0)                          # balcão cozinha -> gourmet
    vao(ax, 7.6, 18.0, 12.9, 18.0, correr=True)            # jantar -> gourmet (vidro de correr)
    porta(ax, 13.0, 7.9, 0.9, "v", abre=1)                 # home office (da sala)
    vao(ax, 13.0, 9.1, 13.0, 10.4)                         # sala -> corredor íntimo
    porta(ax, 14.2, 9.3, 0.7, "v", abre=1)                 # banho social
    porta(ax, 14.2, 11.6, 0.8, "v", abre=1)                # quarto da filha
    porta(ax, 13.1, 18.0, 0.85, "h", abre=1)               # SUÍTE: corredor -> quarto
    porta(ax, 14.75, 18.0, 0.75, "h", abre=-1)             # quarto -> closet
    porta(ax, 16.3, 18.0, 0.7, "h", abre=-1)               # quarto -> banho suíte
    # gourmet aberta para o deck (pilares)
    vao(ax, 1.6, 22.0, 12.9, 22.0)
    for x in (1.5, 4.5, 7.5, 10.25, 13.0):
        ax.add_patch(Rectangle((x - 0.15, 21.85), 0.3, 0.3, fc="#2B2B2B", zorder=7))
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
    janela(ax, 8.2, 5.0, 9.3, 5.0); janela(ax, 9.5, 5.0, 10.6, 5.0)   # sala de estar
    janela(ax, 14.6, 5.0, 17.9, 5.0)      # office frente
    janela(ax, 18.5, 5.8, 18.5, 8.0)      # office lateral
    janela(ax, 18.5, 9.6, 18.5, 10.8)     # banho
    janela(ax, 18.5, 11.8, 18.5, 14.2)    # quarto filha
    janela(ax, 18.5, 14.9, 18.5, 16.2)    # banho suíte
    janela(ax, 18.5, 18.6, 18.5, 21.4)    # suíte lateral
    janela(ax, 1.5, 14.0, 1.5, 16.5)      # cozinha
    janela(ax, 1.5, 7.0, 1.5, 9.0)        # garagem ventilação



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
    ordem = ["Sala de estar", "Jantar + jogos", "Cozinha", "Varanda gourmet", "Lavabo",
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
    for z, nome in [("social", "Sala integrada em L"), ("trabalho", "Trabalho"),
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
    fig.text(0.02, 0.935, "Estudo preliminar de layout (versão 3) — sala integrada em L, suíte do casal, quarto da filha, home office, sala de jogos, "
             "área de receber, espaço de brincar e espaço do cachorro", fontsize=9.5, color="#444")
    q = fig.add_axes([0.74, 0.05, 0.24, 0.85])
    quadro(q)
    fig.savefig(os.path.join(OUT, "planta.png"), dpi=170)
    with PdfPages(os.path.join(OUT, "planta.pdf")) as pdf:
        pdf.savefig(fig)
    print({k: round(v, 1) for k, v in areas().items()}, round(sum(areas().values()), 1))


if __name__ == "__main__":
    main()
