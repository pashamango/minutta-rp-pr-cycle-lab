#!/usr/bin/env bash
set -euo pipefail
repo='pashamango/minutta-rp-pr-cycle-lab'
out="${1:?output directory required}"
mkdir -p "$out/raw" "$out/jsonl" "$out/ledger"
gh api --paginate --slurp "repos/$repo/issues?state=all&per_page=100" > "$out/raw/issues-pages.json"
jq -c '.[] | .[]' "$out/raw/issues-pages.json" > "$out/jsonl/issues-index.jsonl"
jq -c 'select(.pull_request == null)' "$out/jsonl/issues-index.jsonl" > "$out/jsonl/issues.jsonl"
jq -c 'select(.pull_request != null)' "$out/jsonl/issues-index.jsonl" > "$out/jsonl/pr-index.jsonl"
while IFS= read -r n; do
  gh api "repos/$repo/issues/$n/comments?per_page=100" > "$out/raw/issue-$n-comments.json"
done < <(jq -r 'select((.comments // 0) > 0 and .pull_request == null) | .number' "$out/jsonl/issues-index.jsonl")
while IFS= read -r n; do gh api "repos/$repo/pulls/$n" > "$out/raw/pr-$n.json"; done < <(jq -r '.number' "$out/jsonl/pr-index.jsonl")
python3 - "$out" <<'PY'
import json, pathlib, sys, hashlib, datetime
out=pathlib.Path(sys.argv[1])
for srcname,dstname,prefix in [('issues.jsonl','issues-full.jsonl','issue'),('pr-index.jsonl','prs-full.jsonl','pr')]:
    with (out/'jsonl'/srcname).open() as f, (out/'jsonl'/dstname).open('w') as w:
        for line in f:
            obj=json.loads(line); n=obj['number']; detail=out/'raw'/f'{prefix}-{n}.json'
            if detail.exists(): obj=json.loads(detail.read_text())
            c=out/'raw'/f'issue-{n}-comments.json'
            if c.exists(): obj['comments']=json.loads(c.read_text())
            w.write(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',',':'))+'\n')
pages=json.loads((out/'raw/issues-pages.json').read_text())
(out/'ledger/pages.json').write_text(json.dumps([{'pass':'extract','page':i,'per_page':100,'items':len(p),'status':'captured'} for i,p in enumerate(pages,1)],indent=2)+'\n')
summary={'repo':'pashamango/minutta-rp-pr-cycle-lab','issues':sum(1 for _ in open(out/'jsonl/issues-full.jsonl')),'prs':sum(1 for _ in open(out/'jsonl/prs-full.jsonl')),'pages':len(pages),'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(out/'ledger/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
manifest=[]
for p in sorted(out.rglob('*')):
    if p.is_file() and p.name!='SHA256SUMS': manifest.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}')
(out/'SHA256SUMS').write_text('\n'.join(manifest)+'\n')
PY
