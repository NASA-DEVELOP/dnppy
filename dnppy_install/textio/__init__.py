"""
This text I/O (textio) module has been added as a place to put scripts
and functions realated to reading very speficic customized data formats

Any function in this module may read from any number of very specifically
formatted text formats (usually weather data), but all of them return
a "text file object" or "tfo"
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

from .text_data_class import *
from .read_csv import *
from .read_DS3505 import *
from .log import *
