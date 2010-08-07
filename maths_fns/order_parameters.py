###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful;                    #
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
"""Module for the conversion of order parameters to specific model parameters and vice versa."""

# Python module imports.
from math import cos


def iso_cone_theta_to_S(theta):
    """Convert the isotropic cone angle to the order parameter S.

    This uses Woessner's diffusion in a cone order parameter defined as::

        S = 1/2 (1 + cos(theta)) * cos(theta)

    @param theta:   The isotropic cone angle.
    @type theta:    float
    @return:        The order parameter value.
    @rtype:         float
    """

    # Convert.
    S = 0.5 * (1.0 + cos(theta)) * cos(theta)

    # Return the order parameter.
    return S


def iso_cone_S_to_cos_theta(S):
    """Convert the isotropic cone order parameter S into the cosine of the cone angle.

    @param S:   The order parameter value (not squared).
    @type S:    float
    @return:    The value of cos(theta).
    @rtype:     float
    """

    # Convert.
    cos_theta = S

    # Return cos(theta).
    return cos_theta
