"""Small examples of what the benchmark checks do and do not establish."""
import json
import unittest

from scripts.check import passes_check
from scripts.common import load_dataset
from scripts.extract import matches_schema, score_image


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.parse = load_dataset('parse')
        self.extract = load_dataset('extract')

    def check(self, image_id, check_id):
        return next(c for c in self.parse[image_id]['checks'] if c['id'] == check_id)

    def test_payment_requires_payment_wording(self):
        check = self.check('06', 3)
        self.assertTrue(passes_check('You may **pay 3 life**.', check))
        self.assertFalse(passes_check('You may pay three life.', check))
        self.assertFalse(passes_check('They refuse 3 life.', check))

    def test_parse_requires_printed_words_instead_of_expansions(self):
        for image_id, check_id, visible, expanded in [
            ('01', 4, 'more than 60', 'over sixty'),
            ('05', 2, 'HP 270', 'hit points 270'),
            ('05', 5, "can't use more than 1 GX attack", 'cannot use more than one GX attack'),
            ('05', 6, '3 Prize cards', 'three Prize cards'),
            ('06', 1, 'Meathook Massacre II', 'Meathook Massacre 2'),
            ('08', 3, 'W36 L34', 'waist 36 inseam 34'),
            ('08', 4, 'LEVI STRAUSS & CO. S.F. CAL.', 'Levi Strauss & Co San Francisco California'),
            ('10', 2, 'TRUCTION\nBOOKLET', 'Instruction Booklet'),
        ]:
            with self.subTest(image_id=image_id, check_id=check_id):
                check = self.check(image_id, check_id)
                self.assertTrue(passes_check(visible, check))
                self.assertFalse(passes_check(expanded, check))

    def test_extract_preserves_fragments_and_abbreviations(self):
        for image_id, field, visible, completed in [
            ('04', 'title', 'RS FROM A STOIC', 'Letters from a Stoic'),
            ('04', 'author', 'Seneca', 'Lucius Annaeus Seneca'),
            ('07', 'front_card_title', 'Elesh Norn, Mothe ... Machines', 'Elesh Norn, Mother of Machines'),
            ('06', 'title', 'Meathook Massacre II', 'Meathook Massacre 2'),
            ('08', 'button_location_abbreviation', 'SF CAL', 'San Francisco California'),
            ('10', 'cartridge_title', None, 'Pokémon Black Version 2'),
        ]:
            with self.subTest(image_id=image_id, field=field):
                self.assertEqual(self.score_field(image_id, field, visible), (True, True))
                self.assertEqual(self.score_field(image_id, field, completed), (True, False))
        # Boundary letters are partly clipped; the missing words are not optional.
        self.assertEqual(self.score_field('07', 'front_card_title',
                         'lesh Norn, Mothe … achines'), (True, True))
        for wrong in ['Elesh Norn, Mother … Machines', 'Elesh Norn, Mothe of Machines',
                      'Elesh Norn', None]:
            self.assertFalse(self.score_field('07', 'front_card_title', wrong)[1])

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
        output['author_surname'] = 'Shaw'
        result = score_image(json.dumps(output), self.extract['11'])
        self.assertTrue(result['schema_valid'])
        self.assertFalse(next(c for c in result['checks'] if c['field'] == 'author_surname')['pass'])

    def score_field(self, image_id, field, value):
        data = self.extract[image_id]
        output = {c['field']: c['expected'] for c in data['checks']}
        output[field] = value
        result = score_image(json.dumps(output), data)
        check = next(c for c in result['checks'] if c['field'] == field)
        return result['schema_valid'], check['pass']

    def test_subtypes_allow_reordering_but_not_omissions_or_duplicates(self):
        self.assertEqual(self.score_field('07', 'creature_subtypes',
                         ['Phyrexian Chimera', 'Phyrexian Praetor']), (True, True))
        for wrong in [[], ['Phyrexian Chimera'], ['Phyrexian Chimera', 'Phyrexian Chimera'],
                      ['Phyrexian Chimera', 'Phyrexian Praetor', 'Human']]:
            with self.subTest(wrong=wrong):
                self.assertEqual(self.score_field('07', 'creature_subtypes', wrong), (True, False))

    def test_flavor_attribution_is_not_an_artist_credit(self):
        self.assertEqual(self.score_field('07', 'artist_credits', ['Johan Grenier']), (True, True))
        self.assertEqual(self.score_field('07', 'artist_credits', ['Johan Grenier', 'Nokar']), (True, False))

    def test_numbered_attack_damage_excludes_prose_and_conditional_totals(self):
        output = {'hp': 270, 'attack_1_printed_damage': None,
                  'attack_2_printed_damage': 160, 'attack_3_printed_damage': None,
                  'attack_2_damage_against_damaged_active': 240}
        result = score_image(json.dumps(output), self.extract['05'])
        self.assertTrue(result['schema_valid'])
        self.assertEqual(result['score'], 1)
        # Rules-prose damage, a shifted attack, and calculated damage all fail.
        for field, wrong in [('attack_1_printed_damage', 40),
                             ('attack_1_printed_damage', 160),
                             ('attack_2_printed_damage', 240),
                             ('attack_3_printed_damage', 0)]:
            with self.subTest(field=field, wrong=wrong):
                self.assertEqual(self.score_field('05', field, wrong), (True, False))
        for malformed in ['160', '160+', True]:
            with self.subTest(malformed=malformed):
                self.assertEqual(self.score_field('05', 'attack_2_printed_damage', malformed),
                                 (False, False))
        # Omitting a null field is not equivalent to explicitly returning null.
        del output['attack_3_printed_damage']
        result = score_image(json.dumps(output), self.extract['05'])
        self.assertFalse(result['schema_valid'])
        self.assertFalse(next(c for c in result['checks']
                              if c['field'] == 'attack_3_printed_damage')['pass'])

    def test_inferences_require_the_bound_and_conditional_bonus(self):
        for image_id, field, correct, wrong_values in [
            ('01', 'minimum_catalogue_titles', 61, [60, 62, None, '61', True]),
            ('05', 'attack_2_damage_against_damaged_active', 240, [160, 80, None, '240', True]),
        ]:
            self.assertEqual(self.score_field(image_id, field, correct), (True, True))
            for wrong in wrong_values:
                with self.subTest(field=field, wrong=wrong):
                    self.assertFalse(self.score_field(image_id, field, wrong)[1])
        spec = self.extract['05']['schema']['properties']['attack_2_damage_against_damaged_active']
        for clue in ['Calamitous', '160', '80', '240']:
            self.assertNotIn(clue, spec['description'])

    def test_life_payments_are_distinct_and_typed(self):
        self.assertEqual(self.score_field('06', 'life_payments', [3]), (True, True))
        self.assertEqual(self.score_field('06', 'life_payments', [3, 3]), (True, False))
        for malformed in [['3'], [True], 3, None]:
            with self.subTest(malformed=malformed):
                self.assertEqual(self.score_field('06', 'life_payments', malformed), (False, False))

    def test_advertised_work_requires_correct_author(self):
        self.assertEqual(self.score_field('04', 'advertised_works',
                         [{'title': 'Meditations', 'author': 'Marcus Aurelius'}]), (True, True))
        self.assertEqual(self.score_field('04', 'advertised_works',
                         [{'title': 'Meditations', 'author': 'Seneca'}]), (True, False))

    def test_banknote_list_excludes_partial_serials(self):
        self.assertEqual(self.score_field('09', 'serial_numbers', ['A16281158A']), (True, True))
        self.assertEqual(self.score_field('09', 'serial_numbers',
                         ['A16281158A', 'L133']), (True, False))

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
                                self.assertTrue(matches_schema(value, spec))
                    if track == 'extract':
                        fields = [c['field'] for c in checks]
                        self.assertEqual(len(fields), len(set(fields)))
                        self.assertEqual(set(fields), set(data['schema']['properties']))
                        self.assertEqual(set(fields), set(data['schema']['required']))


if __name__ == '__main__':
    unittest.main()
