# matching-index-verification

Checks for the generator-load matching index `M_E(G)`.

Author: Shamilov Batyi Aitmerekovich

Copyright (c) 2026 Shamilov Batyi Aitmerekovich. All rights reserved.

## Run

```bash
pip install -r requirements.txt
python matching_index.py
```

The script checks the small paper example, the 33-bus and 69-bus test
networks, a capacity-feasible variant, a weighted variant, and random
graphs for the bound `0 <= M_E(G) <= 1`.

Failures stop with an `assert`. A normal run prints the computed fractions
and ends with:

```text
bounds checked on 2000 random graphs
```
