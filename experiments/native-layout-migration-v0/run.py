"""Fresh deterministic execution. Stored reports are never used as verdict inputs."""
import argparse
import importlib.metadata
import io
import json
import platform
import sys
import unittest
from pathlib import Path

import checker as ck

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='517d407f507fd6401bc6edb4979b5a6673122d40'
TEST_COUNT=25
DEPENDENCIES={'attrs':'26.1.0','cffi':'2.1.1','cryptography':'50.0.2','jsonschema':'4.26.0',
              'jsonschema-specifications':'2025.9.1','pycparser':'3.12','referencing':'0.37.0',
              'rfc8785':'0.1.4','rpds-py':'2026.9.1','typing_extensions':'4.16.0'}
ASSETS={'checker.py','schema_builder.py','candidate.schema.json','fixtures.py','test_checker.py','run.py',
        'requirements.txt','report_controls.py','sources.json','data/cases.json',
        'data/example-bundle.json','data/example-context.json','data/coverage.json'}

def audit():
    versions={k:importlib.metadata.version(k) for k in DEPENDENCIES}
    ck.need(versions==DEPENDENCIES,'research dependency version mismatch')
    src=ck.strict_json((HERE/'sources.json').read_bytes())
    ck.need(set(src)=={'base_commit','status','files'} and src['base_commit']==BASE and src['status']=='UNADOPTED','source manifest context')
    ck.need(len(src['files'])==204,'baseline inventory count')
    for name,digest in src['files'].items():
        p=ROOT/name;ck.need(p.resolve().is_relative_to(ROOT.resolve()),'unsafe source path')
        ck.need(ck.digest(p.read_bytes())==digest,'baseline file changed: '+name)
    manifest=ck.strict_json((HERE/'manifest.json').read_bytes())
    ck.need(set(manifest)=={'status','assets'} and manifest['status']=='UNADOPTED' and set(manifest['assets'])==ASSETS,'experiment asset inventory')
    for name,digest in manifest['assets'].items():ck.need(ck.digest((HERE/name).read_bytes())==digest,'experiment asset changed: '+name)
    coverage=ck.strict_json((HERE/'data/coverage.json').read_bytes())
    inv=ck.strict_json((ROOT/'proposals/numeric-fields-2026-10-25/inventory.json').read_bytes())
    ck.need([r['id'] for r in coverage['entries']]==[r['id'] for r in inv['fields']],'coverage inventory order')
    ck.need(all(r['source_path']==s['path'] for r,s in zip(coverage['entries'],inv['fields'])),'coverage path drift')
    ck.need({s:sum(r['status']==s for r in coverage['entries']) for s in
             ('EXERCISED_SUBSET','NEW_SEMANTICS_ONLY','UNASSESSED')}==
            {'EXERCISED_SUBSET':9,'NEW_SEMANTICS_ONLY':1,'UNASSESSED':64},'coverage status accounting')
    return versions,manifest

def execute():
    versions,manifest=audit()
    data=ck.strict_json((HERE/'data/cases.json').read_bytes())
    ck.need(set(data)=={'status','independent_reproduction','cases','unit_cases'} and data['status']=='UNADOPTED' and data['independent_reproduction']=='not_established','case metadata')
    ck.need(len(data['cases'])==55 and len({c['id'] for c in data['cases']})==55,'bundle case inventory')
    outputs=[];mismatches=[];counts={s:0 for s in ('PASS','FAIL','UNASSESSED')}
    for case in data['cases']:
        ck.need(set(case)=={'id','reason','bundle','context','expected'} and set(case['expected'])==set(ck.AXES),'case shape')
        ck.need(set(case['expected'].values())<={'PASS','FAIL','UNASSESSED'},'expectation status')
        result=ck.check(case['bundle'],case['context'])
        actual={k:v['status'] for k,v in result['checks'].items()}
        if actual!=case['expected']:mismatches.append(case['id'])
        counts[result['covered_checks']]+=1
        outputs.append({'id':case['id'],'bundle_digest':ck.digest(ck.jcs(case['bundle'])),
                        'context_digest':ck.digest(ck.jcs(case['context'])),'result':result})
    units=[];unit_counts={s:0 for s in counts}
    ck.need(len(data['unit_cases'])==14 and len({u['id'] for u in data['unit_cases']})==14,'unit case inventory')
    for c in data['unit_cases']:
        try:value=ck.convert(c['value'],c['source_unit'],c['target_unit']);status='PASS'
        except ck.Finding as e:value=None;status=e.status
        if not ck.same((status,value),(c['expected_status'],c['expected_value'])):mismatches.append(c['id'])
        unit_counts[status]+=1;units.append({'id':c['id'],'status':status,'value':value})
    suite=unittest.defaultTestLoader.discover(str(HERE),pattern='test_checker.py')
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    tests_ok=(result.wasSuccessful() and result.testsRun==TEST_COUNT and not result.skipped
              and not result.expectedFailures and not result.unexpectedSuccesses)
    report={'status':'UNADOPTED','independent_reproduction':'not_established','native_conformance':'UNASSESSED',
      'base_commit':BASE,'implementation_and_inputs_digest':ck.digest(ck.jcs(manifest)),
      'environment':{'python':platform.python_version(),'platform':sys.platform,'dependencies':versions},
      'summary':{'bundle_cases':len(outputs),'bundle_status_counts':counts,'unit_cases':len(units),
                 'unit_status_counts':unit_counts,'regression_tests':result.testsRun,
                 'no_skips_or_expected_failures':not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses,
                 'mismatches':mismatches,'all_expected_results_and_controls_pass':not mismatches and tests_ok},
      'cases':outputs,'unit_results':units,
      'regressions':{'success':tests_ok,'failures':[(str(t),s) for t,s in result.failures],
                    'errors':[(str(t),s) for t,s in result.errors]}}
    if not tests_ok:print(stream.getvalue(),file=sys.stderr)
    return report

def verify_report(stored,fresh):
    # Exact typed comparison of the whole output, not only counts or success flags.
    ck.need(ck.same(stored,fresh),'stored report differs from fresh execution')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--verify-report',type=Path)
    a=p.parse_args()
    try:
        result=execute()
        if a.verify_report:verify_report(ck.strict_json(a.verify_report.read_bytes()),result)
        if a.output:
            with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
        print(json.dumps(result['summary'],indent=2))
        return 0 if result['summary']['all_expected_results_and_controls_pass'] else 1
    except (ck.Finding,ValueError,OSError) as e:
        print(str(e),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
