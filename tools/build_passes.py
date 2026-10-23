import json, pathlib, re, sys
root=pathlib.Path(sys.argv[1]); out=root/'passes'; out.mkdir(exist_ok=True)
rows=[]
for name,kind in [('issues-full.jsonl','issue'),('prs-full.jsonl','pr')]:
    for line in (root/'jsonl'/name).read_text().splitlines():
        x=json.loads(line); text=' '.join(str(x.get(k,'')) for k in ('title','body','html_url')).lower()
        if re.search(r'infinite books|infinite book|самопишущ|wasm|gaza|остров крым|narrative|text gen',text): route='INFINITE-BOOKS'
        elif re.search(r'feistel|bip39|bip450',text): route='FEISTEL-BIP39-BIP450'
        else: route='FORGEJO-DRAFT'
        claim='implementation' if re.search(r'implement|add|fix|build|create|implement',text) else ('research' if re.search(r'research|hypothes|claim|proof|theorem|experiment',text) else 'observation')
        falsifiable='yes' if route!='FORGEJO-DRAFT' or claim!='observation' else 'needs-review'
        rows.append({'source':kind,'number':x['number'],'title':x.get('title'),'url':x.get('html_url'),'route':route,'claim_type':claim,'falsifiable':falsifiable,'body':x.get('body'),'labels':[l.get('name') for l in x.get('labels',[]) if isinstance(l,dict)]})
for route in ('INFINITE-BOOKS','FEISTEL-BIP39-BIP450','FORGEJO-DRAFT'):
    with (out/f'{route.lower()}.jsonl').open('w') as f:
        for x in rows:
            if x['route']==route: f.write(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n')
(out/'type-ledger.json').write_text(json.dumps({'status':'provisional','records':len(rows),'rule':'keyword routing plus claim-type/falsifiability heuristic; human/registry review required'},indent=2)+'\n')
(out/'dedup-ledger.json').write_text(json.dumps({'status':'blocked','reason':'MIN/PRD and PR-168 triage-pass1.jsonl were not present in the isolated workspace; no dedup claim is made','records_pending_dedup':len(rows)},indent=2)+'\n')
(out/'route-ledger.json').write_text(json.dumps({'status':'provisional','routes':{r:sum(x['route']==r for x in rows) for r in ('INFINITE-BOOKS','FEISTEL-BIP39-BIP450','FORGEJO-DRAFT')}},indent=2)+'\n')
