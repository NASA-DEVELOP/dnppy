__author__ = 'jwely'
__all__ = ["_gdal_command"]

import sys
import os
import subprocess
import collections


def _gdal_command(*command):
    """
    This function wraps gdal commands that one would call from the console.
    python has several different methods of spawning processes, and using this
    function for all gdal command line calls helps to centralize the methods
    for easy quality assurance. Python also appears to be in a state of flux as
    far as the best method, so we expect that the current "os.system()" method
    will not be supported indefinitely.

    :param command:  command can be virtually any number of string arguments in
                     any configuration of args, lists, and tuples. This function
                     will take all input strings in the order in which they are
                     given and place a " " between each argument before passing
                     it to the command line.

    Examples

    .. code-block:: python

        # all of these are valid syntax
        core._gdal_command(arg1, arg2)
        core._gdal_command([arg1, arg2])
        core._gdal_command(arg1, [arg2, arg3])
        core._gdal_command(arg1, [arg2, arg3, [arg4, arg5], (arg7, arg8))
    """

    # get python version info
    py_major = sys.version_info.major
    py_minor = sys.version_info.minor

    # create both a single string command and a list of args.
    command_list = list(_flatten_args(command))
    command_str  = " ".join(map(str, command_list))
    command_args = command_str.split(" ")



    print(command_str)

    # python 2.7 syntax with os.system command
    if py_major == 2:

        os.system(command_str)

    # python 3 syntax with subprocess.call(*args)
    if py_minor == 3:
        subprocess.call(command_args)

    return


# tiny function for flattening unknown nested argument structure
def _flatten_args(l):
    """
    flattens a list with nested lists, tuples, and other irregular structures
    :param l:   list to flatten
    :return:    generator object that can be converted to list with list().
    """
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in _flatten_args(el):
                yield sub
        else:
            yield el