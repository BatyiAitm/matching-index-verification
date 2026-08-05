# matching-index-verification

Checks for the generator-load matching index `M_E(G)`.

Author: Shamilov Batyi Aitmerekovich

Copyright (c) 2026 Shamilov Batyi Aitmerekovich. All rights reserved.

## Run

```bash
pip install -r requirements.txt
python matching_index.py
```

One file, `matching_index.py`, runs in about 8 seconds and covers:

- the section 5 example, before and after removing edge (g3,l4);
- the 33-bus and 69-bus scenario table of section 7;
- the centralities and algebraic connectivity of section 8;
- the capacity-feasible variant `M_E'` of section 9;
- the weighted variant `M_E^w` of section 10;
- a looped microgrid with no direct generator-load edges (proposition 3.2);
- theorem 3.1 on random graphs.

Fractions are compared in integer form (`nu` against `k`), so no check
rides on floating-point equality. The random pass is a spot check of the
bound, not a proof of it: theorem 3.1 is proved in the paper, and the 2000
graphs only confirm the implementation agrees with it.

Failures stop with an `assert`. A normal run prints the computed fractions
and ends with:

```text
structural M_E = 3/3 = 1.0000
capacity-feasible M_E' = 2/3 = 0.6667

unweighted M_E = 3/3 = 1.0000
weighted M_E^w = 1.0000

looped microgrid, no direct G-L edges: M_E = 0/3 = 0.0000
after adding one direct edge (g1,l1): M_E = 1/3 = 0.3333

bounds hold on 2000 random graphs
```
