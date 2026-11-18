"""Saved results must not silently outlive the inputs that produced them."""
from pathlib import Path
import tempfile
import unittest

from scripts.review_results import build_html
from scripts.solution import record_prediction, prediction_status


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / 'image.jpg'
        self.image.write_bytes(b'original image')
        self.prediction = self.root / 'output' / '01.json'
        self.prediction.parent.mkdir()
        self.schema = {'type': 'object', 'properties': {'title': {'type': ['string', 'null']}}}
        self.settings = {'model': 'example'}

    def save(self):
        self.prediction.write_text('{"title": "Example"}')
        record_prediction(self.prediction, self.image, self.settings, self.schema)

    def status(self):
        return prediction_status(self.prediction, self.image, self.schema, self.settings)

    def test_missing_and_legacy_outputs_are_not_current(self):
        self.assertEqual(self.status(), 'not run')
        self.prediction.write_text('{}')
        self.assertEqual(self.status(), 'unverified input version')

    def test_new_schema_and_image_invalidate_prediction(self):
        self.save()
        self.assertEqual(self.status(), 'current')
        self.schema['properties']['subtitle'] = {'type': ['string', 'null']}
        self.assertNotEqual(self.status(), 'current')
        self.save()
        self.image.write_bytes(b'changed image')
        self.assertNotEqual(self.status(), 'current')

    def test_modified_output_or_settings_invalidate_prediction(self):
        self.save()
        self.prediction.write_text('{"title": "Corrected after seeing answers"}')
        self.assertNotEqual(self.status(), 'current')
        self.save()
        self.settings['model'] = 'different model'
        self.assertNotEqual(self.status(), 'current')

    def test_provider_output_cannot_close_the_script_element(self):
        html = build_html({'output': '</script><script>alert(1)</script>'})
        self.assertNotIn('</script><script>alert(1)', html)
        self.assertIn('\\u003c/script>', html)
        self.assertEqual(html.count('<script>'), 1)
        self.assertEqual(html.count('</script>'), 1)


if __name__ == '__main__':
    unittest.main()
