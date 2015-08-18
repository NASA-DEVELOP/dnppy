GitHub Best Practices
=====================

A basic understanding of Git is key to expanding dnppy, as it is with many other large software packages such as `numpy`_,  `scipy`_,  `gdal`_ and others you may be familiar with. If you'd like an introduction to git, checkout :doc:`Git Basics <../trub/git>`. There are are a small set of best practices that should be employed where possible.

What to include in a Git repo
-----------------------------

There are certain files that you might want to store near your development environment, but that you do not want to upload to your repository. Git uses a special file called ``.gitignore`` that can be used to ignore specific files or directories in a repository, which allows them to peacefully exist in your local repository without tracking their changes and updating them in the origin on GitHubs website. The .gitignore for dnppy is already set up to ignore several files by name, as well as several files by extension such as ``.pyc's``.

Things to include in your repository:
    * Any kind of raw text or code. Tracking changes in text is what git was built for!
    * Helpful description files such as ``README.md`` that can be interpreted by GitHub and displayed while browsing.
    * Small static assets or images that are helpful for documentation purposes that do not frequently change.

Things to omit from your git repository
    * Raster data! you never ever want to include raster data in your online repository, as this data will then be permanently included in your git and dramatically decrease performance in every aspect.
    * Any kind of fairly constant binary data that github cannot interpret as text. These types of files are best stored in the release assets independent from repository tracking.


Committing to the ``master`` branch
-----------------------------------

We typically direct people to simply download the most recent version of the master branch. As a general rule, the master branch should always be "deployable", meaning it should work reliably.

    * Simple bug fixes can be committed directly to the master branch.
    * Commits in which changes to documentation, docstrings, or comments to improve clarity, but preserve function can be committed directly to the master branch.

When adding some kind of new functionality, you should always create a new branch for development and testing. When you are satisfied with the new additions, you can then merge that branch with the master branch with a pull request. Learn more about the `GitHub Flow`_

.. _GitHub Flow: https://guides.github.com/introduction/flow/


.. note:: We started out as noobs, and did not institute proper git workflow with dnppy from the beginning. Nothing terrible happened, but some things were more difficult than they would have been otherwise. Just do your best, and learn as much as you can!


Versioning
----------
We expect that a new version should be always be released immediately after, and sometimes immediately before every DEVELOP term. This is due in part to the inclusion of the ``undeployed/proj_code`` folder and the fact that it needs to be made available for project partners very quickly.

.. rubric:: version numbers

The numbering is pretty simple, and takes the format of

    ``major_revision.two_digit_year.minor_revision``

The major revision is reserved for very large changes. When dnppy reaches complete ``arcpy`` independence, an increase in the major revision number would be justified. It is difficult for us to know what future scenarios may arise, but anything that changes the major revision number should be a pretty big deal. The two digit year is a simple record keeping device to associate a version of dnppy with NASA's fiscal year, which turns over each September. The minor revision is the smallest revision increment for the year, and should just go up every time there is a revision change worth changing the number over.

Example revision schedule:
    * ``dnppy 1.16.1`` Fall 2015, at the beginning of FY16
    * ``dnppy 1.16.2`` Miscellaneous update that required new version number
    * ``dnppy 1.16.3`` Fall 2015, end of the term update with new proj_code for partners
    * ``dnppy 1.16.4`` Spring 2016, mid term fixes of something
    * ``dnppy 1.16.5`` Sprint 2016, end of the term update with new proj_code for partners
    * ...
    * ``dnppy 1.17.1`` Fall 2016, beginning of FY17

.. _numpy: https://github.com/numpy/numpy
.. _scipy: https://github.com/scipy/scipy
.. _gdal: https://github.com/OSGeo/gdal