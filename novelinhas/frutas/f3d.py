"""Personagens de fruta em 3D, feitos só com código (Blender como módulo Python: pip install bpy).

Cada fruta é um objeto vazio (raiz, apoiada no chão em z=0) com o corpo, o rosto e os bracinhos pendurados nele.
A classe Fruta guarda as peças que se mexem (pálpebras, sobrancelhas, boca, mãos) para a animação quadro a quadro.
"""
import math
import random

import bpy  # noqa: I001 (o bpy precisa vir antes do bmesh)
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


# ------------------------------------------------------------------ básicos
def limpa():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(nome, cor, rough=0.4, sss=0.0, spec=0.5, emis=None, forca=1.0, coat=0.0, alpha=1.0, metal=0.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.08
    b.inputs["Specular IOR Level"].default_value = spec
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    if emis:
        b.inputs["Emission Color"].default_value = (*emis, 1)
        b.inputs["Emission Strength"].default_value = forca
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    return m


def relevo(m, escala=18, forca=0.08, tipo="noise"):
    """Bump procedural na pele (tira a cara de plástico)."""
    nt = m.node_tree
    if tipo == "voronoi":
        tx = nt.nodes.new("ShaderNodeTexVoronoi")
        tx.feature = "DISTANCE_TO_EDGE"
        tx.inputs["Scale"].default_value = escala
        saida = tx.outputs["Distance"]
    else:
        tx = nt.nodes.new("ShaderNodeTexNoise")
        tx.inputs["Scale"].default_value = escala
        tx.inputs["Detail"].default_value = 6
        saida = tx.outputs["Fac"]
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = forca
    nt.links.new(saida, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    return m


def objeto(nome, malha, mats=(), pai=None):
    ob = bpy.data.objects.new(nome, malha)
    bpy.context.scene.collection.objects.link(ob)
    for m in mats:
        ob.data.materials.append(m)
    if pai is not None:
        ob.parent = pai
    return ob


def malha_esfera(nome, r=1.0, seg=48, anel=32, suave=True):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=anel, radius=r)
    bm.to_mesh(me)
    bm.free()
    if suave:
        for p in me.polygons:
            p.use_smooth = True
    return me


def esfera(nome, r=1.0, seg=48, anel=32, mats=(), pai=None, loc=(0, 0, 0), escala=(1, 1, 1), suave=True):
    ob = objeto(nome, malha_esfera(nome, r, seg, anel, suave), mats, pai)
    ob.location = loc
    ob.scale = escala
    return ob


def vazio(nome, pai=None, loc=(0, 0, 0)):
    ob = bpy.data.objects.new(nome, None)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = pai
    ob.location = loc
    return ob


def subdiv(ob, n=2):
    md = ob.modifiers.new("sub", "SUBSURF")
    md.levels = n
    md.render_levels = n


def deforma(ob, f):
    """f(Vector) -> Vector aplicado a cada vértice."""
    for v in ob.data.vertices:
        v.co = f(v.co.copy())


def mira(ob, normal, frente=Vector((0, -1, 0))):
    """Gira o objeto para que a sua 'frente' (-Y) aponte para a normal."""
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = frente.rotation_difference(normal)


# ------------------------------------------------------------------ rosto
def palpebra(nome, pai, r, pele):
    """Meia esfera (cúpula de cima) da cor da pele; girando em X ela abre e fecha o olho."""
    me = malha_esfera(nome, r * 1.06, 40, 24)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context="VERTS")
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=r * 0.05)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return objeto(nome, me, [pele], pai)


def olho(nome, pai, r, iris, pele, cilios=False, lado=1):
    """Olho de desenho: globo, íris, pupila, dois brilhos e a pálpebra. A frente é -Y."""
    piv = vazio(nome, pai)
    branco = mat(nome + "_b", (0.95, 0.94, 0.92), rough=0.15, coat=0.6)
    esfera(nome + "_globo", r, mats=[branco], pai=piv)
    ir = vazio(nome + "_mira", piv)   # gira para o olhar
    esfera(nome + "_iris", r * 0.6, mats=[mat(nome + "_i", iris, rough=0.2, coat=1.0)], pai=ir,
           loc=(0, -r * 0.74, 0), escala=(1, 0.42, 1))
    esfera(nome + "_pup", r * 0.32, mats=[mat(nome + "_p", (0.01, 0.01, 0.01), rough=0.1, coat=1.0)], pai=ir,
           loc=(0, -r * 0.92, 0), escala=(1, 0.3, 1))
    bri = mat(nome + "_l", (1, 1, 1), emis=(1, 1, 1), forca=4)
    esfera(nome + "_bri", r * 0.13, 16, 12, mats=[bri], pai=ir, loc=(r * 0.2 * lado, -r * 1.0, r * 0.22))
    esfera(nome + "_bri2", r * 0.06, 16, 12, mats=[bri], pai=ir, loc=(-r * 0.15 * lado, -r * 1.0, -r * 0.16))
    tampa = palpebra(nome + "_palp", piv, r, pele)
    tampa.rotation_euler = (math.radians(-55), 0, 0)
    if cilios:
        m_c = mat(nome + "_c", (0.03, 0.01, 0.01), rough=0.5)
        for k in range(4):
            a = math.radians(-50 + 22 * k) * lado
            c = esfera(nome + f"_cil{k}", r * 0.06, 12, 8, mats=[m_c], pai=tampa,
                       loc=(math.sin(a) * r * 1.02, -math.cos(a) * r * 0.25, r * 0.98),
                       escala=(0.6, 0.6, 3.4))
            c.rotation_euler = (math.radians(-30), -a * 0.9, 0)
    return piv, tampa, ir


