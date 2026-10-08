import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).parents[1]; KIT=ROOT/'project-office'
sys.path.insert(0,str(KIT)); from validate import validate
def load(): return json.loads((KIT/'fixtures/vimana-pilot.json').read_text())
def test_shadow_fixture_valid(): assert validate(load()) == []
def test_execution_requires_all_authorities():
    s=load(); s['execution_requested']=True; s['synthesis']=None; s['ic_decision']=None; s['founder_charter']=None
    assert 'RP -> EXECUTION invalid without synthesis + IC decision + founder charter' in validate(s)
def test_conflict_and_provenance_survive():
    s=load(); assert len(s['research'])==2 and s['research'][0]['provenance'] != s['research'][1]['provenance']; assert 'disagreement' in s['synthesis']
def test_founder_cannot_activate_without_ic():
    s=load(); s['status']='FOUNDER_CHARTER'; s['ic_decision']=None; assert 'IC decision required' in validate(s)
