import importlib.util, pathlib, unittest, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('hs', ROOT / 'scripts/hermes_host_setup.py')
hs = importlib.util.module_from_spec(spec); spec.loader.exec_module(hs)

class HostSetupTests(unittest.TestCase):
    def test_parent_chain(self):
        p = list(hs.parent_chain(pathlib.Path('/home/alice/projects/repo')))
        self.assertEqual(p, [pathlib.Path('/home/alice'), pathlib.Path('/home/alice/projects')])

    def test_no_workspace_symlink_created(self):
        text = (ROOT / 'scripts/hermes_host_setup.py').read_text()
        self.assertNotIn('ln", "-s', text)
        self.assertNotIn('sudo("ln", "-s"', text)
