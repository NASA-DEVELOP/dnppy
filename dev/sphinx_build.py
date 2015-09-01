__author__ = 'jwely'

import pip
import os

"""
Running this script will create the sphinx build in the local repository.
As you might notice, this folder is in the .gitignore, so it
doesn't add to the git history. Why is this? We choose to follow
the best practice of keeping the entire documentation set
on a distinct branch, called "gh-pages" away from the master and
development branches. The whole documentation website is rebuilt
from source and pushed to the "gh-pages" branch every time a commit
is made to the master branch of dnppy, so you do not need to worry about
performing this process manually.

However! before making a commit to the master branch, you should
run this sphinx_build script to build a copy of the doc pages in your
local "docs/build" folder. Make sure you resolve any errors or warnings
given by sphinx, then open up "index.html" and browse the new
build to make sure it displays as intended. You should do this in addition
to any other quality assurance and testing checks you deem necessary. Once
everything looks good, commit to the master branch, and updates should go
live to "https://nasa-develop.github.io/dnppy/" within two minutes.
"""


def get_sphinx():
    """ sub function to make sure modules are available """
    try:
        import sphinx
    except ImportError:
        pip.main(["install", "sphinx"])
    try:
        import graphviz
    except ImportError:
        pip.main(["install", "graphviz"])
    try:
        import mock
    except ImportError:
        pip.main(["install", "mock"])


def build_sphinx():
    """
    This function creates a batch file for running sphinx-build on
    the developers system then runs it. The batch file is saved
    for troubleshooting purposes. This uses absolute filepaths,
    so the developer does not need to modify their PATH variable.
    """

    # make sure sphinx is available
    get_sphinx()

    # assemble filepaths
    sphinx_path = pip.__file__.replace("\\", "/").replace(
        "lib/site-packages/pip/__init__.pyc",
        "Scripts/sphinx-build.exe")

    self_path = __file__.replace("\\", "/")
    source_path = self_path.replace("dev/sphinx_build.py", "docs/source")
    dest_path = self_path.replace("dev/sphinx_build.py", "docs/build")

    # remove key files to force rebuild
    buildinfo = os.path.join(dest_path, ".buildinfo")
    pickle = os.path.join(dest_path, ".doctrees", "environment.pickle")
    if os.path.exists(pickle):
        os.remove(pickle)
    if os.path.exists(buildinfo):
        os.remove(buildinfo)

    with open("make_html.bat", "w+") as f:
        line1 = "{0} -b html {1} {2}".format(sphinx_path, source_path, dest_path)
        f.write(line1)
        f.write("\n\nPAUSE")

    os.system("make_html.bat")


if __name__ == "__main__":
    build_sphinx()

