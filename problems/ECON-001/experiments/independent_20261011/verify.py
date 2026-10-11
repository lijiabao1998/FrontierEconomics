"""UNEXECUTED proposal: eight-corner Fraction oracle and fixed mutation probes."""
import argparse
import ast
import copy
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from admission_guard import require_admission

HERE=Path(__file__).resolve().parent
OLDROUND='runs/20261009T115523985642Z-gpt-ECON-001'
SOURCE=OLDROUND+'/source-extract.json'
SPEC=OLDROUND+'/frozen-spec.json'
BASELINE='problems/ECON-001/results/btos-baseline.json'
AUTHOR='problems/ECON-001/experiments/btos_baseline.py'
EXISTING='problems/ECON-001/experiments/independent_review/verify_economics.py'
EXPECTED_NAMES=('p0-difference-lo','p0-difference-hi','p0-ratio-lo','p0-ratio-hi',
                'p1-difference-lo','p1-difference-hi','p1-ratio-lo','p1-ratio-hi',
                'p2-difference-lo','p2-difference-hi','p2-ratio-lo','p2-ratio-hi')

def fixed(f,places):
    # Integer arithmetic ties-to-even, independent of the author's Decimal display.
    sign='-' if f<0 else ''; f=abs(f);scale=10**places
    q,r=divmod(f.numerator*scale,f.denominator)
    if 2*r>f.denominator or (2*r==f.denominator and q%2):q+=1
    if not places:return sign+str(q)
    return sign+str(q//scale)+'.'+str(q%scale).zfill(places)

def oracle(data):
    cells=data['cells'];groups=['Information','Finance and Insurance','National']
    if [x['group'] for x in cells]!=groups or [x['rate_percent'] for x in cells]!=['39.7','33.9','19.8']:
        raise ValueError('frozen cells mismatch')
    rates=[F(x['rate_percent']) for x in cells]
    corners=[tuple(x+F(s,20) for x,s in zip(rates,signs)) for signs in itertools.product((-1,1),repeat=3)]
    contrasts=[]; certificates=[]
    for i,j in ((0,1),(0,2),(1,2)):
        differences=[c[i]-c[j] for c in corners];ratios=[c[i]/c[j] for c in corners]
        lo_d,hi_d=min(differences),max(differences);lo_r,hi_r=min(ratios),max(ratios)
        contrasts.append({'numerator':groups[i],'denominator':groups[j],
          'difference_pp':fixed(rates[i]-rates[j],1),'ratio':fixed(rates[i]/rates[j],12),
          'conditional_rounding_difference_pp':[fixed(lo_d,2),fixed(hi_d,2)],
          'conditional_rounding_ratio':[fixed(lo_r,12),fixed(hi_r,12)]})
        certificates.append({'pair':[i,j],'difference_extrema_exact':[str(lo_d),str(hi_d)],
                             'ratio_extrema_exact':[str(lo_r),str(hi_r)],
                             'eight_corner_differences':[str(x) for x in differences],
                             'eight_corner_ratios':[str(x) for x in ratios]})
    return contrasts,certificates

def strict(data,value,expected):
    if 'NOT_ESTIMATED' not in value.get('inference',''):return False
    if len(value.get('contrasts',[]))!=3:return False
    for v,e in zip(value['contrasts'],expected):
        if v.get('numerator')!=e['numerator'] or v.get('denominator')!=e['denominator']:return False
        for field in ('difference_pp','conditional_rounding_difference_pp'):
            try:
                if isinstance(e[field],list):
                    if list(map(F,v[field]))!=list(map(F,e[field])):return False
                elif F(v[field])!=F(e[field]):return False
            except Exception:return False
        for field in ('ratio','conditional_rounding_ratio'):
            if v.get(field)!=e[field]:return False
    return True

def author_verifier(path):
    # Extract the actual reviewed verify/validate component, avoiding author main.
    tree=ast.parse(path.read_text(encoding='utf-8'))
    nodes=[]
    for n in tree.body:
        if isinstance(n,ast.ImportFrom) and n.module=='decimal':nodes.append(n)
        elif isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'GROUPS','PAIRS','Q','HALF_STEP'} for t in n.targets):nodes.append(n)
        elif isinstance(n,ast.FunctionDef) and n.name in {'validate','verify'}:nodes.append(n)
    namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
    return namespace['verify']

