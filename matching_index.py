# Checks for the generator-load matching index M_E(G).
# Run: python matching_index.py

import networkx as nx


def build_energy_network(gen_nodes, load_nodes, aux_nodes, edges):
    G = nx.Graph()
    G.add_nodes_from(gen_nodes, kind="gen")
    G.add_nodes_from(load_nodes, kind="load")
    G.add_nodes_from(aux_nodes, kind="aux")
    G.add_edges_from(edges)
    return G


def gl_subgraph(G, gen_nodes, load_nodes):
    gen_set, load_set = set(gen_nodes), set(load_nodes)
    gl_edges = [
        (u, v) for u, v in G.edges()
        if (u in gen_set and v in load_set) or (v in gen_set and u in load_set)
    ]
    B = nx.Graph()
    B.add_nodes_from(gen_nodes, bipartite=0)
    B.add_nodes_from(load_nodes, bipartite=1)
    B.add_edges_from(gl_edges)
    return B


def matching_energy_index(G, gen_nodes, load_nodes):
    if len(gen_nodes) == 0 or len(load_nodes) == 0:
        raise ValueError("V_G and V_L must be non-empty")

    B = gl_subgraph(G, gen_nodes, load_nodes)
    denom = min(len(gen_nodes), len(load_nodes))
    if B.number_of_edges() == 0:
        return 0.0, 0, denom, []

    top = [n for n in gen_nodes if n in B]
    matching = nx.algorithms.bipartite.maximum_matching(B, top_nodes=top)
    matched_edges = list({frozenset((u, v)) for u, v in matching.items()})
    nu = len(matched_edges)
    return nu / denom, nu, denom, matched_edges


def capacity_feasible_index(G, gen_nodes, load_nodes, gen_capacity, load_demand):
    gen_set, load_set = set(gen_nodes), set(load_nodes)
    eligible = [
        (u, v) for u, v in G.edges()
        if (u in gen_set and v in load_set and gen_capacity[u] >= load_demand[v])
        or (v in gen_set and u in load_set and gen_capacity[v] >= load_demand[u])
    ]
    B = nx.Graph()
    B.add_nodes_from(gen_nodes, bipartite=0)
    B.add_nodes_from(load_nodes, bipartite=1)
    B.add_edges_from(eligible)
    denom = min(len(gen_nodes), len(load_nodes))
    if B.number_of_edges() == 0:
        return 0.0, 0, denom
    top = [n for n in gen_nodes if n in B]
    matching = nx.algorithms.bipartite.maximum_matching(B, top_nodes=top)
    nu = len({frozenset((u, v)) for u, v in matching.items()})
    return nu / denom, nu, denom


def weighted_matching_index(G, gen_nodes, load_nodes, weight="capacity"):
    B = gl_subgraph(G, gen_nodes, load_nodes)
    for u, v in B.edges():
        B[u][v][weight] = G[u][v].get(weight, 1.0)

    k = min(len(gen_nodes), len(load_nodes))
    if B.number_of_edges() == 0:
        return 0.0

    matching = nx.max_weight_matching(B, weight=weight)
    nu_w = sum(B[u][v][weight] for u, v in matching)

    # W_k is the sum of the k largest direct generator-load edge weights.
    all_weights = sorted([B[u][v][weight] for u, v in B.edges()], reverse=True)
    W_k = sum(all_weights[:k]) if len(all_weights) >= k else sum(all_weights)
    return nu_w / W_k if W_k > 0 else 0.0


IEEE_33_BUS_BRANCHES = [
    (1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),
    (11,12),(12,13),(13,14),(14,15),(15,16),(16,17),(17,18),
    (2,19),(19,20),(20,21),(21,22),
    (3,23),(23,24),(24,25),
    (6,26),(26,27),(27,28),(28,29),(29,30),(30,31),(31,32),(32,33),
]

