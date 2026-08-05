# Checks for the generator-load matching index M_E(G): theorem 3.1 (bounds),
# propositions 3.2 and 3.3 (the two extreme cases), the section 5 example,
# the section 7 scenario table, the section 8 comparison with standard
# centralities, and the variants of sections 9 and 10.
# Run: python matching_index.py

import networkx as nx


def gl_subgraph(G, gens, loads):
    gen_set, load_set = set(gens), set(loads)
    B = nx.Graph()
    B.add_nodes_from(gens)
    B.add_nodes_from(loads)
    B.add_edges_from(
        (u, v) for u, v in G.edges()
        if (u in gen_set and v in load_set) or (v in gen_set and u in load_set)
    )
    return B


def matching_index(G, gens, loads):
    # M_E(G) = nu(G_GL) / min(|V_G|, |V_L|)
    if not gens or not loads:
        raise ValueError("V_G and V_L must be non-empty")
    B = gl_subgraph(G, gens, loads)
    k = min(len(gens), len(loads))
    if B.number_of_edges() == 0:
        return 0.0, 0, k
    m = nx.algorithms.bipartite.maximum_matching(B, top_nodes=list(gens))
    nu = len(m) // 2  # the dict lists every matched node twice
    return nu / k, nu, k


def capacity_feasible_index(G, gens, loads, capacity, demand):
    # same index, but edge (g, l) is allowed only if capacity(g) >= demand(l)
    gen_set, load_set = set(gens), set(loads)
    G2 = nx.Graph()
    G2.add_nodes_from(G.nodes())
    for u, v in G.edges():
        if u in load_set and v in gen_set:
            u, v = v, u
        if u in gen_set and v in load_set and capacity[u] < demand[v]:
            continue
        G2.add_edge(u, v)
    return matching_index(G2, gens, loads)


def weighted_index(G, gens, loads, weight="capacity"):
    # M_E^w(G) = nu_w(G_GL) / W_k, W_k = sum of the k largest weights in E_GL
    B = gl_subgraph(G, gens, loads)
    k = min(len(gens), len(loads))
    if B.number_of_edges() == 0:
        return 0.0
    for u, v in B.edges():
        B[u][v][weight] = G[u][v].get(weight, 1.0)
    m = nx.max_weight_matching(B, weight=weight)
    nu_w = sum(B[u][v][weight] for u, v in m)
    top_weights = sorted((d[weight] for _, _, d in B.edges(data=True)), reverse=True)
    W_k = sum(top_weights[:k])
    return nu_w / W_k if W_k > 0 else 0.0


BRANCHES_33 = [
    (1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),
    (11,12),(12,13),(13,14),(14,15),(15,16),(16,17),(17,18),
    (2,19),(19,20),(20,21),(21,22),
    (3,23),(23,24),(24,25),
    (6,26),(26,27),(27,28),(28,29),(29,30),(30,31),(31,32),(32,33),
]

BRANCHES_69 = [
    (1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),(11,12),
    (12,13),(13,14),(14,15),(15,16),(16,17),(17,18),(18,19),(19,20),(20,21),
    (21,22),(22,23),(23,24),(24,25),(25,26),(26,27),(3,28),(28,29),(29,30),
    (30,31),(31,32),(32,33),(33,34),(34,35),(3,36),(36,37),(37,38),(38,39),
    (39,40),(40,41),(41,42),(42,43),(43,44),(44,45),(45,46),(4,47),(47,48),
    (48,49),(49,50),(8,51),(51,52),(9,53),(53,54),(54,55),(55,56),(56,57),
    (57,58),(58,59),(59,60),(60,61),(61,62),(62,63),(63,64),(64,65),(11,66),
    (66,67),(12,68),(68,69),
]


def verify_paper_example():
    gens = ["g1", "g2", "g3"]
    loads = ["l1", "l2", "l3", "l4"]
    edges = [
        ("g1","l1"), ("g1","l2"), ("g2","l2"), ("g2","l3"), ("g3","l4"),
        ("g2","a1"), ("a1","l3"),
    ]
    G = nx.Graph(edges)
    me, nu, k = matching_index(G, gens, loads)
    assert (nu, k) == (3, 3), (nu, k)  # compare the fraction, not the float
    G.remove_edge("g3", "l4")
    me2, nu2, k2 = matching_index(G, gens, loads)
    assert (nu2, k2) == (2, 3), (nu2, k2)
    print(f"section 5 example: M_E={me:.4f}; without (g3,l4): M_E={me2:.4f}")


