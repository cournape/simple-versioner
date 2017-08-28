# Copyright (c) 2017 by David Cournapeau
# This software is released under the MIT license. See LICENSE file for the
# actual license.
import contextlib
import importlib.util
import mock
import os
import os.path
import shutil
import tempfile
import textwrap
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

    def test_git_mode_simple(self):
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

    def test_sdist_mode_simple(self):
        # Given
        package_name = "yolo"
        version = "1.0"

        os.makedirs(os.path.join(self.prefix, package_name))

        _version_path = os.path.join(self.prefix, package_name, "_version.py")
        with open(_version_path, "wt") as fp:
            fp.write(textwrap.dedent("""\
            # THIS FILE IS GENERATED FROM TFBOOST SETUP.PY
            version = '1.0'
            full_version = '1.0.dev1'
            git_revision = 'fbd0fc1adb572405db7ce0da4fe56f8d7de5ed4d'
            is_released = False

            if is_released:
                version_info = (1, 0, 'final', 0)
            else:
                version = full_version
                version_info = (1, 0, 'dev', 1)
            """))


        # When
        with cd(self.prefix):
            full_version = write_version_py(package_name, version)

        # Then
        self.assertEqual(full_version, "1.0.dev1")
