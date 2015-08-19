__author__ = 'jwely'

import pip
import sys
import platform
import os

__all__ = ["install_from_wheel"]


def install_from_wheel(whl_filepath):
    """
    This script can be used to add python libraries to the arcmap
    installation of python from wheel files. A great source of wheel files
    can be found at [http://www.lfd.uci.edu/~gohlke/pythonlibs/]

    :param whl_filepath:    the full local filepath to a downloaded wheel file.
    """

    head, tail = os.path.split(whl_filepath)

    py_architecture = platform.architecture()[0]
    py_version = "".join(map(str,sys.version_info[0:2]))

    # make sure the wheel file appears to be the correct version
    if py_architecture in tail and py_version in tail:
        pip.main(["install", whl_filepath])
    else:
        if py_architecture == "64bit":
            ending = "_amd64.whl"
        else:
            ending = "32.whl"

        filesuffix = "-cp{0}-none-win{1}".format(py_version, ending)

        raise Exception('''Bad wheel file for your version and architecture!
                    the wheel file you want should end with "{0}"'''.format(filesuffix))
    return


if __name__ == "__main__":
    install_from_wheel("bad_test")