def boca(nome, pai, larg, pele_escura=(0.14, 0.01, 0.03), lingua=(0.88, 0.3, 0.34)):
    """Boca com shape keys: 'aberta', 'sorriso', 'triste' e 'o' (para o lip-sync e as expressões)."""
    piv = vazio(nome, pai)
    me = malha_esfera(nome + "_cav", 1, 40, 20)
    cav = objeto(nome + "_cav", me, [mat(nome + "_d", pele_escura, rough=0.6)], piv)
    hz, hy = 0.09, 0.3
    base = [Vector((v.co.x * larg, v.co.y * larg * hy, v.co.z * larg * hz)) for v in me.vertices]
    for v, b in zip(me.vertices, base):
        v.co = b
    cav.shape_key_add(name="Basis", from_mix=False)

    def chave(nm, f):
        k = cav.shape_key_add(name=nm, from_mix=False)
        for i, b in enumerate(base):
            k.data[i].co = f(b.copy())
    X = lambda b: b.x / larg   # -1..1 de canto a canto
    chave("aberta", lambda b: Vector((b.x * 0.9, b.y, b.z * 3.0 - (larg * 0.3 if b.z < 0 else 0) * max(0.0, 1 - X(b) ** 2) ** 0.7)))
    chave("sorriso", lambda b: Vector((b.x * 1.1, b.y, b.z * 1.6 + larg * 0.4 * X(b) ** 2 - larg * 0.12 - (larg * 0.12 if b.z < 0 else 0) * (1 - X(b) ** 2))))
    chave("triste", lambda b: Vector((b.x * 0.88, b.y, b.z * 1.3 - larg * 0.36 * X(b) ** 2 + larg * 0.1 + (larg * 0.08 if b.z > 0 else 0) * (1 - X(b) ** 2))))
    chave("o", lambda b: Vector((b.x * 0.5, b.y, b.z * 3.6)))
    lin = esfera(nome + "_lin", 1, 24, 12, mats=[mat(nome + "_lg", lingua, rough=0.35, sss=0.3)], pai=piv,
                 loc=(0, -larg * 0.06, -larg * 0.05), escala=(larg * 0.5, larg * 0.22, larg * 0.08))
    return piv, cav, lin


