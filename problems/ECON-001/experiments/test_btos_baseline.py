import copy
import importlib.util
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

P=Path(__file__).parent
spec=importlib.util.spec_from_file_location('baseline',P/'btos_baseline.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=P.parents[2]
ROUND=ROOT/'runs/20261009T115523985642Z-gpt-ECON-001'
DATA=json.loads((ROUND/'source-extract.json').read_text())

class BaselineTests(unittest.TestCase):
    def test_positive_decimal(self):
        self.assertEqual(m.contrast(Decimal('10.0'),Decimal('5.0'))['difference_pp'],'5.0')
        self.assertEqual(m.contrast(Decimal('10.0'),Decimal('5.0'))['ratio'],'2.000000000000')
    def test_equal_rate_boundary(self):
        r=m.contrast(Decimal('1.0'),Decimal('1.0'))
        self.assertEqual(Decimal(r['difference_pp']),0);self.assertEqual(Decimal(r['ratio']),1)
    def test_zero_denominator_boundary(self):
        with self.assertRaises(ValueError):m.contrast(Decimal('1.0'),Decimal('0.0'))
    def test_valid_frozen_data(self):
        data=m.read_inputs(ROOT,ROUND/'round.json');r=m.compute(data);m.verify(data,r)
    def test_missing_cell(self):
        d=copy.deepcopy(DATA);d['cells'].pop()
        with self.assertRaises(ValueError):m.validate(d)
    def test_duplicate_cell(self):
        d=copy.deepcopy(DATA);d['cells'][1]=d['cells'][0]
        with self.assertRaises(ValueError):m.validate(d)
    def test_invalid_rates(self):
        for invalid in ('101.0','-0.1','NaN','Infinity','not a number',None):
            with self.subTest(invalid=invalid):
                d=copy.deepcopy(DATA);d['cells'][0]['rate_percent']=invalid
                with self.assertRaises(ValueError):m.validate(d)
    def test_wrong_date(self):
        d=copy.deepcopy(DATA);d['reference_period_end']='2023-11-13'
        with self.assertRaises(ValueError):m.validate(d)
    def test_wrong_units(self):
        d=copy.deepcopy(DATA);d['unit']='proportion'
        with self.assertRaises(ValueError):m.validate(d)
    def test_wrong_measure(self):
        d=copy.deepcopy(DATA);d['measure']='AI exposure'
        with self.assertRaises(ValueError):m.validate(d)
    def test_deliberately_wrong_arithmetic(self):
        r=m.compute(DATA);r['contrasts'][0]['difference_pp']='999.0'
        with self.assertRaises(ValueError):m.verify(DATA,r)
    def test_deliberately_wrong_ratio(self):
        r=m.compute(DATA);r['contrasts'][0]['ratio']='999.0'
        with self.assertRaises(ValueError):m.verify(DATA,r)
    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);run=root/ROUND.relative_to(ROOT);run.mkdir(parents=True)
            for f in ('round.json','frozen-spec.json','source-extract.json'):(run/f).write_bytes((ROUND/f).read_bytes())
            with (run/'source-extract.json').open('a') as f:f.write(' ')
            with self.assertRaisesRegex(ValueError,'source checksum'):m.read_inputs(root,run/'round.json')
if __name__=='__main__':unittest.main(verbosity=2)
