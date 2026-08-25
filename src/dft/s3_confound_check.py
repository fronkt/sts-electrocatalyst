# -*- coding: utf-8 -*-
"""
0.05 uB magnetic CONFOUND check over the S3 readout (state of record 2026-08-24).
Disclosed AI-drafted infrastructure. Reads ONLY runs/s3/readout/s3_readout_2026-08-24.json.
Registered rule applied verbatim (docs/43:1566-1569, DEPOSITED, GOVERNS); treatment precedent
docs/43:306-310. No new threshold, formula, or interpretation is introduced; every scope
question the registered text leaves open is FLAGGED, not resolved.
"""
import json, os

RY_TO_MEV = 13605.693
TOL = 0.05  # uB, docs/43:1566-1569

src = os.path.join('runs', 's3', 'readout', 's3_readout_2026-08-24.json')
d = json.load(open(src, encoding='utf-8'))
rows, cells = d['rows'], d['cells']

row_by_job = {}
for r in rows:
    row_by_job[(r['metal'], r['job'])] = r
row_by_file = {r['file']: r for r in rows if r.get('file')}
cell_by = {(c['metal'], c['state'], c['coverage'], c['arm']): c for c in cells}

NSPIN1 = {'Ru', 'Ir', 'Ti'}  # rows print no M (docs/54:64-66)
METALS = ['Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Ru', 'Ir', 'Ti']
STATES = ['O', 'OH', 'OOH']
COVS = ['1x1', '2x1v']


def exceeds(dm):
    return (abs(dm) - TOL) > 1e-9


def mev(e1, e2):
    if e1 is None or e2 is None:
        return None
    return round((e1 - e2) * RY_TO_MEV, 2)


pairs = []


def add_pair(pid, klass, metal, state, contrast, a, b, verdict, dM, notes, extra=None):
    p = {
        'pair_id': pid, 'class': klass, 'metal': metal, 'state': state,
        'contrast': contrast,
        'member_a': a, 'member_b': b,
        'delta_M_uB': (round(abs(dM), 4) if dM is not None else None),
        'verdict': verdict,
        'delta_E_meV_a_minus_b': mev(a.get('energy_ry'), b.get('energy_ry')),
        'notes': notes,
    }
    if extra:
        p.update(extra)
    pairs.append(p)


def mem_from_cell(c):
    return {
        'file': c.get('energy_of_record_file'),
        'energy_ry': c.get('energy_of_record_ry'),
        'M_uB': c.get('total_magnetization_bohr'),
        'status': c.get('status'),
        'cell': c.get('cell'),
    }


def mem_from_row(r):
    return {
        'file': r.get('file'),
        'energy_ry': r.get('energy_ry'),
        'M_uB': r.get('total_magnetization_bohr'),
        'status': r.get('status'),
        'job': r.get('job'),
    }