# ------------------------------------------------------------------ personagem
class Fruta:
    def __init__(self, nome, corpo_fn, pele, rosto, loc=(0, 0, 0), alt=1.0, bracos=None, extras=None, palp0=0.0):
        self.nome = nome
        self.palp0 = palp0
        self.raiz = vazio(nome, loc=loc)
        self.base_loc = Vector(loc)
        self.corpo_piv = vazio(nome + "_cp", self.raiz)   # balanço e squash do corpo
        self.pele = pele
        self.corpo = corpo_fn(nome, self.corpo_piv, pele)
        self.alt = alt
        me = self.corpo.data
        self.bvh = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [p.vertices[:] for p in me.polygons])
        self.olhos, self.sobr = [], []
        self._rosto(**rosto)
        self.maos = []
        if bracos:
            self._bracos(**bracos)
        if extras:
            extras(self)
        self.raiz.scale = (alt, alt, alt)
        self.estado = {}

    def superficie(self, x, z):
        """Ponto e normal na frente do corpo (raio a partir de -Y)."""
        hit = self.bvh.ray_cast(Vector((x, -10, z)), Vector((0, 1, 0)))
        return hit[0], hit[1]

    def _rosto(self, olho_x=0.27, olho_z=1.35, olho_r=0.2, iris=(0.3, 0.14, 0.05), cilios=False,
               sob=(0.3, 0.02, 0.03), sob_larg=0.15, boca_z=0.95, boca_larg=0.16, blush=(1.0, 0.35, 0.4),
               blush_x=0.47, blush_z=1.05, olhar=0.0):
        n = self.nome
        for lado in (-1, 1):
            p, nrm = self.superficie(olho_x * lado, olho_z)
            piv, tampa, ir = olho(n + f"_olho{lado}", self.corpo_piv, olho_r, iris, self.pele, cilios, lado)
            piv.location = p - nrm * olho_r * 0.45
            mira(piv, (nrm + Vector((0, -1.2, 0))).normalized())
            self.olhos.append((piv, tampa, ir))
            ps, ns = self.superficie(olho_x * lado * 1.05, olho_z + olho_r * 1.55)
            s = esfera(n + f"_sob{lado}", 1, 24, 12, mats=[mat(n + f"_sb{lado}", sob, rough=0.6)], pai=self.corpo_piv,
                       escala=(sob_larg, sob_larg * 0.25, sob_larg * 0.26))
            s.location = ps + ns * 0.01
            s.rotation_euler = (0, math.radians(-8 * lado), 0)
            self.sobr.append((s, s.location.copy(), lado))
            if blush:
                pb, nb = self.superficie(blush_x * lado, blush_z)
                b = esfera(n + f"_bl{lado}", 1, 24, 12, mats=[mat(n + f"_blm{lado}", blush, rough=0.7, alpha=0.4)],
                           pai=self.corpo_piv, escala=(0.11, 0.025, 0.065))
                b.location = pb
                mira(b, nb)
        pb, nb = self.superficie(0, boca_z)
        self.boca = boca(n + "_boca", self.corpo_piv, boca_larg)
        self.boca[0].location = pb + nb * 0.005
        mira(self.boca[0], nb)

    def _bracos(self, z=0.8, cor=None, mao=None, comp=0.55):
        """Bracinhos de tubo com mãozinha redonda (as mãos ficam livres para a animação)."""
        n = self.nome
        m_b = mat(n + "_braco", cor or (0.5, 0.05, 0.05), rough=0.45, sss=0.1)
        m_m = mat(n + "_maom", mao or cor or (0.5, 0.05, 0.05), rough=0.45, sss=0.1)
        for lado in (-1, 1):
            # ombro: ponto na lateral do corpo
            hit = self.bvh.ray_cast(Vector((10 * lado, -0.05, z)), Vector((-lado, 0, 0)))
            ombro = hit[0] - Vector((0.04 * lado, 0, 0))
            cu = bpy.data.curves.new(n + f"_br{lado}", "CURVE")
            cu.dimensions = "3D"
            cu.bevel_depth = 0.045
            cu.bevel_resolution = 6
            cu.use_fill_caps = True
            sp = cu.splines.new("NURBS")
            sp.points.add(3)
            sp.use_endpoint_u = True
            sp.order_u = 3
            ob = objeto(n + f"_br{lado}", cu, [m_b], self.corpo_piv)
            mao_ob = esfera(n + f"_mao{lado}", 0.1, 24, 16, mats=[m_m], pai=self.corpo_piv, escala=(1, 0.8, 1.1))
            dedo = esfera(n + f"_ded{lado}", 0.045, 16, 10, mats=[m_m], pai=mao_ob, loc=(-0.07 * lado, -0.04, 0.05),
                          escala=(1, 1, 1.4))
            self.maos.append(dict(lado=lado, ombro=ombro, spline=sp, mao=mao_ob, comp=comp))
            self.mao(lado, (ombro.x + 0.2 * lado, ombro.y - 0.05, ombro.z - 0.4))

    def mao(self, lado, pos):
        """Coloca a mão (lado -1 = direita da personagem, à esquerda na tela) em pos (coordenadas do corpo)."""
        b = next(b for b in self.maos if b["lado"] == lado)
        o, p = b["ombro"], Vector(pos)
        meio = (o + p) / 2 + Vector((0.12 * lado, -0.02, -0.05))
        pts = [o, o.lerp(meio, 0.6), meio.lerp(p, 0.5), p]
        for sp, q in zip(b["spline"].points, pts):
            sp.co = (*q, 1)
        b["mao"].location = p

    # -------------------------------------------------- animação
    def pose(self, piscar=0.0, abertura=0.0, sorriso=0.0, triste=0.0, o=0.0, sob=0.0, sob_raiva=0.0,
             olhar=(0.0, 0.0), inclina=0.0, pulo=0.0, squash=0.0, gira=0.0, palp=None):
        """piscar 0..1, abertura 0..1 (fala), sorriso/triste 0..1, sob -1..1 (sobe/desce),
        sob_raiva 0..1 (franze), olhar (x, z) em radianos, inclina (rad), pulo (unidades), squash (+achata)."""
        palp = self.palp0 if palp is None else palp
        for piv, tampa, ir in self.olhos:
            aberto = math.radians(-55 + 30 * palp)
            tampa.rotation_euler = (aberto + (math.radians(95) - aberto) * piscar, 0, 0)
            ir.rotation_euler = (olhar[1], 0, olhar[0])
        for s, loc0, lado in self.sobr:
            s.location = loc0 + Vector((0, 0, 0.07 * sob - 0.05 * sob_raiva))
            s.rotation_euler = (0, math.radians(-8 * lado + 28 * sob_raiva * lado - 16 * triste * lado), 0)
        piv, cav, lin = self.boca
        ks = cav.data.shape_keys.key_blocks
        ks["aberta"].value = abertura
        ks["sorriso"].value = sorriso
        ks["triste"].value = triste
        ks["o"].value = o
        lin.location.z = -0.02 - 0.06 * abertura
        cp = self.corpo_piv
        cp.location = (0, 0, pulo)
        sz = 1 - squash
        cp.scale = (1 / math.sqrt(sz), 1 / math.sqrt(sz), sz)
        cp.rotation_euler = (0, inclina, gira)


