# Copyright (c) 2017 by David Cournapeau
# This software is released under the MIT license. See LICENSE file for the
# actual license.
import os.path
import re
import subprocess


_DOT_NUMBERS_RE = re.compile("v?(\d+!)?(\d+(\.\d+)*)")


# Return the git revision as a string
def git_version(previous_commit=None):
    """
    Compute the current git revision, and the number of commits since
    <previous_commit>.

    Parameters
    ----------
    previous_commit : string or None
        If specified and not None, git_count will be the number of commits
        between this value and HEAD. Useful to e.g. compute a build number.
    """
    try:
        out = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    if previous_commit is None:
        previous_commit += ".."
    else:
        cmd = ["git", "rev-list", "--max-parents=0", "HEAD"]
        try:
            out = subprocess.check_output(cmd)
            first_commit = out.splitlines()[-1]
        except OSError:
            return git_version, 0

        previous_commit = first_commit

    try:
        out = subprocess.check_output(
            ['git', 'rev-list', '--count', previous_commit]
        )
        git_count = int(out.strip().decode('ascii'))
    except OSError:
        git_count = 0

    return git_revision, git_count


def write_version_py(package_name, version, previous_commit=None,
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

if is_released:
    version_info = ({dot_numbers}, 'final', 0)
else:
    version = full_version
    version_info = ({dot_numbers}, 'dev', {dev_num})
"""

    fullversion = version
    if os.path.exists('.git'):
        git_rev, dev_num = git_version(previous_commit)
    elif os.path.exists(filename):
        # must be a source distribution, use existing version file
        try:
            m = __import__(package_name + "._version")
            git_rev = m._version.git_revision
            full_v = m._version.full_version
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "{0} and the build directory "
                              "before building.".format(filename))

        match = re.match(r'.*?\.dev(?P<dev_num>\d+)', full_v)
        if match is None:
            dev_num = 0
        else:
            dev_num = int(match.group('dev_num'))
    else:
        git_rev = "Unknown"
        dev_num = 0

    if not is_released:
        fullversion += '.dev' + str(dev_num)

    dot_numbers_string = ", ".join(str(item) for item in dot_numbers)

    with open(filename, "wt") as fp:
        data = template.format(
            version=version, full_version=fullversion,
            git_revision=git_rev, is_released=is_released,
            dot_numbers=dot_numbers_string, dev_num=dev_num,
            package_name=package_name.upper(),
        )
        fp.write(data)

    return fullversion
