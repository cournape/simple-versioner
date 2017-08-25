import contextlib
import importlib.util
import mock
import os
import os.path
import shutil
import tempfile
import unittest

from simple_versioner import write_version_py


def import_from_path(path, module_name="<dummy>"):
    # Works on 3.5 and above only
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def cd(d):
    # Obviously non-threadsafe
    old_cwd = os.getcwd()

    try:
        os.chdir(d)
        yield
    finally:
        os.chdir(old_cwd)


class TestVersioner(unittest.TestCase):
    def setUp(self):
        self.prefix = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.prefix)

    def test_simple(self):
        # Given
        package_name = "yolo"
        version = "1.0.0"

        filename = os.path.join(self.prefix, "_version.py")
        os.makedirs(os.path.join(self.prefix, ".git"))

        # When
        with cd(self.prefix):
            with mock.patch("simple_versioner.git_version", return_value=("abcd", 0)):
                write_version_py(package_name, version, filename=filename)

        # Then
        m = import_from_path(filename)

        self.assertIs(m.is_released, False)
        self.assertEqual(m.version_info, (1, 0, 0, "dev", 0))
        self.assertEqual(m.git_revision, "abcd")
