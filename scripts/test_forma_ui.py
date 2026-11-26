#!/usr/bin/env python3
"""Deterministic static CLI checks; optional browser evidence is separate."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/'scripts/forma_ui.py'
EX=ROOT/'references/examples'

def run(*args, ok=True):
    p=subprocess.run([sys.executable,str(CLI),*map(str,args)],capture_output=True,text=True)
    if ok:
        if p.returncode:raise AssertionError(p.stderr)
        return json.loads(p.stdout)
    return p

class TestCLI(unittest.TestCase):
    def test_verify(self):self.assertTrue(run('verify')['ok'])
    def test_components(self):self.assertEqual(len(run('components')),114);self.assertTrue(any(x['component']=='Core.DataTable' for x in run('components','DataTable')))
    def test_pages(self):
        rows=run('pages');self.assertEqual(len(rows),116);self.assertEqual(len({x['route'] for x in rows}),116);self.assertTrue(any(x['route']=='pilot/admin/catalog' for x in rows));self.assertTrue(any(x['route']=='pilot/public/catalog' for x in rows));self.assertTrue(any(x['route']=='pilot/utility/f33register' for x in rows));self.assertFalse(any(x['route']=='pilot/public/f33register' for x in rows))
    def test_tokens(self):self.assertEqual(run('tokens')['controlHeightPx']['compact'],30);self.assertEqual(run('tokens')['colors']['surface']['dark'],'#20232a')
    def test_keys(self):self.assertEqual(len(run('keys')),16);self.assertEqual(run('keys','forma.collection.adaptive')[0]['id'],'forma.collection.adaptive')
    def test_context(self):self.assertEqual(run('context','Core.DataTable')['mappingStatus'],'mapped');self.assertEqual(len(run('context','Core.Button')['mappings']),0)
    def test_locate(self):self.assertTrue(run('locate','dtPopup','--limit','2'));self.assertEqual(run('locate','definitely_not_a_real_forma_token_987654'),[])
    def test_inspect(self):
        d=run('inspect',EX/'example-inventory-1440.json','Core.Button@1vrx2c5');self.assertEqual(len(d['matches']),1);self.assertEqual(d['matches'][0]['label'],'Filter')
    def test_issue(self):
        d=run('issue',EX/'example-reference-1440.json','--problem','spacing','--expected','preserve touch area');self.assertEqual(d['reference']['label'],'Filter');self.assertTrue(d['sourceCandidates']['dtPopup']);self.assertTrue(d['context']['visualKeys'])
    def test_compare(self):
        p=EX/'example-inventory-1440.json';d=run('compare',p,p);self.assertTrue(d['sameViewport']);self.assertEqual(d['changed'],[]);self.assertEqual(d['onlyBefore'],[])
        d=run('compare',p,EX/'example-inventory-390.json');self.assertFalse(d['sameViewport']);self.assertTrue(d['changed'])
    def test_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{}');self.assertNotEqual(run('inspect',p,ok=False).returncode,0)
        self.assertNotEqual(run('capture','https://example.com','--out','/tmp/never-created-forma',ok=False).returncode,0)
if __name__=='__main__':unittest.main(verbosity=2)
