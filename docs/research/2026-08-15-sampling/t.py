import numpy as np
from pymatgen.core import Structure, Lattice, Molecule
from pymatgen.core.surface import SlabGenerator
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# rutile RuO2 P4_2/mnm a=4.49 c=3.11, u=0.305
a,c,u = 4.4919, 3.1066, 0.3058
lat = Lattice.tetragonal(a,c)
sp = ["Ru","Ru","O","O","O","O"]
co = [[0,0,0],[0.5,0.5,0.5],[u,u,0],[1-u,1-u,0],[0.5+u,0.5-u,0.5],[0.5-u,0.5+u,0.5]]
bulk = Structure(lat, sp, co)
print("bulk sg:", SpacegroupAnalyzer(bulk).get_space_group_symbol())

sg = SlabGenerator(bulk, (1,1,0), min_slab_size=9.0, min_vacuum_size=15.0, center_slab=True, lll_reduce=False, primitive=True)
slabs = sg.get_slabs()
print("n slabs:", len(slabs))
s = slabs[0]
print("slab formula", s.composition.reduced_formula, "natoms", len(s))
print("slab lattice abc", np.round(s.lattice.abc,4))
sa = SpacegroupAnalyzer(s, symprec=1e-3)
print("slab spacegroup:", sa.get_space_group_symbol())
ops = sa.get_symmetry_operations(cartesian=True)
print("n symmops slab:", len(ops))

asf = AdsorbateSiteFinder(s)
sites = asf.find_adsorption_sites(distance=2.0)
for k,v in sites.items():
    print(k, len(v) if hasattr(v,'__len__') else v)
    if k!="all":
        for p in v: print("   ", np.round(p,4))
