__author__ = 'jwely'
__all__ = ["_gdal_command"]

import sys
import os
import subprocess


def _gdal_command(command):
    """
    This function wraps gdal commands that one would call from the console.
    python has several different methods of spawning processes, and using this
    function for all gdal command line calls helps to centralize the methods
    for easy quality assurance. Python also appears to be in a state of flux as
    far as the best method, so we expect that the current "os.system()" method
    will not be supported indefinitely.

    :param command:     A string representing a gdal command, or a list of strings
                        representing each argument of the gdal command call.
    """

    # create both a single string command and a list of args.
    if isinstance(command, str):
        command_args = command.split(" ")
        command_str  = command

    elif isinstance(command, list):
        command_args = command
        command_str = " ".join(command)
    else:
        raise Exception("Invalid command type! must be string or list of strings")


    # get python version info
    py_major = sys.version_info.major
    py_minor = sys.version_info.minor

    # python 2.7 syntax with os.system command
    if py_major == 2:
        os.system(command_str)

    # python 3 syntax with subprocess.call(*args)
    if py_minor == 3:
        subprocess.call(command_args)

    return

