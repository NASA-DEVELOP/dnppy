"""
 This is a barebones install script to install the dnppy module
 
 It simply checks the version numbers indicated in __init__.py and
 copies the dnppy_install folder contents into a new folder named
 dnppy in the site-packages folder in the currently running python library.

 It duplicates this action for a version specific named folder so users can
 switch back and forth between old and new versions by explicitly importing,
 for example:

   from dnppy0.0.2     import core as old_core
   from dnppy1.15.1    import core as new_core

 If you have knowledge of setuptools and time to make this setuptools compatible and
 can allow dnppy installation with pip directly, please do so.
"""

import os, shutil, sys, dnppy_install, time
import install_dependencies


def upgrading(now_vers, up_vers):
    """
    compares two version strings and returns True if up_vers is more recent than
    now_vers
    """
    now    = now_vers.split('.')
    up     = up_vers.split('.')
    length = min([len(now),len(up)])

    for i in range(length):
        now[i] = now[i].ljust(5,'0')
        up[i]  = up[i].ljust(5,'0')

    if int(''.join(up)) >= int(''.join(now)):
        return True
    else:
        return False


def setup():
    """performs setup of dnppy by copying files to site-packages """

    up_vers = dnppy_install.__version__

    library_path, _ = os.path.split(os.__file__)
    source_path, _  = os.path.split(dnppy_install.__file__)
    dest_path       = os.path.join(library_path, 'site-packages', 'dnppy')
    dest_path2      = dest_path + up_vers

    if os.path.isdir(dest_path):
        try:
            import dnppy
            now_vers = dnppy.__version__

            if upgrading(now_vers, up_vers):
                print("\nUpdating from dnppy version [{0}] to version [{1}]...".format(now_vers, up_vers))

                shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)

                try: shutil.rmtree(dest_path2)
                except: pass

                shutil.copytree(source_path, dest_path2)
            else:
                print("you are trying to replace your dnppy with an older version!")
                print("Are you sure you wish to downgrade")
                downgrade = raw_input("from version [{0}] to [{1}]? (y/n): ".format(now_vers, up_vers))
                if downgrade == 'y' or downgrade == 'Y':
                    shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path)
                    shutil.rmtree(dest_path2)
                    shutil.copytree(source_path, dest_path2)
                else:
                    print("Setup aborted!")

        # handles the case where dnppy is installed, but cannot import for some reason.
        except:
            print("installing dnppy version [{0}]".format(up_vers))
            shutil.rmtree(dest_path)
            shutil.rmtree(dest_path2)
            shutil.copytree(source_path, dest_path)
            shutil.copytree(source_path, dest_path2)
    else:
        print("installing dnppy version [{0}]".format(up_vers))
        shutil.copytree(source_path, dest_path)
        shutil.copytree(source_path, dest_path2)

    print('\nSource path       : ' + source_path)
    print('Destination path 1: '   + dest_path)
    print('Destination path 2: '   + dest_path2)


def test_setup():
    """ returns True if all modules of dnppy import properly"""

    # ensure every module imports OK
    print("convert")
    from dnppy import convert
    print("core")
    from dnppy import core
    print("download")
    from dnppy import download
    print("landsat")
    from dnppy import landsat
    print("modis")
    from dnppy import modis
    print("radar")
    from dnppy import radar
    print("raster")
    from dnppy import raster
    print("solar")
    from dnppy import solar
    print("textio")
    from dnppy import textio
    print("time_series")
    from dnppy import time_series
    return True



def main():
    """ main function for installing dnppy """

    print("====================================================================")
    print("   Setting up dnppy! the DEVELOP National Program python package!")
    print("====================================================================")

    print("\nSetting up other libraries!")
    install_dependencies.main()
    setup()

    print("\nValidating setup of each module...")
    if test_setup() is True:
        print("\nSetup was successful!")
    else:
        print("\nSetup has failed!")

    print("You may close this window")
    time.sleep(20)
    # sys.exit()


if __name__ == "__main__":
    main()