# ------------------------------------------------------------------ corpos
def perfil_morango(t):
    """Raio do morango na altura t (0 = ponta de baixo, 1 = topo): ombros largos em cima, ponta arredondada."""
    t = min(max(t, 0.0), 1.0)
    return math.sin(math.pi * t) ** 0.55 * (0.42 + 0.62 * t)


def corpo_morango(nome, pai, pele, H=2.3, seed=1, n_sem=300, r_sem=0.028):
    corpo = objeto(nome + "_corpo", malha_esfera(nome + "_corpo", 1, 64, 48), [pele], pai)

    def forma(v):
        t = (v.z + 1) / 2
        h = Vector((v.x, v.y, 0))
        d = h.normalized() if h.length > 1e-6 else Vector((0, 0, 0))
        R = perfil_morango(t)
        return Vector((d.x * R, d.y * R * 0.9, t * H))
    deforma(corpo, forma)
    subdiv(corpo, 1)
    sem = mat(nome + "_sem", (0.96, 0.8, 0.3), rough=0.3, coat=0.5)
    rnd = random.Random(seed)
    golden = math.pi * (3 - math.sqrt(5))
    n = n_sem
    for i in range(n):
        t = 0.05 + 0.88 * (i + 0.5) / n
        a = i * golden + rnd.uniform(-0.1, 0.1)
        R = perfil_morango(t)
        p = Vector((math.cos(a) * R, math.sin(a) * R * 0.9, t * H))
        if p.y < -0.2 and 0.62 * H > p.z > 0.25 * H and abs(p.x) < 0.66:
            continue   # rosto limpo
        esfera(nome + f"_s{i}", r_sem, 10, 6, mats=[sem], pai=pai, loc=p * 1.0, escala=(0.8, 0.8, 1.45))
    folha = mat(nome + "_folha", (0.1, 0.45, 0.08), rough=0.45, sss=0.2)
    relevo(folha, 30, 0.1)
    for k in range(8):
        a = k / 8 * 2 * math.pi + 0.2
        f = esfera(nome + f"_f{k}", 1, 24, 12, mats=[folha], pai=pai, escala=(0.42, 0.15, 0.03))
        deforma(f, lambda v: Vector((v.x, v.y * (1 - 0.65 * max(0, v.x)), v.z - 0.9 * max(0, v.x) ** 2)))
        f.location = (math.cos(a) * 0.32, math.sin(a) * 0.3, H - 0.02)
        f.rotation_euler = (0, math.radians(8), a)
    cab = esfera(nome + "_cabo", 0.07, 16, 8, mats=[folha], pai=pai, loc=(0.02, 0, H + 0.15), escala=(1, 1, 2.6))
    cab.rotation_euler = (0.25, 0.3, 0)
    return corpo


def corpo_uva(nome, pai, pele):
    corpo = objeto(nome + "_corpo", malha_esfera(nome + "_corpo", 1, 64, 48), [pele], pai)
    deforma(corpo, lambda v: Vector((v.x * 0.95, v.y * 0.9, (v.z + 1) * 1.05)))
    cab = esfera(nome + "_cabo", 0.07, 16, 8, mats=[mat(nome + "_cab", (0.35, 0.25, 0.1), rough=0.7)], pai=pai,
                 loc=(0, 0, 2.18), escala=(1, 1, 2.4))
    f = esfera(nome + "_folha", 1, 24, 12, mats=[mat(nome + "_fo", (0.15, 0.5, 0.1), rough=0.45, sss=0.15)], pai=pai,
               loc=(0.28, 0, 2.25), escala=(0.34, 0.2, 0.03))
    f.rotation_euler = (0, math.radians(-25), 0.3)
    return corpo


def mat_abacaxi(nome):
    """Casca de abacaxi: losangos dourados com sulcos verde-escuros, feitos com dois senos cruzados."""
    m = mat(nome, (0.8, 0.55, 0.12), rough=0.5, sss=0.05)
    nt = m.node_tree
    N = nt.nodes
    L = nt.links
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])

    def op(tipo, a, b=None, v=None):
        n = N.new("ShaderNodeMath")
        n.operation = tipo
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                L.new(x, n.inputs[i])
        return n.outputs[0]
    ang = op("ARCTAN2", sep.outputs["Y"], sep.outputs["X"])
    u = op("ADD", op("MULTIPLY", ang, 5.0), op("MULTIPLY", sep.outputs["Z"], 6.5))
    v = op("SUBTRACT", op("MULTIPLY", ang, 5.0), op("MULTIPLY", sep.outputs["Z"], 6.5))
    pad = op("MULTIPLY", op("ABSOLUTE", op("SINE", u)), op("ABSOLUTE", op("SINE", v)))
    pad = op("POWER", pad, 0.4)
    rampa = N.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].position = 0.12
    rampa.color_ramp.elements[0].color = (0.1, 0.12, 0.02, 1)
    e = rampa.color_ramp.elements.new(0.4)
    e.color = (0.55, 0.42, 0.06, 1)
    rampa.color_ramp.elements[2].position = 0.9
    rampa.color_ramp.elements[2].color = (0.95, 0.58, 0.08, 1)
    L.new(pad, rampa.inputs[0])
    L.new(rampa.outputs[0], N["Principled BSDF"].inputs["Base Color"])
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    L.new(pad, bump.inputs["Height"])
    L.new(bump.outputs["Normal"], N["Principled BSDF"].inputs["Normal"])
    return m


