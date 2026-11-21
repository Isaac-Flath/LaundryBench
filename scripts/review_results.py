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
    'parse': {'Custom · Tesseract': 'tesseract', 'Custom · LightOn': 'lighton'},
    'extract': {'Custom · Tesseract → Luna/Jev': 'tesseract-luna-jev',
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
  .result-details { margin: 0 0 10px; }
  .result-details .output-label { margin: 8px 0 4px; }
  .result-details pre { background: #f8fafc; border: 1px solid #dce1e6; border-radius: 5px; padding: 8px 10px; margin: 0; max-height: 240px; overflow: auto; }
  .note-box { margin-top: 12px; padding-top: 10px; border-top: 1px dashed #dce1e6; }
  .note-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
  .note-header label { font-size: 12px; font-weight: 600; color: #526271; }
  .note-btn { font-size: 12px; padding: 3px 9px; }
  .note-btn.recording { background: #fee2e2; border-color: #dc2626; color: #991b1b; }
  .note-status { font-size: 12px; color: #697582; margin-left: auto; }
  .note-status.error { color: #991b1b; }
  .note-input { width: 100%; font: 13px/1.5 system-ui, sans-serif; color: #202a35; background: #fbfcfd; border: 1px solid #ccd2d8; border-radius: 6px; padding: 8px 10px; resize: vertical; }
  .note-input:focus { outline: none; border-color: #3177b9; background: #fff; }
  .summary-actions { display: flex; align-items: center; gap: 8px; margin-top: 6px; flex-wrap: wrap; }
  #results-summary { padding: 8px 16px; border-bottom: 1px solid #dce1e6; max-height: 30vh; overflow: auto; }
  #results-summary details + details { margin-top: 4px; }
  @media (max-width: 760px) {
    .pane[aria-label="Checks and JSON"] { display: block; overflow-y: auto; }
    #results-summary { max-height: none; }
    #checks-pane { overflow: visible; }
  }
'''

JAVASCRIPT = r'''
  let notes = {}, activeRecorder = null;
  const notesReady = fetch('notes.json', {cache: 'no-store'})
    .then(response => response.ok ? response.json() : {})
    .then(data => { notes = data || {}; })
    .catch(() => { notes = {}; });

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
              actual: row?.actual, missing: row?.missing, output: saved?.output,
              schemaValid: saved?.schema_valid};
    });
  }
  function comparisonBadges(check, schema) {
    const block = element('div'), badges = element('div', undefined, 'results');
    const results = comparisons(check, schema);
    for (const result of results) {
      const state = result.pass === null ? 'unknown' : result.pass ? 'pass' : 'fail';
      const text = result.pass === null ? result.reason : result.pass ? 'Pass' : 'Fail';
      badges.append(element('span', `${result.label}: ${text}`, `badge ${state}`));
    }
    block.append(badges);
    const failures = results.filter(result => result.pass === false);
    if (failures.length) {
      const details = element('details', undefined, 'result-details');
      details.append(element('summary', `Failed ${failures.length === 1 ? 'output' : 'outputs'} (${failures.length})`));
      for (const result of failures) {
        const value = schema
          ? (result.missing ? '(missing field)' : JSON.stringify(result.actual, null, 2))
          : (result.output?.trim() ? result.output : '(empty output)');
        details.append(element('p', result.label, 'muted output-label'), element('pre', value));
      }
      block.append(details);
    } else if (schema) {
      const details = element('details', undefined, 'result-details');
      details.append(element('summary', 'Predicted values'));
      for (const result of results) {
        const value = result.pass === null ? result.reason
          : result.missing ? '(missing field)' : JSON.stringify(result.actual, null, 2);
        details.append(element('p', result.label, 'muted output-label'), element('pre', value));
      }
      block.append(details);
    }
    return block;
  }
  function checkLabel(check, schema) {
    if (schema) return check.field;
    const order = check.type === 'order';
    const groups = order ? check.sequence : check.contains_all;
    return groups.map(group => group.any_of[0]).join(order ? ' → ' : ' + ');
  }
  function updateNotesBadge() {
    const badge = $('notes-count');
    if (badge) badge.textContent = `Notes: ${Object.keys(notes).length} saved`;
  }
  async function persistNote(key, meta, text, statusEl) {
    const trimmed = text.trim();
    const note = trimmed ? {...meta, text, updated_at: new Date().toISOString()} : null;
    if (note) notes[key] = note; else delete notes[key];
    updateNotesBadge();
    statusEl.textContent = 'Saving…';
    statusEl.classList.remove('error');
    try {
      const response = await fetch('notes.json', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({key, note}),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      statusEl.textContent = trimmed ? 'Saved' : '';
    } catch (error) {
      statusEl.textContent = `Save failed (${error.message})`;
      statusEl.classList.add('error');
    }
  }
  function buildNoteEditor(key, meta, heading, placeholder) {
    const box = element('div', undefined, 'note-box');
    const header = element('div', undefined, 'note-header');
    const inputId = `note-${key.replace(/[^a-z0-9_-]/gi, '-')}`;
    const label = element('label', heading);
    label.htmlFor = inputId;
    const recordBtn = element('button', 'Record', 'note-btn');
    recordBtn.type = 'button';
    const status = element('span', notes[key]?.text ? 'Saved' : '', 'note-status');
    const area = element('textarea', undefined, 'note-input');
    area.id = inputId;
    area.rows = 2;
    area.placeholder = placeholder;
    area.value = notes[key]?.text || '';
    let timer = null;
    const saveNow = () => {
      if (timer) { clearTimeout(timer); timer = null; }
      persistNote(key, meta, area.value, status);
    };
    area.oninput = () => {
      status.textContent = 'Unsaved…';
      status.classList.remove('error');
      if (timer) clearTimeout(timer);
      timer = setTimeout(saveNow, 500);
    };
    area.onblur = () => { if (timer) saveNow(); };
    recordBtn.onclick = async () => {
      if (activeRecorder && activeRecorder.button === recordBtn) {
        activeRecorder.stop();
        return;
      }
      if (activeRecorder) activeRecorder.stop();
      if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
        status.textContent = 'Mic unavailable here — dictate into the box or open in Chrome/Safari';
        status.classList.add('error');
        return;
      }
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({audio: true});
      } catch (error) {
        status.textContent = `Mic blocked (${error.name}) — dictate into the box or open in Chrome/Safari`;
        status.classList.add('error');
        return;
      }
      const chunks = [];
      const mimeType = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4']
        .find(type => MediaRecorder.isTypeSupported(type));
      const recorder = mimeType ? new MediaRecorder(stream, {mimeType}) : new MediaRecorder(stream);
      recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        if (activeRecorder?.recorder === recorder) activeRecorder = null;
        recordBtn.textContent = 'Record';
        recordBtn.classList.remove('recording');
        recordBtn.disabled = true;
        status.textContent = 'Transcribing…';
        status.classList.remove('error');
        try {
          const blob = new Blob(chunks, {type: recorder.mimeType || 'audio/webm'});
          const response = await fetch('transcribe', {
            method: 'POST',
            headers: {'Content-Type': blob.type || 'application/octet-stream'},
            body: blob,
          });
          const data = await response.json();
          if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
          const transcript = (data.text || '').trim();
          if (transcript) {
            area.value = area.value.trim() ? `${area.value.trim()}\n${transcript}` : transcript;
            await persistNote(key, meta, area.value, status);
          } else {
            status.textContent = 'No speech detected';
          }
        } catch (error) {
          status.textContent = `Transcription failed: ${error.message}`;
          status.classList.add('error');
        } finally {
          recordBtn.disabled = false;
        }
      };
      activeRecorder = {button: recordBtn, recorder, stop: () => recorder.state !== 'inactive' && recorder.stop()};
      recorder.start();
      recordBtn.textContent = 'Stop & transcribe';
      recordBtn.classList.add('recording');
      status.textContent = 'Recording…';
      status.classList.remove('error');
    };
    header.append(label, recordBtn, status);
    box.append(header, area);
    return box;
  }
  function checkNotesBox(check, schema) {
    const track = $('track').value, item = images[Number(picker.value)];
    const key = `${track}:${item.id}:${check.id}`;
    const meta = {image_id: item.id, image_title: item.title, track, check_id: check.id, label: checkLabel(check, schema)};
    return buildNoteEditor(key, meta, 'Your thoughts', 'Record or type your thoughts on this check…');
  }
  function formatNotesMarkdown() {
    const entries = Object.entries(notes).sort(([a], [b]) => a.localeCompare(b));
    if (!entries.length) return 'No saved notes yet.';
    return entries.map(([, note]) => {
      const heading = note.track === 'doc'
        ? `## ${note.image_id} · ${note.image_title} (document)`
        : `## ${note.image_id} · ${note.image_title} — ${note.track} #${note.check_id} (${note.label})`;
      return `${heading}\n\n${note.text.trim()}`;
    }).join('\n\n---\n\n');
  }
  function renderComparisonSummary(checks, schema) {
    const track = $('track').value, item = images[Number(picker.value)], id = item.id;
    const summary = $('results-summary'), badges = element('div', undefined, 'results');
    summary.replaceChildren();
    const results = checks.map(check => comparisons(check, schema));
    Object.entries(snapshot.results[track]).forEach(([label, documents], index) => {
      const known = results.map(row => row[index]).filter(row => row.pass !== null);
      const passed = known.filter(row => row.pass).length;
      badges.append(element('span', `${label}: ${passed}/${known.length} pass${known.length < checks.length ? ` · ${checks.length - known.length} unavailable` : ''}`, 'badge unknown'));
    });
    const notesBadge = element('span', `Notes: ${Object.keys(notes).length} saved`, 'badge unknown');
    notesBadge.id = 'notes-count';
    badges.append(notesBadge);
    const actions = element('div', undefined, 'summary-actions');
    actions.append(element('span', `Saved comparison · ${new Date(snapshot.created_at).toLocaleString()} · Counts for displayed checks.`, 'muted'));
    const copyBtn = element('button', 'Copy all notes', 'note-btn');
    copyBtn.type = 'button';
    copyBtn.onclick = async () => {
      try {
        await navigator.clipboard.writeText(formatNotesMarkdown());
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy all notes'; }, 1500);
      } catch {
        copyBtn.textContent = 'Saved in review-notes.json';
      }
    };
    actions.append(copyBtn);
    summary.append(badges, actions);
    const docDetails = element('details');
    const docKey = `doc:${id}`;
    docDetails.append(element('summary', notes[docKey]?.text ? 'Document notes (has note)' : 'Document notes'));
    docDetails.append(buildNoteEditor(docKey, {image_id: id, image_title: item.title, track: 'doc', check_id: null, label: item.title},
      `Overall thoughts on ${id} · ${item.title}`, 'Record or type overall thoughts on this document…'));
    summary.append(docDetails);
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
    anchor = "    body.append(element('p', `${schema ? 'Human reference' : 'Find it'}: ${check.human_reference}`, 'location'));"
    html = replace_once(html, anchor, anchor + '\n    body.append(checkNotesBox(check, schema));')
    anchor = '    const checks = matchingChecks(item);'
    html = replace_once(html, anchor, '    await notesReady;\n' + anchor + '\n    renderComparisonSummary(checks, schema);')
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
