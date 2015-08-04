__author__ = 'jwely'

import pip

def build_dev_env():
    """
    builds the development environment used to create autodocs through
    sphinx.
    """

    got_sphinx = pip.main(["install","sphinx"])
    got_graphviz = pip.main(["install","graphviz"])

    if got_sphinx == 0 and got_graphviz == 0:
        path = pip.__file__.replace("lib\\site-packages\\pip\\__init__.pyc", "Scripts")
        print("Modules ready!, ensure '{0}' is added to your PATH variable to continue!".format(path))


if __name__ == "__main__":
    build_dev_env()

