"""Internal saved-report mutation checks; no host or operator authentication."""
import copy
import json
import sys
from pathlib import Path
import checker as ck
import run

def main():
    stored=ck.strict_json(Path(sys.argv[1]).read_bytes())
    fresh=run.execute()
    ck.need(fresh['summary']['all_expected_results_and_controls_pass'],'fresh execution failed')
    run.verify_report(stored,fresh)
    outcomes=[]
    mutations=[
      ('case-omitted',lambda r:r['cases'].pop()),
      ('count-forged',lambda r:r['summary'].update(regression_tests=999)),
      ('boolean-for-count',lambda r:r['summary'].update(regression_tests=True)),
      ('dependency-forged',lambda r:r['environment']['dependencies'].update(cryptography='0.0.0')),
      ('input-fingerprint-forged',lambda r:r['cases'][0].update(bundle_digest='sha256:'+'0'*64)),
      ('unassessed-promoted',lambda r:r.update(native_conformance='PASS')),
      ('source-failure-promoted',lambda r:next(c for c in r['cases'] if c['id']=='retained-source-byte-changed')['result']['checks']['source_retention'].update(status='PASS')),
      ('implementation-fingerprint-forged',lambda r:r.update(implementation_and_inputs_digest='sha256:'+'0'*64)),
    ]
    for name,mutate in mutations:
        bad=copy.deepcopy(stored);mutate(bad)
        try:run.verify_report(bad,fresh)
        except ck.Finding:outcomes.append({'id':name,'rejected':True})
        else:outcomes.append({'id':name,'rejected':False})
    result={'status':'UNADOPTED','independent_reproduction':'not_established','controls':outcomes,
            'all_controls_matched':all(c['rejected'] for c in outcomes)}
    print(json.dumps(result,indent=2));return 0 if result['all_controls_matched'] else 1

if __name__=='__main__':raise SystemExit(main())
