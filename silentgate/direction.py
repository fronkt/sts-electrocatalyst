"""All-atom, all-printed-step directional evidence; no tolerance for LOCKED."""
import math

def direction_map(steps, atoms, noise_floor, n_symops=None, force_only=False):
    if not steps or not atoms:
        raise ValueError('direction evidence requires atoms and printed force steps')
    if not force_only and (not math.isfinite(noise_floor) or noise_floor <= 0):
        raise ValueError('noise floor must be finite and positive')
    result = {}
    for axis, k in [('x',0),('y',1),('z',2)]:
        values = [step[i][k] for step in steps for i in atoms]
        if not all(math.isfinite(x) for x in values):
            raise ValueError('nonfinite force')
        exact = all(x == 0.0 for x in values)
        maximum = max(abs(x) for x in values)
        locked = exact and (force_only or (n_symops is not None and n_symops >= 2))
        label = ('LOCKED' if exact else 'not-LOCKED') if force_only else 'LOCKED' if locked else ('EXPLORED' if maximum >= noise_floor else 'ON_PLANE' if n_symops == 1 or force_only else 'UNRESOLVED')
        result[axis] = dict(exact_zero_every_step_all_atoms=exact,max_abs_force=maximum,classification=label)
    return result
