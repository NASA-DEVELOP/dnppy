tsa
===

.. automodule:: dnppy.tsa
    :members:

Examples
--------

.. rubric:: time_series basics

Users with text data, or sequential raster images with identical spatial extents may wish to perform time specific operations on that data set. A time_series object may be easily used to perform tasks like subsetting, plotting, sorting, taking statistics, interpolating between values, sanitizing data for bad entries, and more.

This use case below is an example of using weather data downloaded from `this NOAA website`_. Firstly, take a look at the format of this `sample weather data`_, and take special note of the column labeled ``"YR--MODAHRMN"`` and the format of it.

.. _this NOAA website: http://gis.ncdc.noaa.gov/map/viewer/#app=cdo&cfg=cdo&theme=hourly&layers=1&node=gi
.. _sample weather data: https://github.com/NASA-DEVELOP/dnppy/blob/master/dnppy/time_series/test_data/weather_example.csv

We want to parse this weather data, and perform a variety of manipulations on it, but first we have to get it into python. To see how this is done, open up your preferred interpreter (IDLE by default) and retype this code step by step.

.. code-block:: python

    from dnppy import textio

    filepath = "test_data/weather_dat.txt"       # define the text filepath
    tdo      = textio.read_DS3505(filepath)      # build a text data object

    print(tdo.headers)                           # print the headers
    print(tdo.row_data[0])                       # print the first row

We now have ``text_data`` object. To read more about ``text_data`` objects, check out the ``textio`` module.
To turn this tdo into a ``time_series``, we can do

.. code-block:: python

    from dnppy import time_series                # import the time_series class

    ts = time_series.time_series('weather_data')
    ts.from_tdo(tdo)                             # use contents of the tdo

    print(ts.headers)                            # print the headers
    print(ts.row_data[0])                        # print the first row

We can see that similar headers and the same row data can be found in the ``time_series`` object ``ts``. Next we need to tell python how to interpret this data to assign times to each row. dnppy does this with python ``datetime`` objects from the native ``datetime`` module. The actual operations are hidden to the user, but we need to use ``datetime`` syntax to tell it how our dates are formatted like so:

.. code-block:: python

    timecol = "YR--MODAHRMN"                        # time data column header
    fmt     = "%Y%m%d%H%M"                          # datetime format

    ts.define_time(timecol, fmt)                    # interpret strings
    ts.interogate()                                 # print a heads up summary

As we can see above, we are telling the ``time_series`` object ``ts`` to execute its internal ``define_time`` method with arguments specifying which column contains the time information, and the ``fmt`` string to use to interpret it. This specific ``fmt`` string is used to read strings such as ``201307180054``, of format YYYYMMDDHHMMSS. `read more on datetime formatting syntax`_

.. _read more on datetime formatting syntax: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

Now we can do cool stuff, like split it into subsets.

.. code-block:: python

    ts.make_subsets("%d")     # subset the data into daily chunks
    ts.interogate()           # print a heads up summary

As you can see from the report, there are now many "subsets" of this time series. Each of these subsets is actually its own `time_series` object! and all the same manipulations can be performed on them individually as can be performed on the whole series. Lets go ahead and do a quick plot of the temperature data in here.

.. code-block:: python

    ts.column_plot("TEMP")  # no frills plot of temperature

notice that we used the column name for temperature data from our weather file. This doesn't make very pretty plots, so if we want, we can rename parameters. Lets say july 21st is the most interesting day and we want to see temperature and dewpoint next to eachtother, but we also want our plot to be a little prettier.

.. code-block:: python

    ts.rename_header("TEMP","Temperature")          # give header better name
    ts.rename_header("DEWP","Dewpoint")             # give header better name

    jul21 = ts["2013-07-21"]                        # pull out subset july 21st

    jul21.column_plot(["Temperature","Dewpoint"],   # make plot with labels
            title = "Temperature and Dewpoint",
            xlabel = "Date and Time",
            ylabel = "Degrees F")

This is much better, but now we decide that we don't just want july 21st, but also the days on either side of it. To do this, we can use an overlap_width in our subsetting command to make more of a moving window through this time series, centered around july 21st.

.. code-block:: python

    ts.make_subsets("%d", overlap_width = 1,       # subset with 1 overlap
                    discard_old = True)            # discard the old subsets

    ts.interogate()                                # print a heads up summary

    jul21 = ts["2013-07-21"]                       # pull july 21st subset
    jul21.column_plot(["Temperature","Dewpoint"],  # save the plot this time
            title = "Temperature and Dewpoint",
            ylabel = "Degrees F",
            save_path = "test.png")

Now we actually have three days in our ``jul21`` time series. And we are happy with this.
So far, this has only introduced you to about a third of the functionality available in the time_series module, but it should be enough to get you started. Consult the internal help docs and function list below to learn more!

.. rubric:: rast_series basics

The ``rast_series`` class is a child of ``time_series`` class, where each row in ``rast_series.row_data`` contains the values ``[filepath, filename, fmt_name]`` for a raster image.

There are some cool functions in the ``raster`` module that are tailored to time series type raster images, and the ``rast_series`` is a type of container to manage your raster data and pass it into more complex raster functions. This example is going to use example data following on from the `MODIS extracting and mosaicing example`_

.. _MODIS extracting and mosaicing example: https://nasa-develop.github.io/dnppy/modules/modis.html#examples

A ``rast_series`` object can be created and populated with

.. code-block:: python

    from dnppy import time_series
    rs = time_series.rast_series()

    rastdir  = r"C:\Users\jwely\mosaics"  # directory of our MODIS mosaics
    fmt      = "%Y%j"
    fmt_mask = range(9,16)

    rs.from_directory(rastdir, fmt, fmt_mask)

The ``rastdir`` variable in this example is the same place our MODIS mosaics are stored from the MODIS mosaic example. The ``fmt`` variable should be familiar to you from the ``time_series`` example above, but the ``fmt_mask`` is new. The ``fmt_mask`` is simply a list of character locations within the filename strings where the information matching ``fmt`` can be found. Our filenames look something like ``MOD10A1.A2015001.mosaic.005.2015006011526_FracSnowCover.tif``. And ``fmt_mask`` is simply telling us that characters 9 through 15 are where the date information can be found. Remember python counts up from zero.

For this example, we want to remove all values that are not telling us about the fractional snow cover on the ground. Since these values are represented by integers 1 through 100, we can set all other values to NoData with

.. code-block:: python

    rs.null_set_range(high_thresh = 100, NoData_Value = 101)

Which  simply calls ``raster.null_set_range`` on every image in this ``rast_series``, and sets all numbers over 100 to equal 101, and sets 101 as the NoData_Value for these images. Now lets say we want rolling average type statistics, with a window 7 days wide to represent a week of data centered around any given day. We can divide the data in week long chunks (with overlap) in the same way we do with ``time_series``.

.. code-block:: python

    rs.make_subsets("%d", overlap_width = 3)
    rs.interrogate()

An overlap width of three signifies grabbing three days on each side of the center day. And now to take the statistics with.

.. code-block:: python

    statsdir = r"C:\Users\jwely\statistics"   # directory to save our statistics
    rs.series_stats(statsdir)

Which calls the ``raster.many_stats`` function on every subset in this ``rast_series`` object. Now we have weekly snapshots for each day in our data record!

Code Help
---------

Auto-documentation for functions and classes within this module is generated below!

.. automodule:: dnppy.tsa.time_series
    :members:
    :private-members:

.. automodule:: dnppy.tsa.rast_series
    :members:
    :private-members:




