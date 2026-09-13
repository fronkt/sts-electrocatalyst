"""JSON-only census interface for explicit QE paths or an OC20 sample directory."""
import argparse
import json
from pathlib import Path
from . import __version__
from .census import census

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',action='version',version=__version__)
    subs=p.add_subparsers(dest='command',required=True)
    c=subs.add_parser('census')
    inputs=c.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--paths-from',type=Path)
    inputs.add_argument('--oc20',type=Path)
    c.add_argument('--json',action='store_true',help='JSON output (also the default)')
    args=p.parse_args(argv)
    if args.paths_from:
        paths=[x.strip().replace('\\','/') for x in args.paths_from.read_text(encoding='utf8').splitlines() if x.strip()]
    else:
        if not args.oc20.is_dir(): p.error('OC20 sample directory does not exist')
        paths=sorted(x for x in args.oc20.iterdir() if x.name.endswith(('.extxyz','.extxyz.xz')))
        if not paths: p.error('OC20 sample has no extended-XYZ trajectories')
    print(json.dumps(census(paths,oc20=args.oc20 is not None),allow_nan=False))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
