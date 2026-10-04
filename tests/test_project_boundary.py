"""Prevent copied harness configuration and private provenance crossing projects."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import common
import bootstrap_env
import configure_clients
import session_state


class ProjectBoundaryTests(unittest.TestCase):
    def test_current_root_and_auto_are_allowed_but_foreign_root_is_not_inspected(self):
        with tempfile.TemporaryDirectory() as raw:
            current = Path(raw) / 'current-project'
            current.mkdir()
            current = current.resolve()
            foreign = current.parent / 'other-project'
            for value in ['auto', '.', '', str(current)]:
                self.assertEqual(common.project_root({'PROJECT_ROOT': value}, harness_root=current), current)
            original = Path.resolve
            def resolve(path, *args, **kwargs):
                if path == foreign:
                    raise AssertionError('foreign path inspected')
                return original(path, *args, **kwargs)
            with mock.patch.object(Path, 'resolve', resolve), self.assertRaises(RuntimeError):
                common.project_root({'PROJECT_ROOT': str(foreign)}, harness_root=current)

    def test_bootstrap_rejects_copied_root_before_setup(self):
        with mock.patch.object(bootstrap_env, 'parse_env', return_value={'PROJECT_ROOT': '../other-project'}), mock.patch.object(bootstrap_env, 'sync_missing') as setup:
            with self.assertRaises(RuntimeError):
                bootstrap_env.main()
            setup.assert_not_called()

    def test_disabled_mcp_does_not_bypass_configuration_boundary(self):
        with tempfile.TemporaryDirectory() as raw:
            generated = Path(raw) / 'generated'
            env = {'PROJECT_ROOT': '../other-project', 'PROJECT_CONTEXT_MCP_ENABLED': 'false'}
            with mock.patch.object(configure_clients, 'parse_env', return_value=env), mock.patch.object(configure_clients, 'GEN', generated), mock.patch.object(configure_clients, 'write_secrets') as write:
                with self.assertRaises(RuntimeError):
                    configure_clients.main()
                write.assert_not_called()
                self.assertFalse(generated.exists())

    def test_template_has_no_personal_workspace_paths(self):
        # Generic pattern: never put the private identifier into the regression itself.
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        pattern = re.compile(r'/home/[^/\s`]+/workspace/')
        for relative in paths:
            path = ROOT / relative
            if not relative or not path.is_file() or path.name == 'ARTIFACT_MANIFEST.sha256':
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            self.assertIsNone(pattern.search(text), relative)

    def test_forget_protects_current_and_unfinished_state(self):
        with mock.patch.object(session_state, 'current_session_id', return_value='CURRENT-TASK'):
            with self.assertRaises(session_state.StateError):
                session_state.forget('CURRENT-TASK')
            with mock.patch.object(session_state, 'read', return_value={'task': {'status': 'executing'}}), self.assertRaises(session_state.StateError):
                session_state.forget('OLDER-TASK')


if __name__ == '__main__':
    unittest.main()
