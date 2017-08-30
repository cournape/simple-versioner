# Copyright (c) 2017 by David Cournapeau
# This software is released under the MIT license. See LICENSE file for the
# actual license.
import contextlib
import mock
import os
import os.path
import shutil
import sys
import tempfile
import textwrap
import unittest

from simple_versioner import git_version, write_version_py


HERE = os.path.dirname(__file__)
DUMMY_GIT_REPO = os.path.join(HERE, "git-repo")


def import_from_path(path, module_name="<dummy>"):
    if sys.version_info[0] < 3:
        import imp
        return imp.load_source(module_name, path)
    else:
        # Works on 3.5 and above only
        import importlib.util
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


class TempdirMixin(object):
    def setUp(self):
        self.prefix = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.prefix)


class TestGitVersion(TempdirMixin, unittest.TestCase):
    def setUp(self):
        super(TestGitVersion, self).setUp()

        git_root = os.path.join(self.prefix, ".git")
        shutil.copytree(DUMMY_GIT_REPO, git_root)

    def test_no_since_commit(self):
        # When
        with cd(self.prefix):
            _, build_number = git_version()

        # Then
        self.assertEqual(build_number, 3)

    def test_since_a_tag(self):
        # When
        with cd(self.prefix):
            _, build_number = git_version(since_commit="v0.0.1")

        # Then
        self.assertEqual(build_number, 1)


class TestVersioner(TempdirMixin, unittest.TestCase):
    def test_git_mode_simple(self):
        # Given
        package_name = "yolo"
        version = "1.0.0"

        filename = os.path.join(self.prefix, "_version.py")
        os.makedirs(os.path.join(self.prefix, ".git"))

        # When
        with cd(self.prefix):
            with mock.patch(
                "simple_versioner.git_version", return_value=("abcd", 0)
            ):
                write_version_py(package_name, version, filename=filename)

        # Then
        m = import_from_path(filename)

        self.assertIs(m.is_released, False)
        self.assertEqual(m.version_info, (1, 0, 0, "dev", 0))
        self.assertEqual(m.git_revision, "abcd")

    def test_sdist_mode_bootstrap_init(self):
        # Sometimes, package.__init__ implies imports of 3rd packages that are
        # not available when running setup.py, so it is important to make sure
        # we can import package._version without trouble.

        # Given
        package_name = "yolo"
        version = "1.0"

        os.makedirs(os.path.join(self.prefix, package_name))

        init_path = os.path.join(self.prefix, package_name, "__init__.py")
        with open(init_path, "wt") as fp:
            fp.write(
                "# 3rd party library that will fail to import\nimport foo")

        _version_path = os.path.join(self.prefix, package_name, "_version.py")
        with open(_version_path, "wt") as fp:
            fp.write(textwrap.dedent("""\
            # THIS FILE IS GENERATED FROM TFBOOST SETUP.PY
            version = '1.0.dev1'
            full_version = '1.0.dev1'
            git_revision = 'fbd0fc1adb572405db7ce0da4fe56f8d7de5ed4d'
            is_released = False

            version_info = (1, 0, 'dev', 1)
            """))

        # When
        with cd(self.prefix):
            full_version = write_version_py(package_name, version)

        # Then
        self.assertEqual(full_version, "1.0.dev1")

    def test_sdist_mode_simple(self):
        # Given
        package_name = "yolo"
        version = "1.0"

        os.makedirs(os.path.join(self.prefix, package_name))

        init_path = os.path.join(self.prefix, package_name, "__init__.py")
        with open(init_path, "wt") as fp:
            fp.write("")

        _version_path = os.path.join(self.prefix, package_name, "_version.py")
        with open(_version_path, "wt") as fp:
            fp.write(textwrap.dedent("""\
            # THIS FILE IS GENERATED FROM TFBOOST SETUP.PY
            version = '1.0.dev1'
            full_version = '1.0.dev1'
            git_revision = 'fbd0fc1adb572405db7ce0da4fe56f8d7de5ed4d'
            is_released = False

            version_info = (1, 0, 'dev', 1)
            """))

        # When
        with cd(self.prefix):
            full_version = write_version_py(package_name, version)

        # Then
        self.assertEqual(full_version, "1.0.dev1")
