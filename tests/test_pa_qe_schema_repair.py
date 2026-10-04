"""Cause-specific QE7.5 new-format Hubbard XML repair; offline raw fixtures."""
import copy
import xml.etree.ElementTree as ET

import pytest

import test_pa_qe_adapter as raw


adapter = raw.adapter


def scientific_xml(tmp_path):
    directory, expected = raw.scientific_arm(tmp_path)
    path = directory/'data-file-schema.xml'
    root = ET.fromstring(path.read_text(encoding='utf-8'))
    dft = root.find('./input/dft')
    return directory, expected, path, root, dft, dft.find('dftU')


def rewrite(path, root):
    path.write_text(ET.tostring(root, encoding='unicode'), encoding='utf-8')


def test_qe75_new_format_without_nonexistent_flag_is_raw_validated(tmp_path):
    directory, expected, _, _, dft, dftu = scientific_xml(tmp_path)
    assert len(dft.findall('dftU')) == 1
    assert dftu.attrib['new_format'] == 'true'
    assert dftu.findall('lda_plus_u') == []
    record = raw.parse_arm(directory, expected)
    assert record['raw_validated'] is True
    assert record['settings_identity'] == expected['settings_identity']
    assert record['input']['settings']['hubbard']['rows'] == [['U', 'H-1s', '3.32']]
    assert record['production_accepted'] is False


def test_optional_unique_true_flag_is_checked_not_required(tmp_path):
    directory, expected, path, root, _, dftu = scientific_xml(tmp_path)
    ET.SubElement(dftu, 'lda_plus_u').text = 'true'
    rewrite(path, root)
    assert raw.parse_arm(directory, expected)['raw_validated'] is True


@pytest.mark.parametrize('case', ['missing', 'duplicate'])
def test_source_hubbard_requires_exactly_one_dftu(tmp_path, case):
    directory, expected, path, root, dft, dftu = scientific_xml(tmp_path)
    if case == 'missing':
        dft.remove(dftu)
    else:
        dft.append(copy.deepcopy(dftu))
    rewrite(path, root)
    with pytest.raises(adapter.AdapterError, match='one source-matched XML Hubbard'):
        raw.parse_arm(directory, expected)


@pytest.mark.parametrize('new_format', [None, 'false', 'True', '1', ''])
def test_new_format_must_be_explicit_true(tmp_path, new_format):
    directory, expected, path, root, _, dftu = scientific_xml(tmp_path)
    if new_format is None:
        dftu.attrib.pop('new_format')
    else:
        dftu.set('new_format', new_format)
    rewrite(path, root)
    with pytest.raises(adapter.AdapterError, match='new-format XML Hubbard'):
        raw.parse_arm(directory, expected)


@pytest.mark.parametrize('values', [('false',), ('True',), ('1',), ('',),
                                    ('true', 'true'), ('true', 'false')])
def test_optional_flag_cannot_be_false_malformed_or_duplicate(tmp_path, values):
    directory, expected, path, root, _, dftu = scientific_xml(tmp_path)
    for value in values:
        ET.SubElement(dftu, 'lda_plus_u').text = value
    rewrite(path, root)
    with pytest.raises(adapter.AdapterError):
        raw.parse_arm(directory, expected)


@pytest.mark.parametrize('tag,bad_value', [('lda_plus_u_kind', '1'),
                                        ('U_projection_type', 'ortho-atomic')])
@pytest.mark.parametrize('case', ['missing', 'duplicate', 'changed'])
def test_kind_and_projector_remain_explicit_source_bound(tmp_path, tag, bad_value, case):
    directory, expected, path, root, _, dftu = scientific_xml(tmp_path)
    child = dftu.find(tag)
    if case == 'missing':
        dftu.remove(child)
    elif case == 'duplicate':
        dftu.append(copy.deepcopy(child))
    else:
        child.text = bad_value
    rewrite(path, root)
    with pytest.raises(adapter.AdapterError):
        raw.parse_arm(directory, expected)


@pytest.mark.parametrize('case', ['species', 'species_case', 'shell', 'value',
                                 'value_wrong_units', 'drop', 'extra', 'duplicate', 'nonfinite'])
