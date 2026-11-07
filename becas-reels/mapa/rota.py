"""Grafo das ruas a pé (OSM) e menor caminho estação/terminal → Beca’s."""
import heapq, math, xml.etree.ElementTree as ET, os
AQ = os.path.dirname(os.path.abspath(__file__))
r = ET.parse(os.path.join(AQ, "area.osm")).getroot()
ND = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in r.iter('node')}
WAYS = []
for w in r.iter('way'):
    t = {x.get('k'): x.get('v') for x in w.iter('tag')}
    WAYS.append((w.get('id'), t, [x.get('ref') for x in w.iter('nd')]))
A_PE = {"residential", "secondary", "tertiary", "primary", "footway", "pedestrian", "living_street", "service",
        "unclassified", "steps", "secondary_link", "tertiary_link", "corridor", "platform", "path"}


def m(a, b):
    la = math.radians((a[0] + b[0]) / 2)
    return math.hypot((a[0] - b[0]) * 111320, (a[1] - b[1]) * 111320 * math.cos(la))


G = {}
for _, t, ns in WAYS:
    if t.get("highway") in A_PE:
        for a, b in zip(ns, ns[1:]):
            d = m(ND[a], ND[b])
            G.setdefault(a, []).append((b, d)); G.setdefault(b, []).append((a, d))


def perto(p):
    return min(G, key=lambda n: m(ND[n], p))


def caminho(p0, p1):
    s, e = perto(p0), perto(p1)
    dist, prev, q = {s: 0}, {}, [(0, s)]
    while q:
        d, u = heapq.heappop(q)
        if u == e: break
        if d > dist[u]: continue
        for v, w in G[u]:
            if d + w < dist.get(v, 1e18):
                dist[v] = d + w; prev[v] = u; heapq.heappush(q, (d + w, v))
    out = [e]
    while out[-1] != s: out.append(prev[out[-1]])
    return [ND[n] for n in out[::-1]], dist[e]


ESTACAO = (-23.6685196, -46.4615921)   # entrada principal (sul) da estação Mauá
TERMINAL = (-23.6676076, -46.4603577)  # Terminal Municipal de Mauá
MATRIZ = (-23.6698336, -46.4622664)
ALQUI = (-23.6700413, -46.4616973)
BECAS = (-23.66992, -46.46197)         # Rua Sorocaba, 35 (aprox.: entre a esquina da Sta. Cecília e o nº 69)

if __name__ == "__main__":
    for nome, p in (("estação", ESTACAO), ("terminal", TERMINAL)):
        c, d = caminho(p, BECAS)
        print(nome, round(d), "m", round(d / 80, 1), "min", len(c))
        nomes = []
        for wid, t, ns in WAYS:
            pass
