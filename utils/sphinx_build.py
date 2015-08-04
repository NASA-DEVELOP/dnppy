__author__ = 'jwely'

import pip
import os

def get_sphinx():
    """ subfunction to make sure modules are available """
    try: import sphinx
    except ImportError: pip.main(["install","sphinx"])
    try: import graphviz
    except ImportError: pip.main(["install","graphviz"])


def build_sphinx():
    """
    This function creates a batch file for running sphinx-build on
    the developers system then runs it. The batch file is saved
    for troubleshooting purposes.
    """

    # make sure sphinx is available
    get_sphinx()

    # assemble filepaths
    sphinx_path = pip.__file__.replace("lib\\site-packages\\pip\\__init__.pyc",
                                       "Scripts\sphinx-build.exe")
    source_path = __file__.replace("utils/build_dev_env.py","docs/source")

    # assemble the command and write it to a file
    with open("make_html.bat","w+") as f:
        bat_txt = "{0} -b html {1} ../../docpage".format(sphinx_path, source_path)
        f.write(bat_txt)

    os.system("make_html.bat")


def main():
    build_sphinx()


if __name__ == "__main__":
    main()