# ---------- Class 1: symmetry pairs (mir vs off), per metal/state/coverage ----------
for metal in METALS:
    for state in STATES:
        for cov in COVS:
            ca = cell_by.get((metal, state, cov, 'mir'))
            cb = cell_by.get((metal, state, cov, 'off'))
            if ca is None and cb is None:
                continue  # cell pair absent entirely (e.g. Ti 1x1) - A8.2 GAP territory
            pid = 'SYM|%s|%s|%s' % (metal, state, cov)
            notes = []
            if ca is None or cb is None:
                add_pair(pid, 'symmetry(mir-vs-off)', metal, state, cov,
                         mem_from_cell(ca) if ca else {'status': 'ABSENT'},
                         mem_from_cell(cb) if cb else {'status': 'ABSENT'},
                         'NOT-EVALUABLE(member-absent)', None,
                         ['one member cell absent from the state of record'])
                continue
            a, b = mem_from_cell(ca), mem_from_cell(cb)
            if metal in NSPIN1:
                add_pair(pid, 'symmetry(mir-vs-off)', metal, state, cov, a, b,
                         'NOT-EVALUABLE(nspin=1, no M printed)', None,
                         ['docs/54:64-66: nspin=1 rows print no M; whether the 0.05 uB rule is trivially satisfied for a metal with no magnetic degrees of freedom is unstated - FLAG'])
                continue
            Ma, Mb = a['M_uB'], b['M_uB']
            if Ma is not None and Mb is not None:
                dM = Ma - Mb
                v = 'CONFOUNDED' if exceeds(dM) else 'WITHIN'
                if metal == 'Cr' and state == 'OH' and cov == '1x1':
                    notes.append('docs/54:147 records this pair CONFOUNDED; computed |dM| from the readout printed moments is 0.00 - the recorded verdict is NOT reproduced from printed M; carried as recorded, discrepancy FLAGGED for entrant')
                    if not exceeds(dM):
                        v = 'CONFOUNDED(per docs/54:147; not reproduced from printed M)'
                if metal == 'Cr' and state == 'OOH' and cov == '2x1v':
                    notes.append('docs/54:152 recorded the (saddle-mir, off) pair CONFOUNDED (Delta_sym 1.188 eV); docs/55 R3 has since made the escape minimum the mir-arm energy of record and the saddle a DIAGNOSTIC; computed |dM| escape-vs-off = 0.00 (both M 23.0); whether the docs/54:152 CONFOUND survives R3 is an interpretive call - ENTRANT, not resolved here')
                    if not exceeds(dM):
                        v = 'RECORD-CONFLICT(docs/54:152 CONFOUNDED vs R3 escape-member printed-M 0.00) - ENTRANT CALL'
                if metal == 'Cr' and state == 'OOH' and cov == '1x1':
                    notes.append('docs/54:150 + :400-405: mir member identity OPEN (basin -1636.48393 M 11.00 vs production -1636.47080 M 11.80), recorded "pair CONFOUNDED either way"; with the basin member printed |dM|=0.00, with the production member |dM|=0.80 > 0.05 - member identity is the entrant call, both computations reported, recorded verdict carried')
                    extra = {'alternate_member_a': {'file': 'runs/Cr_slab/s0_OOH.out', 'M_uB': 11.8,
                                                    'delta_M_uB_vs_off': 0.8, 'verdict_if_member': 'CONFOUNDED'}}
                    if not exceeds(dM):
                        v = 'CONFOUNDED(per docs/54:150 "either way"; basin-member printed M reads 0.00, production-member 0.80 - member OPEN)'
                    add_pair(pid, 'symmetry(mir-vs-off)', metal, state, cov, a, b, v, dM, notes, extra)
                    continue
                if metal == 'Ni' and state == 'OH' and cov == '1x1' and exceeds(dM):
                    notes.append('member A is the basin-substitution record whose own __g1 child is a refused-candidate (+177.10 meV, docs/43:1589-1592 re-run owed) - the mir-member moment may move; CONFOUNDED stands on the current energy-of-record members')
                if cov == '1x1' and metal in ('Mn', 'Fe', 'Co', 'Ni') and (a.get('file') or '').startswith('runs/%s_slab/' % metal):
                    notes.append('mir member is tier_v2 nosym reuse - whether it stands as a mirror-arm member is OPEN (docs/54:406-411, section 6 item 5); if it does not, this is an A8.2 gap, not a pair')
                add_pair(pid, 'symmetry(mir-vs-off)', metal, state, cov, a, b, v, dM, notes)
                continue

            # one/both members lack an M of record -> pending / unverified / gap
            def cand_moments(c):
                out = []
                if c.get('total_magnetization_bohr') is not None:
                    out.append(('record', c['total_magnetization_bohr'], c.get('energy_of_record_file')))
                for k, lab in (('parent_quoted', 'parent'), ('child_quoted', 'child')):
                    q = c.get(k)
                    if q and q.get('file') in row_by_file:
                        m = row_by_file[q['file']].get('total_magnetization_bohr')
                        if m is not None:
                            out.append((lab, m, q['file']))
                if not out:
                    # fall back to readout rows by canonical job name (e.g. Ni s0_O__1x1_off + __g1)
                    base = 's0_%s__%s_%s' % (c['state'], c['coverage'], c['arm'])
                    for jn, lab in ((base, 'row-parent'), (base + '__g1', 'row-child')):
                        rr = row_by_job.get((c['metal'], jn))
                        if rr and rr.get('total_magnetization_bohr') is not None:
                            out.append((lab, rr['total_magnetization_bohr'], rr.get('file')))
                return out

            prov = []
            ams, bms = cand_moments(ca), cand_moments(cb)
            if ams and bms:
                for la, ma, fa in ams:
                    for lb, mb2, fb in bms:
                        dm = ma - mb2
                        prov.append({'a': {'which': la, 'M_uB': ma, 'file': fa},
                                     'b': {'which': lb, 'M_uB': mb2, 'file': fb},
                                     'delta_M_uB': round(abs(dm), 4),
                                     'exceeds_0.05': exceeds(dm)})
            sub = 'PENDING-RERELAX' if 'PENDING-RERELAX' in (ca['status'], cb['status']) else (
                  'UNVERIFIED' if 'UNVERIFIED' in (ca['status'], cb['status']) else (
                  'GAP' if 'GAP' in (ca['status'], cb['status']) else (
                  'UNCLASSIFIED' if 'UNCLASSIFIED' in (ca['status'], cb['status']) else 'PENDING-RETRY')))
            v = 'NOT-EVALUABLE(%s)' % sub
            if prov and all(x['exceeds_0.05'] for x in prov):
                v = 'EXCEEDS-PROVISIONAL(%s)' % sub
                notes.append('every available candidate-moment pairing exceeds 0.05 uB; no banked energy of record on both sides, so no CONFOUNDED verdict is banked - FLAGGED for entrant')
                if metal == 'Ni' and state == 'OH' and cov == '2x1v':
                    notes.append('margin over the threshold is 0.01-0.02 uB on moments printed to 2 decimals - unrounded moments should be checked before any verdict is banked; which member M enters (mir child 14.47 vs mir parent 14.48) is itself the unstated-member ambiguity')
            elif prov and any(x['exceeds_0.05'] for x in prov):
                v = 'SPLIT-PROVISIONAL(%s)' % sub
                notes.append('candidate-moment pairings disagree on the 0.05 uB test (member identity / pending outcome decides) - FLAGGED for entrant')
            add_pair(pid, 'symmetry(mir-vs-off)', metal, state, cov, a, b, v, None, notes,
                     {'provisional_pairings': prov} if prov else None)