def verify_test_networks():
    G33 = nx.Graph(BRANCHES_33)
    scenarios_33 = {
        "A (single source)": [1],
        "B (multi-DG illustrative)": [1, 6, 12, 25, 30],
        "C (clustered)": [1, 2, 3],
        "D (dispersed)": [1, 19, 23],
    }
    for label, gens in scenarios_33.items():
        loads = [n for n in G33 if n not in gens]
        me, nu, k = matching_index(G33, gens, loads)
        print(f"33-bus, {label}: V_G={gens}, M_E={nu}/{k}={me:.4f}")

    G69 = nx.Graph(BRANCHES_69)
    scenarios_69 = {
        "clustered": [1, 2, 3],
        "dispersed": [1, 28, 36],
        "clustered, 5 nodes": [39, 40, 41, 42, 43],
        "dispersed, 5 nodes": [1, 8, 9, 11, 12],
    }
    for label, gens in scenarios_69.items():
        loads = [n for n in G69 if n not in gens]
        me, nu, k = matching_index(G69, gens, loads)
        print(f"69-bus, {label}: V_G={gens}, M_E={nu}/{k}={me:.4f}")


def verify_standard_metrics():
    G33 = nx.Graph(BRANCHES_33)
    deg = nx.degree_centrality(G33)
    clo = nx.closeness_centrality(G33)
    bet = nx.betweenness_centrality(G33)
    for label, gens in [("clustered {1,2,3}", [1,2,3]), ("dispersed {1,19,23}", [1,19,23])]:
        print(f"{label}: sum(degree)={sum(deg[n] for n in gens):.4f}, "
              f"sum(closeness)={sum(clo[n] for n in gens):.4f}, "
              f"sum(betweenness)={sum(bet[n] for n in gens):.4f}")
    print(f"lambda_2(33-bus) = {nx.algebraic_connectivity(G33):.6f}")
    print(f"lambda_2(69-bus) = {nx.algebraic_connectivity(nx.Graph(BRANCHES_69)):.6f}")


def verify_capacity_feasibility():
    import random
    random.seed(7)
    G33 = nx.Graph(BRANCHES_33)
    gens = [1, 19, 23]
    loads = [n for n in G33 if n not in gens]
    capacity = {g: random.uniform(50, 150) for g in gens}
    demand = {l: random.uniform(10, 200) for l in loads}

    me, nu, k = matching_index(G33, gens, loads)
    me_f, nu_f, k_f = capacity_feasible_index(G33, gens, loads, capacity, demand)
    print(f"structural M_E = {nu}/{k} = {me:.4f}")
    print(f"capacity-feasible M_E' = {nu_f}/{k_f} = {me_f:.4f}")
    assert nu_f <= nu, f"M_E' must be <= M_E, got {nu_f}/{k_f} vs {nu}/{k}"


def verify_weighted_example():
    gens = ["g1", "g2", "g3"]
    loads = ["l1", "l2", "l3", "l4"]
    weights = {("g1","l1"):40, ("g1","l2"):25, ("g2","l2"):60, ("g2","l3"):30, ("g3","l4"):50}
    G = nx.Graph()
    for (u, v), w in weights.items():
        G.add_edge(u, v, capacity=w)
    me, nu, k = matching_index(G, gens, loads)
    me_w = weighted_index(G, gens, loads)
    print(f"unweighted M_E = {nu}/{k} = {me:.4f}")
    print(f"weighted M_E^w = {me_w:.4f}")


def verify_looped_microgrid():
    # ring of aux nodes, generators and loads hang off it: no direct G-L edges at all
    edges = [
        ("a1","a2"),("a2","a3"),("a3","a4"),("a4","a5"),("a5","a6"),("a6","a1"),
        ("g1","a1"),("g2","a2"),("g3","a3"),
        ("l1","a4"),("l2","a5"),("l3","a6"),
    ]
    G = nx.Graph(edges)
    gens, loads = ["g1","g2","g3"], ["l1","l2","l3"]
    me, nu, k = matching_index(G, gens, loads)
    print(f"looped microgrid, no direct G-L edges: M_E = {nu}/{k} = {me:.4f}")
    assert nu == 0, nu
    G.add_edge("g1", "l1")
    me2, nu2, k2 = matching_index(G, gens, loads)
    print(f"after adding one direct edge (g1,l1): M_E = {nu2}/{k2} = {me2:.4f}")


def verify_bounds_random(trials=2000, max_n=12, seed=0):
    # spot check of theorem 3.1, not a proof: random graphs, integer form 0 <= nu <= k
    import random
    from itertools import combinations
    rng = random.Random(seed)
    bad = 0
    for _ in range(trials):
        n = rng.randint(2, max_n)
        nodes = list(range(n))
        n_gen = rng.randint(1, n - 1)
        gens = nodes[:n_gen]
        rest = nodes[n_gen:]
        n_load = rng.randint(1, len(rest))
        loads = rest[:n_load]
        p = rng.uniform(0.1, 0.7)
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from((u, v) for u, v in combinations(nodes, 2) if rng.random() < p)
        me, nu, k = matching_index(G, gens, loads)
        if not 0 <= nu <= k:
            bad += 1
    if bad:
        print(f"FAIL: {bad} bound violations")
    else:
        print(f"bounds hold on {trials} random graphs")


if __name__ == "__main__":
    verify_paper_example()
    print()
    verify_test_networks()
    print()
    verify_standard_metrics()
    print()
    verify_capacity_feasibility()
    print()
    verify_weighted_example()
    print()
    verify_looped_microgrid()
    print()
    verify_bounds_random()
