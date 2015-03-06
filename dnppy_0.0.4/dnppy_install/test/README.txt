this directory contains simple scripts to test the functionality of all
dnppy functions.

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
            1_reverb_filelist.txt      (will not be run, because it isnt a .py file)
            1_test_download.py
            2_test_fetch.py


To keep your testing scripts stand_alone while still writing to the user defined
test_dir, invoke the following. This function works by saving the local test directory
in a text file on testing setup, then referencing that text file for each of your 
individual scripts.

    from dnppy import test
    test_dir = test.test_dir()