# ---------- Class 2: cell pairs (1x1 vs 2x1v), per metal/state/arm ----------
# No registered rule compares total magnetisation across cells of different atom count;
# literal application of docs/43:1566-1569 flags every measured pair trivially (the 2x1v
# supercell carries ~2x the moment). Both the literal |dM| and the descriptive doubled-1x1
# residual |M(2x1v) - 2*M(1x1)| are reported; NEITHER is a registered verdict.
for metal in METALS:
    for state in STATES + ['ref']:
        arms = ['-'] if state == 'ref' else ['mir', 'off']
        for arm in arms:
            ca = cell_by.get((metal, state, '1x1', arm))
            cb = cell_by.get((metal, state, '2x1v', arm))
            if ca is None or cb is None:
                continue
            pid = 'CELL|%s|%s|%s' % (metal, state, arm)
            a, b = mem_from_cell(ca), mem_from_cell(cb)
            if metal in NSPIN1:
                add_pair(pid, 'cell(1x1-vs-2x1v)', metal, state, arm, a, b,
                         'NOT-EVALUABLE(nspin=1, no M printed)', None,
                         ['docs/54:64-66: nspin=1 rows print no M'])
                continue
            Ma, Mb = a['M_uB'], b['M_uB']
            if Ma is None or Mb is None:
                add_pair(pid, 'cell(1x1-vs-2x1v)', metal, state, arm, a, b,
                         'NOT-EVALUABLE(member pending/unverified)', None, [])
                continue
            dM = Ma - Mb
            resid = Mb - 2.0 * Ma
            add_pair(pid, 'cell(1x1-vs-2x1v)', metal, state, arm, a, b,
                     'LITERAL-EXCEEDS(cross-cell scope UNREGISTERED - FLAG)' if exceeds(dM) else 'WITHIN',
                     dM,
                     ['literal docs/43:1566-1569 application across different atom counts flags trivially; no registered text defines a cross-cell M comparison - FLAGGED, not resolved'],
                     {'descriptive_residual_M2x1v_minus_2xM1x1_uB': round(resid, 4),
                      'descriptive_residual_basis': 'NO REGISTERED BASIS - descriptive only'})