def corpo_abacaxi(nome, pai, pele, H=2.5):
    corpo = objeto(nome + "_corpo", malha_esfera(nome + "_corpo", 1, 64, 48), [pele], pai)

    def forma(v):
        t = (v.z + 1) / 2
        h = Vector((v.x, v.y, 0))
        d = h.normalized() if h.length > 1e-6 else Vector((0, 0, 0))
        R = math.sin(math.pi * t) ** 0.7 * 0.82 * (1 - 0.08 * t)
        return Vector((d.x * R, d.y * R * 0.92, t * H))
    deforma(corpo, forma)
    subdiv(corpo, 1)
    # coroa: folhas compridas e pontudas em espiral
    folha = mat(nome + "_coroa", (0.15, 0.4, 0.15), rough=0.5, sss=0.1)
    relevo(folha, 40, 0.15)
    rnd = random.Random(4)
    for k in range(22):
        a = k * 2.4
        incl = 0.15 + 0.75 * (1 - k / 22)
        comp = 0.55 + 0.6 * (k / 22) + rnd.uniform(-0.08, 0.08)
        f = esfera(nome + f"_fl{k}", 1, 16, 10, mats=[folha], pai=pai, escala=(comp, 0.09, 0.02))
        deforma(f, lambda v, c=comp: Vector((v.x + 1, v.y * (1 - 0.95 * max(0, v.x)), v.z + 0.25 * (v.x + 1) ** 2)))
        f.location = (math.cos(a) * 0.1, math.sin(a) * 0.1, H - 0.08)
        f.rotation_euler = (0, -math.pi / 2 + incl, a)
    return corpo


# ------------------------------------------------------------------ acessórios
def oculos_escuros(fr, z_extra=0.55):
    """Óculos escuros levantados na testa (o pai 'descolado')."""
    n = fr.nome
    preto = mat(n + "_oc", (0.01, 0.01, 0.012), rough=0.05, coat=1.0)
    p, nrm = fr.superficie(0, 1.35 + z_extra)
    piv = vazio(n + "_oculos", fr.corpo_piv)
    piv.location = p + nrm * 0.02
    mira(piv, nrm)
    for lado in (-1, 1):
        esfera(n + f"_lente{lado}", 1, 32, 16, mats=[preto], pai=piv, loc=(0.24 * lado, -0.02, 0),
               escala=(0.2, 0.05, 0.14))
    esfera(n + "_ponte", 1, 16, 8, mats=[preto], pai=piv, loc=(0, -0.03, 0.04), escala=(0.08, 0.02, 0.02))
    return piv


def corrente(fr, z=0.75, cor=(1.0, 0.75, 0.25)):
    """Corrente de ouro no 'pescoço'."""
    n = fr.nome
    ouro = mat(n + "_ouro", cor, rough=0.2, metal=1.0)
    for k in range(28):
        a = math.pi * (0.15 + 0.7 * k / 27)
        hit = fr.bvh.ray_cast(Vector((math.cos(a) * 10, -math.sin(a) * 10, z)), Vector((-math.cos(a), math.sin(a), 0)))
        if hit[0] is None:
            continue
        p = hit[0] + hit[1] * 0.02 - Vector((0, 0, 0.12 * math.sin(a) ** 4))
        e = esfera(n + f"_elo{k}", 0.035, 12, 8, mats=[ouro], pai=fr.corpo_piv, loc=p, escala=(1.4, 1, 0.8))


def laco(fr, cor=(1.0, 0.4, 0.62), z=2.0, x=0.42):
    n = fr.nome
    m = mat(n + "_laco", cor, rough=0.4, sss=0.1)
    piv = vazio(n + "_laco", fr.corpo_piv, (x, -0.25, z))
    piv.rotation_euler = (0.1, -0.6, 0)
    piv.scale = (1.6, 1.6, 1.6)
    for lado in (-1, 1):
        a = esfera(n + f"_lc{lado}", 1, 24, 12, mats=[m], pai=piv, loc=(0.15 * lado, 0, 0), escala=(0.17, 0.07, 0.12))
        a.rotation_euler = (0, 0.3 * lado, 0)
    esfera(n + "_lcn", 0.06, 16, 8, mats=[m], pai=piv)


