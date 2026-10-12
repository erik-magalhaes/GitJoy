"""Planta 3D (casa de bonecas): casa sem telhado, paredes cortadas a ~2,5 m e mobiliada.

  blender -b -P interior3d.py -- <camera> <amostras> <saida.png> [largura altura]
Câmeras: planta3d (frente/esquerda), planta3d_fundo (fundos/direita), topo.
Usa os materiais e o terreno de casa3d.py; coordenadas iguais às de planta.py.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import casa3d as C
from casa3d import M, box, lin, novo_mat, madeira, piso_pavers, liso

random.seed(11)
F = 0.32                 # nível do piso acabado
H = F + 2.0              # altura do corte das paredes
EXT, INT = 0.2, 0.12     # espessuras


# ----------------------------------------------------------------- materiais extras
def vidro_claro():
    m, nt, b = novo_mat("vidro_claro")
    b.inputs["Base Color"].default_value = (0.9, 0.95, 1.0, 1)
    b.inputs["Roughness"].default_value = 0.0
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = 1.45
    return m


M.update(
    parede=liso("parede", "#F3F0E9", 0.85),
    corte=liso("corte", "#3A3A3A", 0.9),
    assoalho=madeira("assoalho", "#9C6B43", "#C08A5A", "X", 0.18),
    piso_social=piso_pavers("piso_social", "#E4DED3", "#DDD6CA", 1.2, 0.6),
    piso_banho=piso_pavers("piso_banho", "#D9D9D6", "#CFCFCB", 0.6, 0.6),
    cimento=liso("cimento", "#9C9C98", 0.8),
    vidro_c=vidro_claro(),
    marcenaria=madeira("marcenaria", "#B08458", "#C99A68", "Y", 0.6),
    quartzo=liso("quartzo", "#EDEBE6", 0.25),
    sofa=liso("sofa", "#7F8A93", 0.95),
    sofa2=liso("sofa2", "#C9BBA3", 0.95),
    feltro=liso("feltro", "#2F6B45", 1.0),
    inox=liso("inox", "#C8CACC", 0.25, 1.0),
    loucas=liso("loucas", "#FAFAFA", 0.15),
    rosa=liso("rosa", "#E8A9B8", 0.9),
    lilas=liso("lilas", "#B9A6D9", 0.9),
    tapete=liso("tapete", "#BFB1A0", 1.0),
    tapete2=liso("tapete2", "#8D9AA6", 1.0),
    lencol=liso("lencol", "#F7F5F0", 0.9),
    edredom=liso("edredom", "#5E7A8C", 0.95),
    carro1=liso("carro1", "#24344F", 0.2, 0.6),
    carro2=liso("carro2", "#B9BCC0", 0.25, 0.8),
    pneu=liso("pneu", "#1B1B1B", 0.8),
    tela=liso("tela", "#0E0F12", 0.1),
)
CORES_JOGOS = ["#C0392B", "#2471A3", "#F1C40F", "#27AE60", "#8E44AD", "#E67E22", "#16A085", "#2C3E50",
               "#D35400", "#F39C12", "#1ABC9C", "#7D3C98", "#A93226", "#F4D03F", "#5DADE2", "#EC7063",
               "#45B39D", "#F5B041", "#283747", "#FDFEFE"]
MAT_JOGOS = [liso(f"jogo{i}", c, 0.45) for i, c in enumerate(CORES_JOGOS)]


def macio(o, w=0.03, seg=3):
    md = o.modifiers.new("bev", "BEVEL"); md.width = w; md.segments = seg; md.limit_method = "ANGLE"
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def bf(x0, x1, y0, y1, z0, z1, mat, nome="movel", bev=0.0):
    o = box(x0, x1, y0, y1, F + z0, F + z1, mat, nome)
    if bev:
        macio(o, bev)
    return o


def cilindro(x, y, z0, z1, r, mat, verts=24, eixo="z"):
    if eixo == "z":
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0, location=(x, y, 0),
                                            rotation=(0, math.pi / 2, 0) if eixo == "x" else (math.pi / 2, 0, 0))
    o = bpy.context.active_object
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


# ----------------------------------------------------------------- paredes
def parede(x0, y0, x1, y1, esp, aberturas=(), fora=0):
    """Parede reta (horizontal ou vertical) com aberturas [(a, b, tipo)].
    tipo: porta, vao, janela, alta, vidro, passa. fora = lado externo (+1/-1) para o siding."""
    horiz = (y0 == y1)
    a0, a1 = (x0, x1) if horiz else (y0, y1)
    c = y0 if horiz else x0

    def peca(u0, u1, z0, z1, mat=M["parede"], e=esp, desloc=0.0):
        if mat is not M["corte"]:
            z1 = min(z1, H)
        if u1 - u0 <= 1e-3 or z1 - z0 <= 1e-3:
            return
        cc = c + desloc
        if horiz:
            box(u0, u1, cc - e / 2, cc + e / 2, z0, z1, mat, "parede")
        else:
            box(cc - e / 2, cc + e / 2, u0, u1, z0, z1, mat, "parede")

    def tudo(u0, u1, z0, z1):
        peca(u0, u1, z0, z1)
        if fora:
            peca(u0, u1, max(z0, 0.0), z1, M["siding"], 0.02, fora * (esp / 2 + 0.01))
        if abs(z1 - H) < 1e-6:
            peca(u0 - (esp / 2 if False else 0), u1, H, H + 0.006, M["corte"], esp + (0.04 if fora else 0), fora * 0.02)

    pos = a0
    for (a, b, tipo) in sorted(aberturas):
        tudo(pos, a, 0.0 if fora else F, H)
        if tipo == "porta":
            tudo(a, b, F + 2.1, H)
            folha(horiz, c, a, b, esp)
        elif tipo == "janela" or tipo == "alta":
            zp = F + (1.0 if tipo == "janela" else 1.6)
            tudo(a, b, 0.0 if fora else F, zp)
            tudo(a, b, F + 2.2, H)
            peca(a, b, zp, F + 2.2, M["vidro_c"], 0.02)
            peca(a, b, zp - 0.03, zp, M["branco"], esp + 0.06)
        elif tipo == "vidro":
            tudo(a, b, F + 2.4, H)
            peca(a, b, F, F + 2.4, M["vidro_c"], 0.02)
            n = max(2, round((b - a) / 1.3))
            for k in range(n + 1):
                u = a + (b - a) * k / n
                peca(u - 0.03, u + 0.03, F, F + 2.4, M["branco"], 0.06)
        elif tipo == "passa":
            tudo(a, b, F, F + 1.05)
            tudo(a, b, F + 2.1, H)
            peca(a, b, F + 1.0, F + 1.06, M["quartzo"], esp + 0.3)
        elif tipo == "portao":
            tudo(a, b, F + 2.45, H)
        pos = b
    tudo(pos, a1, 0.0 if fora else F, H)


def folha(horiz, c, a, b, esp, lado=1):
    """Folha de porta aberta a 90°."""
    w = b - a
    if horiz:
        box(a + 0.02, a + 0.06, c + lado * esp / 2, c + lado * (esp / 2 + w - 0.05), F, H - 0.02, M["porta"], "folha")
    else:
        box(c + lado * esp / 2, c + lado * (esp / 2 + w - 0.05), a + 0.02, a + 0.06, F, H - 0.02, M["porta"], "folha")


def paredes():
    # externas
    parede(1.5, 5.0, 18.5, 5.0, EXT, [(2.0, 7.0, "portao"), (9.5, 10.7, "porta"), (11.0, 12.2, "janela"),
                                      (13.3, 17.5, "janela")], fora=-1)
    parede(18.5, 5.0, 18.5, 22.0, EXT, [(5.8, 7.6, "janela"), (9.2, 10.4, "alta"), (11.6, 12.7, "janela"),
                                        (13.1, 14.2, "janela"), (15.6, 16.8, "alta"), (18.2, 19.6, "janela"),
                                        (19.9, 21.2, "janela")], fora=1)
    parede(7.5, 22.0, 18.5, 22.0, EXT, [(8.0, 12.0, "vidro"), (13.3, 17.7, "vidro")], fora=1)
    parede(1.5, 5.0, 1.5, 17.0, EXT, [(7.0, 9.0, "alta"), (11.3, 12.2, "porta"), (13.6, 15.9, "janela")], fora=-1)
    # internas
    parede(7.5, 5.0, 7.5, 22.0, INT, [(5.8, 6.6, "porta"), (15.1, 16.9, "vao"), (17.4, 21.6, "vidro")])
    parede(1.5, 10.5, 7.5, 10.5, INT, [(5.6, 6.4, "porta")])
    parede(1.5, 13.0, 7.5, 13.0, INT, [(5.8, 6.6, "porta")])
    parede(1.5, 17.0, 7.5, 17.0, INT, [(4.0, 7.0, "passa")])
    parede(9.3, 8.0, 9.3, 10.0, INT, [(8.4, 9.1, "porta")])
    parede(7.5, 8.0, 9.3, 8.0, INT)
    parede(7.5, 10.0, 12.5, 10.0, INT, [(9.6, 12.4, "vidro")])
    parede(7.5, 15.0, 12.5, 15.0, INT, [(8.2, 12.3, "vidro")])
    parede(12.5, 5.0, 12.5, 22.0, INT, [(5.9, 6.8, "porta"), (8.6, 9.9, "vao")])
    parede(12.5, 8.5, 18.5, 8.5, INT)
    parede(13.7, 8.5, 13.7, 15.0, INT, [(8.7, 9.4, "porta"), (11.3, 12.1, "porta")])
    parede(13.7, 11.0, 18.5, 11.0, INT)
    parede(12.5, 15.0, 18.5, 15.0, INT, [(12.6, 13.4, "porta")])
    parede(15.3, 15.0, 15.3, 17.3, INT, [(15.75, 16.45, "porta")])
    parede(12.5, 17.3, 18.5, 17.3, INT, [(12.6, 13.7, "vao")])
    # varanda gourmet: pilares e vigas baixas não entram (corte); só pilares
    for (x, y) in ((1.65, 21.85), (4.5, 21.85), (1.65, 19.4), (7.4, 21.85)):
        box(x - 0.14, x + 0.14, y - 0.14, y + 0.14, F, H, M["branco"], "pilar")
        box(x - 0.14, x + 0.14, y - 0.14, y + 0.14, H, H + 0.006, M["corte"], "corte")


def pisos():
    box(1.4, 18.6, 4.9, 22.1, 0, 0.3, M["pedra"], "embasamento")
    salas = [
        (1.5, 7.5, 5.0, 10.5, "cimento"), (1.5, 7.5, 10.5, 13.0, "piso_banho"), (1.5, 7.5, 13.0, 17.0, "piso_social"),
        (1.5, 7.5, 17.0, 22.0, "porcelanato"), (7.5, 12.5, 5.0, 10.0, "piso_social"), (7.5, 9.3, 8.0, 10.0, "piso_banho"),
        (7.5, 12.5, 10.0, 15.0, "assoalho"), (7.5, 12.5, 15.0, 22.0, "piso_social"), (12.5, 18.5, 5.0, 8.5, "assoalho"),
        (12.5, 13.7, 8.5, 15.0, "assoalho"), (13.7, 18.5, 8.5, 11.0, "piso_banho"), (13.7, 18.5, 11.0, 15.0, "assoalho"),
        (12.5, 15.3, 15.0, 17.3, "assoalho"), (15.3, 18.5, 15.0, 17.3, "piso_banho"), (12.5, 18.5, 17.3, 22.0, "assoalho"),
    ]
    for (x0, x1, y0, y1, m) in salas:
        box(x0, x1, y0, y1, 0.3, F - 0.001 if m != "piso_banho" else F - 0.0005, M[m], "piso")
    # varanda de entrada
    box(7.3, 12.7, 3.3, 5.0, 0, F - 0.002, M["porcelanato"], "varanda")
    for (y0, z) in ((2.95, 0.1), (3.12, 0.2)):
        box(9.0, 11.2, y0, 3.3, 0, z, M["pedra"], "degrau")
    for x in (7.7, 12.3):
        box(x - 0.3, x + 0.3, 3.35, 3.95, F, F + 1.0, M["pedra"], "pedestal")
        box(x - 0.15, x + 0.15, 3.5, 3.8, F + 1.0, H, M["branco"], "coluna")
        box(x - 0.15, x + 0.15, 3.5, 3.8, H, H + 0.006, M["corte"], "corte")


# ----------------------------------------------------------------- móveis
def cadeira(x, y, rot, mat=None):
    mat = mat or M["marcenaria"]
    bf(x - 0.22, x + 0.22, y - 0.22, y + 0.22, 0.44, 0.49, mat, "assento", 0.01)
    dx, dy = {0: (0, -0.2), 1: (0.2, 0), 2: (0, 0.2), 3: (-0.2, 0)}[rot]
    if dy:
        bf(x - 0.21, x + 0.21, y + dy - 0.02, y + dy + 0.02, 0.49, 0.92, mat, "encosto", 0.01)
    else:
        bf(x + dx - 0.02, x + dx + 0.02, y - 0.21, y + 0.21, 0.49, 0.92, mat, "encosto", 0.01)
    for ex in (-0.18, 0.18):
        for ey in (-0.18, 0.18):
            bf(x + ex - 0.02, x + ex + 0.02, y + ey - 0.02, y + ey + 0.02, 0, 0.44, M["preto"], "pe")


def mesa(x0, x1, y0, y1, h=0.75, tampo=None, pes=M["preto"]):
    bf(x0, x1, y0, y1, h - 0.04, h, tampo or M["marcenaria"], "tampo", 0.01)
    for x in (x0 + 0.06, x1 - 0.1):
        for y in (y0 + 0.06, y1 - 0.1):
            bf(x, x + 0.04, y, y + 0.04, 0, h - 0.04, pes, "pe")


def sofa(x0, x1, y0, y1, encosto, mat=None):
    """encosto: lado do encosto ('x0','x1','y0','y1')."""
    mat = mat or M["sofa"]
    bf(x0, x1, y0, y1, 0.08, 0.42, mat, "base", 0.04)
    e = 0.22
    if encosto == "y1":
        bf(x0, x1, y1 - e, y1, 0.42, 0.85, mat, "encosto", 0.06)
    elif encosto == "y0":
        bf(x0, x1, y0, y0 + e, 0.42, 0.85, mat, "encosto", 0.06)
    elif encosto == "x0":
        bf(x0, x0 + e, y0, y1, 0.42, 0.85, mat, "encosto", 0.06)
    else:
        bf(x1 - e, x1, y0, y1, 0.42, 0.85, mat, "encosto", 0.06)
    # almofadas
    for k in range(3):
        if encosto in ("y0", "y1"):
            w = (x1 - x0) / 3
            yy = y1 - e - 0.12 if encosto == "y1" else y0 + e + 0.02
            bf(x0 + w * k + 0.05, x0 + w * (k + 1) - 0.05, yy, yy + 0.1, 0.42, 0.75, M["sofa2"], "almofada", 0.04)
        else:
            w = (y1 - y0) / 3
            xx = x1 - e - 0.12 if encosto == "x1" else x0 + e + 0.02
            bf(xx, xx + 0.1, y0 + w * k + 0.05, y0 + w * (k + 1) - 0.05, 0.42, 0.75, M["sofa2"], "almofada", 0.04)


def cama(x0, x1, y0, y1, cabeceira, edredom, travesseiros=2):
    bf(x0, x1, y0, y1, 0.05, 0.32, M["marcenaria"], "base", 0.01)
    bf(x0 + 0.02, x1 - 0.02, y0 + 0.02, y1 - 0.02, 0.32, 0.55, M["lencol"], "colchao", 0.05)
    if cabeceira == "x1":
        bf(x1, x1 + 0.08, y0 - 0.05, y1 + 0.05, 0.05, 1.15, M["sofa2"], "cabeceira", 0.03)
        bf(x0 - 0.03, x1 - 0.55, y0, y1, 0.5, 0.6, edredom, "edredom", 0.04)
        n = travesseiros
        for k in range(n):
            w = (y1 - y0) / n
            bf(x1 - 0.5, x1 - 0.1, y0 + w * k + 0.06, y0 + w * (k + 1) - 0.06, 0.55, 0.7, M["lencol"], "travesseiro", 0.06)
    elif cabeceira == "y1":
        bf(x0 - 0.05, x1 + 0.05, y1, y1 + 0.08, 0.05, 1.0, M["sofa2"], "cabeceira", 0.03)
        bf(x0, x1, y0 - 0.03, y1 - 0.55, 0.5, 0.6, edredom, "edredom", 0.04)
        for k in range(travesseiros):
            w = (x1 - x0) / travesseiros
            bf(x0 + w * k + 0.06, x0 + w * (k + 1) - 0.06, y1 - 0.5, y1 - 0.1, 0.55, 0.7, M["lencol"], "travesseiro", 0.06)


def vaso_sanitario(x, y, rot):
    dx, dy = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}[rot]   # direção da parede (caixa acoplada)
    bf(x - 0.19, x + 0.19, y - 0.19, y + 0.19, 0, 0.4, M["loucas"], "vaso", 0.12)
    tx, ty = x + dx * 0.27, y + dy * 0.27
    if dx:
        bf(tx - 0.09, tx + 0.09, ty - 0.2, ty + 0.2, 0.35, 0.8, M["loucas"], "caixa", 0.03)
    else:
        bf(tx - 0.2, tx + 0.2, ty - 0.09, ty + 0.09, 0.35, 0.8, M["loucas"], "caixa", 0.03)


def bancada_pia(x0, x1, y0, y1, cubas=1):
    bf(x0, x1, y0, y1, 0.1, 0.82, M["marcenaria"], "gabinete", 0.01)
    bf(x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, 0.82, 0.86, M["quartzo"], "tampo")
    horiz = (x1 - x0) > (y1 - y0)
    for k in range(cubas):
        if horiz:
            cx = x0 + (x1 - x0) * (k + 0.5) / cubas
            cy = (y0 + y1) / 2
        else:
            cx = (x0 + x1) / 2
            cy = y0 + (y1 - y0) * (k + 0.5) / cubas
        bf(cx - 0.2, cx + 0.2, cy - 0.15, cy + 0.15, 0.86, 0.99, M["loucas"], "cuba", 0.06)


def box_chuveiro(x0, x1, y0, y1, vidros):
    bf(x0, x1, y0, y1, 0, 0.02, M["piso_banho"], "box")
    for (a0, a1, b0, b1) in vidros:
        bf(a0, a1, b0, b1, 0.02, 1.9, M["vidro_c"], "vidro_box")


def planta_vaso(x, y, h=1.1, r=0.35):
    cilindro(x, y, F, F + 0.45, 0.2, M["terra"] if False else M["corte"])
    C.esfera("planta", (x, y, F + 0.45 + h * 0.5), r, M["folha2"], 0.5, 4, sub=3, achata=h / (2 * r))


def estante_jogos(x0, x1, y0, y1, frente, h=2.2, n=5):
    """Estante com prateleiras cheias de caixas de jogos coloridas. frente: '+x','-x','+y','-y'."""
    bf(x0, x1, y0, y1, 0, 0.06, M["marcenaria"], "rodape")
    ao_longo_x = frente in ("+y", "-y")
    L0, L1 = (x0, x1) if ao_longo_x else (y0, y1)
    P0, P1 = (y0, y1) if ao_longo_x else (x0, x1)
    for k in range(n + 1):
        z = 0.06 + k * (h - 0.06) / n
        bf(x0, x1, y0, y1, z, z + 0.025, M["marcenaria"], "prateleira")
    for lado in (L0, L1):
        if ao_longo_x:
            bf(lado - 0.02, lado + 0.02, y0, y1, 0, h + 0.03, M["marcenaria"], "lateral")
        else:
            bf(x0, x1, lado - 0.02, lado + 0.02, 0, h + 0.03, M["marcenaria"], "lateral")
    for k in range(n):
        z0 = 0.06 + k * (h - 0.06) / n + 0.025
        zmax = (h - 0.06) / n - 0.06
        u = L0 + 0.03
        while u < L1 - 0.1:
            if random.random() < 0.3:          # pilha deitada
                w = random.uniform(0.28, 0.32)
                if u + w > L1 - 0.03:
                    break
                zz = z0
                for _ in range(random.randint(2, 4)):
                    t = random.uniform(0.05, 0.1)
                    if zz + t > z0 + zmax:
                        break
                    peca_jogo(ao_longo_x, u, u + w, P0, P1, frente, zz, zz + t)
                    zz += t
                u += w + 0.02
            else:
                w = random.uniform(0.05, 0.11)
                t = random.uniform(0.22, min(0.31, zmax))
                peca_jogo(ao_longo_x, u, u + w, P0, P1, frente, z0, z0 + t)
                u += w + 0.003


def peca_jogo(ao_longo_x, u0, u1, P0, P1, frente, z0, z1):
    prof = min(0.3, P1 - P0 - 0.02)
    if frente in ("+y", "+x"):
        p0, p1 = P1 - prof - 0.01, P1 - 0.01
    else:
        p0, p1 = P0 + 0.01, P0 + 0.01 + prof
    mat = random.choice(MAT_JOGOS)
    if ao_longo_x:
        bf(u0, u1, p0, p1, z0, z1, mat, "jogo")
    else:
        bf(p0, p1, u0, u1, z0, z1, mat, "jogo")


def carro(cx, cy, mat):
    bf(cx - 0.88, cx + 0.88, cy - 2.2, cy + 2.2, 0.28, 0.85, mat, "carroceria", 0.12)
    v = []
    for (w, y0, y1, z) in ((0.82, -1.0, 1.15, 0.85), (0.7, -0.55, 0.75, 1.38)):
        for dx in (-w, w):
            for yy in (y0, y1):
                v.append((cx + dx, cy + yy, F + z))
    # ordem (i,j,k) = (base/topo trocada) -> reorganiza para caixa8: x,y,z
    c = [v[0], v[4], v[1], v[5], v[2], v[6], v[3], v[7]]
    o = C.caixa8(c, M["tela"], "cabine")
    macio(o, 0.06)
    for sx in (-0.8, 0.8):
        for sy in (-1.35, 1.35):
            r = cilindro(cx + sx, cy + sy, -0.11, 0.11, 0.33, M["pneu"], 24, "x")
            r.location = (cx + sx, cy + sy, F + 0.33)


def moveis():
    # garagem: 2 carros (frente para a rua)
    carro(3.05, 7.75, M["carro1"]); carro(5.95, 7.75, M["carro2"])
    # lavanderia: lava e seca, tanque, armário, ducha pet
    for x in (1.65, 2.35):
        bf(x, x + 0.62, 10.6, 11.22, 0, 0.88, M["loucas"], "maquina", 0.02)
        cilindro(x + 0.31, 10.585, F + 0.25, F + 0.65, 0.2, M["tela"], 24, "y").location = (x + 0.31, 10.59, F + 0.45)
    bf(3.1, 5.0, 10.6, 11.2, 0.1, 0.88, M["marcenaria"], "armario", 0.01)
    bf(3.1, 5.0, 10.6, 11.2, 0.88, 0.92, M["quartzo"], "tampo")
    bf(5.05, 5.85, 10.6, 11.2, 0, 0.9, M["loucas"], "tanque", 0.03)
    bf(6.2, 7.4, 12.0, 12.9, 0, 0.25, M["piso_banho"], "ducha_pet")
    bf(6.2, 7.4, 12.86, 12.9, 0.25, 1.6, M["vidro_c"], "vidro")
    bf(1.6, 2.2, 11.4, 12.9, 0, 2.2, M["marcenaria"], "armario_alto", 0.01) if False else None
    # cozinha: bancada em L, torre quente, geladeira, ilha com banquetas
    bf(1.62, 2.25, 13.75, 16.9, 0.1, 0.88, M["marcenaria"], "gabinete", 0.01)
    bf(1.6, 2.28, 13.75, 16.92, 0.88, 0.92, M["quartzo"], "tampo")
    bf(1.65, 2.15, 14.3, 15.0, 0.92, 0.95, M["inox"], "cuba")
    bf(1.68, 2.22, 15.6, 16.3, 0.92, 0.93, M["tela"], "cooktop")
    bf(1.62, 2.0, 13.75, 16.9, 1.4, 1.95, M["marcenaria"], "aereo", 0.01)
    bf(1.62, 2.6, 13.08, 13.72, 0, 1.95, M["marcenaria"], "torre", 0.01)
    bf(2.65, 3.55, 13.1, 13.78, 0, 1.9, M["inox"], "geladeira", 0.02)
    bf(3.3, 5.9, 14.6, 15.6, 0.1, 0.9, M["marcenaria"], "ilha", 0.01)
    bf(3.25, 5.95, 14.55, 15.65, 0.9, 0.95, M["quartzo"], "tampo_ilha")
    for x in (3.75, 4.6, 5.45):
        cilindro(x, 16.0, F, F + 0.68, 0.2, M["preto"], 20)
        cilindro(x, 16.0, F + 0.68, F + 0.72, 0.21, M["sofa2"], 20)
    # varanda gourmet
    bf(1.75, 3.1, 17.08, 17.8, 0.0, 0.7, M["tijolo"], "churrasqueira")
    bf(1.75, 3.1, 17.08, 17.8, 0.7, 0.74, M["pedra"], "tampo")
    bf(1.95, 2.9, 17.08, 17.6, 0.74, 1.6, M["tela"], "boca")
    bf(1.75, 3.1, 17.08, 17.8, 1.6, 1.98, M["tijolo"], "coifa")
    bf(3.1, 5.6, 17.08, 17.7, 0.1, 0.9, M["marcenaria"], "bancada", 0.01)
    bf(3.1, 5.6, 17.08, 17.7, 0.9, 0.94, M["quartzo"], "tampo")
    mesa(2.9, 3.9, 18.6, 20.9, 0.76, M["marcenaria"])
    for y in (18.95, 19.75, 20.55):
        cadeira(2.55, y, 3); cadeira(4.25, y, 1)
    cadeira(3.4, 18.25, 0); cadeira(3.4, 21.25, 2)
    sofa(5.6, 7.2, 19.0, 21.4, "x1", M["sofa2"])
    # hall / galeria: estante de jogos + aparador + tapete
    estante_jogos(7.6, 8.0, 5.15, 7.85, "+x", 1.9, 5)
    bf(11.35, 12.4, 9.45, 9.9, 0, 0.8, M["marcenaria"], "aparador", 0.01)
    bf(8.8, 11.8, 5.6, 7.6, 0, 0.01, M["tapete2"], "tapete")
    planta_vaso(12.1, 5.5)
    # lavabo
    vaso_sanitario(7.85, 8.6, 3); bancada_pia(8.55, 9.2, 9.3, 9.92, 1)
    # sala de jogos: estantes em L cheias, mesa com feltro, 6 cadeiras, jogo montado
    estante_jogos(7.6, 7.95, 10.08, 14.92, "+x", 1.9, 5)
    estante_jogos(8.0, 12.42, 10.08, 10.43, "+y", 1.9, 5)
    bf(8.4, 12.2, 10.9, 14.6, 0, 0.01, M["tapete"], "tapete")
    mesa(9.2, 11.4, 11.8, 13.0, 0.76, M["marcenaria"])
    bf(9.32, 11.28, 11.92, 12.88, 0.76, 0.77, M["feltro"], "feltro")
    for x in (9.75, 10.85):
        cadeira(x, 11.35, 0); cadeira(x, 13.45, 2)
    cadeira(8.75, 12.4, 3); cadeira(11.85, 12.4, 1)
    bf(9.9, 10.7, 12.1, 12.7, 0.77, 0.785, M["lencol"], "tabuleiro")
    for k in range(18):
        x, y = random.uniform(9.45, 11.15), random.uniform(12.0, 12.8)
        if 9.9 < x < 10.7 and 12.1 < y < 12.7:
            continue
        m = random.choice(MAT_JOGOS[:8])
        bf(x, x + 0.04, y, y + 0.04, 0.77, 0.81, m, "peca")
    for (x, y) in ((9.6, 12.0), (11.0, 12.75)):
        bf(x, x + 0.25, y, y + 0.18, 0.77, 0.8, random.choice(MAT_JOGOS), "cartas")
    # estar / jantar
    mesa(8.9, 9.9, 15.6, 17.8, 0.76, M["marcenaria"])
    for y in (15.95, 16.7, 17.45):
        cadeira(8.55, y, 3); cadeira(10.25, y, 1)
    bf(8.4, 12.3, 18.5, 21.8, 0, 0.01, M["tapete"], "tapete")
    sofa(7.65, 8.55, 18.8, 21.85, "x0")
    sofa(8.55, 10.6, 20.95, 21.85, "y1")
    bf(9.2, 10.4, 19.3, 20.2, 0.0, 0.4, M["marcenaria"], "centro", 0.02)
    bf(12.05, 12.4, 18.6, 21.0, 0, 0.5, M["marcenaria"], "rack", 0.01)
    bf(12.25, 12.32, 19.0, 20.6, 0.9, 1.75, M["tela"], "tv")
    planta_vaso(12.1, 21.6); planta_vaso(7.9, 15.5, 0.9, 0.3)
    # home office: mesa com monitor, cadeira, sofá-cama, estante
    mesa(12.75, 15.15, 5.15, 5.9, 0.75, M["marcenaria"])
    bf(13.5, 14.3, 5.25, 5.3, 0.95, 1.4, M["tela"], "monitor")
    bf(13.85, 13.95, 5.25, 5.4, 0.75, 0.95, M["preto"], "suporte")
    cadeira(13.9, 6.35, 2, M["preto"])
    sofa(17.6, 18.4, 5.15, 7.9, "x1", M["sofa"])
    estante_jogos(15.6, 17.4, 8.0, 8.4, "-y", 1.9, 4)
    bf(14.2, 17.2, 6.3, 7.8, 0, 0.01, M["tapete2"], "tapete")
    # banho social
    bancada_pia(15.0, 16.9, 8.55, 9.05, 2)
    vaso_sanitario(18.1, 9.4, 1)
    box_chuveiro(13.8, 15.2, 9.6, 10.95, [(15.17, 15.2, 9.6, 10.95), (13.8, 15.2, 9.6, 9.63)])
    # quarto da filha
    cama(17.35, 18.4, 11.6, 13.6, "x1", M["rosa"], 1)
    bf(13.8, 16.2, 14.35, 14.95, 0, 1.9, M["loucas"], "guarda_roupa", 0.01)
    mesa(13.8, 15.2, 11.08, 11.65, 0.65, M["loucas"])
    cadeira(14.5, 12.0, 2, M["lilas"])
    cilindro(15.8, 12.7, F, F + 0.012, 0.75, M["rosa"], 40)
    for (x, y, m) in ((15.6, 12.5, MAT_JOGOS[2]), (16.0, 12.9, MAT_JOGOS[1]), (15.9, 12.4, MAT_JOGOS[3])):
        bf(x, x + 0.18, y, y + 0.18, 0.012, 0.19, m, "brinquedo", 0.02)
    bf(17.3, 18.4, 14.1, 14.55, 0, 0.6, M["lilas"], "bau", 0.03)
    # closet
    for (y0, y1) in ((15.08, 15.62), (16.68, 17.22)):
        bf(12.6, 15.2, y0, y1, 0, 1.9, M["marcenaria"], "closet", 0.005)
        for k in range(14):
            x = 12.75 + k * 0.17
            bf(x, x + 0.06, y0 + 0.05 if y0 < 16 else y1 - 0.52, (y0 + 0.52) if y0 < 16 else y1 - 0.05, 1.0, 1.85,
               random.choice(MAT_JOGOS[:6] + [M["lencol"], M["sofa"]]), "roupa", 0.01)
    # banho suíte
    bancada_pia(15.4, 16.9, 15.08, 15.58, 2)
    vaso_sanitario(15.7, 16.9, 0)
    box_chuveiro(17.0, 18.42, 15.08, 17.22, [(16.97, 17.0, 15.08, 17.22)])
    # suíte do casal
    cama(16.4, 18.38, 18.55, 20.65, "x1", M["edredom"], 2)
    for y in (18.0, 20.75):
        bf(17.85, 18.38, y, y + 0.45, 0, 0.5, M["marcenaria"], "criado", 0.01)
    bf(14.9, 17.9, 18.1, 21.1, 0, 0.01, M["tapete"], "tapete")
    sofa(12.7, 13.6, 18.2, 19.2, "x0", M["sofa2"])
    planta_vaso(12.9, 21.6)


ROTULOS = [
    ("Garagem", 4.5, 9.6), ("Lavanderia", 4.0, 11.9), ("Cozinha", 4.6, 13.6), ("Varanda gourmet", 4.5, 20.0),
    ("Hall", 10.4, 6.6), ("Lavabo", 8.4, 9.0), ("Sala de jogos", 10.3, 12.4), ("Jantar", 9.4, 16.7),
    ("Estar", 10.0, 19.8), ("Home office", 15.0, 6.9), ("Banho", 16.5, 9.8), ("Quarto da filha", 16.0, 12.9),
    ("Closet", 13.9, 16.2), ("Banho suíte", 16.9, 16.2), ("Suíte do casal", 15.5, 19.6), ("Deck", 13.0, 23.1),
    ("Brincar", 11.4, 27.2), ("Cachorro", 2.2, 26.6), ("Horta", 17.6, 27.2), ("Varanda", 10.0, 4.2),
]


def rotulos():
    """Projeta o centro de cada cômodo na imagem e salva em <saida>.json (os textos entram depois, no PIL)."""
    import json
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    bpy.context.view_layer.update()
    cam = C.cena.camera
    pts = []
    for (nome, x, y) in ROTULOS:
        v = world_to_camera_view(C.cena, cam, Vector((x, y, F + 0.9)))
        pts.append((nome, v.x, 1 - v.y))
    with open(os.path.splitext(C.SAIDA)[0] + ".json", "w") as f:
        json.dump(pts, f, ensure_ascii=False)


CAMERAS = {
    "planta3d":       ((-1.0, -6.5, 25.0), (10.2, 14.2, 0.0), 30),
    "planta3d_fundo": ((23.0, 33.0, 24.0), (10.0, 13.8, 0.0), 30),
    "topo":           ((10.0, 13.5, 40.0), (10.0, 13.50001, 0.0), 30),
}

if __name__ == "__main__":
    pisos()
    paredes()
    moveis()
    C.terreno(arvore_frente=False)
    for o in list(bpy.data.objects):          # tira as árvores da lateral esquerda que tampam a vista
        if (o.name.startswith("copa") or o.name.startswith("Cone")) and (o.location.x < -5 and o.location.y < 30 or
                                                                              o.location.x > 18.6 and 17 < o.location.y < 23):
            bpy.data.objects.remove(o, do_unlink=True)
    C.luz_e_ceu()
    C.CAMERAS.update(CAMERAS)
    C.camera(C.CAM)
    rotulos()
    C.render()
