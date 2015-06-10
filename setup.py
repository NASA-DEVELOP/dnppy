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

 If you have knowledge of setuptools and time to make this setuptools compatible,
 please do so!
"""

import os, shutil, sys, dnppy_install, time

# determine if the version being installed is newer than the current version
def upgrading(now_vers,up_vers):
    now = now_vers.split('.')
    up  = up_vers.split('.')
    length = min([len(now),len(up)])
    for i in range(length):
        now[i] = now[i].ljust(5,'0')
        up[i]  = up[i].ljust(5,'0')
    if int(''.join(up)) >= int(''.join(now)):
        return True
    return False

print("====================================================================")
print("   Setting up dnnpy! the DEVELOP National Program python package!")
print("====================================================================\n")


up_vers = dnppy_install.__version__

library_path, _ = os.path.split(os.__file__)
source_path, _  = os.path.split(dnppy_install.__file__)
dest_path       = os.path.join(library_path,'site-packages','dnppy')
dest_path2      = dest_path + up_vers

if os.path.isdir(dest_path):
    try:
        import dnppy
        now_vers = dnppy.__version__

        if upgrading(now_vers , up_vers):
            print("Updating from dnppy version [{0}] to version [{1}]...".format(now_vers, up_vers))
            
            shutil.rmtree(dest_path)
            shutil.copytree(source_path,dest_path)
            
            try: shutil.rmtree(dest_path2)
            except: pass
            
            shutil.copytree(source_path,dest_path2)
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
    shutil.copytree(source_path,dest_path)
    shutil.copytree(source_path,dest_path2)
    

print('\nSource path       : ' + source_path)
print('Destination path 1: '   + dest_path)
print('Destination path 2: '   + dest_path2)

try:
    from dnppy import convert
    from dnppy import core
    from dnppy import download
    from dnppy import landsat
    from dnppy import modis
    from dnppy import radar
    from dnppy import raster
    from dnppy import solar
    from dnppy import test
    from dnppy import textio
    from dnppy import time_series

    print "\nSetup validated and finished!"
    print("Window will close in 10 seconds")

except:
    raise ImportError("Something went wrong!")

time.sleep(10)
sys.exit()

