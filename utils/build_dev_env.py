__author__ = 'jwely'

import pip
import os

def build_dev_env():
    """
    builds the development environment used to create autodocs through
    sphinx.
    """
    got_sphinx = pip.main(["install","sphinx"])
    got_graphviz = pip.main(["install","graphviz"])


def create_make_html():
    """
    this function builds a batch file that can be run to build sphinx on
    the any developers system.
    """
    sphinx_path = pip.__file__.replace("lib\\site-packages\\pip\\__init__.pyc",
                                       "Scripts\sphinx-build.exe")
    source_path = __file__.replace("utils/build_dev_env.py","docs/source")

    bat_txt = "{0} -b html {1} ../../docpage\nPAUSE".format(sphinx_path, source_path)

    with open("make_html.bat","w+") as f:
        f.write(bat_txt)
        print("Created make_html.bat! Run that file to build sphinx docs!")


if __name__ == "__main__":
    build_dev_env()
    create_make_html()

