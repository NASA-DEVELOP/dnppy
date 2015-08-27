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
    version='1.15.3b1',
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
    download_url="https://github.com/NASA-DEVELOP/dnppy/archive/1.15.3b1.zip",
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
    include_package_data=True
)