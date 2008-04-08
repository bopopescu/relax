###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
"""Module containing all physical constants used in relax, as well as all associated functions."""


# Python module imports.
from math import pi

# relax module imports.
from relax_errors import RelaxError


# Misc. constants.
##################

h = 6.62606876 * 1e-34
"""Planck's constant."""

h_bar = h / (2.0 * pi)
"""Dirac's constant."""

mu0 = 4.0 * pi * 1e-7
"""The magnetic constant or the permeability of vacuum."""


# CSA and bond lengths.
#######################

N15_CSA = -172 * 1e-6
"""The 15N CSA in the NH bond (default value)."""

NH_BOND_LENGTH = 1.02 * 1e-10
"""The length of the NH bond (default value)."""


# Gyromagnetic ratios.
######################

g13C = 6.728 * 1e7
"""The 13C gyromagnetic ratio."""

g1H = 26.7522212 * 1e7
"""The 1H gyromagnetic ratio."""

g15N = -2.7126 * 1e7
"""The 15N gyromagnetic ratio."""

g17O = -3.628 * 1e7
"""The 17O gyromagnetic ratio."""

g31P = 10.841 * 1e7
"""The 31P gyromagnetic ratio."""

# Function for returning the desired gyromagnetic ratio.
def return_gyromagnetic_ratio(nucleus=None):
    """Return the gyromagnetic ratio for the given nucleus type.
 
    @keyword nucleus:   The nucleus type.
    @type nucleus:      str
    @raises RelaxError: If the nucleus type is unknown.           
    @returns:           The desired gyromagnetic ratio.
    @rtype:             float
    """

    # Matching loop.
    if nucleus == '13C':
        return g13C
    elif nucleus == '1H':
        return g1H
    elif nucleus == '15N':
        return g15N
    elif nucleus == '17O':
        return g17O
    elif nucleus == '31P':
        return g31P
    else:
        raise RelaxError, "The nucleus type " + `nucleus` + " is unknown."


# Relative atomic masses.
#########################

ArH = 1.00794
"""Proton atomic mass."""

ArC = 12.0107
"""Carbon atomic mass."""

ArN = 14.0067
"""Nitrogen atomic mass."""

ArO = 15.9994
"""Oxygen atomic mass."""

ArS = 32.065
"""Sulphur atomic mass."""


# Function for returning the desired atomic mass.
def return_atomic_mass(element=None):
    """Return the atomic mass for the given element type.

    @keyword element:   The element type.
    @type element:      str
    @raises RelaxError: If the element type is unknown.           
    @returns:           The desired atomic mass.
    @rtype:             float
    """

    # Protons, deuterons.
    if element == 'H':
        return ArH
    if element == '1H':
        return 1.0
    if element == '2H':
        return 2.0

    # Carbons.
    if element == 'C':
        return ArC
    if element == '12C':
        return 12.0
    if element == '13C':
        return 13.0

    # Nitrogens.
    if element == 'N':
        return ArN
    if element == '14N':
        return 14.0
    if element == '15N':
        return 15.0

    # Oxygens.
    if element == 'O':
        return ArO
    if element == '16O':
        return 16.0
    if element == '17O':
        return 17.0

    # Sulphurs.
    if element == 'S':
        return ArS

    # Unknown mass.
    raise RelaxError, "The mass of the element " + `element` + " has not yet been programmed into relax."
