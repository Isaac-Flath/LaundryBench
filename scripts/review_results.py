"""Build the ignored comparison snapshot without changing the dataset viewer.

Run: python3 -m scripts.review_results
Then serve with python3 -m scripts.review and open /review-results.html.
This only reads saved predictions; it never calls a model.
"""
from datetime import datetime, timezone
import json

from .common import ROOT, list_images, load_dataset
from .check import passes_check
from .extract import score_image
from .solution import prediction_status, metadata_path

SOLUTIONS = {
    'parse': {'Reducto': 'reducto', 'Datalab': 'datalab',
              'Custom · Tesseract': 'tesseract', 'Custom · LightOn': 'lighton'},
    'extract': {'Reducto': 'reducto', 'Datalab': 'datalab',
                'Custom · Tesseract → Luna/Jev': 'tesseract-luna-jev',
                'Custom · LightOn → Luna/Jev': 'luna-jev'},
}


def build_snapshot():
    snapshot = {'created_at': datetime.now(timezone.utc).isoformat(), 'results': {}, 'schemas': {}}
    images = {p.parent.name.split('-', 1)[0]: p for p in list_images()}
    for track, solutions in SOLUTIONS.items():
        dataset = load_dataset(track)
        snapshot['results'][track] = {}
        for label, folder in solutions.items():
            rows = snapshot['results'][track][label] = {}
            for image_id, data in dataset.items():
                schema = data.get('schema')
                if schema:
                    snapshot['schemas'][image_id] = schema
                suffix = 'md' if track == 'parse' else 'json'
                prediction = ROOT / 'solutions' / track / folder / 'output' / f'{image_id}.{suffix}'
                status = prediction_status(prediction, images[image_id], schema)
                row = rows[image_id] = {'status': status}
                if status != 'current':
                    continue
                text = prediction.read_text()
                row['output'] = text
                row['created_at'] = json.loads(metadata_path(prediction).read_text())['created_at']
                if track == 'parse':
                    row['checks'] = [{'test': c, 'pass': passes_check(text, c)} for c in data['checks']]
                else:
                    report = score_image(text, data)
                    row['schema_valid'] = report['schema_valid']
                    row['checks'] = [{'test': c, 'pass': scored['pass'], 'actual': scored['actual'],
                                      'missing': scored['missing']}
                                     for c, scored in zip(data['checks'], report['checks'])]
    return snapshot


STYLES = '''
  .results { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 10px; }
  .badge { border-radius: 4px; padding: 3px 7px; font-size: 12px; }
  .pass { background: #dcfce7; color: #166534; }
  .fail { background: #fee2e2; color: #991b1b; }
  .unknown { background: #e5e7eb; color: #374151; }
  #results-summary { padding: 8px 16px; border-bottom: 1px solid #dce1e6; max-height: 25vh; overflow: auto; }
  #results-summary details + details { margin-top: 4px; }
  @media (max-width: 760px) {
    .pane[aria-label="Checks and JSON"] { display: block; overflow-y: auto; }
    #results-summary { max-height: none; }
    #checks-pane { overflow: visible; }
  }
'''

