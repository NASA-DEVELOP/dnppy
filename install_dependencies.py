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
        print("imported pip")

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


def check_pip():
    """checks that pip imports OK"""
    try:
        import pip
        return True
    except ImportError:
        return False


def get_gdal():
    """
    easy installation of gdal is a little different than other packages, but
    a pretty reliable method of arcmap compatible installation has been discovered
    with the use of a wheel file. This function grabs that wheel file from
    the assets of dnppys first beta release, and installs gdal on any system
    """

    try:
        import gdal
        print("imported gdal")

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


def check_gdal():
    """ checks that gdal imports OK """
    try:
        import gdal
        return True
    except ImportError:
        return False


def get_modules(dependencies):
    """
    attempts pip install of all dependencies in the input list of
    tupled package names and version numbers (package, version).
    use "None" to leave version unspecified.
    """

    import pip

    for package, version in dependencies:
        if version is not None:
            pip.main(["install", package + "==" + version])
        else:
            pip.main(["install", package])
    return


def main():
    """
    setup commonly had to be run twice to succeeed, the reason wasn't determined,
    as an immediate hack fix, each of these functions is simply called twice
    """
    get_pip()
    get_pip()
    get_modules([("wheel", None)])
    get_modules([("wheel", None)])
    get_modules([("requests", None)])
    get_modules([("requests", None)])
    get_gdal()
    get_gdal()

    if check_pip() and check_gdal():
        print("dependencies fetched!")
    else:
        raise Exception("Dependencies could not be installed!")

if __name__ == "__main__":
    main()