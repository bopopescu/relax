###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""Functions for manipulating NMR-STAR dictionary data."""


def translate(data):
    """Translate all None values into the '?' string.

    @param data:    The data to translate.
    @type data:     anything
    """

    # List data.
    if type(data) == list:
        # Loop over the data.
        for i in range(len(data)):
            if data[i] == None or data[i] == 'None':
                data[i] = '?'

    # None.
    if data == None:
        data = '?'

    # Return the translated result.
    return data