JAVASCRIPT = '''
  function canonical(value) {
    if (Array.isArray(value)) return value.map(canonical);
    if (value && typeof value === 'object') return Object.fromEntries(
      Object.keys(value).sort().map(key => [key, canonical(value[key])]));
    return value;
  }
  function same(a, b) { return JSON.stringify(canonical(a)) === JSON.stringify(canonical(b)); }
  function comparisons(check, schema) {
    const track = $('track').value, id = images[Number(picker.value)].id;
    return Object.entries(snapshot.results[track]).map(([label, documents]) => {
      const saved = documents[id];
      let reason = saved?.status || 'not run';
      if (schema && !same(schema, snapshot.schemas[id])) reason = 'schema changed; regenerate and rerun';
      const row = saved?.checks?.find(row => row.test.id === check.id);
      if (reason === 'current' && (!row || !same(row.test, check))) reason = 'check changed; regenerate snapshot';
      return {label, pass: reason === 'current' ? row.pass : null, reason,
              actual: row?.actual, missing: row?.missing, schemaValid: saved?.schema_valid};
    });
  }
  function comparisonBadges(check, schema) {
    const block = element('div'), badges = element('div', undefined, 'results');
    for (const result of comparisons(check, schema)) {
      const state = result.pass === null ? 'unknown' : result.pass ? 'pass' : 'fail';
      const text = result.pass === null ? result.reason : result.pass ? 'Pass' : 'Fail';
      badges.append(element('span', `${result.label}: ${text}`, `badge ${state}`));
    }
    block.append(badges);
    if (schema) {
      const details = element('details');
      details.append(element('summary', 'Predicted values'));
      for (const result of comparisons(check, schema)) {
        const value = result.pass === null ? result.reason
          : result.missing ? '(missing field)' : JSON.stringify(result.actual, null, 2);
        details.append(element('p', result.label, 'muted'), element('pre', value));
      }
      block.append(details);
    }
    return block;
  }
  function renderComparisonSummary(checks, schema) {
    const track = $('track').value, id = images[Number(picker.value)].id;
    const summary = $('results-summary'), badges = element('div', undefined, 'results');
    summary.replaceChildren();
    const results = checks.map(check => comparisons(check, schema));
    Object.entries(snapshot.results[track]).forEach(([label, documents], index) => {
      const known = results.map(row => row[index]).filter(row => row.pass !== null);
      const passed = known.filter(row => row.pass).length;
      badges.append(element('span', `${label}: ${passed}/${known.length} pass${known.length < checks.length ? ` · ${checks.length - known.length} unavailable` : ''}`, 'badge unknown'));
    });
    summary.append(badges, element('div', `Saved comparison · ${new Date(snapshot.created_at).toLocaleString()} · Counts for displayed checks.`, 'muted'));
    for (const [label, documents] of Object.entries(snapshot.results[track])) {
      const saved = documents[id], details = element('details');
      details.append(element('summary', `${label} — saved output`));
      if (saved?.created_at) details.append(element('p', `Run: ${new Date(saved.created_at).toLocaleString()}`, 'muted'));
      if (schema && saved?.schema_valid !== undefined) details.append(element('p', `Schema valid at snapshot: ${saved.schema_valid ? 'yes' : 'no'}`, 'muted'));
      details.append(element('pre', saved?.output ?? saved?.status ?? 'not run'));
      summary.append(details);
    }
  }
'''


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'Dataset viewer changed; update comparison template anchor: {old[:70]}')
    return source.replace(old, new, 1)


def build_html(snapshot):
    # Reuse current document navigation and category controls in a separate copy.
    html = (ROOT / 'review.html').read_text()
    html = replace_once(html, '<title>LaundryBench · Review</title>', '<title>LaundryBench · Saved results</title>')
    html = replace_once(html, '<strong>LaundryBench</strong>', '<strong>LaundryBench · Results</strong>')
    html = replace_once(html, '</style>', STYLES + '</style>')
    html = replace_once(html, '    <div id="checks-pane">', '    <div id="results-summary" aria-live="polite"></div>\n    <div id="checks-pane">')
    # Escape HTML script terminators in provider text; render outputs with textContent.
    data = json.dumps(snapshot, ensure_ascii=False).replace('<', '\\u003c')
    html = replace_once(html, '<script>', '<script>\n  const snapshot = ' + data + ';\n' + JAVASCRIPT)
    anchor = "    const card = element('article'), body = element('div', undefined, 'check-body');"
    html = replace_once(html, anchor, anchor + '\n    body.append(comparisonBadges(check, schema));')
    anchor = '    const checks = matchingChecks(item);'
    html = replace_once(html, anchor, anchor + '\n    renderComparisonSummary(checks, schema);')
    return html


def main():
    snapshot = build_snapshot()
    path = ROOT / 'review-results.html'
    path.write_text(build_html(snapshot))
    for track, solutions in snapshot['results'].items():
        for label, documents in solutions.items():
            current = sum(row['status'] == 'current' for row in documents.values())
            print(f'{track} / {label}: {current}/{len(documents)} current documents')
    print('Open http://127.0.0.1:8765/review-results.html after starting python3 -m scripts.review')


if __name__ == '__main__':
    main()
