"""A transparent partial-content recall score; this does not detect all hallucinations."""
import argparse
import html
import re
import unicodedata
from html.parser import HTMLParser

from .common import ROOT, digest, event_mean, load_dataset, read_outputs, save_json


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0
        self.tables = []
        self.rows = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.rows = []
        elif tag == 'tr' and self.rows is not None:
            self.row = []
        elif tag in ('td', 'th') and self.row is not None:
            self.cell = []
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag in ('td', 'th', 'tr', 'table'):
            self.parts.append(' ␞ ')
        elif tag not in ('b', 'strong', 'em', 'i', 'span', 'u'):
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(''.join(self.cell))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif tag == 'table' and self.rows is not None:
            self.tables.append(self.rows)
            self.rows = None
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1
        if tag in ('td', 'th', 'tr', 'table'):
            self.parts.append(' ␞ ')
        elif tag not in ('b', 'strong', 'em', 'i', 'span', 'u'):
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)
            if self.cell is not None:
                self.cell.append(data)


def table_associations(tables):
    # Recover column labels for rectangular tables, independent of their rendering.
    facts = []
    for rows in tables:
        if len(rows) < 2 or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
            continue
        for row in rows[1:]:
            facts.extend(f'{label} {value}' for label, value in zip(rows[0], row))
    for rows in tables:
        facts.extend(' '.join(row) for row in rows if len(row) == 2)
    return ' ␞ '.join(facts)


def markdown_tables(text):
    tables, rows = [], []
    for line in text.splitlines() + ['']:
        if '|' in line:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{3,}:?', c) for c in cells):
                continue
            else:
                rows.append(cells)
        else:
            if rows:
                tables.append(rows)
            rows = []
    return tables


def tokens(text):
    # Link targets, image alt text and HTML attributes are not recovered page text.
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'^\s*\[[^\]]+\]:\s*\S+.*$', '', text, flags=re.M)
    text = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', text)
    text = re.sub(r'([*_`~])\1+', '', text)
    md_tables = markdown_tables(text)
    text = '\n'.join(' ␞ '.join(line.strip().strip('|').split('|')) if '|' in line else line for line in text.splitlines())
    parser = VisibleHTML()
    parser.feed(text)
    associations = table_associations(parser.tables + md_tables)
    text = html.unescape(''.join(parser.parts) + ' ␞ ' + associations).replace('\u00ad', '')
    text = unicodedata.normalize('NFKD', text.casefold())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'(?<=\w)[-‐‑]\s*\n\s*(?=\w)', '', text)
    # Keep decimals/signs; never make 27.0 or -270 equal to 270.
    return re.findall(r'␞|[+-]?\d+(?:[.,]\d+)*|[^\W\d_]+', text)


def contains(haystack, needle):
    return bool(needle) and any(haystack[i:i+len(needle)] == needle
                              for i in range(len(haystack) - len(needle) + 1))


def passes(text, check):
    actual = tokens(text)
    return all(any(contains(actual, [t for t in tokens(alias) if t != '␞']) for alias in aliases)
               for aliases in check['all_of'])


def score(outputs, images, checks):
    if set(outputs) != set(images):
        raise ValueError('Missing or extra image outputs; use an empty file for an empty parse')
    rows = []
    for case in checks['cases']:
        image_id = case['image_id']
        results = [{**c, 'pass': passes(outputs[image_id], c)} for c in case['checks']]
        rows.append({'image_id': image_id, 'score': sum(c['pass'] for c in results)/len(results),
                     'output_sha256': digest(outputs[image_id].encode()), 'checks': results})
    return {'metric': 'content_recovery', 'checks_version': checks['version'],
            'checks_sha256': digest((ROOT / 'bench/checks.json').read_bytes()),
            'score': event_mean({r['image_id']: r['score'] for r in rows}, images),
            'passed': sum(c['pass'] for r in rows for c in r['checks']),
            'total': sum(len(r['checks']) for r in rows), 'images': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outputs', help='Directory containing 01.md through 10.md (txt/html also accepted)')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    images, checks = load_dataset()
    result = score(read_outputs(args.outputs, images), images, checks)
    save_json(args.out, result)
    print(f"Content recovery: {result['score']:.1%}; {result['passed']}/{result['total']} checks")


if __name__ == '__main__':
    main()
