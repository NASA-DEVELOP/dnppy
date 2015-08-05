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
#import pip               installs pip, then imports it
#import psutil            installs psutil, then imports it


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
        import pip
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(dlurl))
        pip.main(["install", path])


def get_mod_with_pip(module_name, version = None):
    """
    attempts pip install of all dependencies in the input list of
    tupled package names and version numbers (package, version).
    use "None" to leave version unspecified.
    """

    try:
        newmodule = __import__(module_name)

    except:
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

    get_pip()

    # list of assets to install, add to assets here.
              # module : [version,
              #           64 bit asset link,
              #           32 bit asset link]

    asset_order = ["cython", "scipy", "numpy", "gdal", "h5py"] # installs assets below in this order

    assets = {"cython":[None,
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/Cython-0.22-cp27-none-win_amd64.whl",
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/Cython-0.22-cp27-none-win32.whl"],
              "scipy": [None,
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/scipy-0.15.1-cp27-none-win_amd64.whl",
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/scipy-0.15.1-cp27-none-win32.whl"],
              "gdal" : [None,
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/GDAL-1.11.2-cp27-none-win_amd64.whl",
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/GDAL-1.11.2-cp27-none-win32.whl"],
              "numpy": ["1.9.2",
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/numpy-1.9.2.mkl-cp27-none-win_amd64.whl",
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/numpy-1.9.2.mkl-cp27-none-win32.whl"],
              "h5py":  [None,
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/h5py-2.5.0-cp27-none-win_amd64.whl",
                        "https://github.com/nasa/dnppy/releases/download/1.15.2/h5py-2.5.0-cp27-none-win32.whl"]}

    pip_versions = {"wheel" : None,     # for installing other dependencies
                    "requests": None,   # for better web interfacing
                    "psutil": None      # for killing processes which might lock files we want to modify
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

    # tries failed modules a second time
    for mod in checks:
        if checks[mod] is False:
            if mod in assets:
                get_mod_from_assets(mod, *assets[mod])
            elif mod in pip_versions:
                get_mod_with_pip(mod, pip_versions[mod])

    # perform a second check
    checks = {}
    for key in assets:
        checks[key] = check_mod(key, assets[key][0])
    for key in pip_versions:
        checks[key] = check_mod(key, pip_versions[key])


    # prints status updates
    print("library name    ready?")
    for key in checks:
        print("  {0}{1}".format(key.ljust(14), checks[key]))

    if all(checks):
        print("All dependencies loaded")
    else:
        raise Exception("dependencies could not be loaded properly!")


if __name__ == "__main__":

    # run main
    main()