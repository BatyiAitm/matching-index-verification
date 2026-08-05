# matching-index-verification

Reproducibility code for the generator-load matching index `M_E(G)`.

This repository accompanies a scientific paper on the matching index for
generator-load structure in power networks. It is not a software library.
It is a small verification repo: a reader can clone it, run one script, and
check that the numerical examples and computational claims used in the
paper are reproduced.

Author: Shamilov Batyi Aitmerekovich

Copyright (c) 2026 Shamilov Batyi Aitmerekovich. All rights reserved.

## What is checked

The script `matching_index.py` checks the parts of the paper that are
computational rather than purely written proofs:

- the section 5 example, before and after removing edge (g3,l4);
- the 33-bus and 69-bus scenario table of section 7;
- the centralities and algebraic connectivity comparison of section 8;
- the capacity-feasible variant `M_E'` of section 9;
- the weighted variant `M_E^w` of section 10;
- a looped microgrid with no direct generator-load edges (proposition 3.2);
- theorem 3.1 on random graphs.

The scenario values are checked as integer fractions (`nu` against `k`),
not by floating-point equality. The random pass is a spot check of the
bound, not a proof of theorem 3.1: the theorem is proved in the paper, and
the 2000 graphs only confirm that the implementation agrees with it.

## Run

```bash
git clone https://github.com/BatyiAitm/matching-index-verification.git
cd matching-index-verification
pip install -r requirements.txt
python matching_index.py
```

On a normal laptop the script runs in a few seconds. A successful run exits
with code 0. If a checked value changes, Python stops at an `assert` and
prints the offending value.

## Expected output

The full expected output is stored in `expected_output.txt`. The final
part should be:

```text
structural M_E = 3/3 = 1.0000
capacity-feasible M_E' = 2/3 = 0.6667

unweighted M_E = 3/3 = 1.0000
weighted M_E^w = 1.0000

looped microgrid, no direct G-L edges: M_E = 0/3 = 0.0000
after adding one direct edge (g1,l1): M_E = 1/3 = 0.3333

bounds hold on 2000 random graphs
```

## Citation

If this repository helps you check or reuse the computation, cite the
repository together with the accompanying paper. GitHub will read
`CITATION.cff` and show a citation entry in the repository sidebar.
