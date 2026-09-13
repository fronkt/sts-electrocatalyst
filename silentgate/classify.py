"""Separate incomplete evidence, force-only locking and header-supported locking."""
from .direction import direction_map

def classify(record, force_only=False):
    atoms=record.get('adsorbate_indices') or []
    steps=record.get('force_steps') or []
    fatal=list(record.get('force_issues',[]))+list(record.get('fatal_issues',[]))
    if record.get('unidentified') or not atoms: fatal.append('adsorbate unidentified or no eligible adsorbate atoms')
    if not steps: fatal.append('no printed force steps')
    if any(any(i not in step for i in atoms) for step in steps): fatal.append('a printed force step lacks an eligible adsorbate atom')
    result={k:v for k,v in record.items() if k not in ('force_steps',)}
    result.update(n_adsorbate=record.get('n_adsorbate',len(atoms)) if not record.get('unidentified') else None,n_force_steps=len(steps),force_mode='force-only' if force_only else 'two-witness',unscorable=bool(fatal),scorable=not fatal,unscorable_reasons=fatal)
    if fatal:
        result.update(verdict='unscorable',locked_force_only=None,locked_any_atom_force_only=None,locked_two_witness=None,locked_axes=[],directions={})
        return result
    try:
        noise=None if force_only else float(record.get('forc_conv_thr',.001))/20
        directions=direction_map(steps,atoms,noise,record.get('n_symops'),force_only)
    except (ValueError,TypeError,IndexError) as error:
        result.update(verdict='unscorable',unscorable=True,scorable=False,unscorable_reasons=[str(error)],locked_force_only=None,locked_two_witness=None,locked_axes=[],directions={})
        return result
    axes=[a for a in ('x','y') if directions[a]['exact_zero_every_step_all_atoms']]
    force_locked=bool(axes)
    per_atom={str(i):direction_map(steps,[i],noise,record.get('n_symops'),force_only) for i in atoms}
    any_locked=any(d[a]['exact_zero_every_step_all_atoms'] for d in per_atom.values() for a in ('x','y'))
    sym=record.get('n_symops')
    two=None if sym is None else bool(sym>=2 and force_locked)
    verdict=force_locked if force_only else two
    result.update(verdict='LOCKED' if verdict else 'not-LOCKED' if verdict is not None else 'unscorable',locked_force_only=force_locked,locked_any_atom_force_only=any_locked,per_atom_directions=per_atom,locked_two_witness=two,locked_axes=axes,directions=directions,noise_floor=noise,witness_disagreement=(force_locked!=two) if two is not None else None)
    if verdict is None:
        result.update(unscorable=True,scorable=False,unscorable_reasons=['symmetry header unavailable for two-witness mode'])
    return result
