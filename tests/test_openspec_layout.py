"""Regression proof for accepted-state coverage and dated OpenSpec identities."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openspec_layout import dated_name, validate_layout


class OpenSpecLayoutTests(unittest.TestCase):
    def fixture(self, root):
        spec = root / 'specs/2026-09-07-session-handoff/spec.md'
        spec.parent.mkdir(parents=True)
        spec.write_text('# Spec\n', encoding='utf-8')
        (root / 'changes/add-state-view').mkdir(parents=True)
        (root / 'changes/archive/2026-10-03-add-state-view').mkdir(parents=True)
        (root / 'CURRENT.md').write_text('[Handoff](specs/2026-09-07-session-handoff/spec.md)\n', encoding='utf-8')

    def test_valid_dated_inventory_and_change_names(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.fixture(root)
            self.assertEqual(validate_layout(root), [])

    def test_calendar_and_name_rules(self):
        for invalid in ['2026-02-30-state', 'state', '2026-10-03-State',
                        '2026-10-03-session_handoff', '2026-10-03-2026-09-07-state']:
            with self.subTest(invalid=invalid):
                self.assertFalse(dated_name(invalid))
        self.assertTrue(dated_name('2024-02-29-state'))

    def test_missing_duplicate_and_stale_inventory_entries(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.fixture(root)
            for text, expected in [('', 'missing spec'),
                ('[A](specs/2026-09-07-session-handoff/spec.md)\n' * 2, 'duplicate spec'),
                ('[A](specs/2026-09-07-retired/spec.md)', 'stale spec'),
                ('[A](changes/add-state-view/specs/state/spec.md)', 'must not link')]:
                with self.subTest(expected=expected):
                    (root / 'CURRENT.md').write_text(text, encoding='utf-8')
                    self.assertTrue(any(expected in error for error in validate_layout(root)))
            (root / 'CURRENT.md').unlink()
            self.assertTrue(any('Missing central' in error for error in validate_layout(root)))

    def test_invalid_spec_active_and_archive_names(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.fixture(root)
            (root / 'specs/loose.md').write_text('Loose', encoding='utf-8')
            (root / 'specs/undated').mkdir()
            (root / 'changes/2026-10-03-add-state').mkdir()
            (root / 'changes/archive/2026-02-30-add-state').mkdir()
            errors = validate_layout(root)
            for name in ['loose.md', 'undated', '2026-10-03-add-state', '2026-02-30-add-state']:
                self.assertTrue(any(name in error for error in errors), errors)


if __name__ == '__main__':
    unittest.main()
