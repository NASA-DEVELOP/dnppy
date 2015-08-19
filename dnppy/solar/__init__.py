"""
The solar module contains just one class definition, with many associated methods to perform a plethora
of calculations based around the sun-earth relationship. It replicates the functionality of the `common
NOAA excel calculator`_, including adjustments due to atmospheric refraction. Each method may be run
independently as the user wishes, as each method will automatically invoke any other calculations that
must be performed first, and it will not unnecessarily redo calculations that have already been completed.

A solar class object allows scalar or numpy array inputs for latitude and longitude values for per-pixel
computation and improved accuracy when scene-center calculations are insufficient. The solar class is not
yet capable of ingesting digital elevation models to calculate slope and aspect dependent parameters, but
it is a planned addition.

.. _common NOAA excel calculator: http://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html
"""
from solar import solar
