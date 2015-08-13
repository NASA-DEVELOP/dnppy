__author__ = 'jwely'

import pip
import os
import shutil

"""
Running this script will create the sphinx build in the local repository.
As you might notice, this folder is in the .gitignore, so it
doesn't add to the git history. Why is this? We choose to follow
the best practice of keeping the entire documentation set
on a distinct branch, called "gh-pages" away from the master and
development branches. In order to update the live version of
the website, the changes must be made on the "gh-pages" branch.

The recommended workflow is as follows:
1) Create a clone of the gh-pages branch separate from your main dnppy
   project space. for example:

    /NASA
        /dnppy
        /docpage

2) place the filepath to this branch in a text file right here
   named "docs_dir.txt". for example:
        "C:\Users\jwely\Desktop\GitHub\NASA\dnppy_docs"

This will automatically make changes to both the build folder
here, and the local copy of that branch. You may now freely
commit the changes to both branches.
"""


def get_sphinx():
    """ subfunction to make sure modules are available """
    try: import sphinx
    except ImportError: pip.main(["install", "sphinx"])
    try: import graphviz
    except ImportError: pip.main(["install", "graphviz"])


def _del_dir_contents(dirpath):
    """ subfunction to delete all contents of a directory, but
        not the directory itself """

    for item in os.listdir(dirpath):
        if ".git" not in item:
            try: shutil.rmtree(item)
            except: pass


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
    sphinx_path = pip.__file__.replace("lib\\site-packages\\pip\\__init__.pyc",
                                       "Scripts\sphinx-build.exe")
    source_path = __file__.replace("dev/sphinx_build.py", "docs/source")


    # build in the local docs/build folder
    dest_path1  = __file__.replace("dev/sphinx_build.py", "docs/build")

    # remove the directory if it is already present
    if os.path.exists(dest_path1):
        _del_dir_contents(dest_path1)

    with open("make_html.bat", "w+") as f:
        line1 = "{0} -b html {1} {2}".format(sphinx_path, source_path, dest_path1)
        f.write(line1)

    # build in the user specified gh-pages branch folder
    if os.path.isfile("docs_dir.txt"):
        with open("docs_dir.txt", "r") as d:
            dest_path2  = d.read().replace("\\", "/")

            if os.path.exists(dest_path2):
                _del_dir_contents(dest_path2)

            with open("make_html.bat", "a") as f:
                f.write("\n")
                line2 = "{0} -b html {1} {2}".format(sphinx_path, source_path, dest_path2)
                f.write(line2)

    os.system("make_html.bat")


def main():
    build_sphinx()


if __name__ == "__main__":
    main()

