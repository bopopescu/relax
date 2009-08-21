###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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
"""Module containing the Reduced Spectral Density Mapping 'jw_mapping' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from relax_errors import RelaxStrError
from specific_fns.setup import jw_mapping_obj


class Jw_mapping:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class containing functions specific to reduced spectral density mapping."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def set_frq(self, frq=None):
        """Function for selecting which relaxation data to use in the J(w) mapping.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        frq:  The spectrometer frequency in Hz.


        Description
        ~~~~~~~~~~~

        This function will select the relaxation data to use in the reduced spectral density mapping
        corresponding to the given frequency.


        Examples
        ~~~~~~~~

        relax> jw_mapping.set_frq(600.0 * 1e6)
        relax> jw_mapping.set_frq(frq=600.0 * 1e6)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "jw_mapping.set_frq("
            text = text + "frq=" + repr(frq) + ")"
            print(text)

        # The frq argument.
        if not isinstance(frq, float):
            raise RelaxStrError('frq', frq)

        # Execute the functional code.
        jw_mapping_obj.set_frq(frq=frq)
