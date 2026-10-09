"""Independent exact-rational replay of three published Census cells.
No author imports. Source page separately checked by coordinator2026-10-09.
Usage: python verify_economics.py frozen-spec.json source-extract.json
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
import hashlib,json,sys
spec=Path(sys.argv[1]);extract=Path(sys.argv[2]);s=json.loads(spec.read_text());x=json.loads(extract.read_text())
assert hashlib.sha256(spec.read_bytes()).hexdigest()=='dddbb90164fbc462fc0f0e63c825adba973f75beed41ee3b9e88b8a97168b78c'
assert hashlib.sha256(extract.read_bytes()).hexdigest()==s['dataset_sha256']=='b209468564207f7f29c9d56aaaab831775b951eb1436bf0f076496629ec71cae'
assert x['source_url']=='https://www.census.gov/library/stories/2026/05/ai-use-businesses.html'
assert x['reference_period_end']=='2026-05-03';assert x['unit']=='percent of businesses, as published to one decimal place'
assert x['cells']==[{'group':'Information','rate_percent':'39.7'},{'group':'Finance and Insurance','rate_percent':'33.9'},{'group':'National','rate_percent':'19.8'}]
rates={c['group']:F(c['rate_percent']) for c in x['cells']};assert len(rates)==3
pairs=[('Information','Finance and Insurance'),('Information','National'),('Finance and Insurance','National')]
def dec(f):
 with localcontext() as c:
  c.prec=60
  return str((Decimal(f.numerator)/Decimal(f.denominator)).quantize(Decimal('0.000000000001'),rounding=ROUND_HALF_EVEN))
out=[]
for a,b in pairs:
 u,v=rates[a],rates[b];q=u/v;lo=(u-F(1,20))/(v+F(1,20));hi=(u+F(1,20))/(v-F(1,20));assert lo<=q<=hi
 out.append({'numerator':a,'denominator':b,'difference_pp_exact':str(u-v),'difference_pp_decimal':dec(u-v),'rate_ratio_exact':str(q),'rate_ratio_12dp':dec(q),'rounding_only_difference_pp':[dec(u-v-F(1,10)),dec(u-v+F(1,10))],'rounding_only_ratio':[dec(lo),dec(hi)]})
assert rates['Information']-rates['National']==(rates['Information']-rates['Finance and Insurance'])+(rates['Finance and Insurance']-rates['National'])
assert rates['Information']/rates['National']==(rates['Information']/rates['Finance and Insurance'])*(rates['Finance and Insurance']/rates['National'])
if len(sys.argv)>3:
 author=json.loads(Path(sys.argv[3]).read_text())
 assert len(author['contrasts'])==3
 for a,b in zip(author['contrasts'],out):
  assert a['numerator']==b['numerator'] and a['denominator']==b['denominator']
  assert F(a['difference_pp'])==F(b['difference_pp_exact'])
  assert a['ratio']==b['rate_ratio_12dp']
  assert list(map(F,a['conditional_rounding_difference_pp']))==list(map(F,b['rounding_only_difference_pp']))
  assert a['conditional_rounding_ratio']==b['rounding_only_ratio']
 assert 'NOT_ESTIMATED' in author['inference']
print(json.dumps({'status':'PASS','comparisons':out,'source_independently_read':'Census article section AI Trends Across Sectors first bullet, accessed2026-10-09; three cells and November17,2025 wording break confirmed','limits':'Arithmetic of published rounded survey estimates only; assumed rounding envelope is not sampling CI; overlapping national domain; no unrounded microdata, weights, SEs, productivity outcome or causal identification verified. No article text copied.'},indent=2))
