# matching-index-verification

Code used to check the calculations for the generator-load matching index
`M_E(G)`.

Author: Shamilov Batyi Aitmerekovich

Copyright (c) 2026 Shamilov Batyi Aitmerekovich. All rights reserved.

## Contents

The main file is `matching_index.py`. It includes:

- construction of simple graph models with generator, load, and auxiliary nodes;
- extraction of direct generator-load edges;
- calculation of `M_E(G)` by maximum bipartite matching;
- checks on small example networks;
- runs on 33-bus and 69-bus radial test networks;
- comparison with degree, closeness, betweenness, and algebraic connectivity;
- a simple capacity-feasible variant;
- a weighted version of the index;
- random tests for the bounds `0 <= M_E(G) <= 1`.

## Run

```bash
pip install -r requirements.txt
python matching_index.py
```

The script prints intermediate values and uses `assert` checks for the main
expected results.

## Main Functions

| Function | Purpose |
|---|---|
| `matching_energy_index` | Computes the main index |
| `verify_paper_example` | Checks a small example |
| `verify_test_networks` | Runs the 33-bus and 69-bus examples |
| `verify_comparison_with_standard_metrics` | Compares with common graph metrics |
| `capacity_feasible_index` | Applies a simple capacity constraint |
| `weighted_matching_index` | Computes the weighted version |
| `verify_bounds_random` | Runs random bound checks |
