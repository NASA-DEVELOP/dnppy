"""
The textio module, read like "text I/O", is a repository of functions for reading specific `text`
data formats as they are served up from their respective DAACs. Custom text file formats are
common in historical weather data and other ground based data collection networks. This module
aims to convert them to something more standardized. Currently, custom ``text_data_objects``
are used, but migrating to something based on standard `json`_ is envisioned.

.. _json: http://json.org/

Requires ``arcpy``: No
"""

__author__ = ["Jwely"]

from ioconfig import *
from read_csv import *
from read_DS3505 import *
from logfile import *
from text_data import *
