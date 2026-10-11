"""Vista 3D da casa (estilo americano craftsman) sobre a planta de planta.py.

Rodar com o Blender 4.2:
  blender -b -P casa3d.py -- <camera> <amostras> <saida.png> [largura altura]
Câmeras: frente, aerea_frente, aerea_fundo.
Coordenadas iguais às da planta: x para a direita, y da rua para o fundo, z para cima (metros).
"""
import bpy, bmesh, math, sys, random
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
CAM = argv[0] if len(argv) > 0 else "frente"
SAMPLES = int(argv[1]) if len(argv) > 1 else 64
SAIDA = argv[2] if len(argv) > 2 else "/tmp/casa.png"
RES = (int(argv[3]), int(argv[4])) if len(argv) > 4 else (1920, 1080)
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene

ZE = 3.2          # altura do beiral
T40 = math.tan(math.radians(40))
T28 = math.tan(math.radians(28))


# ----------------------------------------------------------------- materiais
def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


def novo_mat(nome):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    return m, nt, b


def coords(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return tc.outputs["Object"]


def liso(nome, cor, rough=0.5, metal=0.0, spec=0.5):
    m, nt, b = novo_mat(nome)
    b.inputs["Base Color"].default_value = lin(cor)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Specular IOR Level"].default_value = spec
    return m


def variacao(nt, b, cor1, cor2, escala=3.0, vetor=None):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = escala
    if vetor is not None:
        nt.links.new(vetor, n.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = lin(cor1)
    r.color_ramp.elements[1].color = lin(cor2)
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])


def bump(nt, b, saida, forca=0.5, dist=0.02):
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = forca
    bp.inputs["Distance"].default_value = dist
    nt.links.new(saida, bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])


def lap_siding(nome, cor1, cor2):
    """Tábuas horizontais sobrepostas (lap siding), 18 cm de exposição."""
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.62
    co = coords(nt)
    variacao(nt, b, cor1, cor2, 0.8, co)
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"; w.bands_direction = "Z"; w.wave_profile = "SAW"
    w.inputs["Scale"].default_value = 0.314 / 0.18 / 2 * 2
    w.inputs["Distortion"].default_value = 0.0
    nt.links.new(co, w.inputs["Vector"])
    bump(nt, b, w.outputs["Fac"], 0.55, 0.012)
    return m


