"""
======================================================================================
                                   dnppy.core
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

It contains some core functions to assist in data formatting , path manipulation, and
logical checks. It is commonly called by other modules in the dnppy package.


 Requirements:
   Python 2.7
   Arcmap 10.2 or newer for some functions

   Example:
   from dnppy import core
   core.function_name(args)
"""

__author__ = ["Jeffry Ely, jwely, jeff.ely.08@gmail.com",
              "Lauren Makely, lmakely, lmakely09@gmail.com"]

# local imports
from check_module import *
from create_outname import *
from del_empty_dirs import *
from enf_featlist import *
from enf_filelist import *
from enf_list import *
from exists import *
from list_files import *
from move import *
from rename import *
