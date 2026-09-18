"""F8 clearance (docs/43 A9.5 item 8, :1945; item 7, :1944).

Five checks, each a module with a pure core (tested offline) and a thin
network/cache layer:

- ``sun2004``          the Sun, Reuter & Scheffler PRB 70, 235402 citation
- ``structures``       PbO2 / OsO2 / SnO2 / GeO2 / PtO2 structure-type assignments
- ``zpe``              the +0.40 eV *OOH ZPE - TS constant
- ``intercept_floor``  residual uses of 3.18 +/- 0.12 eV and the ~0.12 V code floor
- ``bibcheck``         Crossref comparison of docs/references.bib, docs/28 DOI defects

``python -m s2.f8.run`` (with ``src`` on ``sys.path``) writes every output under
``results/s2_2026-09-16/f8/`` and a sha256 manifest of every input.
"""

__all__ = ["common", "textnorm", "bib", "registry", "sun2004", "structures",
           "zpe", "intercept_floor", "bibcheck", "run"]
