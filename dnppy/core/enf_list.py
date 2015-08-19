__author__ = 'jwely'


def enf_list(item):
    """
    When a list is expected, this function can be used to ensure
    non-list data types are placed inside of a single entry list.

    :param item:    any datatype
    :return list:   a list type
    """

    if not isinstance(item,list) and item:
        return [item]
    else:
        return item