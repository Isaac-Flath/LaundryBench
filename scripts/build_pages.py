"""Rebuild the image/check READMEs from checks.json. Never reads model runs."""
from .common import ROOT, load_dataset


def main():
    images, checks = load_dataset()
    for case in checks['cases']:
        item = images[case['image_id']]
        path = ROOT / item['file']
        lines = [f"# {item['id']} · {item['title']}", '',
                 f"![{item['title']}]({path.name})", '',
                 '| Check | Expected content | Location |', '| --- | --- | --- |']
        for check in case['checks']:
            answer = ' **and** '.join(group[0] for group in check['all_of'])
            lines.append(f"| {check['question']} | {answer} | {check['evidence']} |")
        lines += ['', '[Exact checks and accepted alternatives](checks.json) · [Run the benchmark](../../README.md#run)', '']
        (path.parent / 'README.md').write_text('\n'.join(lines))
    print(f'Updated {len(images)} image/check pages.')


if __name__ == '__main__':
    main()