# ---------- Class 3: parent vs __g1 child ----------
BASIN_PARENT = {
    ('Co', 's0_OH__basin_g1'): 'runs/probe/Co_basin/s0_OH.out',
    ('Cr', 's0_OOH__basin_g1'): 'runs/probe/Cr_basin/s0_OOH.out',
    ('Ni', 's0_OH__basin_g1'): 'runs/probe/Ni_basin/s0_OH.out',
}
for r in rows:
    if not r.get('is_g1_child'):
        continue
    metal, job = r['metal'], r['job']
    key = (metal, job)
    if key in BASIN_PARENT:
        pr = row_by_file.get(BASIN_PARENT[key])
    else:
        pjob = job[:-len('__g1')] if job.endswith('__g1') else None
        pr = row_by_job.get((metal, pjob)) if pjob else None
    pid = 'PC|%s|%s' % (metal, job)
    child = mem_from_row(r)
    if pr is None:
        add_pair(pid, 'parent-vs-g1-child', metal, r['state'], '%s/%s' % (r['coverage'], r['arm']),
                 {'status': 'PARENT-NOT-IN-READOUT'}, child,
                 'NOT-EVALUABLE(parent not in readout)', None, [])
        continue
    parent = mem_from_row(pr)
    Mp, Mc = parent['M_uB'], child['M_uB']
    notes = ['A8.3 registers parent-child handling as the 1 meV refusal rule (docs/43:1589-1592); whether a parent-child moment drift is itself an A8.3 "contrast pair" under the 0.05 uB rule is unstated (the A8.3 evidence table is exactly this case, docs/43:1573-1587) - scope FLAGGED, |dM| computed as tasked']
    if Mp is None or Mc is None:
        if metal in NSPIN1:
            v, notes2 = 'NOT-EVALUABLE(nspin=1, no M printed)', ['docs/54:64-66: nspin=1 rows print no M']
        else:
            v, notes2 = 'NOT-EVALUABLE(child pending)', notes
        add_pair(pid, 'parent-vs-g1-child', metal, r['state'], '%s/%s' % (r['coverage'], r['arm']),
                 parent, child, v, None, notes2)
        continue
    dM = Mp - Mc
    v = 'DRIFT-EXCEEDS-0.05uB' if exceeds(dM) else 'WITHIN'
    if r['status'] == 'PENDING-RERELAX':
        notes.append('docs/55 R1: quote parent AND child, bank neither as final; __basin re-relaxation in flight (array 20123293)')
    if metal == 'Ni' and job == 's0_OH__basin_g1':
        notes.append('child is +177.10 meV above its parent - refused-candidate under docs/43:1589-1592 (re-run from parent density owed; MULTISTABLE on second failure)')
    if metal == 'Ni' and job == 's0_O__1x1_off__g1':
        notes.append('GATE-1 census: child +85.10 meV, refused; remedy re-run exists only as the spec-excluded .fromparent.out (readout builder note); row UNCLASSIFIED')
    add_pair(pid, 'parent-vs-g1-child', metal, r['state'], '%s/%s' % (r['coverage'], r['arm']),
             parent, child, v, dM, notes)

