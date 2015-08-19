solar
=====

.. automodule:: dnppy.solar
    :members:

Examples
--------

.. rubric:: Compute all available solar parameters

For a simple example, lets just assume we want to go ahead and calculate everything. The inputs for all solar calculations come down to space and time. More specifically, latitude and longitude coordinates and a precise time in standard GMT. For the example below, we are going to use 2015-May-15th at exactly noon local time, in Hampton Virginia USA. Note that while observing daylight savings time, the east coast observes EDT, which is GMT-4, watch out for mistakes with time zones!

.. code-block:: python

    from dnppy import solar

    lat         = 37                    # lat (N positive)
    lon         = -76.4                 # lon (E positive)
    datestamp   = "20150515-120000"     # date stamp
    fmt         = "%Y%m%d-%H%M%S"       # datestamp format
    tz          = -4                    # timezone (GMT/UTC) offset

    sc  = solar(lat, lon, datestamp, tz, fmt)
    sc.compute_all()

The code above successfully updates ``solar`` instance ``sc`` to have all the attributes supported by the class, and prints a summary with descriptive variable names, values, and units. If the ``datestamp`` and ``fmt`` variables are unfamiliar to you, you can read more about python `datetime objects`_ and how to create them from strings with `fmt syntax`_.

Once you master datetime objects, you will probably want to use them all the time (they are pretty great). Fortunately, you can simply input a datetime object in place of the ``datestamp`` variable in the code above, and omit the ``fmt`` variable entirely, such as:

.. code-block:: python

    from dnppy import solar
    from datetime import datetime

    lat     = 37
    lon     = -76.4
    dt_obj  = datetime(2015,5,15,12,0,0)
    tz      = -4

    sc  = solar(lat, lon, dt_obj, tz)
    sc.compute_all()


Lets say you aren't interested in anything except the solar elevation angle. After consulting ``help(solar)`` or the function list below, we see there is a method called ``get_elevation``, and decide to invoke that instead of ``compute_all()`` and save it  in a new variable called ``solar_elevation``.

.. code-block:: python

    solar_elevation = sc.get_elevation()  # invoke method of solar instance "sc"

That's it! you can get any available attribute of a solar instance in exactly the same way!

.. _datetime objects: https://docs.python.org/2/library/datetime.html#datetime-objects
.. _fmt syntax: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

Code Help
---------

Auto-documentation for functions and classes within this module is generated below!

.. automodule:: dnppy.solar.solar
    :members:

