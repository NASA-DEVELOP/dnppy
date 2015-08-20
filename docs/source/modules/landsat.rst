landsat
=======

.. automodule:: dnppy.landsat
    :members:

Examples
--------

.. rubric:: Accessing Landsat metadata

Sometimes you need to access landsat metadata from its MTL file in a programmatic fashion. We have a class for that, called ``landsat_metadata``. This class exists almost entirely for its attributes, which are built from an input MTL file quite easily.

Here is some example syntax for delcaring the object, exploring attributes, and accessing specific attributes.

.. code-block:: python

    from dnppy import landsat
    meta = landsat.landsat_metadata(my_MTL_filepath) # create object

    from pprint import pprint                        # import pprint
    pprint(vars(m))                                  # pretty print output
    scene_id = meta.LANDSAT_SCENE_ID                 # access specific attribute

You can read more about ``landsat_metadata`` in the code help below!


.. rubric:: Converting to Top-of-Atmosphere Reflectance

Raw Landsat data comes in a collection of tiff files that whose values (Digital Numbers) are on a 8-bit (Landsat 4, 5, and 7) or 16-bit (Landsat 8) scale. These tiffs often need to be converted to reflectance values, such that each pixel represents the proportion of radiation, scaled from 0 to 1, in that band's bandwidth that is reflected. Note that this includes atmospheric conditions that may be responsible for reflecting a portion of that radiation. Processing these data is now very easy in dnppy, as shown in the code below. First, import the landsat module from dnppy. Then, type in the command landsat.toa_reflectance_457 or landsat.toa_reflectance_8. The first parameter to fill out is the list of band numbers you wish to convert, which should be entered as [1,2,3,4,5,7] for example. The second parameter is the file path to the Landsat scene's metadata file, which ends in _MTL.txt. The last parameter, which is optional, is the directory you wish to deposit the output tiffs in. If left out, the output tiffs will be placed in the same folder as the input data. Now just close the parentheses and execute the command to convert the data.

.. code-block:: python

    from dnppy import landsat

    band_nums = [1,2,3,4,5,7]
    meta_path = r"C:\folder\LE70410362002335EDC00\LE70410362002335EDC00_MTL.txt"
    outdir = r"C:\folder\output"

    landsat.toa_reflectance_457(band_nums, meta_path, outdir)


Code Help
---------

Auto-documentation for functions and classes within this module is generated below!

.. automodule:: dnppy.landsat.atsat_bright_temp
    :members:

.. automodule:: dnppy.landsat.cloud_mask
    :members:

.. automodule:: dnppy.landsat.grab_meta
    :members:

.. automodule:: dnppy.landsat.ndvi
    :members:

.. automodule:: dnppy.landsat.surface_reflectance
    :members:

.. automodule:: dnppy.landsat.surface_temp
    :members:

.. automodule:: dnppy.landsat.toa_radiance
    :members:

.. automodule:: dnppy.landsat.toa_reflectance
    :members:
