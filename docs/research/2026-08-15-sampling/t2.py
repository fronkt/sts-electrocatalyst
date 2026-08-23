import numpy as np
from pymatgen.core import Structure, Lattice, Molecule
from pymatgen.core.surface import SlabGenerator
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

a,c,u = 4.4919, 3.1066, 0.3058
bulk = Structure(Lattice.tetragonal(a,c), ["Ru","Ru","O","O","O","O"],
 [[0,0,0],[.5,.5,.5],[u,u,0],[1-u,1-u,0],[.5+u,.5-u,.5],[.5-u,.5+u,.5]])
sg = SlabGenerator(bulk,(1,1,0),min_slab_size=9.,min_vacuum_size=15.,center_slab=True,lll_reduce=False,primitive=True)
s = sg.get_slabs()[0]
asf = AdsorbateSiteFinder(s)

for adsname, mol in [("O", Molecule(["O"],[[0,0,0]])),
                     ("OH", Molecule(["O","H"],[[0,0,0],[0,0,0.98]])),
                     ("OOH", Molecule(["O","O","H"],[[0,0,0],[1.29,0,0.7],[1.29,0.9,1.0]]))]:
    ads_structs = asf.generate_adsorption_structures(mol, repeat=[1,1,1], find_args={"distance":2.0})
    print(f"=== {adsname}: {len(ads_structs)} configs")
    for i,st in enumerate(ads_structs):
        spg = SpacegroupAnalyzer(st, symprec=1e-3)
        sym = spg.get_space_group_symbol()
        ops = spg.get_symmetry_operations(cartesian=True)
        # which cartesian force components are forced to zero on adsorbate atoms?
        n_ads = len(mol)
        zeroed = set()
        idxs = [j for j,site in enumerate(st) if site.properties.get("surface_properties")=="adsorbate"]
        for j in idxs:
            p = st[j].coords
            for op in ops:
                q = op.operate(p)
                # is atom mapped to itself (mod lattice)?
                d = st.lattice.get_all_distances(st.lattice.get_fractional_coords(q), st[j].frac_coords)[0][0]
                if d < 1e-3 and not np.allclose(op.rotation_matrix, np.eye(3), atol=1e-6):
                    R = op.rotation_matrix
                    ev = np.linalg.eigvals(R)
                    # force must satisfy F = R F  -> components in eigenspace of eigenvalue -1 vanish
                    w,v = np.linalg.eig(R)
                    for k in range(3):
                        if abs(w[k]+1) < 1e-6:
                            zeroed.add(tuple(np.round(np.real(v[:,k]),3)))
        print(f"  cfg{i} spg={sym} nops={len(ops)} adsorbate site-symmetry zeroed force dirs: {sorted(zeroed)}")