IEEE_69_BUS_BRANCHES = [
    (1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),(11,12),
    (12,13),(13,14),(14,15),(15,16),(16,17),(17,18),(18,19),(19,20),(20,21),
    (21,22),(22,23),(23,24),(24,25),(25,26),(26,27),(3,28),(28,29),(29,30),
    (30,31),(31,32),(32,33),(33,34),(34,35),(3,36),(36,37),(37,38),(38,39),
    (39,40),(40,41),(41,42),(42,43),(43,44),(44,45),(45,46),(4,47),(47,48),
    (48,49),(49,50),(8,51),(51,52),(9,53),(53,54),(54,55),(55,56),(56,57),
    (57,58),(58,59),(59,60),(60,61),(61,62),(62,63),(63,64),(64,65),(11,66),
    (66,67),(12,68),(68,69),
]


def build_ieee33():
    G = nx.Graph()
    G.add_edges_from(IEEE_33_BUS_BRANCHES)
    return G


def build_ieee69():
    G = nx.Graph()
    G.add_edges_from(IEEE_69_BUS_BRANCHES)
    return G


def build_looped_microgrid():
    edges = [
        ("a1","a2"),("a2","a3"),("a3","a4"),("a4","a5"),("a5","a6"),("a6","a1"),
        ("g1","a1"),("g2","a2"),("g3","a3"),
        ("l1","a4"),("l2","a5"),("l3","a6"),
    ]
    G = nx.Graph()
    G.add_edges_from(edges)
    return G


def verify_paper_example():
    gen = ["g1", "g2", "g3"]
    load = ["l1", "l2", "l3", "l4"]
    aux = ["a1"]
    edges_full = [
        ("g1","l1"), ("g1","l2"), ("g2","l2"), ("g2","l3"), ("g3","l4"),
        ("g2","a1"), ("a1","l3"),
    ]
    G = build_energy_network(gen, load, aux, edges_full)
    me, nu, denom, _ = matching_energy_index(G, gen, load)
    assert abs(me - 1.0) < 1e-9, f"Expected M_E=1, got {me}"

    edges_reduced = [e for e in edges_full if e != ("g3","l4")]
    G2 = build_energy_network(gen, load, aux, edges_reduced)
    me2, nu2, denom2, _ = matching_energy_index(G2, gen, load)
    assert abs(me2 - 2/3) < 1e-9, f"Expected M_E=2/3, got {me2}"
    print(f"small example: M_E={me:.4f}; after removing (g3,l4), M_E={me2:.4f}")


def verify_test_networks():
    G33 = build_ieee33()
    scenarios_33 = {
        "A (single source)": [1],
        "B (multi-DG illustrative)": [1, 6, 12, 25, 30],
        "C (clustered)": [1, 2, 3],
        "D (dispersed)": [1, 19, 23],
    }
    for label, gen in scenarios_33.items():
        load = [n for n in G33.nodes() if n not in gen]
        me, nu, denom, _ = matching_energy_index(G33, gen, load)
        print(f"33-bus, {label}: V_G={gen}, M_E={nu}/{denom}={me:.4f}")

    G69 = build_ieee69()
    scenarios_69 = {
        "clustered": [1, 2, 3],
        "dispersed": [1, 28, 36],
        "clustered, 5 nodes": [39, 40, 41, 42, 43],
        "dispersed, 5 nodes": [1, 8, 9, 11, 12],
    }
    for label, gen in scenarios_69.items():
        load = [n for n in G69.nodes() if n not in gen]
        me, nu, denom, _ = matching_energy_index(G69, gen, load)
        print(f"69-bus, {label}: V_G={gen}, M_E={nu}/{denom}={me:.4f}")


def verify_comparison_with_standard_metrics():
    G33 = build_ieee33()
    deg_cent = nx.degree_centrality(G33)
    clos_cent = nx.closeness_centrality(G33)
    betw = nx.betweenness_centrality(G33)
    alg_conn = nx.algebraic_connectivity(G33)

    for label, gen in [("clustered {1,2,3}", [1,2,3]), ("dispersed {1,19,23}", [1,19,23])]:
        print(f"{label}: sum(degree)={sum(deg_cent[n] for n in gen):.4f}, "
              f"sum(closeness)={sum(clos_cent[n] for n in gen):.4f}, "
              f"sum(betweenness)={sum(betw[n] for n in gen):.4f}")
    print(f"algebraic_connectivity(G) = {alg_conn:.6f}")


