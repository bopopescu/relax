###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2009 Edward d'Auvergne                            #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing the 'vmd' user function class for controlling VMD."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from base_class import User_fn_class
import check
from generic_fns import vmd


class Vmd(User_fn_class):
    """Class for interfacing with VMD."""

    def view(self):
        """Function for viewing the collection of molecules extracted from the PDB file.

        Example
        ~~~~~~~

        relax> vmd.view()
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "vmd.view()"
            print(text)

        # Execute the functional code.
        vmd.view()
