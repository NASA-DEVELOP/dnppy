"""
setup installer for dnppy.
"""

# sets up dependencies that pip alone seems to frequently fail at.
import install_dependencies
install_dependencies.main()

# standard setup
from distutils.core import setup

setup(
    name='dnppy',
    version='1.15.3b2',
    packages=['dnppy',
              'dnppy.convert',
              'dnppy.core',
              'dnppy.download',
              'dnppy.landsat',
              'dnppy.modis',
              'dnppy.radar',
              'dnppy.raster',
              'dnppy.solar',
              'dnppy.textio',
              'dnppy.tsa'],
    url='https://github.com/NASA-DEVELOP/dnppy',
    download_url="https://github.com/NASA-DEVELOP/dnppy/archive/master.zip",
    license='NASA OPEN SOURCE AGREEMENT VERSION 1.3',
    author=["Jwely",
            "djjensen",
            "Syntaf",
            "lancewatkins",
            "lmakely",
            "qgeddes",
            "Scott Baron",
            ],
    author_email='',
    description='DEVELOP National Program python package',
    package_data={'dnppy.convert' : ['lib/datatype_library.csv',
                                     'lib/prj/*'],
                  'dnppy.landsat' : ['metadata/*'],
                  'dnppy.solar'   : ['ref/*'],
                  'dnppy.textio'  : ['test_data/*'],
                  'dnppy.tsa'     : ['test_data/*']},
    include_package_data=True
)