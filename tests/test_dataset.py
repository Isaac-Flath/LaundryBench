"""Small examples of what the benchmark checks do and do not establish."""
import json
import unittest

from scripts.check import passes_check
from scripts.common import load_dataset
from scripts.extract import has_allowed_type, score_image


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.parse = load_dataset('parse')
        self.extract = load_dataset('extract')

    def check(self, image_id, check_id):
        return next(c for c in self.parse[image_id]['checks'] if c['id'] == check_id)

    def test_payment_requires_payment_wording(self):
        check = self.check('06', 3)
        self.assertTrue(passes_check('You may **pay 3 life**.', check))
        self.assertTrue(passes_check('You may pay three life.', check))
        self.assertFalse(passes_check('They refuse 3 life.', check))

    def test_banknote_requires_the_visible_phrase(self):
        check = self.check('09', 2)
        self.assertTrue(passes_check('FOR ALL\nDEBTS, PUBLIC AND PRIVATE', check))
        self.assertFalse(passes_check('one unreadable fragment', check))
        self.assertFalse(passes_check('ONE', check))

    def test_text_presence_does_not_score_author_association(self):
        check = self.check('04', 4)
        # Both snippets are present, even though this associates the wrong author.
        self.assertTrue(passes_check('Meditations by Seneca. Other book: Marcus Aurelius.', check))
        self.assertFalse(passes_check('Meditations by Seneca.', check))

    def test_order_requires_both_anchors_in_order(self):
        check = self.check('06', 4)
        self.assertTrue(passes_check('You may pay 3 life. If you do, return that card.', check))
        self.assertFalse(passes_check('If you do, you may pay 3 life.', check))
        self.assertFalse(passes_check('You may pay 3 life.', check))

    def test_book_schema_is_reused_without_document_hints(self):
        self.assertEqual(self.extract['02']['schema'], self.extract['11']['schema'])
        self.assertEqual(set(self.extract['11']['schema']['properties']),
                         {'title', 'subtitle', 'author_surname'})

    def test_reviewer_is_not_the_author(self):
        output = {'title': 'The DaVinci Curse', 'subtitle': None, 'author_surname': None}
        result = score_image(json.dumps(output), self.extract['11'])
        self.assertTrue(result['schema_valid'])
        self.assertEqual(result['score'], 1)
        output['author_surname'] = 'Sher'
        result = score_image(json.dumps(output), self.extract['11'])
        self.assertTrue(result['schema_valid'])
        self.assertFalse(next(c for c in result['checks'] if c['field'] == 'author_surname')['pass'])

    def test_dataset_contract(self):
        tags = {'document_specific', 'rotated_text', 'small_text', 'curved_text',
                'damaged_or_occluded_text', 'low_contrast', 'multiple_objects'}
        self.assertEqual(set(self.parse), set(self.extract))
        for track, dataset in [('parse', self.parse), ('extract', self.extract)]:
            for image_id, data in dataset.items():
                with self.subTest(track=track, image_id=image_id):
                    checks = data['checks']
                    self.assertTrue(checks)
                    self.assertEqual(len({c['id'] for c in checks}), len(checks))
                    for check in checks:
                        self.assertEqual(len(check['tags']), len(set(check['tags'])))
                        self.assertLessEqual(set(check['tags']), tags)
                        if track == 'parse':
                            self.assertNotIn('document_specific', check['tags'])
                            groups = check['sequence'] if check.get('type') == 'order' else check['contains_all']
                            self.assertTrue(groups)
                            for group in groups:
                                self.assertTrue(group['any_of'])
                                self.assertTrue(all(isinstance(s, str) and s.strip() for s in group['any_of']))
                        else:
                            self.assertIn(check['basis'], {'visible', 'inferred', 'unavailable'})
                            self.assertEqual(check['expected'] is None, check['basis'] == 'unavailable')
                            spec = data['schema']['properties'][check['field']]
                            for value in [check['expected'], *check.get('alternatives', [])]:
                                self.assertTrue(has_allowed_type(value, spec['type']))
                    if track == 'extract':
                        fields = [c['field'] for c in checks]
                        self.assertEqual(len(fields), len(set(fields)))
                        self.assertEqual(set(fields), set(data['schema']['properties']))
                        self.assertEqual(set(fields), set(data['schema']['required']))


if __name__ == '__main__':
    unittest.main()