def existing_probe(ref, result, destination):
    args=[sys.executable,str(ref/EXISTING),str(ref/SPEC),str(ref/SOURCE),str(result)]
    try:
        p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
        destination.with_suffix('.stdout.txt').write_bytes(p.stdout)
        destination.with_suffix('.stderr.txt').write_bytes(p.stderr)
        assertion=(p.returncode==1 and p.stderr.decode('utf-8',errors='replace').strip().splitlines()[-1].startswith('AssertionError')) if p.stderr.strip() else False
        record={'args':args,'exit_code':p.returncode,'accepted':p.returncode==0,'timeout':False,
                'rejection_kind':'ASSERTION_REJECTION' if assertion else 'ACCEPTED' if p.returncode==0 else 'INFRASTRUCTURE_ERROR'}
    except subprocess.TimeoutExpired as exc:
        destination.with_suffix('.stdout.txt').write_bytes(exc.stdout or b'')
        destination.with_suffix('.stderr.txt').write_bytes(exc.stderr or b'')
        record={'args':args,'exit_code':None,'accepted':False,'timeout':True,'rejection_kind':'TIMEOUT'}
    destination.with_suffix('.execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record

def probe_author(fn,data,result):
    try:fn(data,result);return {'accepted':True,'exception':None}
    except ValueError as exc:return {'accepted':False,'exception':str(exc)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--round',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();require_admission(a.repo,a.round,'ECON-001',HERE/'PROTOCOL.json')
    ref=HERE/'reference';a.output.parent.mkdir(parents=True,exist_ok=True)
    for relative,digest in [(SPEC,'dddbb90164fbc462fc0f0e63c825adba973f75beed41ee3b9e88b8a97168b78c'),(SOURCE,'b209468564207f7f29c9d56aaaab831775b951eb1436bf0f076496629ec71cae')]:
        if hashlib.sha256((ref/relative).read_bytes()).hexdigest()!=digest:raise ValueError('frozen input hash mismatch')
    data=json.loads((ref/SOURCE).read_text());baseline=json.loads((ref/BASELINE).read_text())
    contrasts,certificate=oracle(data);fn=author_verifier(ref/AUTHOR)
    cases=[('normal',baseline)]
    for pair in range(3):
        for field,label,places in [('conditional_rounding_difference_pp','difference',2),('conditional_rounding_ratio','ratio',12)]:
            for end,side in enumerate(('lo','hi')):
                value=copy.deepcopy(baseline);point=F(value['contrasts'][pair][field][end])+F(-1 if end==0 else 1,100)
                value['contrasts'][pair][field][end]=fixed(point,places)
                cases.append((f'p{pair}-{label}-{side}',value))
    if tuple(n for n,_ in cases[1:])!=EXPECTED_NAMES:raise ValueError('negative-control completeness failure')
    matrix=[]
    for name,value in cases:
        path=a.output.parent/(name+'.json');path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        author=probe_author(fn,data,value)
        existing=existing_probe(ref,path,a.output.parent/(name+'-existing'))
        matrix.append({'name':name,'new_fraction_accepts':strict(data,value,contrasts),'author':author,'existing_independent':existing})
    normal=matrix[0];normal_pass=normal['new_fraction_accepts'] and normal['author']['accepted'] and normal['existing_independent']['accepted']
    no_timeouts=all(not m['existing_independent']['timeout'] for m in matrix)
    negatives=matrix[1:]
    new_reject=all(not m['new_fraction_accepts'] for m in negatives)
    existing_reject=all(m['existing_independent']['rejection_kind']=='ASSERTION_REJECTION' for m in negatives)
    author_reject=all(not m['author']['accepted'] for m in negatives)
    verdict='AUDIT_PASS' if normal_pass and no_timeouts and new_reject and existing_reject and author_reject else 'AUDIT_FAIL_EVALUATOR_CONTRACT'
    if not normal_pass or not no_timeouts or not new_reject or not existing_reject:verdict='FAIL_CLOSED_OR_ORACLE_MISMATCH'
    result={'verdict':verdict,'matrix':matrix,'exact_corner_certificates':certificate,'normal_pass':normal_pass,
            'new_rejects_all12':new_reject,'existing_rejects_all12':existing_reject,'author_rejects_all12':author_reject,
            'smallest_fixed_order_counterexample':next((m for m in negatives if m['author']['accepted'] and not m['new_fraction_accepts'] and not m['existing_independent']['accepted']),None),
            'scope':'Three rounded manually transcribed cells only; rounding envelopes are not sampling CI. No causal/productivity inference.'}
    text=json.dumps(result,indent=2)+'\n';a.output.write_text(text,encoding='utf-8');print(text,end='')
    return 0 if verdict=='AUDIT_PASS' else 1 if verdict=='AUDIT_FAIL_EVALUATOR_CONTRACT' else 2

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        import traceback
        print(json.dumps({'status':'FAIL_CLOSED','error':str(exc)}),file=sys.stderr);traceback.print_exc();sys.exit(2)