def board_batten(nome, cor1, cor2):
    """Tábua e mata-junta vertical (oitões)."""
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.6
    co = coords(nt)
    variacao(nt, b, cor1, cor2, 0.7, co)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(co, sep.inputs[0])
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    nt.links.new(sep.outputs[0], add.inputs[0]); nt.links.new(sep.outputs[1], add.inputs[1])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 1 / 0.40
    nt.links.new(add.outputs[0], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"; nt.links.new(mul.outputs[0], fr.inputs[0])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.85
    nt.links.new(fr.outputs[0], gt.inputs[0])
    bump(nt, b, gt.outputs[0], 0.7, 0.01)
    return m


def telha_shingle(nome):
    """Telha shingle asfáltica cinza-grafite, fiadas paralelas à cumeeira."""
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.85
    co = coords(nt)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(co, sep.inputs[0])
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    nt.links.new(sep.outputs[0], add.inputs[0]); nt.links.new(sep.outputs[1], add.inputs[1])
    mz = nt.nodes.new("ShaderNodeMath"); mz.operation = "MULTIPLY"; mz.inputs[1].default_value = 1.7
    nt.links.new(sep.outputs[2], mz.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(add.outputs[0], comb.inputs[0]); nt.links.new(mz.outputs[0], comb.inputs[1])
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.34
    br.inputs["Row Height"].default_value = 0.2
    br.inputs["Mortar Size"].default_value = 0.008
    br.inputs["Mortar Smooth"].default_value = 0.3
    br.offset = 0.5
    br.inputs["Color1"].default_value = lin("#3B3D41")
    br.inputs["Color2"].default_value = lin("#2E3033")
    br.inputs["Mortar"].default_value = lin("#18191B")
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(comb.outputs[0], br.inputs["Vector"])
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 60
    nt.links.new(co, n.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "OVERLAY"
    mix.inputs["Factor"].default_value = 0.35
    nt.links.new(br.outputs["Color"], mix.inputs[6]); nt.links.new(n.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs["Fac"], inv.inputs[1])
    bump(nt, b, inv.outputs[0], 0.8, 0.02)
    return m


def pedra(nome):
    """Pedra natural assentada (base da fachada, colunas e chaminé)."""
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.85
    co = coords(nt)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 1.9)
    nt.links.new(co, mp.inputs["Vector"])
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.feature = "DISTANCE_TO_EDGE"
    v.inputs["Scale"].default_value = 4.5
    nt.links.new(mp.outputs[0], v.inputs["Vector"])
    vc = nt.nodes.new("ShaderNodeTexVoronoi"); vc.inputs["Scale"].default_value = 4.5
    nt.links.new(mp.outputs[0], vc.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = lin("#8C7B66")
    r.color_ramp.elements[1].color = lin("#C4B59D")
    r.color_ramp.elements.new(0.5).color = lin("#A39279")
    sp = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(vc.outputs["Color"], sp.inputs[0])
    nt.links.new(sp.outputs[0], r.inputs["Fac"])
    rj = nt.nodes.new("ShaderNodeValToRGB")
    rj.color_ramp.elements[0].position = 0.02; rj.color_ramp.elements[1].position = 0.06
    nt.links.new(v.outputs["Distance"], rj.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs[6].default_value = lin("#6E665C")
    nt.links.new(rj.outputs["Color"], mix.inputs["Factor"])
    nt.links.new(r.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 25
    nt.links.new(co, n.inputs["Vector"])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"
    ad.inputs[1].default_value = 0.15
    nt.links.new(n.outputs["Fac"], ad.inputs[0]); nt.links.new(rj.outputs["Color"], ad.inputs[2])
    bump(nt, b, ad.outputs[0], 0.9, 0.04)
    return m


def piso_pavers(nome, c1, c2, w=0.4, h=0.2):
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.8
    co = coords(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = w
    br.inputs["Row Height"].default_value = h
    br.inputs["Mortar Size"].default_value = 0.006
    br.inputs["Color1"].default_value = lin(c1)
    br.inputs["Color2"].default_value = lin(c2)
    br.inputs["Mortar"].default_value = lin("#77736C")
    nt.links.new(co, br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs["Fac"], inv.inputs[1])
    bump(nt, b, inv.outputs[0], 0.5, 0.01)
    return m


def madeira(nome, c1, c2, eixo="X", escala=0.15):
    """Tábuas de madeira (deck, forro) ao longo do eixo dado."""
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.55
    co = coords(nt)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(co, sep.inputs[0])
    i = 1 if eixo == "X" else 0          # tábuas ao longo de X variam em Y
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 1 / escala
    nt.links.new(sep.outputs[i], mul.inputs[0])
    fl = nt.nodes.new("ShaderNodeMath"); fl.operation = "FLOOR"; nt.links.new(mul.outputs[0], fl.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"; nt.links.new(mul.outputs[0], fr.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "1D"
    nt.links.new(fl.outputs[0], wn.inputs["W"])
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 3
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.15, 6, 6) if eixo == "X" else (6, 0.15, 6)
    nt.links.new(co, mp.inputs["Vector"]); nt.links.new(mp.outputs[0], n.inputs["Vector"])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = "MULTIPLY_ADD"; ad.inputs[1].default_value = 0.5
    nt.links.new(n.outputs["Fac"], ad.inputs[0]); nt.links.new(wn.outputs["Value"], ad.inputs[2])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = lin(c1); r.color_ramp.elements[1].color = lin(c2)
    r.color_ramp.elements[0].position = 0.3; r.color_ramp.elements[1].position = 1.2
    nt.links.new(ad.outputs[0], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "LESS_THAN"; gt.inputs[1].default_value = 0.94
    nt.links.new(fr.outputs[0], gt.inputs[0])
    bump(nt, b, gt.outputs[0], 0.6, 0.01)
    return m


def folhagem(nome, c1, c2):
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.7
    b.inputs["Subsurface Weight"].default_value = 0.15
    co = nt.nodes.new("ShaderNodeTexCoord").outputs["Generated"]
    variacao(nt, b, c1, c2, 6.0, co)
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 90; n.inputs["Detail"].default_value = 4
    nt.links.new(co, n.inputs["Vector"])
    bump(nt, b, n.outputs["Fac"], 0.9, 0.08)
    return m


def gramado(nome):
    m, nt, b = novo_mat(nome)
    b.inputs["Roughness"].default_value = 0.9
    co = coords(nt)
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 0.6; n.inputs["Detail"].default_value = 6
    nt.links.new(co, n.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = lin("#3F6B2A"); r.color_ramp.elements[1].color = lin("#6E8F3A")
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 400
    nt.links.new(co, n2.inputs["Vector"])
    bump(nt, b, n2.outputs["Fac"], 0.6, 0.02)
    return m


def vidro():
    m, nt, b = novo_mat("vidro")
    b.inputs["Base Color"].default_value = lin("#1A2329")
    b.inputs["Roughness"].default_value = 0.04
    b.inputs["Specular IOR Level"].default_value = 1.0
    b.inputs["Coat Weight"].default_value = 1.0
    return m


M = dict(
    siding=lap_siding("siding", "#8E9C8C", "#9AA897"),          # verde-sálvia acinzentado
    oitao=board_batten("oitao", "#ECE6D8", "#E2DACA"),          # creme
    branco=liso("branco", "#F2F0EA", 0.4),
    telha=telha_shingle("telha"),
    pedra=pedra("pedra"),
    vidro=vidro(),
    porta=madeira("porta", "#6B3A22", "#8A4E2C", "Y", 0.12),
    deck=madeira("deck", "#8A5E3A", "#B07E52", "X", 0.14),
    forro=madeira("forro", "#B88A5C", "#D2A877", "Y", 0.10),
    calcada=piso_pavers("calcada", "#B9B3A7", "#C9C3B6", 0.6, 0.3),
    pavers=piso_pavers("pavers", "#8F8A82", "#A39D93", 0.3, 0.15),
    porcelanato=piso_pavers("porcelanato", "#CFC8BC", "#D8D2C6", 0.9, 0.9),
    asfalto=liso("asfalto", "#3C3C3E", 0.9),
    guia=liso("guia", "#BEBAB2", 0.8),
    grama=gramado("grama"),
    folha=folhagem("folha", "#2F5A22", "#5F8A34"),
    folha2=folhagem("folha2", "#3E6B2B", "#7A9A3E"),
    arbusto=folhagem("arbusto", "#2B4F22", "#4C7530"),
    tronco=liso("tronco", "#4A3A2C", 0.9),
    terra=liso("terra", "#4A3826", 0.95),
    preto=liso("preto", "#202020", 0.4, 0.6),
    tijolo=piso_pavers("tijolo", "#8A4A34", "#A0583C", 0.22, 0.07),
    areia=liso("areia", "#E3D2A6", 0.95),
    vermelho=liso("vermelho", "#B5483D", 0.5),
    azul=liso("azul", "#3F6FA8", 0.4),
    cerca=madeira("cerca", "#7A5638", "#94694A", "X", 0.15),
    tecido=liso("tecido", "#D9D2C3", 0.9),
    luz=liso("luz", "#FFF1D0", 0.3),
)


# ----------------------------------------------------------------- geometria
def obj(nome, verts, faces, mat, smooth=False):
    me = bpy.data.meshes.new(nome)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me)
    cena.collection.objects.link(o)
    o.data.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return o


FACES_BOX = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def caixa8(c, mat, nome="caixa"):
    """c: 8 cantos na ordem (i,j,k) com i,j,k em {0,1}: idx = i*4 + j*2 + k."""
    return obj(nome, c, FACES_BOX, mat)


def box(x0, x1, y0, y1, z0, z1, mat, nome="box"):
    c = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    return caixa8(c, mat, nome)


def fachada(eixo, valor, sinal):
    """Referencial de uma fachada: F(u, z, d) -> ponto. u corre ao longo da parede, d para fora."""
    if eixo == "y":
        return lambda u, z, d: (u, valor + sinal * d, z)
    return lambda u, z, d: (valor + sinal * d, u, z)


def fbox(F, u0, u1, z0, z1, d0, d1, mat, nome="peca"):
    c = [F(u, z, d) for u in (u0, u1) for z in (z0, z1) for d in (d0, d1)]
    return caixa8(c, mat, nome)


def janela(F, u0, u1, z0, z1, grade=(3, 2), guilhotina=True):
    t = 0.11
    fbox(F, u0 - t, u0, z0, z1, 0, 0.04, M["branco"], "guarnicao")
    fbox(F, u1, u1 + t, z0, z1, 0, 0.04, M["branco"], "guarnicao")
    fbox(F, u0 - t - 0.04, u1 + t + 0.04, z1, z1 + 0.16, 0, 0.06, M["branco"], "verga")
    fbox(F, u0 - t - 0.03, u1 + t + 0.03, z1 + 0.16, z1 + 0.19, 0, 0.08, M["branco"], "capitel")
    fbox(F, u0 - t - 0.05, u1 + t + 0.05, z0 - 0.06, z0, 0, 0.08, M["branco"], "peitoril")
    fbox(F, u0, u1, z0, z1, 0, 0.01, M["vidro"], "vidro")
    b = 0.05
    for (a0, a1, c0, c1) in [(u0, u0 + b, z0, z1), (u1 - b, u1, z0, z1), (u0, u1, z0, z0 + b), (u0, u1, z1 - b, z1)]:
        fbox(F, a0, a1, c0, c1, 0.01, 0.03, M["branco"], "caixilho")
    zt = z0
    if guilhotina:
        zm = (z0 + z1) / 2
        fbox(F, u0, u1, zm - 0.035, zm + 0.035, 0.01, 0.035, M["branco"], "travessa")
        zt = zm
    nu, nz = grade
    for i in range(1, nu):
        u = u0 + (u1 - u0) * i / nu
        fbox(F, u - 0.012, u + 0.012, zt, z1, 0.01, 0.022, M["branco"], "baguete")
    for j in range(1, nz):
        z = zt + (z1 - zt) * j / nz
        fbox(F, u0, u1, z - 0.012, z + 0.012, 0.01, 0.022, M["branco"], "baguete")


def porta_correr(F, u0, u1, z0, z1, folhas=2):
    t = 0.1
    fbox(F, u0 - t, u0, z0, z1 + t, 0, 0.04, M["branco"], "guarnicao")
    fbox(F, u1, u1 + t, z0, z1 + t, 0, 0.04, M["branco"], "guarnicao")
    fbox(F, u0 - t, u1 + t, z1, z1 + t, 0, 0.05, M["branco"], "verga")
    fbox(F, u0, u1, z0, z1, 0, 0.01, M["vidro"], "vidro")
    w = (u1 - u0) / folhas
    for i in range(folhas + 1):
        u = u0 + w * i
        fbox(F, u - 0.035, u + 0.035, z0, z1, 0.01, 0.04, M["branco"], "montante")
    for z in (z0, z1 - 0.06):
        fbox(F, u0, u1, z, z + 0.06, 0.01, 0.04, M["branco"], "travessa")
    for i in range(folhas):                      # bandeira quadriculada (estilo americano)
        zz = z1 - 0.55
        fbox(F, u0 + w * i, u0 + w * (i + 1), zz - 0.02, zz + 0.02, 0.01, 0.03, M["branco"], "travessa")
        for k in (1, 2):
            u = u0 + w * i + w * k / 3
            fbox(F, u - 0.012, u + 0.012, zz, z1, 0.01, 0.025, M["branco"], "baguete")


def porta_entrada(F, u0, u1, z0, z1):
    """Porta craftsman de madeira com visor e duas bandeirolas laterais."""
    lat = 0.32
    t = 0.12
    fbox(F, u0 - lat - t, u0 - lat, z0, z1 + 0.05, 0, 0.05, M["branco"], "guarnicao")
    fbox(F, u1 + lat, u1 + lat + t, z0, z1 + 0.05, 0, 0.05, M["branco"], "guarnicao")
    fbox(F, u0 - lat - t - 0.05, u1 + lat + t + 0.05, z1 + 0.05, z1 + 0.26, 0, 0.07, M["branco"], "verga")
    for a, b2 in ((u0 - lat, u0), (u1, u1 + lat)):
        fbox(F, a, b2, z0, z1 + 0.05, 0, 0.012, M["vidro"], "vidro")
        fbox(F, a, b2, z0, z0 + 0.8, 0.01, 0.03, M["branco"], "almofada")
        fbox(F, a - 0.03 if a < u0 else a, a + 0.03 if a < u0 else a + 0.03, z0, z1 + 0.05, 0.01, 0.04, M["branco"], "montante")
    fbox(F, u0 - 0.03, u0, z0, z1 + 0.05, 0, 0.05, M["branco"], "montante")
    fbox(F, u1, u1 + 0.03, z0, z1 + 0.05, 0, 0.05, M["branco"], "montante")
    fbox(F, u0, u1, z0, z1, 0, 0.03, M["porta"], "porta")
    # visor em 3 vidros no terço superior + almofadas
    zv0, zv1 = z1 - 0.62, z1 - 0.18
    fbox(F, u0 + 0.14, u1 - 0.14, zv0, zv1, 0.03, 0.036, M["vidro"], "visor")
    for k in (1, 2):
        u = u0 + 0.14 + (u1 - u0 - 0.28) * k / 3
        fbox(F, u - 0.015, u + 0.015, zv0, zv1, 0.03, 0.045, M["porta"], "baguete")
    fbox(F, u0 + 0.14, u1 - 0.14, zv0 - 0.12, zv0 - 0.06, 0.03, 0.05, M["porta"], "dentil")
    for (a0, a1) in ((z0 + 0.15, z0 + 0.85), (z0 + 0.95, zv0 - 0.2)):
        fbox(F, u0 + 0.14, u1 - 0.14, a0, a1, 0.03, 0.045, M["porta"], "almofada")
    fbox(F, u1 - 0.14, u1 - 0.1, z0 + 0.95, z0 + 1.15, 0.03, 0.08, M["preto"], "puxador")


def portao_garagem(F, u0, u1, z0, z1):
    """Portão seccionado estilo 'carriage house', branco com visores no topo."""
    t = 0.14
    fbox(F, u0 - t, u0, z0, z1 + t, 0, 0.05, M["branco"], "guarnicao")
    fbox(F, u1, u1 + t, z0, z1 + t, 0, 0.05, M["branco"], "guarnicao")
    fbox(F, u0 - t - 0.05, u1 + t + 0.05, z1, z1 + t + 0.08, 0, 0.07, M["branco"], "verga")
    fbox(F, u0, u1, z0, z1, -0.05, -0.01, M["branco"], "portao")
    nl, nc = 4, 8
    hz = (z1 - z0) / nl
    wu = (u1 - u0) / nc
    for i in range(nl):
        for j in range(nc):
            a0, a1 = u0 + wu * j + 0.06, u0 + wu * (j + 1) - 0.06
            c0, c1 = z0 + hz * i + 0.07, z0 + hz * (i + 1) - 0.07
            if i == nl - 1:
                fbox(F, a0, a1, c0, c1, -0.01, -0.005, M["vidro"], "visor")
            else:
                fbox(F, a0, a1, c0, c1, -0.01, 0.005, M["branco"], "almofada")
    for k in range(1, nl):
        fbox(F, u0, u1, z0 + hz * k - 0.008, z0 + hz * k + 0.008, -0.01, -0.0, M["preto"], "junta")
    for u in (u0 + (u1 - u0) * 0.25, u0 + (u1 - u0) * 0.75):     # ferragens decorativas
        fbox(F, u - 0.2, u + 0.2, z0 + hz * 1.5 - 0.02, z0 + hz * 1.5 + 0.02, -0.01, 0.015, M["preto"], "ferragem")
    for u in (u0 + (u1 - u0) / 2 - 0.12, u0 + (u1 - u0) / 2 + 0.12):
        fbox(F, u - 0.015, u + 0.015, z0 + hz * 1.2, z0 + hz * 1.8, -0.01, 0.02, M["preto"], "puxador")


def luminaria(F, u, z):
    fbox(F, u - 0.06, u + 0.06, z - 0.12, z + 0.12, 0, 0.04, M["preto"], "base_lum")
    fbox(F, u - 0.09, u + 0.09, z - 0.2, z + 0.08, 0.06, 0.24, M["luz"], "lanterna")
    fbox(F, u - 0.11, u + 0.11, z + 0.08, z + 0.13, 0.04, 0.26, M["preto"], "chapeu")


# ------------------------------------------------------------ telhado e oitões
def P(eixo, s, r, z):
    return (s, r, z) if eixo == "y" else (r, s, z)


def volume_oitao(eixo, s0, s1, r0, r1, ze, tg, mat=None):
    """Prisma triangular do oitão (sobre as paredes), cumeeira ao longo do eixo."""
    sc, zr = (s0 + s1) / 2, ze + (s1 - s0) / 2 * tg
    v = []
    for r in (r0, r1):
        v += [P(eixo, s0, r, ze), P(eixo, s1, r, ze), P(eixo, sc, r, zr)]
    return obj("oitao", v, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], mat or M["oitao"])


def telhado(eixo, s0, s1, r0, r1, ze, tg, oe=0.5, og0=0.4, og1=0.4, rake0=True, rake1=True):
    """Telhado de duas águas: cumeeira ao longo de 'eixo' (x ou y), vão de s0 a s1."""
    t = 0.14
    sc, zr = (s0 + s1) / 2, ze + (s1 - s0) / 2 * tg
    ra, rb = r0 - og0, r1 + og1
    sec = math.sqrt(1 + tg * tg)
    for se in (s0 - oe, s1 + oe):
        zed = ze - oe * tg
        v = []
        for (s, z) in ((se, zed), (sc, zr)):
            for r in (ra, rb):
                for dz in (0, t * sec):
                    v.append(P(eixo, s, r, z + dz))
        caixa8([v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]], M["telha"], "agua")
        # testeira (fascia) branca no beiral
        sgn = -1 if se < sc else 1
        c = [P(eixo, s, r, z) for s in (se + sgn * 0.0, se + sgn * 0.04) for r in (ra, rb) for z in (zed - 0.2, zed + t * sec + 0.02)]
        caixa8(c, M["branco"], "testeira")
        # calha (gutter)
        c = [P(eixo, s, r, z) for s in (se + sgn * 0.04, se + sgn * 0.16) for r in (ra, rb) for z in (zed - 0.15, zed + 0.0)]
        caixa8(c, M["branco"], "calha")
    # cumeeira
    c = [P(eixo, s, r, z) for s in (sc - 0.12, sc + 0.12) for r in (ra, rb) for z in (zr + t * sec - 0.05, zr + t * sec + 0.05)]
    caixa8(c, M["telha"], "cumeeira")
    # beirada inclinada (rake) nas empenas
    for (r, ok, sg) in ((ra, rake0, -1), (rb, rake1, 1)):
        if not ok:
            continue
        for se in (s0 - oe, s1 + oe):
            zed = ze - oe * tg
            v = []
            for (s, z) in ((se, zed), (sc, zr)):
                for rr in (r, r + sg * 0.05):
                    for dz in (-0.22, t * sec + 0.03):
                        v.append(P(eixo, s, rr, z + dz))
            caixa8(v, M["branco"], "rake")
    return zr


def mao_francesa(eixo, s, r, ze, sinal):
    """Mão-francesa decorativa craftsman sob o beiral da empena."""
    pts = []
    for (ds, dz) in ((0, -0.55), (0, 0.0), (sinal * 0.45, 0.0)):
        pts.append((ds, dz))
    w = 0.05
    for (a, b) in ((pts[0], pts[2]), (pts[1], pts[2])):
        v = []
        for (ds, dz) in (a, b):
            for rr in (r - w, r + w):
                for dd in (-0.04, 0.04):
                    v.append(P(eixo, s + ds, rr, ze + dz + dd))
        caixa8(v, M["branco"], "mao_francesa")


def respiro(F, u, z):
    """Veneziana triangular/retangular do oitão."""
    fbox(F, u - 0.35, u + 0.35, z - 0.3, z + 0.3, 0, 0.05, M["branco"], "respiro")
    for k in range(6):
        zz = z - 0.24 + k * 0.09
        fbox(F, u - 0.27, u + 0.27, zz, zz + 0.04, 0.05, 0.075, M["branco"], "aleta")


# ----------------------------------------------------------------- a casa
def casa():
    # corpos de parede (lap siding)
    box(1.5, 7.5, 5.0, 13.6, 0, ZE, M["siding"], "ala_garagem")
    box(12.5, 18.5, 5.0, 13.6, 0, ZE, M["siding"], "ala_office")
    box(7.5, 12.5, 5.0, 9.0, 0, ZE, M["siding"], "hall")
    box(7.5, 18.5, 8.5, 22.0, 0, ZE, M["siding"], "corpo")
    box(1.5, 7.5, 8.5, 17.0, 0, ZE, M["siding"], "cozinha")
    box(12.5, 18.5, 17.0, 22.0, 0, ZE, M["siding"], "suite")

    # embasamento de pedra (0,9 m) na fachada da frente e nas laterais visíveis
    box(1.45, 7.55, 4.94, 5.0, 0, 0.9, M["pedra"], "pedra")
    box(12.45, 18.55, 4.94, 5.0, 0, 0.9, M["pedra"], "pedra")
    box(1.44, 1.5, 4.94, 22.0, 0, 0.45, M["pedra"], "pedra")
    box(18.5, 18.56, 4.94, 22.06, 0, 0.45, M["pedra"], "pedra")
    box(7.5, 18.56, 22.0, 22.06, 0, 0.45, M["pedra"], "pedra")
    for (x0, x1, y0, y1) in ((1.42, 7.58, 4.92, 4.96), (12.42, 18.58, 4.92, 4.96)):
        box(x0, x1, y0, y1, 0.9, 0.96, M["branco"], "capa_pedra")

    # telhados: corpo principal (cumeeira em x) + alas frontais e de fundo (cumeeira em y)
    telhado("x", 8.5, 22.0, 1.5, 18.5, ZE, T28, oe=0.5, og0=0.45, og1=0.45)
    volume_oitao("x", 8.5, 22.0, 1.5, 18.5, ZE, T28)
    telhado("y", 1.5, 7.5, 5.0, 13.6, ZE, T40, og0=0.45, og1=0.0, rake1=False)
    volume_oitao("y", 1.5, 7.5, 5.0, 13.6, ZE, T40)
    telhado("y", 12.5, 18.5, 5.0, 13.6, ZE, T40, og0=0.45, og1=0.0, rake1=False)
    volume_oitao("y", 12.5, 18.5, 5.0, 13.6, ZE, T40)
    # entrada: oitão menor que avança sobre a varanda
    telhado("y", 7.5, 12.5, 3.3, 12.8, ZE, T40, oe=0.35, og0=0.35, og1=0.0, rake1=False)
    volume_oitao("y", 7.5, 12.5, 3.3, 12.8, ZE, T40)
    # fundos: oitões da suíte e da varanda gourmet
    telhado("y", 12.5, 18.5, 17.0, 22.0, ZE, T40, og0=0.0, og1=0.45, rake0=False)
    volume_oitao("y", 12.5, 18.5, 17.2, 22.0, ZE, T40)
    telhado("y", 1.5, 7.5, 17.0, 22.0, ZE, T40, og0=0.0, og1=0.45, rake0=False)
    volume_oitao("y", 1.5, 7.5, 17.2, 22.0, ZE, T40)

    # faixas brancas na base dos oitões e mãos-francesas
    for (x0, x1, y) in ((1.5, 7.5, 5.0), (12.5, 18.5, 5.0), (7.5, 12.5, 3.3)):
        box(x0 - 0.06, x1 + 0.06, y - 0.07, y + 0.02, ZE - 0.1, ZE + 0.06, M["branco"], "friso")
        mao_francesa("y", x0 + 0.02, y - 0.45, ZE, -1)
        mao_francesa("y", x1 - 0.02, y - 0.45, ZE, 1)
    for (x0, x1, y) in ((1.5, 7.5, 22.0), (12.5, 18.5, 22.0)):
        box(x0 - 0.06, x1 + 0.06, y - 0.02, y + 0.07, ZE - 0.1, ZE + 0.06, M["branco"], "friso")
    for x in (1.5, 18.5):
        sg = -1 if x < 5 else 1
        box(min(x, x + sg * 0.07), max(x, x + sg * 0.07), 8.44, 22.06, ZE - 0.1, ZE + 0.06, M["branco"], "friso")

    # respiros nos oitões
    respiro(fachada("y", 5.0, -1), 4.5, ZE + 1.25)
    respiro(fachada("y", 5.0, -1), 15.5, ZE + 1.25)
    respiro(fachada("y", 22.0, 1), 15.5, ZE + 1.25)
    respiro(fachada("x", 1.5, -1), 15.25, ZE + 1.9)
    respiro(fachada("x", 18.5, 1), 15.25, ZE + 1.9)

    # cantoneiras brancas nas quinas
    for (x, y) in ((1.5, 5.0), (7.5, 5.0), (12.5, 5.0), (18.5, 5.0), (18.5, 22.0), (12.5, 22.0)):
        box(x - 0.07, x + 0.07, y - 0.07, y + 0.07, 0.9 if y == 5.0 else 0.45, ZE, M["branco"], "cantoneira")

    # ---- frente
    Ff = fachada("y", 5.0, -1)
    portao_garagem(Ff, 2.0, 7.0, 0.0, 2.45)
    luminaria(Ff, 1.75, 2.0); luminaria(Ff, 7.25, 2.0)
    for u0 in (13.3, 14.45, 15.6):                         # janela tripla do home office
        janela(Ff, u0, u0 + 1.0, 1.0, 2.6)
    janela(fachada("y", 5.0, -1), 11.1, 12.1, 1.0, 2.6)
    porta_entrada(Ff, 9.6, 10.6, 0.3, 2.55)
    luminaria(Ff, 9.0, 2.15)

    # ---- lateral direita
    Fd = fachada("x", 18.5, 1)
    janela(Fd, 5.9, 7.5, 1.0, 2.6, grade=(4, 2))
    janela(Fd, 9.3, 10.3, 2.0, 2.7, grade=(3, 1), guilhotina=False)
    janela(Fd, 11.6, 12.7, 1.0, 2.6); janela(Fd, 13.1, 14.2, 1.0, 2.6)
    janela(Fd, 15.7, 16.7, 2.0, 2.7, grade=(3, 1), guilhotina=False)
    janela(Fd, 18.3, 19.6, 1.0, 2.6); janela(Fd, 19.9, 21.2, 1.0, 2.6)

    # ---- lateral esquerda
    Fe = fachada("x", 1.5, -1)
    janela(Fe, 7.0, 9.0, 1.7, 2.6, grade=(4, 1), guilhotina=False)
    janela(Fe, 13.6, 15.9, 1.1, 2.6, grade=(4, 2))
    porta_correr(Fe, 11.3, 12.3, 0.3, 2.5, folhas=1)

    # ---- fundos
    Ft = fachada("y", 22.0, 1)
    porta_correr(Ft, 8.0, 12.0, 0.3, 2.6, folhas=3)
    porta_correr(Ft, 13.3, 17.7, 0.3, 2.6, folhas=3)
    luminaria(Ft, 7.75, 2.2); luminaria(Ft, 12.25, 2.2)

    # ---- varanda de entrada
    box(7.3, 12.7, 3.3, 5.0, 0, 0.3, M["pedra"], "piso_varanda_base")
    box(7.3, 12.7, 3.3, 5.0, 0.3, 0.33, M["porcelanato"], "piso_varanda")
    for k, (y0, z) in enumerate(((2.95, 0.1), (3.12, 0.2))):
        box(9.0, 11.2, y0, 3.3, 0, z, M["pedra"], "degrau")
    for x in (7.7, 12.3):
        coluna(x, 3.65, 0.33, ZE - 0.12)
    box(7.4, 12.6, 3.45, 3.85, ZE - 0.3, ZE, M["branco"], "viga_varanda")
    box(7.5, 12.5, 3.3, 5.0, ZE - 0.02, ZE - 0.0, M["forro"], "forro_varanda")

    # ---- varanda gourmet aberta (fundos/esquerda)
    box(1.5, 7.5, 17.0, 22.0, 0, 0.3, M["pedra"], "base_gourmet")
    box(1.5, 7.5, 17.0, 22.0, 0.3, 0.32, M["porcelanato"], "piso_gourmet")
    box(1.5, 7.5, 17.0, 22.0, ZE - 0.22, ZE - 0.2, M["forro"], "forro_gourmet")
    box(1.5, 7.5, 21.75, 22.05, ZE - 0.45, ZE, M["branco"], "viga")
    box(1.45, 1.75, 17.0, 22.05, ZE - 0.45, ZE, M["branco"], "viga")
    for (x, y) in ((1.65, 21.85), (4.5, 21.85), (1.65, 19.4)):
        coluna(x, y, 0.32, ZE - 0.45, base=False)
    janela(fachada("y", 17.0, 1), 4.2, 7.1, 1.2, 2.4, grade=(4, 1), guilhotina=False)
    porta_correr(fachada("x", 7.5, -1), 17.4, 21.6, 0.32, 2.6, folhas=3)
    # churrasqueira de tijolo + chaminé de pedra
    box(1.75, 3.1, 17.0, 17.75, 0.32, 1.0, M["tijolo"], "churrasqueira")
    box(1.75, 3.1, 17.0, 17.75, 1.0, 1.06, M["pedra"], "tampo")
    box(1.95, 2.9, 17.0, 17.55, 1.06, 1.9, M["preto"], "boca")
    box(1.75, 3.1, 17.0, 17.75, 1.9, ZE - 0.2, M["tijolo"], "coifa")
    box(1.75, 3.1, 17.0, 17.75, ZE, 7.2, M["pedra"], "chamine")
    box(1.65, 3.2, 16.9, 17.85, 7.2, 7.32, M["branco"], "capa_chamine")
    box(2.2, 2.65, 17.2, 17.55, 7.32, 7.55, M["preto"], "chapeu_chamine")
    box(3.1, 5.4, 17.0, 17.6, 0.32, 1.0, M["branco"], "bancada")
    box(3.1, 5.4, 17.0, 17.6, 1.0, 1.04, M["pedra"], "tampo")
    mesa(4.6, 19.6, 1.0, 2.2)

    # floreiras na frente (canteiros com arbustos)
    box(1.5, 7.5, 4.2, 4.94, 0, 0.05, M["terra"], "canteiro") if False else None
    box(12.5, 18.5, 3.9, 4.94, 0, 0.06, M["terra"], "canteiro")
    for x in (12.9, 13.9, 14.9, 15.9, 16.9, 17.9):
        arbusto(x, 4.45, 0.45 + random.random() * 0.12)
    for x in (7.0, 12.95):
        arbusto(x - 0.0, 3.4, 0.35)
    box(1.0, 1.5, 4.0, 10.4, 0, 0.06, M["terra"], "canteiro")
    for y in (4.6, 6.0, 7.4, 8.8):
        arbusto(1.05, y, 0.4)
    box(7.55, 9.0, 4.0, 4.94, 0, 0.06, M["terra"], "canteiro")
    box(11.2, 12.45, 4.0, 4.94, 0, 0.06, M["terra"], "canteiro")
    arbusto(8.0, 4.4, 0.42); arbusto(11.9, 4.4, 0.42)


def coluna(x, y, z0, z1, base=True):
    """Coluna craftsman: pedestal de pedra + fuste branco afunilado."""
    zb = z0
    if base:
        box(x - 0.3, x + 0.3, y - 0.3, y + 0.3, z0, z0 + 1.0, M["pedra"], "pedestal")
        box(x - 0.34, x + 0.34, y - 0.34, y + 0.34, z0 + 1.0, z0 + 1.07, M["branco"], "capa_pedestal")
        zb = z0 + 1.07
    rb, rt = (0.17, 0.12) if base else (0.15, 0.13)
    v = []
    for (r, z) in ((rb, zb), (rt, z1 - 0.12)):
        for dx in (-r, r):
            for dy in (-r, r):
                v.append((x + dx, y + dy, z))
    obj("fuste", [v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]],
        [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)], M["branco"])
    box(x - rt - 0.04, x + rt + 0.04, y - rt - 0.04, y + rt + 0.04, z1 - 0.12, z1, M["branco"], "capitel")


def mesa(cx, cy, w, h):
    box(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, 1.05, 1.1, M["forro"], "mesa")
    for dx in (-w / 2 + 0.08, w / 2 - 0.12):
        for dy in (-h / 2 + 0.08, h / 2 - 0.12):
            box(cx + dx, cx + dx + 0.05, cy + dy, cy + dy + 0.05, 0.32, 1.05, M["preto"], "pe")
    for k in range(3):
        y = cy - h / 2 + 0.35 + k * 0.75
        for x in (cx - w / 2 - 0.5, cx + w / 2 + 0.08):
            box(x, x + 0.42, y - 0.21, y + 0.21, 0.75, 0.8, M["forro"], "assento")
            xe = x if x < cx else x + 0.38
            box(xe, xe + 0.04, y - 0.21, y + 0.21, 0.8, 1.3, M["forro"], "encosto")
            box(x + 0.05, x + 0.37, y - 0.15, y + 0.15, 0.32, 0.75, M["preto"], "pe")


# ----------------------------------------------------------------- terreno
def esfera(nome, loc, raio, mat, desloc=0.3, escala_tex=1.2, sub=4, achata=1.0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=raio, location=loc)
    o = bpy.context.active_object
    o.name = nome
    o.scale = (1, 1, achata)
    tex = bpy.data.textures.new(nome + "_tx", "CLOUDS")
    tex.noise_scale = escala_tex * raio
    tex.noise_depth = 2
    md = o.modifiers.new("d", "DISPLACE"); md.texture = tex; md.strength = raio * desloc
    md.texture_coords = "GLOBAL"
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def arvore(x, y, h=6.0, r=2.2, mat=None):
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.16 * h / 6, radius2=0.08 * h / 6, depth=h * 0.65,
                                    location=(x, y, h * 0.325))
    bpy.context.active_object.data.materials.append(M["tronco"])
    mat = mat or random.choice([M["folha"], M["folha2"]])
    for _ in range(16):
        a = random.uniform(0, 2 * math.pi); d = random.uniform(0, 0.7) * r
        dz = random.uniform(-0.45, 0.45) * r
        esfera("copa", (x + d * math.cos(a), y + d * math.sin(a), h - r * 0.6 + dz), r * random.uniform(0.32, 0.48),
               mat, 0.7, 4.0, sub=3)


def arbusto(x, y, r):
    esfera("arbusto", (x, y, r * 0.75), r, M["arbusto"], 0.35, 2.5, sub=3, achata=0.85)


def terreno():
    # gramado com grama de verdade (fios) + rua, calçada e guia
    box(-40, 60, -1.0, 60, -0.02, 0.0, M["grama"], "gramado")
    box(-40, 60, -40, -9.0, -0.02, 0.0, M["grama"], "gramado_vizinho")
    box(-40, 60, -9.0, -3.0, -0.18, -0.15, M["asfalto"], "rua")
    box(-40, 60, -3.0, -2.85, -0.15, 0.0, M["guia"], "guia")
    box(-40, 60, -2.85, -1.0, 0.0, 0.02, M["calcada"], "calcada")
    # entrada de carros e caminho de pedra
    box(1.5, 7.5, -2.85, 5.0, 0.0, 0.025, M["pavers"], "entrada_carros")
    box(9.5, 10.7, -1.0, 2.95, 0.0, 0.025, M["calcada"], "caminho")
    # deck dos fundos
    box(7.5, 18.5, 22.0, 24.2, 0, 0.28, M["deck"], "deck")
    for x in (8.5, 10.5, 12.5, 14.5, 16.5):
        box(x, x + 0.06, 24.2, 24.26, 0, 0.28, M["deck"], "testa_deck")
    # cerca de madeira no quintal (laterais e fundo) e portões
    cerca((0.05, 10.5), (0.05, 29.95))
    cerca((19.95, 8.5), (19.95, 29.95))
    cerca((0.05, 29.95), (19.95, 29.95))
    cerca((0.05, 10.5), (1.5, 10.5)); cerca((18.5, 8.5), (19.95, 8.5))
    # espaço de brincar
    box(8.2, 14.6, 25.2, 29.0, 0, 0.04, M["areia"], "playground")
    for (x0, x1, y0, y1) in ((8.15, 14.65, 25.15, 25.25), (8.15, 14.65, 28.95, 29.05), (8.15, 8.25, 25.15, 29.05), (14.55, 14.65, 25.15, 29.05)):
        box(x0, x1, y0, y1, 0, 0.18, M["deck"], "borda")
    casinha(9.7, 27.5)
    balanco(12.8, 27.9)
    # espaço do cachorro
    casinha_cao(1.7, 27.9)
    box(0.5, 6.0, 24.9, 29.3, 0, 0.012, M["pavers"], "pet") if False else None
    # horta
    for i in range(3):
        y = 25.4 + i * 1.3
        box(16.0, 19.2, y, y + 0.8, 0, 0.4, M["cerca"], "canteiro_horta")
        box(16.05, 19.15, y + 0.05, y + 0.75, 0.4, 0.42, M["terra"], "terra")
        for k in range(6):
            esfera("horta", (16.3 + k * 0.5, y + 0.4, 0.5), 0.16, M["folha2"], 0.4, 3, sub=2)
    # árvores do lote e do entorno
    arvore(16.0, 1.6, 5.5, 2.0); arvore(7.0, 28.6, 5.2, 1.7)
    arvore(19.3, 19.8, 5.0, 1.5)
    for k in range(14):
        arvore(-14 + k * 3.6 + random.uniform(-0.8, 0.8), 52 + random.uniform(-2, 3), random.uniform(7, 10), random.uniform(2.3, 3.2))
    for k in range(5):
        arvore(-9 + random.uniform(-1, 1), 6 + k * 6.5, random.uniform(6, 8), random.uniform(2, 2.8))
        arvore(29 + random.uniform(-1, 1), 6 + k * 6.5, random.uniform(6, 8), random.uniform(2, 2.8))
    # caixa de correio americana
    box(8.55, 8.65, -0.7, -0.6, 0, 1.0, M["branco"], "poste_correio")
    box(8.45, 8.75, -0.95, -0.45, 1.0, 1.22, M["preto"], "correio")


def grama_fios(xr, yr, n):
    bpy.ops.mesh.primitive_plane_add(size=1, location=((xr[0] + xr[1]) / 2, (yr[0] + yr[1]) / 2, 0.002))
    p = bpy.context.active_object
    p.scale = (xr[1] - xr[0], yr[1] - yr[0], 1)
    bpy.ops.object.transform_apply(scale=True)
    p.data.materials.append(M["grama"])
    ps = p.modifiers.new("grama", "PARTICLE_SYSTEM").particle_system
    s = ps.settings
    s.type = "HAIR"; s.count = n; s.hair_length = 0.07
    s.use_advanced_hair = False
    s.child_type = "INTERPOLATED"; s.child_percent = 6; s.rendered_child_count = 6
    s.child_length = 1.0; s.roughness_2 = 0.6; s.roughness_endpoint = 0.04
    s.root_radius = 0.6; s.tip_radius = 0.0; s.radius_scale = 0.004
    s.material = 1
    s.factor_random = 0.04
    s.normal_factor = 1.0
    s.brownian_factor = 0.0
    s.length_random = 0.5


def cerca(a, b):
    ax, ay = a; bx, by = b
    L = math.hypot(bx - ax, by - ay)
    n = max(1, int(L / 2.4))
    for i in range(n + 1):
        t = i / n
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        box(x - 0.06, x + 0.06, y - 0.06, y + 0.06, 0, 1.6, M["cerca"], "mourao")
    for k in range(9):
        z = 0.12 + k * 0.165
        if ax == bx:
            box(ax - 0.02, ax + 0.02, ay, by, z, z + 0.13, M["cerca"], "ripa")
        else:
            box(ax, bx, ay - 0.02, ay + 0.02, z, z + 0.13, M["cerca"], "ripa")


def casinha(x, y):
    box(x - 0.9, x + 0.9, y - 0.9, y + 0.9, 0.04, 1.3, M["vermelho"], "casinha")
    telhado("y", x - 0.9, x + 0.9, y - 0.9, y + 0.9, 1.3, 1.0, oe=0.15, og0=0.15, og1=0.15)
    volume_oitao("y", x - 0.9, x + 0.9, y - 0.9, y + 0.9, 1.3, 1.0, M["branco"])
    F = fachada("y", y - 0.9, -1)
    fbox(F, x - 0.25, x + 0.25, 0.04, 1.05, 0, 0.02, M["porta"], "porta")
    janela(F, x + 0.4, x + 0.75, 0.6, 0.95, grade=(2, 2), guilhotina=False)


def balanco(x, y):
    for dx in (-1.3, 1.3):
        for dy in (-0.6, 0.6):
            v = []
            for (px, py, z) in ((x + dx, y + dy, 0), (x + dx, y, 2.2)):
                for ex in (-0.05, 0.05):
                    for ey in (-0.05, 0.05):
                        v.append((px + ex, py + ey, z))
            caixa8(v, M["cerca"], "perna")
    box(x - 1.4, x + 1.4, y - 0.06, y + 0.06, 2.15, 2.27, M["cerca"], "travessa")
    for sx in (-0.55, 0.55):
        box(x + sx - 0.25, x + sx + 0.25, y - 0.12, y + 0.12, 0.45, 0.5, M["azul"], "assento")
        for e in (-0.22, 0.22):
            box(x + sx + e - 0.008, x + sx + e + 0.008, y - 0.008, y + 0.008, 0.5, 2.15, M["preto"], "corda")


def casinha_cao(x, y):
    box(x - 0.7, x + 0.7, y - 0.6, y + 0.6, 0.0, 0.8, M["cerca"], "casinha_cao")
    telhado("x", y - 0.6, y + 0.6, x - 0.7, x + 0.7, 0.8, 0.8, oe=0.12, og0=0.12, og1=0.12)
    volume_oitao("x", y - 0.6, y + 0.6, x - 0.7, x + 0.7, 0.8, 0.8, M["cerca"])
    fbox(fachada("x", x + 0.7, 1), y - 0.22, y + 0.22, 0.0, 0.6, 0, 0.01, M["preto"], "entrada")


# ----------------------------------------------------------------- luz e câmera
def luz_e_ceu():
    w = bpy.data.worlds.new("ceu"); cena.world = w; w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky"); sky.sky_type = "NISHITA"
    sky.sun_disc = False; sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(200)
    sky.air_density = 1.0; sky.dust_density = 0.6; sky.altitude = 600
    bg = nt.nodes["Background"]; bg.inputs["Strength"].default_value = 0.35
    nt.links.new(sky.outputs[0], bg.inputs[0])
    sol = bpy.data.lights.new("sol", "SUN"); sol.energy = 4.2; sol.angle = math.radians(1.2)
    sol.color = (1.0, 0.95, 0.87)
    so = bpy.data.objects.new("sol", sol); cena.collection.objects.link(so)
    # luz vindo da frente-esquerda, de cima
    d = Vector((0.55, 0.85, -0.75)).normalized()
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


CAMERAS = {
    "frente":       ((0.5, -8.0, 1.7), (10.5, 8.0, 3.0), 22),
    "aerea_frente": ((-9.0, -17.0, 13.0), (10.0, 11.0, 1.5), 28),
    "aerea_fundo":  ((24.0, 41.0, 14.0), (9.0, 18.5, 1.0), 26),
    "entrada":      ((11.5, -4.2, 1.6), (9.2, 4.0, 2.2), 24),
}


def camera(nome):
    loc, alvo, lente = CAMERAS[nome]
    c = bpy.data.cameras.new("cam"); c.lens = lente; c.sensor_width = 36
    o = bpy.data.objects.new("cam", c); cena.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cena.camera = o


def render():
    cena.render.engine = "CYCLES"
    cena.cycles.device = "CPU"
    cena.cycles.samples = SAMPLES
    cena.cycles.use_denoising = True
    cena.cycles.max_bounces = 6
    cena.render.resolution_x, cena.render.resolution_y = RES
    cena.render.resolution_percentage = 100
    cena.view_settings.view_transform = "AgX"
    cena.view_settings.look = "AgX - Medium High Contrast"
    cena.view_settings.exposure = 0.0
    cena.render.film_transparent = False
    cena.render.image_settings.file_format = "PNG"
    cena.render.filepath = SAIDA
    bpy.ops.render.render(write_still=True)


casa()
terreno()
luz_e_ceu()
camera(CAM)
render()
