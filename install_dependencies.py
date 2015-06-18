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
import os
import platform
#import pip               installs pip, then imports it

def get_pip():
    """ ensures pip is installed"""

    try:
        import pip

    except ImportError:
        with open("install_pip.py", 'wb+') as f:
            connection = urllib.urlopen("https://bootstrap.pypa.io/get-pip.py")
            page = connection.read()
            f.write(page)
            f.close()
            del connection

        # run pip and clean up.
        import install_pip
        os.system("install_pip.py")
        os.remove("install_pip.py")
    return

def get_gdal():
    """
    easy installation of gdal is a little different than other packages, but
    a pretty reliable method of arcmap compatible installation has been discovered
    with the use of a wheel file. This function grabs that wheel file from
    the assets of dnppys first beta release, and installs gdal on any system
    """

    try:
        import gdal

    except ImportError:
        print("gathering gdal assets")

        bit64py27 = "https://github.com/nasa/dnppy/releases/download/1.15.2/GDAL-1.11.2-cp27-none-win_amd64.whl"
        bit32py27 = "https://github.com/nasa/dnppy/releases/download/1.15.2/GDAL-1.11.2-cp27-none-win32.whl"

        # determine if python running is 32 or 64 bit
        if platform.architecture()[0] == "64bit":
            dlurl = bit64py27
        else:
            dlurl = bit32py27

        # write the file right next to this setupfile
        with open(os.path.basename(dlurl),"wb+") as f:
            connection = urllib.urlopen(dlurl)
            page = connection.read()
            f.write(page)
            f.close()
            del connection

        # now use pip to install the gdal wheel file
        import pip
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(dlurl))
        pip.main(["install", path])
        os.remove(path)
    return


def get_numpy():
    """ gets numpy 1.9.2 wheel that is compatible with gdal 1.11.2"""

    import numpy

    if numpy.__version__ != "1.9.2":
        print(numpy.__version__)

        bit64py27 = "https://github.com/nasa/dnppy/releases/download/1.15.2/numpy-1.9.2.mkl-cp27-none-win_amd64.whl"
        bit32py27 = "https://github.com/nasa/dnppy/releases/download/1.15.2/numpy-1.9.2.mkl-cp27-none-win32.whl"

        # determine if python running is 32 or 64 bit
        if platform.architecture()[0] == "64bit":
            dlurl = bit64py27
        else:
            dlurl = bit32py27

        # write the file right next to this setupfile
        with open(os.path.basename(dlurl),"wb+") as f:
            connection = urllib.urlopen(dlurl)
            page = connection.read()
            f.write(page)
            f.close()
            del connection

        # now use pip to install the gdal wheel file
        import pip
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(dlurl))
        pip.main(["install", path])
        os.remove(path)
    return


def get_mod_with_pip(modulename, version = None):
    """
    attempts pip install of all dependencies in the input list of
    tupled package names and version numbers (package, version).
    use "None" to leave version unspecified.
    """

    try:
        newmodule = __import__(modulename)

    except:
        import pip

        if version is not None:
            pip.main(["install", modulename + "==" + version])
        else:
            pip.main(["install", modulename])

    return


def check_mod(modulename, version = None):
    """
    returns true if module of input version can be imported
    """

    try:
        newmodule = __import__(modulename)
    except:
        return False

    if version is not None:
        if newmodule.__version__ == version:
            return True
        else:
            return False
    else:
        return True





def main():
    """
    setup commonly had to be run twice to succeed, the reason wasn't determined,
    as an immediate hack fix, each of these functions is simply called twice
    """

    get_pip()
    get_mod_with_pip("wheel", None)
    get_mod_with_pip("requests", None)
    get_numpy()
    get_gdal()

    # run modules that failed one more time
    if not check_mod("pip", None):
        get_pip()

    if not check_mod("wheel", None):
        get_mod_with_pip("wheel")

    if not check_mod("requests", None):
        get_mod_with_pip("requests")

    if not check_mod("numpy", "1.9.2"):
        get_numpy()

    if not check_mod("gdal", None):
        get_gdal()

    # perform final check
    checks = {"pip" :       check_mod("pip", None),
              "wheel":      check_mod("wheel", None),
              "requests":   check_mod("requests", None),
              "numpy":      check_mod("numpy", "1.9.2"),
              "gdal" :      check_mod("gdal", None)}

    print("library name    ready?")
    for key in checks:
        print("  {0}{1}".format(key.ljust(14), checks[key]))

    if all(checks):
        print("All dependencies loaded")
    else:
        raise Exception("dependencies could not be loaded properly!")


if __name__ == "__main__":
    main()