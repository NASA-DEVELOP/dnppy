.. dnppy documentation master file, created by
   sphinx-quickstart on Tue Aug 04 11:29:04 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the dnppy documentation page!
========================================

The DEVELOP national program python package (dnppy) is as a living codebase for the `NASA DEVELOP National Program`_, our project partners, and the GIS programming community! DEVELOP is under NASA's Applied Sciences program, and functions to build capacity its participants and its partners in earth science and remote sensing.

*We try to take a very instructional approach to both user and developer documentation within these pages that assumes a low level of pre-existing knowledge.*
*Novice python users should check out our* :doc:`Python quick-start guide <trub/pythonstarter>` *if some of the terminology used throughout seems unclear*



dnppy was created to improve institutional knowledge retention, open the DEVELOP toolkit for public contributions and use, represent DEVELOP in the public domain, and put more power in the hands of new participants the first day the walk into the program. It is a social media, programming capacity building, and educational endeavor.

Contents
--------

.. toctree::
    :name: Getting Started
    :maxdepth: 2

    overview
    install
    design
    modulesum

.. toctree::
    :name: Modules
    :maxdepth: 2

    modules/convert
    modules/core
    modules/download
    modules/landsat
    modules/modis
    modules/radar
    modules/raster
    modules/solar
    modules/textio
    modules/tsa

.. toctree::
    :name: Developers

    dev_pages/development
    dev_pages/dev_goals
    dev_pages/gdal_tips
    dev_pages/contrib_git
    dev_pages/doc


.. toctree::
    :name: Help and Reference

    trub/git
    trub/pythonstarter
    trub/faq

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Note from the Author
--------------------

The DEVELOP program is a great program, and is that way because of its great participants. I came in as a Fall 2013 participant with a background in aerospace engineering and exposure to image analysis with a method called particle image velocimetry for use in wind tunnels. I had very little knowledge of GIS, earth science, climate science, agronomy, hydrology, geology, or the type of remote sensing done via satellite, but I wanted to learn. I was not a very good programmer. The environment I was exposed to with DEVELOP allowed me to sponge up a fraction of the immense knowledge of my peers from all sorts of disciplines, and I soon realized the importance of good programming in the community as a whole.

Firstly, DEVELOP expects participants to come in, learn about a topic, plan an analysis, and produce results in 10 weeks. I am continuously impressed with the achievements of the DEVELOP cohort, and the frequency with which they meet challenging objectives. Performing an analysis is one thing, but creating software tools for partners and end users to repeat that analysis is something else entirely. With the growing number of freely available earth observation data sources, analyses are growing more complex. Secondly, project partners who come to us often reveal that some of their largest stumbling blocks to using NASA data products are actually quite simple for a programmer to solve. For some, an entire new world can be opened up with the simple ability to mass extract data from an HDF5 or a NetCDF and take some statistics. All they need is the right introduction to the right tools. There clearly exists an opportunity to improve the industry with better software tools that can be learned and implemented quickly.

So, between September 2014 and August 2015, I worked to improve my programming skills to meet the professional standard (which I continue to do). Over a period of nine months, I've worked as part of a team of Geoinformatics Fellows to conceptualize and realize dnppy. It has been a very rewarding and exciting experience for me.

This package is still early in its life, and supports a small fraction of the NASA data types we would like to support. Hopefully, the members of the community will adopt it as their own and continue to find it useful and improve upon it. If you are a student or recent graduate using this package, I encourage you to take a look at the NASA DEVELOP program and consider applying. If you look at some of this code in disgust and anguish at some foolish design choice we've made, or see potential for improvement, we welcome your feedback and contributions through GitHub.

Special thanks to Geoinformatics Fellow team of 2015: Daniel Jensen, Lance Watkins, Amber Brooks

`Jeff Ely`_, August 2015

.. _NASA DEVELOP National Program: http://develop.larc.nasa.gov/
.. _Jeff Ely: https://github.com/Jwely