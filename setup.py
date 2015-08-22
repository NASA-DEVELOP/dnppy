""" installs dnppy """


# sets up dependencies that pip alone seems to frequently fail at.
import install_dependencies
install_dependencies.main()

# standard setup
from distutils.core import setup
from setuptools import find_packages

setup(name='dnppy',
      version='1.15.3b0',
      description='DEVELOP National Program Python Package',
      author=["Jwely",
              "djjensen",
              "Syntaf",
              "lancewatkins",
              "lmakely",
              "qgeddes",
              "Scott Baron",
              ],
      author_email='jeff.ely.08@gmail.com',
      url='https://github.com/NASA-DEVELOP/dnppy',
      download_url = "https://github.com/NASA-DEVELOP/dnppy/archive/master.zip",
      packages=find_packages(),
      include_package_data = True,
     )


# quick setup that will work locally by running this script
if __name__ == "__main__":
    import pip
    # pip.main(["install", "--upgrade", "https://github.com/NASA-DEVELOP/dnppy/archive/setup.zip"])
    pip.main(["install", "--upgrade", "dnppy"])