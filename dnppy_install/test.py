"""
This test module is used to execute test scripts located in the test/[module]
directory of the installation. It can be used to quickly perform a quality check
by verifying the functionality of every function in the dnppy package.

Just run the following:

    from dnppy import test
    test.all_modules(test_dir)

This will automatically execute all python scripts in the "test"
directory of the module installation folder so additional tests may be
very simply added in the future. Test files are automatically sorted in
ascending alphabetical/numerical order, so if the order of execution
matters, put prefix numbers in front of your test scripts. For example,
the structure of the testing scripts for the download module appears as
follows, and will run in the order listed.

    test/
        download/
            0_test_list_contents.py
            1_reverb_filelist.txt        (will not be run, because it isn't a .py file)
            1_test_download.py
            2_test_fetch.py
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

import time
import os
import dnppy
import imp

def all_modules(test_dir = False):
    """
    Runs all the test scripts for all the modules in the dnppy/test
    directory.

    Inputs:
        test_dir        since many functions require downloading and mainpulating
                        large data files, a test_dir is set up to contain this
                        data.
    """

    dnppy_dir,_      = os.path.split(dnppy.__file__)
    test_script_dir  = os.path.join(dnppy_dir,'test')
    module_name_list = os.listdir(test_script_dir )

    # make sure these existing modules get tested before the others.
    first_modules    = ['download','core','raster']
    for first_module in first_modules:
        a_module(first_module, test_dir)
        module_name_list.remove(first_module)

    # execute all remaining module test scripts in the directory
    for module_name in module_name_list:
        if not module_name == "README.txt":
            a_module(module_name, test_dir)

    return


def setup(test_dir = False):
    """
    sets up the testing directory, called by all other test functions
    the filepath for the local test_directory is stored in the text file
    dnppy/test/test_dir.txt
    """

    # if no test dir was specified, put it on the C drive
    if not test_dir:
        test_dir = "C:/"

    test_dir = os.path.join(test_dir,"dnppy_test")

    dnppy_dir,_         = os.path.split(dnppy.__file__)
    test_dir_text_path  = os.path.join(dnppy_dir,"test","test_dir.txt")
    
    with open(test_dir_text_path,'w+') as f:
        f.write(test_dir)
        f.close
 
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print("Test directory has been created at {0}".format(test_dir))
        time.sleep(2)
    return


def a_module(module_name, test_dir = False):
    """runs all the python files in the test/module_name directory""" 
    
    setup(test_dir)
    
    dnppy_dir,_     = os.path.split(dnppy.__file__)
    test_script_dir = os.path.join(dnppy_dir,"test",module_name)
    test_script_list= os.listdir(test_script_dir)
    
    for test_script in test_script_list:
        if ".py" in test_script:
            ts_path = os.path.join(test_script_dir, test_script)
            print("Running testing script '{0}'".format(test_script))
            module  = imp.load_source(test_script.replace('.py',''), ts_path)
        
    return


def test_dir():
    """
    Function to be used with stand_alone testing scripts to read local testing
    directory from the test_dir.txt file without needing to pass the directory
    as an argument between the test call and the testing script.

    To have the testing script write to the test directory, invoke the following.

        from dnppy import test
        test_dir = test.test_dir()
    """
    
    dnppy_dir,_         = os.path.split(dnppy.__file__)
    test_dir_text_path  = os.path.join(dnppy_dir,"test","test_dir.txt")

    if not os.path.isdir(test_dir_text_path):
        setup()

    with open(test_dir_text_path,'r') as f:
        test_dir = next(f)
        f.close()
        
    return test_dir


if __name__ == "__main__":
    all_modules()
    
