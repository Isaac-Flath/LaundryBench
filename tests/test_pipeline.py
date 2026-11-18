"""Extraction must start with OCR, even in a clean output directory."""
from contextlib import ExitStack
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts import luna_jev


class PipelineTests(unittest.TestCase):
    def test_both_backends_run_ocr_before_extraction_and_resume(self):
        for backend in ('lighton', 'tesseract'):
            with self.subTest(backend=backend), tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
                root = Path(tmp).resolve()
                image = root / '01-example' / 'image.jpg'
                image.parent.mkdir()
                image.write_bytes(b'image')
                (image.parent / 'extract_schema.json').write_text(json.dumps({
                    'type': 'object', 'properties': {'title': {'description': 'Title'}},
                }))
                output = root / 'output'
                events = []

                def run(command, **kwargs):
                    if '--output-dir' in command:
                        self.assertEqual(Path(command[1]).parent.name, backend)
                        self.assertIn('--image', command)
                        self.assertEqual(command[command.index('--image') + 1], '01')
                        ocr = Path(command[command.index('--output-dir') + 1])
                        self.assertEqual(ocr, output / 'ocr')
                        ocr.mkdir(parents=True, exist_ok=True)
                        (ocr / '01.md').write_text('Fresh OCR')
                        events.append('ocr')
                    else:
                        self.assertEqual(json.loads((output / '01.json').read_text()), {'title': 'Fresh OCR'})
                        events.append('score')

                def extract(client, lines, schema, raw, image_id):
                    self.assertEqual(lines, {'L1': 'Fresh OCR'})
                    self.assertEqual(events[-1], 'ocr')
                    events.append('extract')
                    return {'values': {'title': 'Fresh OCR'}, 'citations': {'title': []}}

                stack.enter_context(patch.dict(sys.modules, {
                    'dotenv': SimpleNamespace(load_dotenv=Mock()),
                    'openai': SimpleNamespace(OpenAI=Mock()),
                }))
                stack.enter_context(patch.dict('os.environ', {'OPENAI_API_KEY': 'test', 'TYPESAFE_API_KEY': 'test'}))
                stack.enter_context(patch.object(luna_jev, 'select_images', return_value=[image]))
                runner = stack.enter_context(patch.object(luna_jev.subprocess, 'run', side_effect=run))
                extractor = stack.enter_context(patch.object(luna_jev, 'extract_values', side_effect=extract))
                stack.enter_context(patch.object(luna_jev, 'verify_values'))
                args = ['run.py', '--image', '01', '--output-dir', str(output)]
                with patch.object(sys, 'argv', args):
                    luna_jev.main(root, backend)
                    luna_jev.main(root, backend)
                self.assertEqual(events, ['ocr', 'extract', 'score'] * 2)
                self.assertEqual(extractor.call_count, 2)

                with patch.object(sys, 'argv', args + ['--resume']):
                    luna_jev.main(root, backend)
                self.assertEqual(events[-2:], ['ocr', 'score'])
                self.assertEqual(extractor.call_count, 2)
                self.assertIn('--resume', runner.call_args_list[-2].args[0])

                runner.side_effect = subprocess.CalledProcessError(1, 'ocr')
                with patch.object(sys, 'argv', args), self.assertRaises(subprocess.CalledProcessError):
                    luna_jev.main(root, backend)
                self.assertEqual(extractor.call_count, 2)


if __name__ == '__main__':
    unittest.main()
