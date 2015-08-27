__author__ = 'jwely'

"""
This script fetches and installs pip, then uses pip to install
dependencies of dnppy in the active python environment. This is to make
the code available in dnppy as accessible as possible and easy to
get started with straight from the github download.

Several modules that do not successfully install with pip alone are installed
by fetching binaries from the dnppy release assets.
"""

import urllib
import os
import platform
# import pip               installs pip, then imports it
# import psutil            installs psutil, then imports it


def count_user():
    """
    this function attempts to import any version of dnppy. If it finds
    the user does not already have a version of 1.15.3b0 or greater, it
    downloads "_logo.png" from the release assets. These downloads are
    tracked and help us to establish the real size of dnppy's user base

    returns True if new user.
    """

    logo_url = "https://github.com/NASA-DEVELOP/dnppy/releases/download/assets/_logo.png"

    if not check_mod("dnppy"):

        with open(os.path.basename(logo_url), "wb+") as f:
            connection = urllib.urlopen(logo_url)
            page = connection.read()
            f.write(page)
            f.close()
            del connection
        return True
    else:
        return False


def get_pip():
    """ ensures pip is installed"""

    try:
        import pip

        if pip.__version__ < "7.1.1":
            raise ImportError       # just raise an import error for outdated version


    except ImportError:

        # download pip installation file
        with open("install_pip.py", 'wb+') as f:
            connection = urllib.urlopen("https://bootstrap.pypa.io/get-pip.py")
            page = connection.read()
            f.write(page)
            f.close()
            del connection

        # run pip and clean up.
        import install_pip

        # run then remove install_pip
        os.system("install_pip.py")
        os.remove("install_pip.py")

        # use pip to upgrade itself
        import pip
        pip.main(["install", "--upgrade", "pip"])


def check_process_lock():
    """
    raises an exception if processes which may lock dependencies from being
    upgraded are presently running
    """
    import psutil

    bad_list = ["ArcGIS", "ArcMap"]

    for proc in psutil.process_iter():
        try:
            name = proc.name()
            if any([k in name for k in bad_list]):
                raise RuntimeError("Terminate {0} and try running setup again!".format(name))

        except psutil.AccessDenied:
            pass


def get_mod_from_assets(module_name, version, wheel64link, wheel32link):
    """
    function for installing python packages from wheel files hosted in dnppy's assets

    :param module_name:         name of the module
    :param version:             version, use None if no version is preferred
    :param wheel64link:         asset url to 64 bit binaries
    :param wheel32link:         asset url to 32 bit binaries
    :return:
    """

    import pip

    # determine if the module is already good or not
    isready = check_mod(module_name, version)

    if not isready:
        print("gathering {0} assets".format(module_name))

        # determine if python running is 32 or 64 bit
        if platform.architecture()[0] == "64bit":
            dlurl = wheel64link
        else:
            dlurl = wheel32link

        # write the file right next to this setup file
        with open(os.path.basename(dlurl), "wb+") as f:
            connection = urllib.urlopen(dlurl)
            page = connection.read()
            f.write(page)
            f.close()
            del connection


        # now use pip to install the wheel file
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(dlurl))
        pip.main(["install", path])


def get_mod_with_pip(module_name, version = None):
    """
    attempts pip install of all dependencies in the input list of
    tupled package names and version numbers (package, version).
    use "None" to leave version unspecified.
    """

    if check_mod(module_name, version) is False:
        import pip

        if version is not None:
            pip.main(["install", module_name + "==" + version])
        else:
            pip.main(["install", module_name])


def check_mod(module_name, version = None):
    """
    returns true if module of input version can be imported
    """

    try:
        new_module = __import__(module_name)
    except:
        return False

    if version is not None:
        if new_module.__version__ == version:
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

    count_user()
    get_pip()

    # list of assets to install, add to assets here.
    # {module : [version,
    #           64 bit asset link,
    #           32 bit asset link]}

    # installs assets in the order listed here
    asset_order = ["cython", "scipy", "numpy", "gdal", "pycurl", "shapely", "h5py"]
    release_address = "https://github.com/nasa/dnppy/releases/download/1.15.2/"

    #       {module : [version,
    #                   64 bit asset link,
    #                   32 bit asset link]}
    assets = {"cython": [None,
                         release_address + "Cython-0.22-cp27-none-win_amd64.whl",
                         release_address + "Cython-0.22-cp27-none-win32.whl"],
              "scipy":  [None,
                         release_address + "scipy-0.15.1-cp27-none-win_amd64.whl",
                         release_address + "scipy-0.15.1-cp27-none-win32.whl"],
              "gdal":   [None,
                         release_address + "GDAL-1.11.2-cp27-none-win_amd64.whl",
                         release_address + "GDAL-1.11.2-cp27-none-win32.whl"],
              "numpy":  ["1.9.2",
                         release_address + "numpy-1.9.2.mkl-cp27-none-win_amd64.whl",
                         release_address + "numpy-1.9.2.mkl-cp27-none-win32.whl"],
              "h5py":   [None,
                         release_address + "h5py-2.5.0-cp27-none-win_amd64.whl",
                         release_address + "h5py-2.5.0-cp27-none-win32.whl"],
              "pycurl": [None,
                         release_address + "pycurl-7.19.5.1-cp27-none-win_amd64.whl",
                         release_address + "pycurl-7.19.5.1-cp27-none-win32.whl"],
              "shapely":[None,
                         release_address + "Shapely-1.5.9-cp27-none-win_amd64.whl",
                         release_address + "Shapely-1.5.9-cp27-none-win32.whl"]
    }

    pip_versions = {"setuptools": None,  # installs setuptools? maybe not needed?
                    "matplotlib": None,  # for making plots! users with arcpy already have this!
                    "wheel": None,       # for installing other dependencies
                    "requests": None,    # for better web interfacing
                    "psutil": None,      # for killing processes which might lock files we want to modify
                    "urllib3": None,     # magical url library
                    "mock": None,        # used to fake arcpy imports in testing environments
    }

    # installs python packages with simple pip install
    for mod in pip_versions:
        get_mod_with_pip(mod, pip_versions[mod])

    # checks for process that might lock files from modification
    check_process_lock()

    # installs modules from asset wheel files
    for mod in asset_order:
        get_mod_from_assets(mod, *assets[mod])

    # perform a check
    checks = {}
    for key in assets:
        checks[key] = check_mod(key, assets[key][0])
    for key in pip_versions:
        checks[key] = check_mod(key, pip_versions[key])

    # prints status updates
    print("Checking libraries!")
    print("library name    ready?")
    for key in checks:
        print("  {0}{1}".format(key.ljust(14), checks[key]))

    if all(checks):
        print("All dependencies loaded")


if __name__ == "__main__":
    # run main
    main()

