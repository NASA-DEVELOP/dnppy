__author__ = 'jwely'

import webbrowser,time,sys

def check_module(module_name):

    """
    Checks for module installation and guides user to download source if not found

     Simple function that directs the user to download the input module if they do
     not already have it before returning a "False" value. This helps novice users quickly
     raster.identify that a missing module is the problem and attempt to correct it.

     modules with supported download help links are listed below
     module_list=['h5py','numpy','dbfpy','scipy','matplotlib','PIL','gdal']

     Example usage:
       if check_module('numpy'): import numpy
    """

    module_list=['h5py','numpy','dbfpy','scipy','matplotlib','PIL','gdal','pyhdf']

    # try to import the module, if it works return True, otherwise continue
    try:
        modules = map(__import__,[module_name])
        return True
    except:

        for module in module_list:
            if module_name==module:
                print "You do not have " + module_name + ", opening download page for python 2.7 version!"

        # determine the correct url based on module name
        if module_name=='h5py':
            url = 'https://pypi.python.org/pypi/h5py'

        elif module_name == 'numpy':
            url = 'http://sourceforge.net/projects/numpy/files/latest/download?source=files'

        elif module_name == 'dbfpy':
            url = 'http://sourceforge.net/projects/dbfpy/files/latest/download'

        elif module_name == 'pyhdf':
            url = 'http://hdfeos.org/software/pyhdf.php'

        elif module_name == 'scipy':
            url = 'http://sourceforge.net/projects/scipy/files/latest/download?source=files'

        elif module_name == 'matplotlib':
            url = """http://sourceforge.net/projects/matplotlib/files/matplotlib/
            matplotlib-1.4.1/windows/matplotlib-1.4.1.win-amd64-py2.7.exe/
            download?use_mirror=superb-dca3"""

        elif module_name == 'PIL':
            url = 'http://www.pythonware.com/products/pil/'

        elif module_name == 'gdal':
            print 'Follow this tutorial closely for installing gdal for 32 bit UNLESS you have intentionally installed 64 bit python'
            url = 'http://pythongisandstuff.wordpress.com/2011/07/07/installing-gdal-and-ogr-for-python-on-windows/'

        # open the url and HALT operation.
        time.sleep(3)
        webbrowser.open(url)
        sys.exit()
