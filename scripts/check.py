"""A transparent partial-content recall score; this does not detect all hallucinations."""
import argparse
import html
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from statistics import mean

from .common import load_dataset, save_json


class HTMLTextReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text_parts = []
        self.hidden_tag_depth = 0
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
            self.hidden_tag_depth += 1
        if tag in ('td', 'th', 'tr', 'table'):
            self.text_parts.append(' ␞ ')
        elif tag not in ('b', 'strong', 'em', 'i', 'span', 'u'):
            self.text_parts.append(' ')

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
        if tag in ('script', 'style') and self.hidden_tag_depth:
            self.hidden_tag_depth -= 1
        if tag in ('td', 'th', 'tr', 'table'):
            self.text_parts.append(' ␞ ')
        elif tag not in ('b', 'strong', 'em', 'i', 'span', 'u'):
            self.text_parts.append(' ')

    def handle_data(self, data):
        if not self.hidden_tag_depth:
            self.text_parts.append(data)
            if self.cell is not None:
                self.cell.append(data)


def read_table_labels_and_values(tables):
    """Build searchable phrases such as 'HP 270' from table headers and cells."""
    # Recover column labels for rectangular tables, independent of their rendering.
    facts = []
    for rows in tables:
        if len(rows) >= 2 and rows[0] and all(len(row) == len(rows[0]) for row in rows):
            for row in rows[1:]:
                facts.extend(f'{label} {value}' for label, value in zip(rows[0], row))
        facts.extend(' '.join(row) for row in rows if len(row) == 2)
    return ' ␞ '.join(facts)


def read_markdown_tables(text):
    tables, rows = [], []
    for line in text.splitlines() + ['']:
        if '|' in line:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            # Skip Markdown header separators: ---, :---, ---:, or :---:.
            if all(re.fullmatch(r':?-{3,}:?', c) for c in cells):
                continue
            rows.append(cells)
        else:
            if rows:
                tables.append(rows)
            rows = []
    return tables


def read_visible_text(text, include_table_labels=True):
    """Read Markdown/HTML text, keeping table boundaries and optional label/value phrases."""
    # Remove Markdown images: ![alt text](url) is not visible page text.
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)
    # Keep a link's label: [text](url) -> text.
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    # Remove reference definitions, such as a line containing [ref]: https://...
    text = re.sub(r'^\s*\[[^\]]+\]:\s*\S+.*$', '', text, flags=re.M)
    # Keep reference-link labels: [text][ref] -> text.
    text = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', text)
    # Strip repeated formatting markers, such as **, __, ~~, and ```.
    text = re.sub(r'([*_`~])\1+', '', text)
    markdown_tables = read_markdown_tables(text)
    # Mark cell boundaries so a phrase cannot accidentally match across cells.
    lines = []
    for line in text.splitlines():
        if '|' in line:
            line = ' ␞ '.join(line.strip().strip('|').split('|'))
        lines.append(line)
    parser = HTMLTextReader()
    parser.feed('\n'.join(lines))
    text = ''.join(parser.text_parts) + ' ␞ '
    if include_table_labels:
        text += read_table_labels_and_values(parser.tables + markdown_tables)
    return html.unescape(text).replace('\u00ad', '')


def prepare_text_for_matching(text, include_table_labels=True):
    """Return comparable words, numbers, and table boundaries, ignoring formatting."""
    text = read_visible_text(text, include_table_labels)
    # An ampersand is a connector, not optional punctuation.
    text = text.replace('&', ' and ')
    text = unicodedata.normalize('NFKD', text.casefold())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    # Join words split by a hyphen and line break: inter-\nnational -> international.
    text = re.sub(r'(?<=\w)[-‐‑]\s*\n\s*(?=\w)', '', text)
    return re.findall(r'''
        ␞                       # Table boundary.
        | [+-]?\d+(?:[.,]\d+)*  # Numbers with signs/decimals: -270, 27.0, 1,000.
        | [^\W\d_]+             # Unicode words; exclude digits and underscores.
    ''', text, re.VERBOSE)


def find_phrase_end(text_parts, alternatives, search_from=0):
    """Return the earliest end position of a matching phrase, or None."""
    match_ends = []
    for alternative in alternatives:
        phrase = [word for word in prepare_text_for_matching(alternative) if word != '␞']
        for start in range(search_from, len(text_parts) - len(phrase) + 1):
            if text_parts[start:start + len(phrase)] == phrase:
                match_ends.append(start + len(phrase))
                break
    return min(match_ends, default=None)


def passes_check(text, check):
    requires_order = check.get('type') == 'order'
    text_parts = prepare_text_for_matching(text, include_table_labels=not requires_order)
    if requires_order:
        text_parts = [part for part in text_parts if part != '␞']
    search_from = 0
    groups = check['sequence'] if requires_order else check['contains_all']
    for group in groups:
        phrase_end = find_phrase_end(text_parts, group['any_of'], search_from)
        if phrase_end is None:
            return False
        if requires_order:
            search_from = phrase_end
    return True


def score_outputs(outputs, dataset):
    image_results = []
    for image_id, image_tests in dataset.items():
        check_results = [
            {**check, 'pass': passes_check(outputs[image_id], check)}
            for check in image_tests['checks']
        ]
        image_results.append({
            'image_id': image_id,
            'score': mean(check['pass'] for check in check_results),
            'checks': check_results,
        })
    all_checks = [check for image_result in image_results for check in image_result['checks']]
    return {'metric': 'content_recovery',
            'images_evaluated': len(image_results),
            'score': mean(image_result['score'] for image_result in image_results),
            'passed': sum(check['pass'] for check in all_checks),
            'total': len(all_checks), 'images': image_results}


def read_ocr_outputs(directory, image_ids):
    directory = Path(directory)
    outputs = {}
    for image_id in image_ids:
        path, = [path for path in directory.glob(f'{image_id}.*')
                 if path.suffix in ('.md', '.txt', '.html')]
        outputs[image_id] = path.read_text(encoding='utf-8')
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outputs', help='Directory containing 01.md through 10.md (txt/html also accepted)')
    parser.add_argument('--image', help='One image ID, e.g. 01; omit to check all ten')
    parser.add_argument('--out', help='Optional JSON report path')
    args = parser.parse_args()
    dataset = load_dataset('parse', image_id=args.image)
    outputs = read_ocr_outputs(args.outputs, dataset)
    report = score_outputs(outputs, dataset)
    if args.out:
        save_json(args.out, report)
    for image_result in report['images']:
        for check in image_result['checks']:
            requires_order = check.get('type') == 'order'
            groups = check['sequence'] if requires_order else check['contains_all']
            alternatives = [group['any_of'] for group in groups]
            expected = (' → ' if requires_order else ' AND ').join(
                '(' + ' OR '.join(group) + ')' if len(group) > 1 else group[0]
                for group in alternatives)
            print(f"{image_result['image_id']} {'PASS' if check['pass'] else 'MISS'}: {expected}")
    print(f"Content recovery: {report['score']:.1%}; {report['passed']}/{report['total']} checks")


if __name__ == '__main__':
    main()