def test_complete_u_species_shell_and_value_map_remains_mandatory(tmp_path, case):
    directory, expected, path, root, _, dftu = scientific_xml(tmp_path)
    child = dftu.find('Hubbard_U')
    if case == 'species':
        child.set('specie', 'Co')
    elif case == 'species_case':
        child.set('specie', 'h')
    elif case == 'shell':
        child.set('label', '2s')
    elif case == 'value':
        child.text = '{:.17g}'.format(3.33/(2*adapter.RY_EV))
    elif case == 'value_wrong_units':
        child.text = '3.32'
    elif case == 'drop':
        dftu.remove(child)
    elif case == 'extra':
        extra = copy.deepcopy(child)
        extra.set('label', '2s')
        dftu.append(extra)
    elif case == 'duplicate':
        dftu.append(copy.deepcopy(child))
    else:
        child.text = 'NaN'
    rewrite(path, root)
    with pytest.raises(adapter.AdapterError):
        raw.parse_arm(directory, expected)


def test_no_hubbard_source_keeps_dftu_absent(tmp_path):
    directory, expected = raw.arm(tmp_path, 'without-hubbard')
    assert expected['settings']['hubbard'] is None
    assert raw.parse_arm(directory, expected)['raw_validated'] is True
    path = directory/'data-file-schema.xml'
    root = ET.fromstring(path.read_text(encoding='utf-8'))
    dftu = ET.SubElement(root.find('./input/dft'), 'dftU', new_format='true')
    ET.SubElement(dftu, 'lda_plus_u_kind').text = '0'
    ET.SubElement(dftu, 'U_projection_type').text = 'atomic'
    ET.SubElement(dftu, 'Hubbard_U', specie='H', label='1s').text = '{:.17g}'.format(3.32/(2*adapter.RY_EV))
    rewrite(path, root)
    with pytest.raises(adapter.AdapterError, match='no source card'):
        raw.parse_arm(directory, expected)


@pytest.mark.parametrize('tag', ['Hubbard_Um', 'Hubbard_V', 'Hubbard_back'])
@pytest.mark.parametrize('coupling', ['0', '.1'])
def test_unregistered_orbital_intersite_or_background_channel_is_rejected(tmp_path, tag, coupling):
    directory, expected, path, root, _, dftu = scientific_xml(tmp_path)
    if tag == 'Hubbard_Um':
        child = ET.SubElement(dftu, tag, specie='H', label='1s', spin='1', size='1')
        child.text = coupling
    elif tag == 'Hubbard_V':
        child = ET.SubElement(dftu, tag, specie1='H', index1='1', label1='1s',
                              specie2='H', index2='2', label2='1s')
        child.text = coupling
    else:
        child = ET.SubElement(dftu, tag, background='one_orbital', species='H')
        ET.SubElement(child, 'Hubbard_U2').text = coupling
        ET.SubElement(child, 'n2_number').text = '2'
        ET.SubElement(child, 'l2_number').text = '0'
    rewrite(path, root)
    with pytest.raises(adapter.AdapterError, match='unregistered XML Hubbard correction channel'):
        raw.parse_arm(directory, expected)


@pytest.mark.parametrize('tag', ['Hubbard_J0', 'Hubbard_alpha', 'Hubbard_alpha_back',
                               'Hubbard_beta', 'Hubbard_J'])
@pytest.mark.parametrize('coupling', ['0', '.1'])
def test_existing_zero_metadata_permission_does_not_allow_nonzero_correction(tmp_path, tag, coupling):
    directory, expected, path, root, _, dftu = scientific_xml(tmp_path)
    child = ET.SubElement(dftu, tag, specie='H', label='1s')
    child.text = coupling if tag != 'Hubbard_J' else coupling+' 0 0'
    rewrite(path, root)
    if coupling == '0':
        assert raw.parse_arm(directory, expected)['raw_validated'] is True
    else:
        with pytest.raises(adapter.AdapterError, match='unregistered nonzero XML Hubbard correction'):
            raw.parse_arm(directory, expected)
