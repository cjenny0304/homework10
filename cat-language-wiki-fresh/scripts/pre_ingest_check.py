#!/usr/bin/env python3
"""僅檢查準備階段檔案；不代表 Wiki 已 ingest。"""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=json.loads((r/'sources.json').read_text(encoding='utf-8'))
ids=[x['id'] for x in s]
assert len(s)>=5, '來源不足五份'
assert len(ids)==len(set(ids)), '來源 ID 重複'
assert all(x['title'] and x['creators'] and x['url'].startswith('https://') for x in s)
assert all((r/'raw'/f'{x["id"]}.md').is_file() for x in s)
assert (r/'requirements.md').is_file() and (r/'AGENTS.md').is_file()
print(f'PASS: {len(s)} verified source records and {len(s)} source briefing files ready.')
print('NOTE: This is NOT an ingest test; wiki/log.md remains NOT_STARTED.')
