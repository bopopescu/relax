###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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

from math import cos, pi, sin
from Numeric import Float64, array


class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the macro for setting up the diffusion tensor."""

        self.relax = relax


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        names = [ 'diff_type',
                  'diff_params' ]

        return names


    def set(self, run, params, time_scale, d_scale, angle_units, param_types, fixed):
        """Function for setting up the diffusion tensor."""

        # Arguments.
        self.run = run
        self.params = params
        self.time_scale = time_scale
        self.d_scale = d_scale
        self.angle_units = angle_units
        self.param_types = param_types

        # Test if the run already exists.
        if self.relax.data.diff.has_key(run):
            raise RelaxRunError, run

        # Add the run to the diffusion tensor data structure.
        self.relax.data.diff.add_item(run)

        # Add the run to the runs list.
        if not run in self.relax.data.runs:
            self.relax.data.runs.append(run)

        # Set the fixed flag.
        self.relax.data.diff[run].fixed = fixed

        # Isotropic diffusion.
        if type(params) == float:
            self.isotropic()

        # Axially symmetric anisotropic diffusion.
        elif len(params) == 4:
            self.axial()

        # Fully anisotropic diffusion.
        elif len(params) == 6:
            self.anisotropic()


    def anisotropic(self):
        """Function for setting up fully anisotropic diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'iso'

        raise RelaxError, "Fully anisotropic diffusion not coded yet."


    def axial(self):
        """Function for setting up axially symmetric diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'axial'

        # (Dpar, Dper, theta, phi).
        if self.param_types == 0:
            # Unpack the tuple.
            Dpar, Dper, theta, phi = self.params

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Dpar = Dpar * self.d_scale
            self.relax.data.diff[self.run].Dper = Dper * self.d_scale
            self.relax.data.diff[self.run].Diso = (Dpar + 2.0 * Dper) * self.d_scale / 3.0
            self.relax.data.diff[self.run].Dratio = Dpar / Dper

            # Correlation times:  tm, t1, t2, t3.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # (tm, Dratio, theta, phi).
        elif self.param_types == 1:
            # Unpack the tuple.
            tm, Dratio, theta, phi = self.params

            # Diffusion tensor eigenvalues: Dpar, Dper, Diso, Dratio.
            self.relax.data.diff[self.run].Diso = 6.0 / (tm * self.time_scale)
            self.relax.data.diff[self.run].Dratio = Dratio * self.d_scale
            self.relax.data.diff[self.run].Dpar = 3.0 * self.relax.data.diff[self.run].Diso * self.relax.data.diff[self.run].Dratio / (2.0 - self.relax.data.diff[self.run].Dratio)
            self.relax.data.diff[self.run].Dper = 3.0 * self.relax.data.diff[self.run].Diso / (2.0 - self.relax.data.diff[self.run].Dratio)

            # Global correlation time:  tm.
            self.relax.data.diff[self.run].tm = tm * self.time_scale

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', param_types)

        # Correlation times:  t1, t2, t3.
        self.relax.data.diff[self.run].t1 = 1.0 / (6.0 * self.relax.data.diff[self.run].Dper)
        self.relax.data.diff[self.run].t2 = 1.0 / (5.0 * self.relax.data.diff[self.run].Dper + self.relax.data.diff[self.run].Dpar)
        self.relax.data.diff[self.run].t3 = 1.0 / (2.0 * self.relax.data.diff[self.run].Dper + 4.0 * self.relax.data.diff[self.run].Dpar)

        # Angles in radians.
        if self.angle_units == 'deg':
            self.relax.data.diff[self.run].theta = (theta / 360.0) * 2.0 * pi
            self.relax.data.diff[self.run].phi = (phi / 360.0) * 2.0 * pi
        else:
            self.relax.data.diff[self.run].theta = theta
            self.relax.data.diff[self.run].phi = phi

        # Unit symmetry axis vector.
        x = cos(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        y = sin(self.relax.data.diff[self.run].theta) * sin(self.relax.data.diff[self.run].phi)
        z = cos(self.relax.data.diff[self.run].phi)
        self.relax.data.diff[self.run].axis_unit = array([x, y, z], Float64)

        # Full symmetry axis vector.
        self.relax.data.diff[self.run].axis_vect = self.relax.data.diff[self.run].Dpar * self.relax.data.diff[self.run].axis_unit


    def isotropic(self):
        """Function for setting up isotropic diffusion."""

        # The diffusion type.
        self.relax.data.diff[self.run].type = 'iso'

        # tm.
        if self.param_types == 0:
            # Correlation times.
            self.relax.data.diff[self.run].tm = self.params * self.time_scale

            # Diffusion tensor eigenvalues.
            self.relax.data.diff[self.run].Diso = 6.0 / self.relax.data.diff[self.run].tm

        # Diso
        elif self.param_types == 1:
            # Diffusion tensor eigenvalues.
            self.relax.data.diff[self.run].Diso = self.params * self.d_scale

            # Correlation times.
            self.relax.data.diff[self.run].tm = 1.0 / (6.0 * self.relax.data.diff[self.run].Diso)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('param_types', self.param_types)
