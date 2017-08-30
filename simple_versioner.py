# Copyright (c) 2017 by David Cournapeau
# This software is released under the MIT license. See LICENSE file for the
# actual license.
import ast
import os.path
import re
import subprocess


_DOT_NUMBERS_RE = re.compile("v?(\d+!)?(\d+(\.\d+)*)")


class _AssignmentParser(ast.NodeVisitor):
    """ Simple parser for python assignments."""
    def __init__(self):
        self._data = {}

    def parse(self, s):
        self._data.clear()

        root = ast.parse(s)
        self.visit(root)
        return self._data

    def generic_visit(self, node):
        if type(node) != ast.Module:
            raise ValueError(
                "Unexpected expression @ line {0}".format(node.lineno),
                node.lineno
            )
        super(_AssignmentParser, self).generic_visit(node)

    def visit_Assign(self, node):
        value = ast.literal_eval(node.value)
        for target in node.targets:
            self._data[target.id] = value


def parse_version(path):
    with open(path, "rt") as fp:
        return _AssignmentParser().parse(fp.read())["version"]


# Return the git revision as a string
def git_version(since_commit=None):
    """
    Compute the current git revision, and the number of commits since
    <since_commit>.

    Parameters
    ----------
    since_commit : string or None
        If specified and not None, git_count will be the number of commits
        between this value and HEAD. Useful to e.g. compute a build number.
    """
    try:
        out = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    if since_commit is None:
        since_commit = "HEAD"
    else:
        since_commit += ".."

    try:
        out = subprocess.check_output(
            ['git', 'rev-list', '--count', since_commit]
        )
        git_count = int(out.strip().decode('ascii'))
    except OSError:
        git_count = 0

    return git_revision, git_count


def write_version_py(package_name, version, since_commit=None,
                     is_released=False, filename=None):
    if filename is None:
        filename = os.path.abspath(os.path.join(package_name, "_version.py"))

    m = _DOT_NUMBERS_RE.search(version)
    if m is None:
        raise ValueError("Format not supported: {!r}".format(version))

    main_group = m.groups()[1]
    dot_numbers = tuple(int(item) for item in main_group.split("."))

    template = """\
# THIS FILE IS GENERATED FROM {package_name} SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

version_info = {version_info}
"""

    fullversion = version
    if os.path.exists('.git'):
        git_rev, dev_num = git_version(since_commit)
    elif os.path.exists(filename):
        # must be a source distribution, use existing version file
        return parse_version(filename)
    else:
        git_rev = "Unknown"
        dev_num = 0

    if is_released:
        release_level = "final"
    else:
        release_level = "dev"

    if not is_released:
        fullversion += '.dev' + str(dev_num)

    version_info = dot_numbers + (release_level, dev_num)

    with open(filename, "wt") as fp:
        data = template.format(
            version=version, full_version=fullversion, git_revision=git_rev,
            is_released=is_released, version_info=version_info,
            package_name=package_name.upper(),
        )
        fp.write(data)

    return fullversion