# ------------------------------------------------------------------ elenco
def moranga(loc=(0, 0, 0), alt=1.0):
    pele = relevo(mat("moranga_pele", (0.78, 0.04, 0.07), rough=0.32, sss=0.3, coat=0.35), 18, 0.08)
    return Fruta("moranga", corpo_morango, pele,
                 dict(olho_x=0.27, olho_z=1.38, olho_r=0.2, iris=(0.3, 0.14, 0.05), cilios=True, boca_z=0.98,
                      boca_larg=0.22, blush_z=1.1),
                 loc=loc, alt=alt, bracos=dict(z=0.95, cor=(0.62, 0.03, 0.06)))


def gradiente_z(m, cores, z0=0.0, z1=2.3):
    """Cor da pele variando com a altura (ex.: morango mais claro perto das folhas)."""
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = z0
    mr.inputs["From Max"].default_value = z1
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    el = rampa.color_ramp.elements
    el[0].position, el[0].color = cores[0][0], (*cores[0][1], 1)
    el[1].position, el[1].color = cores[-1][0], (*cores[-1][1], 1)
    for pos, c in cores[1:-1]:
        e = el.new(pos)
        e.color = (*c, 1)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], rampa.inputs[0])
    nt.links.new(rampa.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def moranga_real(loc=(0, 0, 0), alt=1.0):
    """Versão mais realista: olhos menores, pele com gradiente e muitas sementes pequenas."""
    pele = relevo(mat("moranga_pele", (0.7, 0.02, 0.04), rough=0.22, sss=0.45, coat=0.6), 40, 0.12, "voronoi")
    gradiente_z(pele, [(0.0, (0.45, 0.0, 0.02)), (0.55, (0.7, 0.02, 0.04)), (0.9, (0.85, 0.2, 0.1)), (1.0, (0.9, 0.85, 0.55))])
    corpo = lambda n, p, pl: corpo_morango(n, p, pl, n_sem=650, r_sem=0.018)
    return Fruta("moranga", corpo, pele,
                 dict(olho_x=0.24, olho_z=1.4, olho_r=0.15, iris=(0.22, 0.1, 0.04), cilios=True, boca_z=1.02,
                      boca_larg=0.19, blush=None, sob=(0.2, 0.01, 0.02), sob_larg=0.12),
                 loc=loc, alt=alt, bracos=dict(z=0.95, cor=(0.55, 0.03, 0.05)), palp0=0.2)


def uvinha(loc=(0, 0, 0), alt=0.45):
    pele = mat("uvinha_pele", (0.24, 0.06, 0.34), rough=0.2, sss=0.35, coat=0.7)
    return Fruta("uvinha", corpo_uva, pele,
                 dict(olho_x=0.3, olho_z=1.2, olho_r=0.25, iris=(0.12, 0.38, 0.16), cilios=False, sob=(0.12, 0.02, 0.15),
                      boca_z=0.8, boca_larg=0.2, blush_x=0.52, blush_z=0.92),
                 loc=loc, alt=alt, bracos=dict(z=0.75, cor=(0.2, 0.05, 0.3), comp=0.4),
                 extras=lambda f: laco(f), palp0=-0.6)


def abacaxi(loc=(0, 0, 0), alt=1.0):
    pele = mat_abacaxi("abacaxi_pele")
    def extras(f):
        oculos_escuros(f)
        corrente(f)
    return Fruta("abacaxi", corpo_abacaxi, pele,
                 dict(olho_x=0.26, olho_z=1.42, olho_r=0.19, iris=(0.15, 0.25, 0.4), cilios=False, sob=(0.2, 0.1, 0.02),
                      sob_larg=0.17, boca_z=1.0, boca_larg=0.24, blush=None),
                 loc=loc, alt=alt, bracos=dict(z=1.0, cor=(0.55, 0.38, 0.08)), extras=extras)


# ------------------------------------------------------------------ cenário
def plano(nome, loc, rot, escala, m):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    p = bpy.context.active_object
    p.name = nome
    p.scale = escala
    p.data.materials.append(m)
    return p


def cozinha(noite=False):
    """Cozinha de desenho animado: parede, barra de azulejo, bancada de madeira e janela."""
    plano("parede", (0, 3.0, 2), (math.radians(90), 0, 0), (14, 8, 1), mat("parede", (0.82, 0.6, 0.45), rough=0.8))
    az = mat("azulejo", (0.5, 0.75, 0.72), rough=0.12, coat=0.6)
    nt = az.node_tree
    tij = nt.nodes.new("ShaderNodeTexBrick")
    tij.inputs["Color1"].default_value = (0.45, 0.72, 0.7, 1)
    tij.inputs["Color2"].default_value = (0.5, 0.78, 0.74, 1)
    tij.inputs["Mortar"].default_value = (0.95, 0.95, 0.92, 1)
    tij.inputs["Scale"].default_value = 6
    tij.inputs["Mortar Size"].default_value = 0.012
    nt.links.new(tij.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    plano("barra", (0, 2.97, 0.6), (math.radians(90), 0, 0), (14, 1.7, 1), az)
    mad = relevo(mat("madeira", (0.42, 0.22, 0.1), rough=0.45, coat=0.3), 3, 0.05)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.25))
    b = bpy.context.active_object
    b.scale = (14, 7, 0.5)
    b.data.materials.append(mad)
    ceu = (0.15, 0.25, 0.55) if noite else (1.0, 0.9, 0.7)
    plano("janela", (-1.6, 2.94, 3.1), (math.radians(90), 0, 0), (1.5, 1.8, 1),
          mat("janela", (0, 0, 0), emis=ceu, forca=2.5 if noite else 3))