def verify_capacity_feasibility():
    import random
    random.seed(7)
    G33 = build_ieee33()
    gen = [1, 19, 23]
    load = [n for n in G33.nodes() if n not in gen]
    gen_capacity = {g: random.uniform(50, 150) for g in gen}
    load_demand = {l: random.uniform(10, 200) for l in load}

    me, nu, denom, _ = matching_energy_index(G33, gen, load)
    me_feas, nu_feas, denom_feas = capacity_feasible_index(G33, gen, load, gen_capacity, load_demand)
    print(f"Structural M_E = {nu}/{denom} = {me:.4f}")
    print(f"Capacity-feasible M_E' = {nu_feas}/{denom_feas} = {me_feas:.4f}")
    assert me_feas <= me + 1e-9, "M_E' must be <= M_E"


def verify_weighted_example():
    gen = ["g1", "g2", "g3"]
    load = ["l1", "l2", "l3", "l4"]
    aux = []
    edges = [("g1","l1"), ("g1","l2"), ("g2","l2"), ("g2","l3"), ("g3","l4")]
    weights = {("g1","l1"):40, ("g1","l2"):25, ("g2","l2"):60, ("g2","l3"):30, ("g3","l4"):50}

    G = build_energy_network(gen, load, aux, edges)
    for (u, v), w in weights.items():
        G[u][v]["capacity"] = w

    me_uw, nu_uw, denom_uw, _ = matching_energy_index(G, gen, load)
    me_w = weighted_matching_index(G, gen, load, weight="capacity")
    print(f"Unweighted M_E = {nu_uw}/{denom_uw} = {me_uw:.4f}")
    print(f"Weighted M_E^w = {me_w:.4f}")


def verify_looped_microgrid():
    G = build_looped_microgrid()
    gen, load = ["g1","g2","g3"], ["l1","l2","l3"]
    me, nu, denom, _ = matching_energy_index(G, gen, load)
    print(f"Looped microgrid, no direct G-L edges: M_E = {nu}/{denom} = {me:.4f}")
    assert me == 0.0

    G2 = G.copy()
    G2.add_edge("g1", "l1")
    me2, nu2, denom2, _ = matching_energy_index(G2, gen, load)
    print(f"After adding one direct edge (g1,l1): M_E = {nu2}/{denom2} = {me2:.4f}")


def verify_bounds_random(trials=2000, max_n=12, seed=0):
    import random
    from itertools import combinations
    rng = random.Random(seed)
    violations = []

    for _ in range(trials):
        n = rng.randint(2, max_n)
        nodes = list(range(n))
        n_gen = rng.randint(1, n - 1)
        gen_nodes = nodes[:n_gen]
        remaining = nodes[n_gen:]
        if not remaining:
            continue
        n_load = rng.randint(1, len(remaining))
        load_nodes = remaining[:n_load]
        aux_nodes = remaining[n_load:]

        p = rng.uniform(0.1, 0.7)
        edges = [(u, v) for u, v in combinations(nodes, 2) if rng.random() < p]

        G = build_energy_network(gen_nodes, load_nodes, aux_nodes, edges)
        me, nu, denom, _ = matching_energy_index(G, gen_nodes, load_nodes)
        if not (0 <= me <= 1 + 1e-9):
            violations.append((gen_nodes, load_nodes, aux_nodes, edges, me))

    if violations:
        print(f"FAIL: bound violations found: {len(violations)}")
    else:
        print(f"bounds checked on {trials} random graphs")


if __name__ == "__main__":
    verify_paper_example()

    print()
    verify_test_networks()

    print()
    verify_comparison_with_standard_metrics()

    print()
    verify_capacity_feasibility()

    print()
    verify_weighted_example()

    print()
    verify_looped_microgrid()

    print()
    verify_bounds_random()