# ---------- Class 4: basin-substitution record vs superseded production ----------
for c in cells:
    pp = c.get('parallel_production')
    if not pp or pp.get('total_magnetization_bohr') is None:
        continue
    pid = 'BP|%s' % c['cell']
    a = {'file': c.get('energy_of_record_file'), 'energy_ry': c.get('energy_of_record_ry'),
         'M_uB': c.get('total_magnetization_bohr'), 'status': c.get('status'), 'cell': c['cell']}
    b = {'file': pp['file'], 'energy_ry': pp['energy_ry'], 'M_uB': pp['total_magnetization_bohr'],
         'status': 'SUPERSEDED-PRODUCTION (retained per docs/43:1754-1764 via docs/54:42-43)'}
    dM = a['M_uB'] - b['M_uB']
    notes = ['record vs superseded production output quoted in parallel (docs/54:400-405); the docs/41 metastable-magnetic class population']
    add_pair(pid, 'record-vs-superseded-production', c['metal'], c['state'],
             '%s/%s' % (c['coverage'], c['arm']), a, b,
             'DRIFT-EXCEEDS-0.05uB' if exceeds(dM) else 'WITHIN', dM, notes)

# ---------- outputs ----------
flagged = [p for p in pairs if p['verdict'].startswith(
    ('CONFOUNDED', 'DRIFT-EXCEEDS', 'EXCEEDS-PROVISIONAL', 'SPLIT-PROVISIONAL', 'LITERAL-EXCEEDS', 'RECORD-CONFLICT'))]
counts = {
    'pairs_total': len(pairs),
    'by_class': {},
    'by_verdict': {},
    'flagged_beyond_0.05uB': len(flagged),
}
for p in pairs:
    counts['by_class'][p['class']] = counts['by_class'].get(p['class'], 0) + 1
    counts['by_verdict'][p['verdict']] = counts['by_verdict'].get(p['verdict'], 0) + 1

out = {
    'generated_by': 'confound_check.py - 0.05 uB magnetic CONFOUND check, state of record 2026-08-24; disclosed AI-drafted infrastructure; reads ONLY runs/s3/readout/s3_readout_2026-08-24.json',
    'registered_rule': {
        'threshold_uB': TOL,
        'text': 'a pair whose members differ in converged total magnetisation by more than 0.05 uB is CONFOUNDED - its energy difference mixes the intended contrast with a basin change - and is excluded from the contrast statistics and reported separately, exactly as a geometry confound is',
        'citation': 'docs/43-prereg-week1-factorial.md:1566-1569 (THRESHOLD adopted as proposed 2026-08-23, DEPOSITED 10.5281/zenodo.22072991, GOVERNS)',
        'rationale_citation': 'docs/43:1569-1571 (0.05 uB sits far below observed drifts 11.00->14.90 / 11.00->14.71 uB, far above SCF noise)',
        'treatment_precedent': 'docs/43:306-310 (geometry confound: own table, excluded from every symmetry-effect statistic, counted in the report)',
        'companion_rules': [
            'docs/43:1589-1592 (__g1 child > 1 meV above parent refused; MULTISTABLE on repeat)',
            'docs/43:306-308 and docs/43:507-510 (older 0.1 uB rules remain in force for their own scopes - which threshold governs a legacy 1x1 pair reused in S3 is a reading, FLAGGED)'],
        'M_source': 'converged TOTAL magnetisation (not absolute) from each member energy-of-record output, as parsed by the readout (docs/54:64-66; nspin=1 rows print no M)',
    },
    'scope_notes_flagged_not_resolved': [
        'which contrasts the exclusion applies to is not enumerated in the deposited text; symmetry pairs and A8.1 corners are the docs/54 infrastructure application (docs/54:55-58)',
        'cross-cell (1x1 vs 2x1v) M comparison has no registered rule; literal application flags trivially (atom count doubles); the descriptive doubled-1x1 residual carries NO registered basis',
        'where GATE-1 AGREE makes the __g1 child the energy of record but parent and child moments differ, which member M enters the comparison is unstated (docs/43:1573-1587 is exactly this case); this check uses the energy-of-record member M for cell-level pairs and reports parent-child drift separately',
        'nspin=1 systems (Ru, Ir, Ti here) print no M; whether they trivially satisfy or sit outside the rule is unstated',
        'PENDING/UNVERIFIED/UNCLASSIFIED members give provisional pairings only - nothing is banked from them',
    ],
    'counts': counts,
    'pairs': pairs,
    'flagged_pairs': [p['pair_id'] for p in flagged],
}