def luz(nome, loc, alvo, energia, cor, tam, tipo="AREA"):
    L = bpy.data.lights.new(nome, tipo)
    L.energy = energia
    L.color = cor
    if tipo == "AREA":
        L.size = tam
    else:
        L.shadow_soft_size = tam
    o = bpy.data.objects.new(nome, L)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


def mundo(cor, forca):
    w = bpy.context.scene.world or bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*cor, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = forca


def luzes(noite=False, forca=1.0, alvo=(0, 0, 1.2)):
    if noite:
        luz("key", (-3.5, -3.5, 4.5), alvo, 420 * forca, (1.0, 0.7, 0.42), 2)
        luz("fill", (4, -4, 2.0), alvo, 45 * forca, (0.45, 0.6, 1.0), 4)
        luz("rim", (2.5, 1.6, 4.0), alvo, 380 * forca, (0.45, 0.62, 1.0), 1.5)
        luz("rim2", (-2.5, 1.6, 3.5), alvo, 200 * forca, (1.0, 0.6, 0.35), 1.5)
        mundo((0.15, 0.2, 0.35), 0.03)
        bpy.context.scene.view_settings.exposure = -1.3
        bpy.context.scene.view_settings.look = "AgX - High Contrast"
    else:
        luz("key", (-3, -4, 5), alvo, 500 * forca, (1.0, 0.93, 0.85), 3)
        luz("fill", (4, -3, 2.5), alvo, 120 * forca, (0.8, 0.88, 1.0), 4)
        luz("rim", (2.5, 1.8, 4.5), alvo, 450 * forca, (1.0, 0.85, 0.7), 2)
        mundo((0.5, 0.45, 0.4), 0.25)


