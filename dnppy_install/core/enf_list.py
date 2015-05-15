__author__ = 'jwely'


def enf_list(item):

    """
    Ensures input item is list format.

     many functions within this module allow the user
     to input either a single input or list of inputs in string format. This function makes
     sure single inputs in string format are handled like single entry lists for iterative
     purposes. It also will output an error if it is given a boolean value to signal that
     an input somewhere else is incorrect.
     """

    if not isinstance(item,list) and item:
        return [item]

    elif isinstance(item,bool):
        Warning('Cannot enforce a bool to be list! at least one list type input is invalid!')
        return False
    else:
        return item