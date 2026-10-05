"""Apply the independent formatting clearance before the unchanged reviewed publisher."""
import hashlib,json,pathlib
ROOT=pathlib.Path('C:/Users/frank/sts-electrocatalyst')
OUT=ROOT/'results/pa_catalyst_retest_readout_2026-10-05'
review=json.loads((OUT/'publication_format_review.json').read_bytes())
assert review['decision']=='GO_EXACT_BYTE_PUBLICATION_ONLY'
assert review['blocking_findings']==[]
for pin in review['pins']:
 path=(ROOT/pin['path']).resolve()
 assert path.is_relative_to(ROOT.resolve())
 assert hashlib.sha256(path.read_bytes()).hexdigest()==pin['sha256'],pin['path']
assert hashlib.sha256((OUT/'independent_readout_review.json').read_bytes()).hexdigest()=='53f929f0f742b4fb2866374893634fc513c69d5705a931625764ff9b09a2b7a0'
assert hashlib.sha256((OUT/'bank_readout.py').read_bytes()).hexdigest()=='2ef2eb16238485c9b1e0de3480a4e19dcebfd660972c16f993e1ac29127f090a'
exec(compile((OUT/'bank_readout.py').read_bytes(),str(OUT/'bank_readout.py'),'exec'))
