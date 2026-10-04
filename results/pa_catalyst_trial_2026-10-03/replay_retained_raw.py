"""Read-only adapter replay of retained actual tiny-QE evidence; no solver."""
import hashlib,json,pathlib,sys
PHASE=pathlib.Path(__file__).resolve().parent
ROOT=PHASE.parents[1]
sys.path.insert(0,str(ROOT/'src/dft'))
import pa_qe_adapter as adapter

def main(label):
    assert label in {'initial','checked','release'}
    receipt=PHASE/('raw_replay_'+label+'.json');assert not receipt.exists()
    raw=ROOT/'results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw/tiny_results'
    directory=raw/'candidate-stop'
    report={'scope':'RETAINED_ACTUAL_TINY_STOP_RAW_REPLAY_ONLY','new_jobs':0,'qe_executed':False,'production_accepted':False,'successful':False}
    try:
        expected=adapter.parse_deck(directory/'input.in')
        pseudo=directory/'H.pbe-rrkjus_psl.1.0.0.UPF'
        expected['upf_pins']={pseudo.name:'27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962'}
        logged='/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/tiny_results/candidate-stop/'+pseudo.name
        expected['upf_read_path_map']={logged:str(pseudo)}
        process=json.loads((directory/'receipt.json').read_text())
        parsed=adapter.read_qe_arm(directory/'input.in',directory/'stdout.log',directory/'stderr.log',
            directory/'scratch/h2_probe.save/data-file-schema.xml',process,expected_settings=expected,
            expected_parallel={'nprocs':1,'nthreads':1,'ntasks':1,'nbgrp':1,'npool':1,'ndiag':1},
            expected_exit='clean_stop',expected_evaluations=1)
        assert parsed['scf_counts']==[1] and parsed['optimizer_counts']==[0]
        history=adapter.read_bfgs(directory/'scratch/h2_probe.bfgs',nat=2,
            cell_bohr=parsed['evaluations'][0]['geometry']['cell'],evaluated=parsed['evaluations'][0])
        assert (history['scf_count'],history['bfgs_count'],history['gdiis_count'])==(1,1,0)
        report.update(successful=True,arm=parsed,saved_optimizer=history)
    except BaseException as exc:
        report['error']=repr(exc);raise
    finally:
        report['adapter_sha256']=hashlib.sha256((ROOT/'src/dft/pa_qe_adapter.py').read_bytes()).hexdigest()
        receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'successful':True,'evaluations':len(parsed['evaluations']),'counters':parsed['scf_counts'],'proposal_distinct':parsed['proposal_geometry']!=parsed['evaluations'][0]['geometry'],'qe_executed':False}))

if __name__=='__main__':main(sys.argv[1])
