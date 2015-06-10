__author__ = 'jwely'

"""
This script fetches and installs pip, then uses pip to install
dependencies of dnppy in the active python environment. This is to make
the code available in dnppy as accessible as possible and easy to
get started with straight from the github download.

NOTE: turns out many dependencies we end up wanting to use have completely
unreasonable installation processes that are difficult to figure out let alone automate
with the added complication of a non-standard arcmap installation of python.
This drastically reduces the utility of this script.

challenging modules include scipy, and h5py.
"""

import urllib
import importlib
import os

def get_pip():
    """ ensures pip is installed"""

    try:
        import pip
        print("pip loaded!")

    except ImportError:
        with open("install_pip.py", 'wb+') as f:
            connection = urllib.urlopen("https://bootstrap.pypa.io/get-pip.py")
            page = connection.read()
            f.write(page)
            f.close()
            del connection

        # run pip and clean up.
        import install_pip
        install_pip.main()
        os.remove("install_pip.py")
    return


def get_dependencies(dependencies):
    """
    attempts pip install of all dependencies in the input list of
    tupled package names and version numbers (package, version).
    use "None" to leave version unspecified.
    """

    get_pip()
    import pip

    for package, version in dependencies:
        try:
            importlib.import_module(package)
            print("imported " + package)

        except ImportError:
            print("Using pip to install " + package)

            if package == "Cython":
                # avoids specific error with Cython
                pip.main(["install", "--no-use-wheel", package])

            else:

                if version is not None:
                    pip.main(["install", package + "==" + version])
                else:
                    pip.main(["install", package])
    return


if __name__ == "__main__":
    get_dependencies([("requests", None),
                      ("wheel", None),
                      #("Cython", None),            # requires C++ visual studio 9.0 libraries
                      #("scipy", "0.9.0"),          # fails for some numpy compiling problem
                      #("h5py", None),              # HDF5 binaries dont seem to install properly
                      ])