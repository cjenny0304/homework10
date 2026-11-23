#!/usr/bin/env python3
"""Validate the delivered wiki against its local source catalog."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'speech': {'S01', 'S02', 'S03'},
    'body-language': {'S05', 'S06'},
    'emotions': {'S04', 'S05'},
    'myths': {'S01', 'S04', 'S05', 'S06'},
    'daily-habits': {'S06', 'S07'},
}
SECTIONS = ['一般讀者解釋', '來源支持的內容', '限制', '來源差異', '來源']
errors = []
counts = Counter()

def check(condition, message):
    if not condition:
        errors.append(message)

def read(path):
    if not path.is_file():
        errors.append(f'Missing file: {path.relative_to(ROOT)}')
        return ''
    return path.read_text(encoding='utf-8')

sources = json.loads(read(ROOT / 'sources.json'))
by_id = {source['id']: source for source in sources}
log = read(ROOT / 'wiki/log.md')
index = read(ROOT / 'wiki/index.md')
review = read(ROOT / 'logs/source_review.md')
check(len(sources) == len(by_id) and len(by_id) >= 5, 'Invalid source count or duplicate ID')
keys = [source['doi'] or source['url'] for source in sources]
check(len(set(keys)) == len(keys), 'Duplicate source publication')
for sid, source in by_id.items():
    check(bool(re.fullmatch(r'S[0-9]{2}', sid)), f'{sid}: invalid ID')
    card = read(ROOT / 'raw' / f'{sid}.md')
    for key in ('title', 'creators', 'dates', 'access', 'claim', 'limit', 'url', 'verified_url'):
        check(bool(source.get(key)) and source[key] in card, f'{sid}: missing card field {key}')
    for key in ('url', 'verified_url'):
        url = urlparse(source[key])
        check(url.scheme == 'https' and bool(url.netloc), f'{sid}: malformed {key}')
    check(f'[{sid}](../raw/{sid}.md) | SUCCESS | {source["access"]} |' in log,
          f'{sid}: missing successful batch result')
    check(f'[{sid}](../raw/{sid}.md)' in review, f'{sid}: missing verification record')
    if 'full_text' in source:
        path = ROOT / source['full_text']
        data = path.read_bytes() if path.is_file() else b''
        check(data.startswith(b'%PDF-') and sha256(data).hexdigest() == source['sha256'],
              f'{sid}: missing or changed PDF')
    for key in ('correction_url', 'author_manuscript_url'):
        if key in source:
            check(source[key] in card, f'{sid}: missing {key} link')

topics_dir = ROOT / 'wiki/topics'
check({path.stem for path in topics_dir.glob('*.md')} == EXPECTED.keys(), 'Topic set mismatch')
for slug, expected in EXPECTED.items():
    topic = read(topics_dir / f'{slug}.md')
    check(f'](topics/{slug}.md)' in index, f'{slug}: missing index entry')
    sections = re.split(r'^## (.+)$', topic, flags=re.M)
    headings = sections[1::2]
    check(headings == SECTIONS, f'{slug}: missing or unexpected section')
    claim_ids = set()
    for heading, body in zip(headings, sections[2::2]):
        body = body.strip()
        check(len(body) > 20, f'{slug}: empty {heading}')
        if heading != '來源':
            for line in filter(str.strip, body.splitlines()):
                ids = set(re.findall(r'\[(S\d{2})\]', line))
                check(bool(ids) and ids <= expected, f'{slug}: missing or invalid claim reference in {heading}')
                check(not re.search(r'\[S\d{2}\]\[S\d{2}\]', line),
                      f'{slug}: adjacent references render as one link in {heading}')
                if heading == '來源支持的內容':
                    claim_ids.update(ids)
    check(claim_ids == expected, f'{slug}: source support coverage mismatch')
    for sid in sorted(expected & by_id.keys()):
        source = by_id[sid]
        row = next((line for line in topic.splitlines() if line.startswith(f'- **{sid}**')), '')
        check(all(source[key] in row for key in ('title', 'creators', 'dates', 'access', 'url', 'verified_url')),
              f'{slug}: incomplete bibliography for {sid}')
        check(f'[{sid}]: ../../raw/{sid}.md' in topic, f'{slug}: missing reference target for {sid}')
        counts[sid] += 1
check(set(counts) == set(by_id), 'Not all ingested sources are covered')
for path in [ROOT / 'wiki/index.md', ROOT / 'wiki/log.md', *topics_dir.glob('*.md')]:
    for target in re.findall(r'\]\(([^)]+)\)', read(path)):
        if not urlparse(target).scheme:
            check((path.parent / target).is_file(), f'{path.name}: broken local link {target}')

if errors:
    for message in sorted(set(errors)):
        print(f'FAIL: {message}')
    raise SystemExit(1)

print(f'PASS: {len(by_id)} distinct sources with verified records, cards and successful batch entries')
print('PASS: PDF hashes, bibliography, source IDs and local Markdown links')
print(f'PASS: {len(EXPECTED)}/{len(EXPECTED)} topics and {len(counts)}/{len(by_id)} sources mapped to supported content')
print('Source appearances: ' + ', '.join(f'{sid}={count}' for sid, count in sorted(counts.items())))
