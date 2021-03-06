###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Script for generating the distribution of PDB structures."""

# Modify the system path to load the base module.
import sys
sys.path.append('..')

# Python module imports.
from math import pi
from numpy import dot, transpose

# relax module imports.
from lib.geometry.angles import wrap_angles
from lib.geometry.rotations import R_random_hypersphere, R_to_tilt_torsion

# Base module import.
from generate_base import Main


class Generate(Main):
    # The number of structures.
    N = 1000000

    # Cone parameters.
    THETA_MAX = 1.3
    SIGMA_MAX = 0.1 * 2.0 * pi / 360.0

    def __init__(self):
        """Model specific setup."""

        # Alias the required methods.
        self.axes_to_pdb = self.axes_to_pdb_main_axis
        self.build_axes = self.build_axes_pivot_com


    def rotation(self, i, motion_index=0):
        """Set up the rotation for state i."""

        # Loop until a valid rotation matrix is found.
        while True:
            # The random rotation matrix.
            R_random_hypersphere(self.R)

            # Rotation in the eigenframe.
            R_eigen = dot(transpose(self.axes), dot(self.R, self.axes))

            # The angles.
            phi, theta, sigma = R_to_tilt_torsion(R_eigen)
            sigma = wrap_angles(sigma, -pi, pi)

            # Skip the rotation if the cone angle is violated.
            if theta > self.THETA_MAX:
                continue

            # Skip the rotation if the torsion angle is violated.
            if sigma > self.SIGMA_MAX or sigma < -self.SIGMA_MAX:
                continue

            # Rotation is ok, so stop looping.
            break


# Execute the code.
generate = Generate()
generate.run()
