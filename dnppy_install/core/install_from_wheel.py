__author__ = 'jwely'

import pip
import sys
import platform
import os

__all__ = ["install_from_wheel"]


def install_from_wheel(filepath_to_wheel_file):
    """
    This script can be used to add python libraries to the arcmap
    installation of python from wheelfiles. A great source of wheelfiles
    can be found here

    http://www.lfd.uci.edu/~gohlke/pythonlibs/

    simply use
        from dnppy import core
        filepath = r"C:\mydirectory\some_wheelfyle.whl"
        core.install_from_wheel(filepath)
    """

    head, tail = os.path.split(filepath_to_wheel_file)

    py_architecture = platform.architecture()[0]
    py_version = "".join(map(str,sys.version_info[0:2]))

    # make sure the wheel file appears to be the correct version
    if py_architecture in tail and py_version in tail:
        pip.main(["install", filepath_to_wheel_file])
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

