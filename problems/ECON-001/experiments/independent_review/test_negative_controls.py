"""Corrupt disposable copies of input/result; unchanged reviewer must reject."""
import json,pathlib,subprocess,sys,tempfile,shutil
spec,source,result=map(pathlib.Path,sys.argv[1:4]);script=pathlib.Path(__file__).with_name('verify_economics.py');reports=[]
for case in ['result_difference','source_rate']:
 with tempfile.TemporaryDirectory() as tmp:
  root=pathlib.Path(tmp);ss=root/'source.json';rr=root/'result.json';shutil.copy(source,ss);shutil.copy(result,rr)
  if case=='result_difference':
   x=json.loads(rr.read_text());x['contrasts'][0]['difference_pp']='5.9';rr.write_text(json.dumps(x))
  else:
   x=json.loads(ss.read_text());x['cells'][0]['rate_percent']='49.7';ss.write_text(json.dumps(x))
  r=subprocess.run([sys.executable,str(script),str(spec),str(ss),str(rr)],capture_output=True,text=True,timeout=10);assert r.returncode!=0
  reports.append({'case':case,'rejected':True,'exit_code':r.returncode,'reason':r.stderr.splitlines()[-1]})
print(json.dumps(reports,indent=2))
