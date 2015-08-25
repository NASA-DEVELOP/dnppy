__author__ = 'jwely'
__all__ = ["run_command"]


import subprocess
import collections


def run_command(*command):
    """
    This function formats and runs commands that one would call from the console.
    Primarily intended for calling gdal commands from other functions in cases
    where the python bindings are absent. Particularly useful for commands with
    list type arguments. This function provides simplicity, but users wanting more
    functionality should use the subprocess module directly.

    :param command:  command can be virtually any number of string arguments in
                     any configuration of args, lists, and tuples. This function
                     will take all input strings in the order in which they are
                     given and place a space ``" "`` between each argument before
                     passing it to the command line.

    .. code-block:: python

        # all of these are valid syntax
        core.run_command(arg1)
        core.run_command(arg1, arg2)
        core.run_command([arg1, arg2])
        core.run_command(arg1, [arg2, arg3])
        core.run_command(arg1, [arg2, arg3, [arg4, arg5]], (arg7, arg8))
    """

    # create both a single string command and a list of args.
    command_list = list(_flatten_args(command))
    command_str  = " ".join(map(str, command_list))
    command_args = command_str.split(" ")

    print(command_str)
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