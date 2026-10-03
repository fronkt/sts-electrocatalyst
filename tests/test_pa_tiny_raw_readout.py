"""Unit and atom-order checks for raw XML readout; no runtime launch."""
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

SOURCE=Path(__file__).resolve().parents[1]/'results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw_readout.py'
spec=importlib.util.spec_from_file_location('tiny_raw_readout',SOURCE)
qc=importlib.util.module_from_spec(spec)
spec.loader.exec_module(qc)


def node():
    return ET.fromstring('''<step><atomic_structure nat="2"><atomic_positions>
<atom name="H" index="1">0 0 0</atom><atom name="H" index="2">0 0 2</atom>
</atomic_positions><cell><a1>20 0 0</a1><a2>0 20 0</a2><a3>0 0 20</a3></cell>
</atomic_structure><total_energy><etot>-1</etot></total_energy>
<forces dims="3 2">0 0 0.1 0 0 -0.1</forces></step>''')


def test_hartree_energy_and_force_conversion_is_explicit():
    data=qc.evaluated(node())
    assert data['energy_Ry']==-2
    assert data['forces_Ry_per_bohr']==[[0,0,.2],[0,0,-.2]]
    assert data['positions_bohr']==[[0,0,0],[0,0,2]]


@pytest.mark.parametrize('text',['nan','inf',''])
def test_nonfinite_and_empty_numbers_refused(text):
    with pytest.raises(AssertionError):qc.numbers(text)


@pytest.mark.parametrize('mutation',['index','cell'])
def test_atom_order_and_cell_identity_required(mutation):
    root=node()
    if mutation=='index':root.find('atomic_structure/atomic_positions/atom').set('index','2')
    else:root.find('atomic_structure/cell/a1').text='21 0 0'
    with pytest.raises(AssertionError):qc.positions(root)


def test_force_dimensions_required():
    root=node();root.find('forces').set('dims','2 3')
    with pytest.raises(AssertionError):qc.evaluated(root)


def test_differences_use_all_coordinates_and_forces():
    first=qc.evaluated(node());second=qc.evaluated(node())
    second['positions_bohr'][1][2]+=0.25
    second['forces_Ry_per_bohr'][0][2]+=0.5
    second['energy_Ry']+=1
    assert qc.differences(first,second)==pytest.approx({'energy_Ry':1,'position_bohr':.25,'force_Ry_per_bohr':.5})
