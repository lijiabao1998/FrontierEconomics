#!/usr/bin/env python3
"""Frozen three-cell description, never a firm productivity/causal estimator.
Python standard library only. No network, randomness, packages or microdata.
"""
import argparse
import hashlib
import json
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path

GROUPS = ('Information', 'Finance and Insurance', 'National')
PAIRS = ((GROUPS[0], GROUPS[1]), (GROUPS[0], GROUPS[2]), (GROUPS[1], GROUPS[2]))
Q = Decimal('0.000000000001')
HALF_STEP = Decimal('0.05')


def validate(data):
    if data.get('unit') != 'percent of businesses, as published to one decimal place':
        raise ValueError('wrong unit')
    if data.get('reference_period_end') != '2026-05-03':
        raise ValueError('wrong endpoint')
    if data.get('measure') != 'self-reported AI use in any business function in the past two weeks':
        raise ValueError('wrong measure')
    cells = data.get('cells', [])
    if len(cells) != 3 or sorted(c['group'] for c in cells) != sorted(GROUPS):
        raise ValueError('missing, extra or duplicate domain')
    rates = {}
    for cell in cells:
        try:
            x = Decimal(cell['rate_percent'])
        except Exception as exc:
            raise ValueError('missing or nonnumeric rate') from exc
        if not x.is_finite() or x < 0 or x > 100:
            raise ValueError('rate outside [0,100]')
        if x.as_tuple().exponent != -1:
            raise ValueError('unexpected source precision')
        rates[cell['group']] = x
    return rates


def contrast(a, b):
    if b <= HALF_STEP:
        raise ValueError('ratio denominator rounding envelope includes zero')
    with localcontext() as ctx:
        ctx.prec = 40
        return {'difference_pp': str(a-b),
                'ratio': str((a/b).quantize(Q, rounding=ROUND_HALF_EVEN)),
                'conditional_rounding_difference_pp': [str(a-b-2*HALF_STEP), str(a-b+2*HALF_STEP)],
                'conditional_rounding_ratio': [str(((a-HALF_STEP)/(b+HALF_STEP)).quantize(Q, rounding=ROUND_HALF_EVEN)),
                                                str(((a+HALF_STEP)/(b-HALF_STEP)).quantize(Q, rounding=ROUND_HALF_EVEN))]}


def compute(data):
    rates = validate(data)
    return {'scope': 'Description of three published rounded AI-use rates only; no causal or productivity estimate.',
            'inference': 'NOT_ESTIMATED: no survey variance, covariance, confidence intervals or p-values.',
            'rounding_note': 'Conditional on nearest 0.1 percentage-point rounding. Envelopes are not statistical confidence intervals.',
            'contrasts': [{'numerator': a, 'denominator': b, **contrast(rates[a], rates[b])} for a, b in PAIRS]}


def verify(data, result):
    # Same author arithmetic checks are NOT independent source/statistical validation.
    rates = validate(data)
    if len(result['contrasts']) != 3:
        raise ValueError('wrong contrast count')
    for item, pair in zip(result['contrasts'], PAIRS):
        a, b = pair
        if (item['numerator'], item['denominator']) != pair:
            raise ValueError('wrong contrast pairing')
        if Decimal(item['difference_pp']) != rates[a] - rates[b]:
            raise ValueError('wrong difference')
        if abs(Decimal(item['ratio']) * rates[b] - rates[a]) > Q*rates[b]/2:
            raise ValueError('wrong ratio')
        for field, point in [('conditional_rounding_difference_pp',Decimal(item['difference_pp'])),
                             ('conditional_rounding_ratio',Decimal(item['ratio']))]:
            lo, hi = map(Decimal, item[field])
            if not lo <= point <= hi:
                raise ValueError('rounding envelope misses point')
    x, y, z = result['contrasts']
    if Decimal(y['difference_pp']) != Decimal(x['difference_pp']) + Decimal(z['difference_pp']):
        raise ValueError('difference consistency failure')
    if abs(Decimal(x['ratio'])*Decimal(z['ratio'])-Decimal(y['ratio'])) > Decimal('2e-12'):
        raise ValueError('ratio consistency failure')


def read_inputs(root, record):
    r = json.loads(record.read_text())
    if r.get('state') not in ('ADMITTED', 'RUNNING', 'FINISHED') or not r.get('admitted_at'):
        raise ValueError('round is not admitted')
    spec_path = record.parent/'frozen-spec.json'
    if hashlib.sha256(spec_path.read_bytes()).hexdigest() not in r['acceptance']:
        raise ValueError('frozen specification checksum mismatch')
    spec = json.loads(spec_path.read_text())
    raw = (root/spec['dataset_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec['dataset_sha256']:
        raise ValueError('source checksum mismatch')
    return json.loads(raw)


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument('--round',required=True);p.add_argument('--output',type=Path)
    args=p.parse_args();result=compute(data:=read_inputs(args.root,args.root/'runs'/args.round/'round.json'));verify(data,result)
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')
if __name__=='__main__':main()
