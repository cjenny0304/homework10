#!/usr/bin/env python3
"""Build the offline slides from the reviewed content and wiki bibliography."""
from html import escape
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
pages = json.loads((HERE / 'content.json').read_text())
sources = {item['id']: item for item in json.loads((ROOT / 'sources.json').read_text())}
topic_names = {
    'speech': '語音', 'body-language': '肢體語言', 'emotions': '情感',
    'myths': '迷思', 'daily-habits': '日常習性',
}
art_alt = {'cover': '橘色虎斑貓原創插圖', 'blink': '眼睛半閉的橘色貓咪示意圖'}

def image(art, alt):
    assert (HERE / 'assets' / f'{art}.webp').is_file()
    return f'<img src="assets/{art}.webp" alt="{escape(alt)}" width="720" height="540">'

def bibliography(page):
    refs = page['refs']
    rows = []
    for sid, topics in refs.items():
        source = sources[sid]
        topics = [topics] if isinstance(topics, str) else topics
        for topic in topics:
            assert f'**{sid}**' in (ROOT / 'wiki/topics' / f'{topic}.md').read_text()
        wiki = ' · '.join(f'<a href="../wiki/topics/{topic}.md">Wiki {topic_names[topic]}</a>' for topic in topics)
        assert (ROOT / 'raw' / f'{sid}.md').is_file()
        credits = '｜'.join(escape(source[key]) for key in ('title', 'creators', 'dates', 'access'))
        rows.append(f'<li><strong>{sid}</strong> {credits}<span class="source-links">{wiki} · '
                    f'<a href="../raw/{sid}.md">來源卡</a> · <a href="{escape(source["url"])}">原始連結</a></span></li>')
    return f'<details class="sources"><summary>來源｜{" · ".join(refs)}</summary><ul>{"".join(rows)}</ul></details>'

def interaction(page):
    if 'guess' in page:
        choices = []
        for i, (asset, alt, feedback) in enumerate(page['guess']):
            choices.append(f'<button type="button" aria-pressed="false" data-feedback="{escape(feedback)}">'
                           f'{image(asset, alt)}<span>圖 {"AB"[i]}</span></button>')
        return f'<div class="guess">{"".join(choices)}</div><p class="feedback" role="status"></p>'
    if 'flips' in page:
        cards = []
        for i, (question, answer, ids) in enumerate(page['flips'], 1):
            cards.append(f'<button type="button" class="tile flip" aria-expanded="false" aria-controls="flip-{i}">'
                         f'<strong>{escape(question)}</strong><span class="flip-label">翻開解答</span>'
                         f'<span class="back" id="flip-{i}" hidden>{escape(answer)} · {ids}</span></button>')
        return f'<div class="flip-grid">{"".join(cards)}</div>'
    if 'quiz' in page:
        questions = []
        for i, (prompt, options, correct, explanation) in enumerate(page['quiz'], 1):
            buttons = []
            for j, option in enumerate(options):
                buttons.append(f'<button type="button" class="answer" aria-pressed="false" data-correct="{str(j == correct).lower()}">'
                               f'{escape(option)}</button>')
            questions.append(f'<section class="tile question" aria-labelledby="question-{i}" data-explanation="{escape(explanation)}">'
                             f'<h2 id="question-{i}">{i}. {escape(prompt)}</h2><div class="options">{"".join(buttons)}</div>'
                             '<p class="feedback" role="status"></p></section>')
        return (f'<div class="quiz">{"".join(questions)}</div><div class="quiz-end">'
                '<button type="button" class="reset" id="reset">重新作答</button>'
                '<span class="score" id="score" role="status"></span></div>')
    return ''

def slide(page, number):
    art = page.get('art')
    layout = 'slide-layout with-art' if art else 'slide-layout'
    hidden = ' hidden' if number != 1 else ''
    parts = [f'<article class="slide" aria-labelledby="title-{number}"{hidden}><div class="{layout}"><div class="copy">',
             f'<span class="tag">{escape(page["tag"])}</span>',
             f'<h1 tabindex="-1" id="title-{number}">{escape(page["title"])}</h1>',
             f'<p class="lead">{escape(page["lead"])}</p>']
    if 'body' in page:
        parts.append(f'<p class="body">{escape(page["body"])}</p>')
    if 'cards' in page:
        cards = [f'<div class="tile"><strong>{escape(title)}</strong><p>{escape(body)}</p></div>'
                 for title, body in page['cards']]
        parts.append(f'<div class="cards">{"".join(cards)}</div>')
    parts.append(interaction(page))
    if 'note' in page:
        parts.append(f'<p class="note">{escape(page["note"])}</p>')
    parts.append('</div>')
    if art:
        parts.append(f'<figure class="art">{image(art, art_alt[art])}</figure>')
    parts.extend(['</div>', bibliography(page), '</article>'])
    return '\n'.join(parts)

assert 10 <= len(pages) <= 12
assert {sid for page in pages for sid in page['refs']} == set(sources)
for asset in ('slides.css','slides.js'):
    assert (HERE / asset).is_file()
markup = '\n'.join(slide(page, number) for number, page in enumerate(pages, 1))
(HERE / 'slides.html').write_text(f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>貓咪真的聽得懂人類說話嗎？｜Cat Language Wiki</title>
<link rel="stylesheet" href="slides.css">
<script src="slides.js" defer></script>
</head>
<body>
<div class="shell">
<header class="masthead">
  <div class="brand"><span class="mark"><img src="assets/cover.webp" alt="" width="29" height="29"></span>Cat Language Wiki</div>
  <div class="position"><span id="position" aria-live="polite">01 / {len(pages)}</span>
    <progress class="progress" id="progress" aria-label="簡報進度" value="1" max="{len(pages)}"></progress></div>
</header>
<noscript><p>請啟用 JavaScript 以使用導覽與互動。</p></noscript>
<main class="stage" aria-label="教學簡報">
{markup}
</main>
<nav class="controls" aria-label="簡報導覽">
  <button type="button" id="previous" disabled>← 上一頁</button>
  <span class="control-hint">可用鍵盤 ← → 切換頁面</span>
  <button type="button" id="next">下一頁 →</button>
</nav>
</div>
</body>
</html>
""", encoding='utf-8')
print(f'PASS: built {len(pages)} slides from {len(sources)} Wiki sources')
