import json
import tempfile
import unittest
from pathlib import Path

from bench.common import ROOT, event_mean, load_dataset, read_outputs
from bench.unit import passes, score
from bench.pair import candidate_points, decode_response, plan, summarize, validate_verdict


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images, cls.checks = load_dataset()
        cls.by_id = {c['image_id']: c['checks'] for c in cls.checks['cases']}

    def test_reviewable_size_and_unique_check_ids(self):
        self.assertEqual(sum(len(c['checks']) for c in self.checks['cases']), 26)
        for checks in self.by_id.values():
            self.assertLessEqual(len(checks), 3)
            self.assertEqual(len(checks), len({c['id'] for c in checks}))
            for c in checks:
                self.assertTrue(c['evidence'])
                self.assertTrue(c['question'])

    def test_format_changes_do_not_change_content(self):
        title = self.by_id['06'][0]
        for text in ('MEATHOOK MASSACRE II', '**Meathook**\nMassacre 2',
                     '<p>Meathook <b>Massacre</b> II</p>', '[Meathook Massacre II](https://example.org)',
                     'Meathook Mas-\nsacre II'):
            with self.subTest(text=text):
                self.assertTrue(passes(text, title))
        for text in ('Seneca', 'SENECA', 'Se<b>ne</b>ca', '**Seneca**'):
            self.assertTrue(passes(text, self.by_id['04'][0]))
        self.assertTrue(passes('Pokémon BLACK 2 VERSION', self.by_id['10'][0]))

    def test_wrong_values_and_swapped_associations_fail(self):
        hp = self.by_id['05'][1]
        for text in ('HP 270', '| HP | 270 |', '<dt>HP</dt><dd>270</dd>'):
            self.assertTrue(passes(text, hp))
        for text in ('HP 2700', 'HP 27.0', 'HP -270', 'HP 270.5', 'HP 260; attack damage 270'):
            self.assertFalse(passes(text, hp))
        size = self.by_id['08'][2]
        self.assertTrue(passes('L34; W36', size))
        self.assertTrue(passes('Waist: 36 / inseam: 34', size))
        self.assertFalse(passes('Waist: 34 / inseam: 36', size))
        self.assertFalse(passes('36, 34', size))
        self.assertTrue(passes('| Waist | Length |\n| --- | --- |\n| 36 | 34 |', size))
        self.assertTrue(passes('<table><tr><th>Length</th><th>Waist</th></tr><tr><td>34</td><td>36</td></tr></table>', size))
        self.assertFalse(passes('| Waist | Length |\n| --- | --- |\n| 34 | 36 |', size))

    def test_hidden_metadata_and_substrings_do_not_supply_answers(self):
        author = self.by_id['04'][0]
        for text in ('Senecal', '<img alt="Seneca">', '<!-- Seneca -->', '<script>Seneca</script>',
                     '[book](https://example.org/Seneca)', '![Seneca](cover.jpg)'):
            self.assertFalse(passes(text, author))

    def test_missing_files_are_errors_but_blank_parses_are_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                read_outputs(tmp, ['01'])
            (Path(tmp)/'01.md').write_text('')
            self.assertEqual(read_outputs(tmp, ['01']), {'01': ''})
            (Path(tmp)/'01.txt').write_text('duplicate')
            with self.assertRaises(ValueError):
                read_outputs(tmp, ['01'])

    def test_empty_outputs_score_zero_and_alias_fixture_scores_one(self):
        outputs = {i: '' for i in self.images}
        self.assertEqual(score(outputs, self.images, self.checks)['score'], 0)
        for case in self.checks['cases']:
            outputs[case['image_id']] = '\n'.join(g[0] for c in case['checks'] for g in c['all_of'])
        self.assertEqual(score(outputs, self.images, self.checks)['score'], 1)
        outputs.pop('01')
        with self.assertRaises(ValueError):
            score(outputs, self.images, self.checks)

    def test_same_event_views_share_one_weight(self):
        images = {'01': {'event_group': 'same'}, '02': {'event_group': 'same'},
                  '03': {'event_group': 'other'}}
        self.assertAlmostEqual(event_mean({'01': 1, '02': 1, '03': 0}, images), 0.5)

    def test_pair_plan_balances_order_and_is_reproducible(self):
        jobs = plan(self.images, 2, 7)
        self.assertEqual(jobs, plan(self.images, 2, 7))
        self.assertEqual(len(jobs), 40)
        for i in self.images:
            for r in (0, 1):
                self.assertEqual(sorted(j['candidate_label'] for j in jobs if j['image_id'] == i and j['round'] == r), ['A', 'B'])
        with self.assertRaises(ValueError):
            plan(self.images, 0, 7)

    def test_pair_labels_map_back_to_the_candidate(self):
        self.assertEqual(candidate_points('A', 'A'), 1)
        self.assertEqual(candidate_points('A', 'B'), 0)
        self.assertEqual(candidate_points('B', 'B'), 1)
        self.assertEqual(candidate_points('tie', 'A'), 0.5)
        self.assertIsNone(candidate_points('unjudgeable', 'A'))
        with self.assertRaises(ValueError):
            candidate_points('C', 'A')

    def test_incomplete_judgments_never_become_ties_or_change_denominator(self):
        jobs = [{**j, 'points': 1.0} for j in plan(self.images, 1, 0)]
        self.assertEqual(summarize(jobs, self.images)['score'], 1)
        jobs[0]['points'] = None
        result = summarize(jobs, self.images)
        self.assertIsNone(result['score'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['valid_judgments'], 19)

    def test_malformed_and_truncated_judge_responses_are_rejected(self):
        good = {'verdict': 'tie', 'evidence': ['Both give the visible W36 L34.'], 'rationale': 'Equivalent content.'}
        raw = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': json.dumps(good)}]}}]}
        self.assertEqual(decode_response(raw), good)
        raw['candidates'][0]['finishReason'] = 'MAX_TOKENS'
        with self.assertRaises(ValueError):
            decode_response(raw)
        with self.assertRaises(ValueError):
            validate_verdict({'verdict': 'A', 'rationale': 'Better', 'evidence': []})


if __name__ == '__main__':
    unittest.main()
