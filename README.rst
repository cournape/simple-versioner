Single-file module for simple python packages' versioning.

This package allows you to achieve the following:

1. define your version in a single place
2. define a dev version with build numbers between releases
3. allow your python package to reflect its version, both when installed from
   an sdist and from a git checkout

It tries to assume as little as possible about your package structure and
versioning scheme. You are expected to manually set release versions. If you
prefer doing things completely automatically from git tags, look at the
`versioneer package <https://github.com/warner/python-versioneer>`.

Usage
=====

You can decide to either install simple_versioner package, or simply copy the
file simple_versioner.py in the directory containing your setup.py. The module
is designed such as copying the file directly is always possible, as
setup-dependencies are not handled very well in python at this time.

Initial setup
-------------

Then, you need to do the following::

  # setup.py
  ...
  
  from simple_versioner import write_version_py
  
  VERSION = "1.0.0"
  IS_RELEASED = False
  
  full_version = write_version_py("my_package", VERSION, is_released=IS_RELEASED1)
  
  ...
  
  setup(version=full_version)

And::

   # my_package/__init__.py
   
   try:
       from ._version import (
           version as __version__, version_info as __version_info__
       )
   except ImportError:
       __version__ = "unknown"
       __version_info__ = (0, 0, 0, "unknown", 0)

Once this is done, full_version will automatically contain a ".devN" suffix for
non released version, where N is the build number.

If a "last_commit" argument is given to write_version_py, the build number will
be computed from there, otherwise it will calculated from the first commit,
defined as the oldest tail of the git graph.

Making a release
----------------

When doing a release, you need to change IS_RELEASED to True, in the same
commit as the one referred to by the corresponding git tag. Again, if you
prefer this step to be automated, you should look at versioneer.
