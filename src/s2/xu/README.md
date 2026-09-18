# Xu S2 adapter

The corpus stays outside git. The expected extracted root is the directory named
zhongnanxu-rutile-OER-c4cb892, below the local extracted/ directory.

From the repository root:

~~~powershell
python -m pytest tests/s2/test_xu_census.py -q
python src/s2/xu/census.py --corpus C:/Users/frank/sts-corpora/xu/extracted/zhongnanxu-rutile-OER-c4cb892 --archive C:/Users/frank/sts-corpora/xu/rutile-OER-v1.0.zip --out results/s2_2026-09-18/xu_census.json
python src/s2/xu/verify.py --primary results/s2_2026-09-18/xu_census.json --corpus C:/Users/frank/sts-corpora/xu/extracted/zhongnanxu-rutile-OER-c4cb892 --out results/s2_2026-09-18/xu_independent_verification.json
~~~

The first command checks numerator definitions, exact threshold boundaries,
fixed populations, missing evidence and gas-independent energy differences.
The primary CLI checks the archive MD5, the registered mirror-tree SHA-256,
and all 1,620 selected input/output Git blob identities before reading results.
It calls the approved silentgate reader and classifier without changing their
source. Additional declared namelist fields and termination checks belong to
this S2 adapter. Every selected output appears in the result.

Header, final-step ALL-atom zero-force and every-step named-pair direction
clauses are evaluated separately. Only UNIDENTIFIED and NO_FORCE_BLOCK remove
outputs from the original 630 adsorbate-force denominator, with overlapping
exclusions counted once. Constraint exclusion can leave no eligible adsorbate
atoms; that case stays unknown in the remaining denominator. It never satisfies
ALL by an empty-set convention. Lower and upper evidence bounds distinguish
missing information from a measured failure.

A primary U span requires all 17 relevant state pairs. An incomplete observed
range is a lower bound, and the ten-metal denominator stays fixed. The
four-state usable-rung count is reported separately from each paired count.
The gas-independent spans do not yield absolute overpotentials or floor margins.

The independent verifier imports neither silentgate nor the primary adapter.
It rechecks source bytes, reparses raw headers, deck geometries/constraints,
force blocks, convergence and decimal energy tokens, then recomputes all scored
numerators and U spans. A mismatch returns exit 2 and names the comparison.
