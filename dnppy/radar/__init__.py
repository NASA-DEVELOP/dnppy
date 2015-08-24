"""
The radar module is very small, but houses functions used to process
radar data. It focuses on UAVSAR data, which is data from a Synthetic Aperture
Radar (SAR) on board an Unmanned Aerial Vehicle (UAV). Assists the user in
building header data and converting to decibels.
"""

__author__ = ["djjensen",
              "Scott Baron",
              "Jwely"]

# local imports
from decibel_convert import *
from create_header import *