jpath = os.path.join('runs', 's3', 'readout', 'confound_2026-08-24.json')
with open(jpath, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, sort_keys=True)


def fmtM(m):
    return ('%.2f' % m) if m is not None else 'n/a'


lines = []
lines.append('# 0.05 uB magnetic CONFOUND check - S3 pair census (2026-08-24)')
lines.append('')
lines.append('Disclosed AI-drafted infrastructure. Input: `runs/s3/readout/s3_readout_2026-08-24.json` only.')
lines.append('No existing file was modified. Interpretive calls are FLAGGED, not resolved.')
lines.append('')
lines.append('## Registered rule (applied verbatim)')
lines.append('')
lines.append('> "a pair whose members differ in converged total magnetisation by more than 0.05 uB is')
lines.append('> CONFOUNDED - its energy difference mixes the intended contrast with a basin change - and is')
lines.append('> excluded from the contrast statistics and reported separately, exactly as a geometry confound is."')
lines.append('> - docs/43-prereg-week1-factorial.md:1566-1569 (THRESHOLD adopted as proposed 2026-08-23; DEPOSITED, GOVERNS)')
lines.append('')
lines.append('- Rationale registered with the threshold: docs/43:1569-1571 (observed drifts 11.00->14.90 and 11.00->14.71 uB).')
lines.append('- Treatment of a confounded pair: geometry precedent docs/43:306-310 (own table, excluded from every symmetry-effect statistic, counted in the report).')
lines.append('- Companion __g1 rule: docs/43:1589-1592 (child > 1 meV above parent refused; MULTISTABLE on repeat).')
lines.append('- M column source and nspin=1 behaviour: docs/54:64-66 (nspin=1 rows print no M).')
lines.append('- Older 0.1 uB rules (docs/43:306-308, :507-510) remain in force for their own scopes; which threshold governs a legacy 1x1 pair reused in S3 is a reading, not a registration - FLAGGED.')
lines.append('')