def camera(loc=(0, -6.5, 1.4), alvo=(0, 0, 1.2), lente=50, foco=None, f=2.8):
    c = bpy.data.cameras.new("cam")
    c.lens = lente
    ob = bpy.data.objects.new("cam", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    d = Vector(alvo) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    if foco is not None:
        c.dof.use_dof = True
        c.dof.focus_distance = foco
        c.dof.aperture_fstop = f
    return ob


def render_cfg(w=540, h=960, amostras=8):
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.resolution_percentage = 100
    s.cycles.device = "CPU"
    s.cycles.samples = amostras
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 4
    s.cycles.diffuse_bounces = 2
    s.cycles.glossy_bounces = 2
    s.cycles.transmission_bounces = 2
    s.render.use_persistent_data = True
    s.view_settings.view_transform = "AgX"
    if s.view_settings.look == "None":
        s.view_settings.look = "AgX - Medium High Contrast"


def render(caminho):
    bpy.context.scene.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


def caixa(nome, loc, dim, m, raio=0.08, sub=2):
    """Caixa de cantos arredondados (bevel + subdivisão)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    b = bpy.context.active_object
    b.name = nome
    b.scale = dim
    bpy.ops.object.transform_apply(scale=True)
    bv = b.modifiers.new("b", "BEVEL")
    bv.width = raio
    bv.segments = 4
    if sub:
        subdiv(b, sub)
    for p in b.data.polygons:
        p.use_smooth = True
    b.data.materials.append(m)
    return b


def cilindro(nome, loc, r, h, m, r2=None, vert=48):
    bpy.ops.mesh.primitive_cone_add(vertices=vert, radius1=r, radius2=r if r2 is None else r2, depth=h, location=loc)
    c = bpy.context.active_object
    c.name = nome
    for p in c.data.polygons:
        p.use_smooth = True
    c.data.materials.append(m)
    return c


def sala(noite=True):
    """Salinha das frutas (na escala delas): piso de taco, papel de parede listrado, sofá, abajur, quadro e janela."""
    # piso de madeira
    piso = mat("piso", (0.45, 0.26, 0.13), rough=0.5, coat=0.1)
    nt = piso.node_tree
    tij = nt.nodes.new("ShaderNodeTexBrick")
    tij.inputs["Color1"].default_value = (0.42, 0.24, 0.12, 1)
    tij.inputs["Color2"].default_value = (0.5, 0.3, 0.15, 1)
    tij.inputs["Mortar"].default_value = (0.2, 0.1, 0.05, 1)
    tij.inputs["Scale"].default_value = 1.2
    tij.inputs["Mortar Size"].default_value = 0.008
    tij.inputs["Brick Width"].default_value = 1.6
    tij.inputs["Row Height"].default_value = 0.25
    nt.links.new(tij.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    plano("piso", (0, 0, 0), (0, 0, 0), (30, 30, 1), piso)
    # parede com listras
    par = mat("parede", (0.85, 0.7, 0.55), rough=0.85)
    nt = par.node_tree
    onda = nt.nodes.new("ShaderNodeTexWave")
    onda.wave_profile = "SIN"
    onda.inputs["Scale"].default_value = 3.0
    onda.inputs["Distortion"].default_value = 0
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.interpolation = "CONSTANT"
    rampa.color_ramp.elements[0].color = (0.62, 0.42, 0.42, 1)
    rampa.color_ramp.elements[1].position = 0.5
    rampa.color_ramp.elements[1].color = (0.7, 0.5, 0.48, 1)
    nt.links.new(onda.outputs["Fac"], rampa.inputs[0])
    nt.links.new(rampa.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"])
    p = plano("parede", (0, 3.2, 5), (math.radians(90), 0, 0), (30, 12, 1), par)
    onda.bands_direction = "X"
    rodape = mat("rodape", (0.95, 0.93, 0.88), rough=0.4)
    caixa("rodape", (0, 3.15, 0.15), (30, 0.1, 0.3), rodape, 0.02, 0)
    # sofá
    tecido = relevo(mat("sofa", (0.22, 0.42, 0.45), rough=0.9, sss=0.05), 120, 0.15)
    caixa("sofa_base", (0.6, 2.4, 0.45), (5.2, 1.4, 0.9), tecido, 0.15)
    caixa("sofa_enc", (0.2, 2.95, 1.25), (5.2, 0.45, 1.6), tecido, 0.2)
    for lado in (-1, 1):
        caixa(f"sofa_br{lado}", (0.2 + 2.55 * lado, 2.4, 0.95), (0.5, 1.4, 1.1), tecido, 0.2)
    almof = relevo(mat("almof", (0.95, 0.65, 0.3), rough=0.9), 140, 0.12)
    for k, x in enumerate((-1.4, 1.8)):
        a = caixa(f"almof{k}", (x, 2.55, 1.3), (0.9, 0.3, 0.8), almof, 0.25)
        a.rotation_euler = (math.radians(-15), 0, math.radians(8 - 16 * k))
    # abajur
    latao = mat("latao", (0.9, 0.65, 0.3), rough=0.25, metal=1.0)
    cilindro("abaj_pe", (-2.9, 2.2, 1.4), 0.05, 2.8, latao)
    cilindro("abaj_base", (-2.9, 2.2, 0.04), 0.35, 0.08, latao)
    cupula = mat("cupula", (1.0, 0.85, 0.6), rough=0.8, emis=(1.0, 0.7, 0.4), forca=6 if noite else 1.5)
    cilindro("abaj_cup", (-2.9, 2.2, 3.0), 0.55, 0.7, cupula, r2=0.35)
    if noite:
        L = bpy.data.lights.new("abajur", "POINT")
        L.energy = 600
        L.color = (1.0, 0.72, 0.45)
        L.shadow_soft_size = 0.4
        o = bpy.data.objects.new("abajur", L)
        bpy.context.scene.collection.objects.link(o)
        o.location = (-2.9, 2.0, 2.9)
    # quadro na parede
    moldura = mat("moldura", (0.9, 0.85, 0.75), rough=0.4)
    caixa("quadro", (2.6, 3.12, 3.6), (1.6, 0.08, 1.2), moldura, 0.02, 0)
    arte = mat("arte", (0.95, 0.75, 0.4), rough=0.7)
    nt = arte.node_tree
    gr = nt.nodes.new("ShaderNodeTexGradient")
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].color = (0.95, 0.5, 0.3, 1)
    rampa.color_ramp.elements[1].color = (0.3, 0.6, 0.75, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], gr.inputs[0])
    nt.links.new(gr.outputs[0], rampa.inputs[0])
    nt.links.new(rampa.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"])
    plano("arte", (2.6, 3.07, 3.6), (math.radians(90), 0, 0), (1.4, 1.0, 1), arte)
    # janela
    ceu = (0.12, 0.2, 0.45) if noite else (1.0, 0.92, 0.75)
    plano("janela", (-1.0, 3.17, 3.9), (math.radians(90), 0, 0), (2.0, 1.8, 1),
          mat("janela", (0, 0, 0), emis=ceu, forca=1.2 if noite else 3))
    for k, x in enumerate((-2.25, 0.25)):
        cort = relevo(mat(f"cortina{k}", (0.85, 0.3, 0.3), rough=0.9, sss=0.1), 2, 0.6, "noise")
        c = caixa(f"cort{k}", (x, 3.05, 3.7), (0.6, 0.12, 2.8), cort, 0.05)
    # tapete
    tap = relevo(mat("tapete", (0.85, 0.75, 0.55), rough=1.0), 200, 0.2)
    t = cilindro("tapete", (0.2, -0.2, 0.01), 3.2, 0.02, tap, vert=96)
    t.scale = (1.3, 0.7, 1)
