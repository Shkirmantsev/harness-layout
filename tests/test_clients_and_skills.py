import pathlib, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]

class ClientTests(unittest.TestCase):
    def test_generator_preserves_client_specific_hermes_transports(self):
        text = (ROOT / 'scripts/configure_clients.py').read_text()
        self.assertIn('HERMES_REMOTE_SIDECAR_PORT', text)
        self.assertIn('tool_dir / "hermes.js"', text)
        self.assertIn('opencode-hermes-runtime.json', text)
        self.assertNotIn('providers["hermes-remote"]', text)
        self.assertNotIn('mode: all', text)
        self.assertIn('Codex receives only optional', text)
        self.assertNotIn('HERMES_CONTROL_MCP_PORT', text)
        self.assertNotIn('hermes-bind', text)
        self.assertNotIn('PROJECT_BRIDGE_TOKEN', text)
        self.assertIn('scripts/skill_router.py --profile local-small', text)

    def test_shared_skills_have_native_contract(self):
        text = '\n'.join(p.read_text() for p in (ROOT / '.agents/skills').rglob('SKILL.md'))
        self.assertIn("OpenCode delegates through project-local `hermes_*` custom tools", text)
        self.assertIn('Claude Code delegates through the dedicated remote Hermes MCP sidecar', text)
        self.assertNotIn('make hermes-bind', text)
        self.assertNotIn('image_paths', text)
        self.assertNotIn('workspace symlink', text.lower())
