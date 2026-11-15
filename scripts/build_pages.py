"""Build the readable example pages from their checks and saved outputs. No model calls."""
import json
from .common import ROOT, load_dataset, read_outputs
from .check import passes


def cell(text):
    return str(text).replace('|', '\\|').replace('\n', ' ')


def main():
    images, checks = load_dataset()
    for case in checks['cases']:
        item = images[case['image_id']]
        folder = (ROOT / item['file']).parent
        names = sorted(p.stem for p in (folder / 'outputs').glob('*.md'))
        outputs = {name: read_outputs(name, {item['id']: item})[item['id']] for name in names}
        lines = [f"# {item['id']} · {item['title']}", '', '[← All examples](../../README.md)', '',
                 f"![{item['title']}]({(ROOT / item['file']).name})", '',
                 '## What are we checking?', '', item['visual_notes'], '',
                 'These are the visible facts we want an OCR output to recover. Each row is one check. These answers were selected by inspecting the photograph; they are not model-generated reference transcripts.', '',
                 '| Check | Expected content | Where to look |' + ''.join(f' {name} |' for name in names),
                 '| --- | --- | --- |' + ' --- |' * len(names)]
        for c in case['checks']:
            expected = ' **and** '.join(g[0] for g in c['all_of'])
            lines.append('| ' + ' | '.join(cell(v) for v in [c['question'], expected, c['evidence']]) + ' |' +
                         ''.join(f" {'Pass' if passes(text, c) else 'Miss'} |" for text in outputs.values()))
        lines += ['', 'The table shows the expected facts, not required formatting. **And** means both pieces must be present. Case, accents, ordinary punctuation and line breaks do not matter; values and labels must still be correct.', '',
                  'The exact rules and accepted alternative spellings are in [checks.json](checks.json). Each `all_of` group must match; any alternative inside that group is accepted.', '',
                  'These few checks measure recovery of selected facts. They do not check every word or catch every invented sentence.', '',
                  '## Actual OCR outputs', '']
        if not outputs:
            lines += ['**Not run yet.** This example has a photograph and content checks, but no saved parser output or judge result. Expected answers above are not measured results.', '']
        else:
            for name, text in outputs.items():
                count = sum(passes(text, c) for c in case['checks'])
                settings_path = folder / 'outputs' / f'{name}-settings.json'
                metadata = json.loads(settings_path.read_text()) if settings_path.exists() else {}
                lines += [f"### {name}: {count}/{len(case['checks'])} checks passed", '',
                          f'[Open the unedited output](outputs/{name}.md)' + (f' · [Run settings](outputs/{name}-settings.json)' if settings_path.exists() else ''), '']
                if metadata.get('model_reported'):
                    lines += [f"Requested `{metadata['model_requested']}`; the API reported `{metadata['model_reported']}`.", '']
                if name == 'datalab':
                    lines += ['Datalab Convert, accurate mode. The request enabled exact transcription and disabled image captions and extraction. The returned text still contains scene descriptions; it is preserved as received. No custom reading prompt was sent.', '']
                fence = '`' * max(4, max((len(s) for s in text.split() if s and set(s) == {'`'}), default=0) + 1)
                lines += ['<details>', '<summary>Read the full output here</summary>', '', fence + 'text', text, fence, '', '</details>', '']
        summary_path = folder / 'comparison/summary.json'
        if summary_path.exists():
            run = json.loads((folder / 'comparison/run.json').read_text())
            lines += ['## What did the image-based judge say?', '',
                      f"The judge saw the photograph and the two outputs, labeled A and B. Parser names were hidden. We reversed their order and asked again. Candidate: **{run['candidate']}**; baseline: **{run['baseline']}**.", '',
                      '| Order | A | B | Judge chose |', '| --- | --- | --- | --- |']
            records = [json.loads(p.read_text()) for p in sorted((folder/'comparison').glob('[0-9]*.json'))]
            for n, record in enumerate(records, 1):
                labels = {record['candidate_label']: run['candidate'], 'B' if record['candidate_label'] == 'A' else 'A': run['baseline']}
                v = record.get('judgment', {}).get('verdict', 'error')
                lines.append(f"| {n} | {labels['A']} | {labels['B']} | {labels.get(v, v)} |")
            lines += ['', 'The explanations below are the judge’s claims. Compare them with the photograph yourself.', '']
            for n, record in enumerate(records, 1):
                j = record.get('judgment', {})
                lines += [f"**Order {n}:** {j.get('rationale', record.get('error', 'No verdict'))}", '']
                lines += ['- ' + cell(e) for e in j.get('evidence', [])] + ['']
            versions = sorted({str(r.get('model_reported')) for r in records})
            lines += [f"Judge API reported: {', '.join(versions)}. Gemini also produced one of the parses, so this is a worked example, not an independent ranking of vendors.", '',
                      '[Judge instructions](../../prompts/compare-outputs.txt) · [Recorded requests and responses](comparison/)', '']
        notes = folder / 'NOTES.md'
        if notes.exists():
            lines += ['## What to notice', '', notes.read_text().strip(), '']
        lines += ['## About this photograph', '', item['notes'], '',
                  ('Source: My nephew 💀' if not item['source_page'] else f"Source: [{item['attribution']}]({item['source_page']})"), '',
                  '[How to run an example](../../scripts/README.md)', '']
        (folder / 'README.md').write_text('\n'.join(lines))
    print(f'Updated {len(images)} readable example pages; no API calls.')


if __name__ == '__main__':
    main()