def table(klass, title, cols_contrast):
    sel = [p for p in pairs if p['class'] == klass]
    if not sel:
        return
    lines.append('## %s (%d pairs)' % (title, len(sel)))
    lines.append('')
    lines.append('| metal | state | %s | member A (file) | M_A (uB) | member B (file) | M_B (uB) | dM (uB) | dE A-B (meV) | verdict |' % cols_contrast)
    lines.append('|---|---|---|---|---|---|---|---|---|---|')
    for p in sel:
        a, b = p['member_a'], p['member_b']
        fa = a.get('file') or a.get('status', '-')
        fb = b.get('file') or b.get('status', '-')
        dm = ('%.2f' % p['delta_M_uB']) if p['delta_M_uB'] is not None else 'n/a'
        de = ('%+.2f' % p['delta_E_meV_a_minus_b']) if p['delta_E_meV_a_minus_b'] is not None else 'n/a'
        lines.append('| %s | %s | %s | `%s` | %s | `%s` | %s | %s | %s | %s |' % (
            p['metal'], p['state'], p['contrast'], fa, fmtM(a.get('M_uB')), fb, fmtM(b.get('M_uB')),
            dm, de, p['verdict']))
    lines.append('')
    noted = [p for p in sel if p['notes'] or p.get('provisional_pairings') or p.get('alternate_member_a')]
    if noted:
        lines.append('Per-row tags:')
        lines.append('')
        for p in noted:
            for n in p['notes']:
                lines.append('- **%s**: %s' % (p['pair_id'], n))
            if p.get('alternate_member_a'):
                am = p['alternate_member_a']
                lines.append('- **%s**: alternate mir member `%s` M %.2f -> |dM| %.2f vs off (%s if that member is chosen)' % (
                    p['pair_id'], am['file'], am['M_uB'], am['delta_M_uB_vs_off'], am['verdict_if_member']))
            for pr in p.get('provisional_pairings', []) or []:
                lines.append('- **%s** provisional: %s `%s` M %.2f vs %s `%s` M %.2f -> |dM| %.2f (%s 0.05 uB) - provisional only, nothing banked' % (
                    p['pair_id'], pr['a']['which'], pr['a']['file'], pr['a']['M_uB'],
                    pr['b']['which'], pr['b']['file'], pr['b']['M_uB'], pr['delta_M_uB'],
                    'exceeds' if pr['exceeds_0.05'] else 'within'))
        lines.append('')


table('symmetry(mir-vs-off)', 'Symmetry pairs (mir vs off) - the registered A8.3 application (docs/54:55-58)', 'coverage')
table('cell(1x1-vs-2x1v)', 'Cell pairs (1x1 vs 2x1v) - NO registered cross-cell M rule; literal + descriptive only', 'arm')
table('parent-vs-g1-child', 'Parent vs __g1 child - A8.3 scope is a reading (docs/43:1589-1592 is the registered parent-child rule); drift computed as tasked', 'coverage/arm')
table('record-vs-superseded-production', 'Basin-substitution record vs superseded production (docs/41 metastable-magnetic class; docs/54:400-405)', 'coverage/arm')

lines.append('## Flagged pairs (beyond 0.05 uB, all classes)')
lines.append('')
for p in flagged:
    a, b = p['member_a'], p['member_b']
    dm = ('%.2f uB' % p['delta_M_uB']) if p['delta_M_uB'] is not None else 'see provisional pairings'
    lines.append('- **%s** [%s]: M_A %s vs M_B %s (|dM| %s)' % (
        p['pair_id'], p['verdict'], fmtM(a.get('M_uB')), fmtM(b.get('M_uB')), dm))
lines.append('')
lines.append('## Counts')
lines.append('')
lines.append('```json')
lines.append(json.dumps(counts, indent=2, sort_keys=True))
lines.append('```')
lines.append('')
lines.append('## Scope questions FLAGGED, not resolved')
lines.append('')
for s in out['scope_notes_flagged_not_resolved']:
    lines.append('- %s' % s)
lines.append('')

mpath = os.path.join('runs', 's3', 'readout', 'confound_2026-08-24.md')
with open(mpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('WROTE', jpath, 'and', mpath)
print('pairs_total', counts['pairs_total'])
print('flagged', counts['flagged_beyond_0.05uB'])
for k, v in sorted(counts['by_verdict'].items()):
    print(' ', k, v)
print('FLAGGED:')
for p in flagged:
    print(' ', p['pair_id'], '|', p['verdict'], '| Ma', p['member_a'].get('M_uB'), 'Mb', p['member_b'].get('M_uB'), '| dM', p['delta_M_uB'])
print('SPLIT/PROV DETAILS:')
for p in pairs:
    for pr in p.get('provisional_pairings', []) or []:
        print(' ', p['pair_id'], pr['a']['which'], pr['a']['M_uB'], 'vs', pr['b']['which'], pr['b']['M_uB'], '->', pr['delta_M_uB'], 'exceeds' if pr['exceeds_0.05'] else 'within')
