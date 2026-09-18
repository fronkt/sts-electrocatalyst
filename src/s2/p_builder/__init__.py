"""P-BUILDER (docs/43 A9.3.5, :1900-1902): prestate construction and the site-symmetry census.

Module map
----------
registered   the arguments A9.3.5 registers, and the per-family values fixed by the
             2026-09-16 operating decision (structure source, termination rule)
structures   source structures (hand-built rutile cell, COD CIFs) and their checks
slabs        SlabGenerator with the registered arguments + termination selection
enumerate    AdsorbateSiteFinder.generate_adsorption_structures only (no symmetry)
prestate     writes results/s2_2026-09-16/p_builder_prestate/ (denominators, hashes)
census       the registered operational definition (SpacegroupAnalyzer, symprec 1e-3)
run_census   execution script: verifies the prestate + boundary, computes the rates
atomate_gate the A9.3.5 atomate input-set verification gate (GitHub API)

`enumerate` and `prestate` never import `census`; a test enforces it.
"""
