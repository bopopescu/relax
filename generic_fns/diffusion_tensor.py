###############################################################################
#                                                                             #
# Copyright (C) 2003-2007 Edward d'Auvergne                                   #
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

# Python module imports.
from copy import deepcopy
from math import cos, pi, sin
from re import search

# relax module imports.
from data import Data as relax_data_store
import pipes
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoTensorError, RelaxTensorError, RelaxUnknownParamCombError, RelaxUnknownParamError


def copy(self, run1=None, run2=None):
    """Function for copying diffusion tensor data from run1 to run2."""

    # Test if run1 exists.
    if not run1 in relax_data_store.run_names:
        raise RelaxNoPipeError, run1

    # Test if run2 exists.
    if not run2 in relax_data_store.run_names:
        raise RelaxNoPipeError, run2

    # Test if run1 contains diffusion tensor data.
    if not relax_data_store.diff.has_key(run1):
        raise RelaxNoTensorError, run1

    # Test if run2 contains diffusion tensor data.
    if relax_data_store.diff.has_key(run2):
        raise RelaxTensorError, run2

    # Copy the data.
    relax_data_store.diff[run2] = deepcopy(relax_data_store.diff[run1])


def data_names(self):
    """Function for returning a list of names of data structures associated with the sequence."""

    names = [ 'diff_type',
              'diff_params' ]

    return names


def default_value(self, param):
    """
    Diffusion tensor parameter default values
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ________________________________________________________________________
    |                        |                    |                        |
    | Data type              | Object name        | Value                  |
    |________________________|____________________|________________________|
    |                        |                    |                        |
    | tm                     | 'tm'               | 10 * 1e-9              |
    |                        |                    |                        |
    | Diso                   | 'Diso'             | 1.666 * 1e7            |
    |                        |                    |                        |
    | Da                     | 'Da'               | 0.0                    |
    |                        |                    |                        |
    | Dr                     | 'Dr'               | 0.0                    |
    |                        |                    |                        |
    | Dx                     | 'Dx'               | 1.666 * 1e7            |
    |                        |                    |                        |
    | Dy                     | 'Dy'               | 1.666 * 1e7            |
    |                        |                    |                        |
    | Dz                     | 'Dz'               | 1.666 * 1e7            |
    |                        |                    |                        |
    | Dpar                   | 'Dpar'             | 1.666 * 1e7            |
    |                        |                    |                        |
    | Dper                   | 'Dper'             | 1.666 * 1e7            |
    |                        |                    |                        |
    | Dratio                 | 'Dratio'           | 1.0                    |
    |                        |                    |                        |
    | alpha                  | 'alpha'            | 0.0                    |
    |                        |                    |                        |
    | beta                   | 'beta'             | 0.0                    |
    |                        |                    |                        |
    | gamma                  | 'gamma'            | 0.0                    |
    |                        |                    |                        |
    | theta                  | 'theta'            | 0.0                    |
    |                        |                    |                        |
    | phi                    | 'phi'              | 0.0                    |
    |________________________|____________________|________________________|

    """

    # tm.
    if param == 'tm':
        return 10.0 * 1e-9

    # Diso, Dx, Dy, Dz, Dpar, Dper.
    elif param == 'Diso' or param == 'Dx' or param == 'Dy' or param == 'Dz' or param == 'Dpar' or param == 'Dper':
        return 1.666 * 1e7

    # Dratio.
    elif param == 'Dratio':
        return 1.0


def delete(self, run=None):
    """Function for deleting diffusion tensor data."""

    # Test if the run exists.
    if not run in relax_data_store.run_names:
        raise RelaxNoPipeError, run

    # Test if diffusion tensor data for the run exists.
    if not relax_data_store.diff.has_key(run):
        raise RelaxNoTensorError, run

    # Delete the diffusion data.
    del(relax_data_store.diff[run])

    # Clean up the runs.
    self.relax.generic.runs.eliminate_unused_runs()


def diff_data_exists():
    """Function for determining if diffusion data exists in the current data pipe.

    @return:        The answer to the question.
    @type return:   bool
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # White list objects.
    white_list = []

    # Loop over the objects in the data structure.
    for name in dir(cdp.diff_tensor):
        # White list names.
        if name in white_list:
            continue

        # Data exists.
        return True

    # No data.
    return False


def display(self, run=None):
    """Function for displaying the diffusion tensor."""

    # Test if the run exists.
    if not run in relax_data_store.run_names:
        raise RelaxNoPipeError, run

    # Test if diffusion tensor data for the run exists.
    if not relax_data_store.diff.has_key(run):
        raise RelaxNoTensorError, run

    # Spherical diffusion.
    if relax_data_store.diff[run].type == 'sphere':
        # Tensor type.
        print "Type:  Spherical diffusion"

        # Parameters.
        print "\nParameters {tm}."
        print "tm (s):  " + `relax_data_store.diff[run].tm`

        # Alternate parameters.
        print "\nAlternate parameters {Diso}."
        print "Diso (1/s):  " + `relax_data_store.diff[run].Diso`

        # Fixed flag.
        print "\nFixed:  " + `relax_data_store.diff[run].fixed`

    # Spheroidal diffusion.
    elif relax_data_store.diff[run].type == 'spheroid':
        # Tensor type.
        print "Type:  Spheroidal diffusion"

        # Parameters.
        print "\nParameters {tm, Da, theta, phi}."
        print "tm (s):  " + `relax_data_store.diff[run].tm`
        print "Da (1/s):  " + `relax_data_store.diff[run].Da`
        print "theta (rad):  " + `relax_data_store.diff[run].theta`
        print "phi (rad):  " + `relax_data_store.diff[run].phi`

        # Alternate parameters.
        print "\nAlternate parameters {Diso, Da, theta, phi}."
        print "Diso (1/s):  " + `relax_data_store.diff[run].Diso`
        print "Da (1/s):  " + `relax_data_store.diff[run].Da`
        print "theta (rad):  " + `relax_data_store.diff[run].theta`
        print "phi (rad):  " + `relax_data_store.diff[run].phi`

        # Alternate parameters.
        print "\nAlternate parameters {Dpar, Dper, theta, phi}."
        print "Dpar (1/s):  " + `relax_data_store.diff[run].Dpar`
        print "Dper (1/s):  " + `relax_data_store.diff[run].Dper`
        print "theta (rad):  " + `relax_data_store.diff[run].theta`
        print "phi (rad):  " + `relax_data_store.diff[run].phi`

        # Alternate parameters.
        print "\nAlternate parameters {tm, Dratio, theta, phi}."
        print "tm (s):  " + `relax_data_store.diff[run].tm`
        print "Dratio:  " + `relax_data_store.diff[run].Dratio`
        print "theta (rad):  " + `relax_data_store.diff[run].theta`
        print "phi (rad):  " + `relax_data_store.diff[run].phi`

        # Fixed flag.
        print "\nFixed:  " + `relax_data_store.diff[run].fixed`

    # Ellipsoidal diffusion.
    elif relax_data_store.diff[run].type == 'ellipsoid':
        # Tensor type.
        print "Type:  Ellipsoidal diffusion"

        # Parameters.
        print "\nParameters {tm, Da, Dr, alpha, beta, gamma}."
        print "tm (s):  " + `relax_data_store.diff[run].tm`
        print "Da (1/s):  " + `relax_data_store.diff[run].Da`
        print "Dr:  " + `relax_data_store.diff[run].Dr`
        print "alpha (rad):  " + `relax_data_store.diff[run].alpha`
        print "beta (rad):  " + `relax_data_store.diff[run].beta`
        print "gamma (rad):  " + `relax_data_store.diff[run].gamma`

        # Alternate parameters.
        print "\nAlternate parameters {Diso, Da, Dr, alpha, beta, gamma}."
        print "Diso (1/s):  " + `relax_data_store.diff[run].Diso`
        print "Da (1/s):  " + `relax_data_store.diff[run].Da`
        print "Dr:  " + `relax_data_store.diff[run].Dr`
        print "alpha (rad):  " + `relax_data_store.diff[run].alpha`
        print "beta (rad):  " + `relax_data_store.diff[run].beta`
        print "gamma (rad):  " + `relax_data_store.diff[run].gamma`

        # Alternate parameters.
        print "\nAlternate parameters {Dx, Dy, Dz, alpha, beta, gamma}."
        print "Dx (1/s):  " + `relax_data_store.diff[run].Dx`
        print "Dy (1/s):  " + `relax_data_store.diff[run].Dy`
        print "Dz (1/s):  " + `relax_data_store.diff[run].Dz`
        print "alpha (rad):  " + `relax_data_store.diff[run].alpha`
        print "beta (rad):  " + `relax_data_store.diff[run].beta`
        print "gamma (rad):  " + `relax_data_store.diff[run].gamma`

        # Fixed flag.
        print "\nFixed:  " + `relax_data_store.diff[run].fixed`


def ellipsoid(self):
    """Function for setting up ellipsoidal diffusion."""

    # The diffusion type.
    cdp.diff_tensor.type = 'ellipsoid'

    # (tm, Da, Dr, alpha, beta, gamma).
    if self.param_types == 0:
        # Unpack the tuple.
        tm, Da, Dr, alpha, beta, gamma = self.params

        # Scaling.
        tm = tm * self.time_scale
        Da = Da * self.d_scale

        # Set the parameters.
        self.set(run=self.run, value=[tm, Da, Dr], param=['tm', 'Da', 'Dr'])

    # (Diso, Da, Dr, alpha, beta, gamma).
    elif self.param_types == 1:
        # Unpack the tuple.
        Diso, Da, Dr, alpha, beta, gamma = self.params

        # Scaling.
        Diso = Diso * self.d_scale
        Da = Da * self.d_scale

        # Set the parameters.
        self.set(run=self.run, value=[Diso, Da, Dr], param=['Diso', 'Da', 'Dr'])

    # (Dx, Dy, Dz, alpha, beta, gamma).
    elif self.param_types == 2:
        # Unpack the tuple.
        Dx, Dy, Dz, alpha, beta, gamma = self.params

        # Scaling.
        Dx = Dx * self.d_scale
        Dy = Dy * self.d_scale
        Dz = Dz * self.d_scale

        # Set the parameters.
        self.set(run=self.run, value=[Dx, Dy, Dz], param=['Dx', 'Dy', 'Dz'])

    # Unknown parameter combination.
    else:
        raise RelaxUnknownParamCombError, ('param_types', self.param_types)

    # Convert the angles to radians.
    if self.angle_units == 'deg':
        alpha = (alpha / 360.0) * 2.0 * pi
        beta = (beta / 360.0) * 2.0 * pi
        gamma = (gamma / 360.0) * 2.0 * pi

    # Set the orientational parameters.
    self.set(run=self.run, value=[alpha, beta, gamma], param=['alpha', 'beta', 'gamma'])


def fold_angles(self, run=None, sim_index=None):
    """Wrap the Euler or spherical angles and remove the glide reflection and translational symmetries.

    Wrap the angles such that

        0 <= theta <= pi,
        0 <= phi <= 2pi,

    and

        0 <= alpha <= 2pi,
        0 <= beta <= pi,
        0 <= gamma <= 2pi.


    For the simulated values, the angles are wrapped as

        theta - pi/2 <= theta_sim <= theta + pi/2
        phi - pi <= phi_sim <= phi + pi

    and

        alpha - pi <= alpha_sim <= alpha + pi
        beta - pi/2 <= beta_sim <= beta + pi/2
        gamma - pi <= gamma_sim <= gamma + pi
    """

    # Arguments.
    self.run = run


    # Wrap the angles.
    ##################

    # Spheroid.
    if cdp.diff_tensor.type == 'spheroid':
        # Get the current angles.
        theta = cdp.diff_tensor.theta
        phi = cdp.diff_tensor.phi

        # Simulated values.
        if sim_index != None:
            theta_sim = cdp.diff_tensor.theta_sim[sim_index]
            phi_sim   = cdp.diff_tensor.phi_sim[sim_index]

        # Normal value.
        if sim_index == None:
            cdp.diff_tensor.theta = self.relax.generic.angles.wrap_angles(theta, 0.0, pi)
            cdp.diff_tensor.phi = self.relax.generic.angles.wrap_angles(phi, 0.0, 2.0*pi)

        # Simulated theta and phi values.
        else:
            cdp.diff_tensor.theta_sim[sim_index] = self.relax.generic.angles.wrap_angles(theta_sim, theta - pi/2.0, theta + pi/2.0)
            cdp.diff_tensor.phi_sim[sim_index]   = self.relax.generic.angles.wrap_angles(phi_sim, phi - pi, phi + pi)

    # Ellipsoid.
    elif cdp.diff_tensor.type == 'ellipsoid':
        # Get the current angles.
        alpha = cdp.diff_tensor.alpha
        beta  = cdp.diff_tensor.beta
        gamma = cdp.diff_tensor.gamma

        # Simulated values.
        if sim_index != None:
            alpha_sim = cdp.diff_tensor.alpha_sim[sim_index]
            beta_sim  = cdp.diff_tensor.beta_sim[sim_index]
            gamma_sim = cdp.diff_tensor.gamma_sim[sim_index]

        # Normal value.
        if sim_index == None:
            cdp.diff_tensor.alpha = self.relax.generic.angles.wrap_angles(alpha, 0.0, 2.0*pi)
            cdp.diff_tensor.beta  = self.relax.generic.angles.wrap_angles(beta, 0.0, 2.0*pi)
            cdp.diff_tensor.gamma = self.relax.generic.angles.wrap_angles(gamma, 0.0, 2.0*pi)

        # Simulated alpha, beta, and gamma values.
        else:
            cdp.diff_tensor.alpha_sim[sim_index] = self.relax.generic.angles.wrap_angles(alpha_sim, alpha - pi, alpha + pi)
            cdp.diff_tensor.beta_sim[sim_index]  = self.relax.generic.angles.wrap_angles(beta_sim, beta - pi, beta + pi)
            cdp.diff_tensor.gamma_sim[sim_index] = self.relax.generic.angles.wrap_angles(gamma_sim, gamma - pi, gamma + pi)


    # Remove the glide reflection and translational symmetries.
    ###########################################################

    # Spheroid.
    if cdp.diff_tensor.type == 'spheroid':
        # Normal value.
        if sim_index == None:
            # Fold phi inside 0 and pi.
            if cdp.diff_tensor.phi >= pi:
                cdp.diff_tensor.theta = pi - cdp.diff_tensor.theta
                cdp.diff_tensor.phi = cdp.diff_tensor.phi - pi

        # Simulated theta and phi values.
        else:
            # Fold phi_sim inside phi-pi/2 and phi+pi/2.
            if cdp.diff_tensor.phi_sim[sim_index] >= cdp.diff_tensor.phi + pi/2.0:
                cdp.diff_tensor.theta_sim[sim_index] = pi - cdp.diff_tensor.theta_sim[sim_index]
                cdp.diff_tensor.phi_sim[sim_index]   = cdp.diff_tensor.phi_sim[sim_index] - pi
            elif cdp.diff_tensor.phi_sim[sim_index] <= cdp.diff_tensor.phi - pi/2.0:
                cdp.diff_tensor.theta_sim[sim_index] = pi - cdp.diff_tensor.theta_sim[sim_index]
                cdp.diff_tensor.phi_sim[sim_index]   = cdp.diff_tensor.phi_sim[sim_index] + pi

    # Ellipsoid.
    elif cdp.diff_tensor.type == 'ellipsoid':
        # Normal value.
        if sim_index == None:
            # Fold alpha inside 0 and pi.
            if cdp.diff_tensor.alpha >= pi:
                cdp.diff_tensor.alpha = cdp.diff_tensor.alpha - pi

            # Fold beta inside 0 and pi.
            if cdp.diff_tensor.beta >= pi:
                cdp.diff_tensor.alpha = pi - cdp.diff_tensor.alpha
                cdp.diff_tensor.beta = cdp.diff_tensor.beta - pi

            # Fold gamma inside 0 and pi.
            if cdp.diff_tensor.gamma >= pi:
                cdp.diff_tensor.alpha = pi - cdp.diff_tensor.alpha
                cdp.diff_tensor.beta = pi - cdp.diff_tensor.beta
                cdp.diff_tensor.gamma = cdp.diff_tensor.gamma - pi

        # Simulated theta and phi values.
        else:
            # Fold alpha_sim inside alpha-pi/2 and alpha+pi/2.
            if cdp.diff_tensor.alpha_sim[sim_index] >= cdp.diff_tensor.alpha + pi/2.0:
                cdp.diff_tensor.alpha_sim[sim_index] = cdp.diff_tensor.alpha_sim[sim_index] - pi
            elif cdp.diff_tensor.alpha_sim[sim_index] <= cdp.diff_tensor.alpha - pi/2.0:
                cdp.diff_tensor.alpha_sim[sim_index] = cdp.diff_tensor.alpha_sim[sim_index] + pi

            # Fold beta_sim inside beta-pi/2 and beta+pi/2.
            if cdp.diff_tensor.beta_sim[sim_index] >= cdp.diff_tensor.beta + pi/2.0:
                cdp.diff_tensor.alpha_sim[sim_index] = pi - cdp.diff_tensor.alpha_sim[sim_index]
                cdp.diff_tensor.beta_sim[sim_index] = cdp.diff_tensor.beta_sim[sim_index] - pi
            elif cdp.diff_tensor.beta_sim[sim_index] <= cdp.diff_tensor.beta - pi/2.0:
                cdp.diff_tensor.alpha_sim[sim_index] = pi - cdp.diff_tensor.alpha_sim[sim_index]
                cdp.diff_tensor.beta_sim[sim_index] = cdp.diff_tensor.beta_sim[sim_index] + pi

            # Fold gamma_sim inside gamma-pi/2 and gamma+pi/2.
            if cdp.diff_tensor.gamma_sim[sim_index] >= cdp.diff_tensor.gamma + pi/2.0:
                cdp.diff_tensor.alpha_sim[sim_index] = pi - cdp.diff_tensor.alpha_sim[sim_index]
                cdp.diff_tensor.beta_sim[sim_index] = pi - cdp.diff_tensor.beta_sim[sim_index]
                cdp.diff_tensor.gamma_sim[sim_index] = cdp.diff_tensor.gamma_sim[sim_index] - pi
            elif cdp.diff_tensor.gamma_sim[sim_index] <= cdp.diff_tensor.gamma - pi/2.0:
                cdp.diff_tensor.alpha_sim[sim_index] = pi - cdp.diff_tensor.alpha_sim[sim_index]
                cdp.diff_tensor.beta_sim[sim_index] = pi - cdp.diff_tensor.beta_sim[sim_index]
                cdp.diff_tensor.gamma_sim[sim_index] = cdp.diff_tensor.gamma_sim[sim_index] + pi


def init(params=None, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, spheroid_type=None, fixed=1):
    """Function for initialising the diffusion tensor.

    @param params:          The diffusion tensor parameters.
    @type params:           float
    @param time_scale:      The correlation time scaling value.
    @type time_scale:       float
    @param d_scale:         The diffusion tensor eigenvalue scaling value.
    @type d_scale:          float
    @param angle_units:     The units for the angle parameters.
    @type angle_units:      str (either 'deg' or 'rad')
    @param param_types:     The type of parameters supplied.  For spherical diffusion, the flag
                            values correspond to 0: tm, 1: Diso.  For spheroidal diffusion, 0: {tm,
                            Da, theta, phi}, 1: {Diso, Da, theta, phi}, 2: {tm, Dratio, theta, phi},
                            3:  {Dpar, Dper, theta, phi}, 4: {Diso, Dratio, theta, phi}.  For
                            ellipsoidal diffusion, 0: {tm, Da, Dr, alpha, beta, gamma}, 1: {Diso,
                            Da, Dr, alpha, beta, gamma}, 2: {Dx, Dy, Dz, alpha, beta, gamma}.
    @type param_types:      int
    @param spheroid_type:   A string which, if supplied together with spheroid parameters, will
                            restrict the tensor to either being 'oblate' or 'prolate'.
    @type spheroid_type:    str
    @param fixed:           A flag specifying whether the diffusion tensor is fixed or can be
                            optimised.
    @type fixed:            bin
    """

    # Test if the current data pipe exists.
    pipes.test(relax_data_store.current_pipe)

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if diffusion tensor data already exists.
    if not diff_data_exists():
        raise RelaxTensorError

    # Check the validity of the angle_units argument.
    valid_types = ['deg', 'rad']
    if not angle_units in valid_types:
        raise RelaxError, "The diffusion tensor 'angle_units' argument " + `angle_units` + " should be either 'deg' or 'rad'."

    # Set the fixed flag.
    cdp.diff_tensor.fixed = fixed

    # Spherical diffusion.
    if type(params) == float:
        num_params = 1
        sphere(params, time_scale, param_types)

    # Spheroidal diffusion.
    elif (type(params) == tuple or type(params) == list) and len(params) == 4:
        num_params = 4
        spheroid(params, time_scale, param_types)

    # Ellipsoidal diffusion.
    elif (type(params) == tuple or type(params) == list) and len(params) == 6:
        num_params = 6
        ellipsoid(params, time_scale, param_types)

    # Unknown.
    else:
        raise RelaxError, "The diffusion tensor parameters " + `params` + " are of an unknown type."

    # Test the validity of the parameters.
    test_params(num_params)


def map_bounds(self, run, param):
    """The function for creating bounds for the mapping function."""

    # Initialise.
    self.run = run

    # tm.
    if param == 'tm':
        return [0, 10.0 * 1e-9]

    # {Diso, Dx, Dy, Dz, Dpar, Dper}.
    if param == 'Diso' or param == 'Dx' or param == 'Dy' or param == 'Dz' or param == 'Dpar' or param == 'Dper':
        return [1e6, 1e7]

    # Da.
    if param == 'Da':
        return [-3.0/2.0 * 1e7, 3.0 * 1e7]

    # Dr.
    elif param == 'Dr':
        return [0, 1]

    # Dratio.
    elif param == 'Dratio':
        return [1.0/3.0, 3.0]

    # theta.
    elif param == 'theta':
        return [0, pi]

    # phi.
    elif param == 'phi':
        return [0, 2*pi]

    # alpha.
    elif param == 'alpha':
        return [0, 2*pi]

    # beta.
    elif param == 'beta':
        return [0, pi]

    # gamma.
    elif param == 'gamma':
        return [0, 2*pi]


def map_labels(self, run, index, params, bounds, swap, inc):
    """Function for creating labels, tick locations, and tick values for an OpenDX map."""

    # Initialise.
    labels = "{"
    tick_locations = []
    tick_values = []
    n = len(params)
    axis_incs = 5
    loc_inc = inc / axis_incs

    # Increment over the model parameters.
    for i in xrange(n):
        # Parameter conversion factors.
        factor = self.return_conversion_factor(params[swap[i]])

        # Parameter units.
        units = self.return_units(params[swap[i]])

        # Labels.
        if units:
            labels = labels + "\"" + params[swap[i]] + " (" + units + ")\""
        else:
            labels = labels + "\"" + params[swap[i]] + "\""

        # Tick values.
        vals = bounds[swap[i], 0] / factor
        val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / (axis_incs * factor)

        if i < n - 1:
            labels = labels + " "
        else:
            labels = labels + "}"

        # Tick locations.
        string = "{"
        val = 0.0
        for j in xrange(axis_incs + 1):
            string = string + " " + `val`
            val = val + loc_inc
        string = string + " }"
        tick_locations.append(string)

        # Tick values.
        string = "{"
        for j in xrange(axis_incs + 1):
            string = string + "\"" + "%.2f" % vals + "\" "
            vals = vals + val_inc
        string = string + "}"
        tick_values.append(string)

    return labels, tick_locations, tick_values


def return_conversion_factor(self, param):
    """Function for returning the factor of conversion between different parameter units.

    For example, the internal representation of tm is in seconds, whereas the external
    representation is in nanoseconds, therefore this function will return 1e-9 for tm.
    """

    # Get the object name.
    object_name = self.return_data_name(param)

    # tm (nanoseconds).
    if object_name == 'tm':
        return 1e-9

    # Diso, Da, Dx, Dy, Dz, Dpar, Dper.
    elif object_name in ['Diso', 'Da', 'Dx', 'Dy', 'Dz', 'Dpar', 'Dper']:
        return 1e6

    # Angles.
    elif object_name in ['theta', 'phi', 'alpha', 'beta', 'gamma']:
        return (2.0*pi) / 360.0

    # No conversion factor.
    else:
        return 1.0


def return_data_name(name):
    """
    Diffusion tensor parameter string matching patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ____________________________________________________________________________________________
    |                                                        |              |                  |
    | Data type                                              | Object name  | Patterns         |
    |________________________________________________________|______________|__________________|
    |                                                        |              |                  |
    | Global correlation time - tm                           | 'tm'         | '^tm$'           |
    |                                                        |              |                  |
    | Isotropic component of the diffusion tensor - Diso     | 'Diso'       | '[Dd]iso'        |
    |                                                        |              |                  |
    | Anisotropic component of the diffusion tensor - Da     | 'Da'         | '[Dd]a'          |
    |                                                        |              |                  |
    | Rhombic component of the diffusion tensor - Dr         | 'Dr'         | '[Dd]r$'         |
    |                                                        |              |                  |
    | Eigenvalue associated with the x-axis of the diffusion | 'Dx'         | '[Dd]x'          |
    | diffusion tensor - Dx                                  |              |                  |
    |                                                        |              |                  |
    | Eigenvalue associated with the y-axis of the diffusion | 'Dy'         | '[Dd]y'          |
    | diffusion tensor - Dy                                  |              |                  |
    |                                                        |              |                  |
    | Eigenvalue associated with the z-axis of the diffusion | 'Dz'         | '[Dd]z'          |
    | diffusion tensor - Dz                                  |              |                  |
    |                                                        |              |                  |
    | Diffusion coefficient parallel to the major axis of    | 'Dpar'       | '[Dd]par'        |
    | the spheroid diffusion tensor - Dpar                   |              |                  |
    |                                                        |              |                  |
    | Diffusion coefficient perpendicular to the major axis  | 'Dper'       | '[Dd]per'        |
    | of the spheroid diffusion tensor - Dper                |              |                  |
    |                                                        |              |                  |
    | Ratio of the parallel and perpendicular components of  | 'Dratio'     | '[Dd]ratio'      |
    | the spheroid diffusion tensor - Dratio                 |              |                  |
    |                                                        |              |                  |
    | The first Euler angle of the ellipsoid diffusion       | 'alpha'      | '^a$' or 'alpha' |
    | tensor - alpha                                         |              |                  |
    |                                                        |              |                  |
    | The second Euler angle of the ellipsoid diffusion      | 'beta'       | '^b$' or 'beta'  |
    | tensor - beta                                          |              |                  |
    |                                                        |              |                  |
    | The third Euler angle of the ellipsoid diffusion       | 'gamma'      | '^g$' or 'gamma' |
    | tensor - gamma                                         |              |                  |
    |                                                        |              |                  |
    | The polar angle defining the major axis of the         | 'theta'      | 'theta'          |
    | spheroid diffusion tensor - theta                      |              |                  |
    |                                                        |              |                  |
    | The azimuthal angle defining the major axis of the     | 'phi'        | 'phi'            |
    | spheroid diffusion tensor - phi                        |              |                  |
    |________________________________________________________|______________|__________________|
    """

    # Local tm.
    if search('^tm$', name):
        return 'tm'

    # Diso.
    if search('[Dd]iso', name):
        return 'Diso'

    # Da.
    if search('[Dd]a', name):
        return 'Da'

    # Dr.
    if search('[Dd]r$', name):
        return 'Dr'

    # Dx.
    if search('[Dd]x', name):
        return 'Dx'

    # Dy.
    if search('[Dd]y', name):
        return 'Dy'

    # Dz.
    if search('[Dd]z', name):
        return 'Dz'

    # Dpar.
    if search('[Dd]par', name):
        return 'Dpar'

    # Dper.
    if search('[Dd]per', name):
        return 'Dper'

    # Dratio.
    if search('[Dd]ratio', name):
        return 'Dratio'

    # alpha.
    if search('^a$', name) or search('alpha', name):
        return 'alpha'

    # beta.
    if search('^b$', name) or search('beta', name):
        return 'beta'

    # gamma.
    if search('^g$', name) or search('gamma', name):
        return 'gamma'

    # theta.
    if search('theta', name):
        return 'theta'

    # phi.
    if search('phi', name):
        return 'phi'


def return_eigenvalues(self, run=None):
    """Function for returning Dx, Dy, and Dz."""

    # Argument.
    if run:
        self.run = run

    # Reassign the data.
    data = cdp.diff_tensor

    # Diso.
    Diso = 1.0 / (6.0 * data.tm)

    # Dx.
    Dx = Diso - 1.0/3.0 * data.Da * (1.0  +  3.0 * data.Dr)

    # Dy.
    Dy = Diso - 1.0/3.0 * data.Da * (1.0  -  3.0 * data.Dr)

    # Dz.
    Dz = Diso + 2.0/3.0 * data.Da

    # Return the eigenvalues.
    return Dx, Dy, Dz


def return_units(self, param):
    """Function for returning a string representing the parameters units.

    For example, the internal representation of tm is in seconds, whereas the external
    representation is in nanoseconds, therefore this function will return the string
    'nanoseconds' for tm.
    """

    # Get the object name.
    object_name = self.return_data_name(param)

    # tm (nanoseconds).
    if object_name == 'tm':
        return 'ns'

    # Diso, Da, Dx, Dy, Dz, Dpar, Dper.
    elif object_name in ['Diso', 'Da', 'Dx', 'Dy', 'Dz', 'Dpar', 'Dper']:
        return '1e6 1/s'

    # Angles.
    elif object_name in ['theta', 'phi', 'alpha', 'beta', 'gamma']:
        return 'deg'


def set(value=None, param=None):
    """
    Diffusion tensor set details
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    If the diffusion tensor has not been setup, use the more powerful function
    'diffusion_tensor.init' to initialise the tensor parameters.

    The diffusion tensor parameters can only be set when the run corresponds to model-free
    analysis.  The units of the parameters are:

        Inverse seconds for tm.
        Seconds for Diso, Da, Dx, Dy, Dz, Dpar, Dper.
        Unitless for Dratio and Dr.
        Radians for all angles (alpha, beta, gamma, theta, phi).


    When setting a diffusion tensor parameter, the residue number has no effect.  As the
    internal parameters of spherical diffusion are {tm}, spheroidal diffusion are {tm, Da,
    theta, phi}, and ellipsoidal diffusion are {tm, Da, Dr, alpha, beta, gamma}, supplying
    geometric parameters must be done in the following way.  If a single geometric parameter is
    supplied, it must be one of tm, Diso, Da, Dr, or Dratio.  For the parameters Dpar, Dper, Dx,
    Dy, and Dx, it is not possible to determine how to use the currently set values together
    with the supplied value to calculate the new internal parameters.  For spheroidal diffusion,
    when supplying multiple geometric parameters, the set must belong to one of

        {tm, Da},
        {Diso, Da},
        {tm, Dratio},
        {Dpar, Dper},
        {Diso, Dratio},

    where either theta, phi, or both orientational parameters can be additionally supplied.  For
    ellipsoidal diffusion, again when supplying multiple geometric parameters, the set must
    belong to one of

        {tm, Da, Dr},
        {Diso, Da, Dr},
        {Dx, Dy, Dz},

    where any number of the orientational parameters, alpha, beta, or gamma can be additionally
    supplied.
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Initialise.
    geo_params = []
    geo_values = []
    orient_params = []
    orient_values = []

    # Loop over the parameters.
    for i in xrange(len(param)):
        # Get the object name.
        param[i] = return_data_name(param[i])

        # Unknown parameter.
        if not param[i]:
            raise RelaxUnknownParamError, ("diffusion tensor", param[i])

        # Default value.
        if value[i] == None:
            value[i] = default_value(object_names[i])

        # Geometric parameter.
        if param[i] in ['tm', 'Diso', 'Da', 'Dratio', 'Dper', 'Dpar', 'Dr', 'Dx', 'Dy', 'Dz']:
            geo_params.append(param[i])
            geo_values.append(value[i])

        # Orientational parameter.
        if param[i] in ['theta', 'phi', 'alpha', 'beta', 'gamma']:
            orient_params.append(param[i])
            orient_values.append(value[i])


    # Spherical diffusion.
    ######################

    if cdp.diff_tensor.type == 'sphere':
        # Geometric parameters.
        #######################

        # A single geometric parameter.
        if len(geo_params) == 1:
            # The single parameter tm.
            if geo_params[0] == 'tm':
                cdp.diff_tensor.tm = geo_values[0]

            # The single parameter Diso.
            elif geo_params[0] == 'Diso':
                cdp.diff_tensor.tm = 1.0 / (6.0 * geo_values[0])

            # Cannot set the single parameter.
            else:
                raise RelaxError, "The geometric diffusion parameter " + `geo_params[0]` + " cannot be set."

        # More than one geometric parameters.
        elif len(geo_params) > 1:
            raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


        # Orientational parameters.
        ###########################

        # ???
        if len(orient_params):
            raise RelaxError, "For spherical diffusion, the orientation parameters " + `orient_params` + " should not exist."


    # Spheroidal diffusion.
    #######################

    elif cdp.diff_tensor.type == 'spheroid':
        # Geometric parameters.
        #######################

        # A single geometric parameter.
        if len(geo_params) == 1:
            # The single parameter tm.
            if geo_params[0] == 'tm':
                cdp.diff_tensor.tm = geo_values[0]

            # The single parameter Diso.
            elif geo_params[0] == 'Diso':
                cdp.diff_tensor.tm = 1.0 / (6.0 * geo_values[0])

            # The single parameter Da.
            elif geo_params[0] == 'Da':
                cdp.diff_tensor.Da = geo_values[0]

            # The single parameter Dratio.
            elif geo_params[0] == 'Dratio':
                Dratio = geo_values[0]
                cdp.diff_tensor.Da = (Dratio - 1.0) / (2.0 * cdp.diff_tensor.tm * (Dratio + 2.0))

            # Cannot set the single parameter.
            else:
                raise RelaxError, "The geometric diffusion parameter " + `geo_params[0]` + " cannot be set."

        # Two geometric parameters.
        elif len(geo_params) == 2:
            # The geometric parameter set {tm, Da}.
            if geo_params.count('tm') == 1 and geo_params.count('Da') == 1:
                # The parameters.
                tm = geo_values[geo_params.index('tm')]
                Da = geo_values[geo_params.index('Da')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = tm
                cdp.diff_tensor.Da = Da

            # The geometric parameter set {Diso, Da}.
            elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1:
                # The parameters.
                Diso = geo_values[geo_params.index('Diso')]
                Da = geo_values[geo_params.index('Da')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = 1.0 / (6.0 * Diso)
                cdp.diff_tensor.Da = Da

            # The geometric parameter set {tm, Dratio}.
            elif geo_params.count('tm') == 1 and geo_params.count('Dratio') == 1:
                # The parameters.
                tm = geo_values[geo_params.index('tm')]
                Dratio = geo_values[geo_params.index('Dratio')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = tm
                cdp.diff_tensor.Da = (Dratio - 1.0) / (2.0 * tm * (Dratio + 2.0))

            # The geometric parameter set {Dpar, Dper}.
            elif geo_params.count('Dpar') == 1 and geo_params.count('Dpar') == 1:
                # The parameters.
                Dpar = geo_values[geo_params.index('Dpar')]
                Dper = geo_values[geo_params.index('Dper')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = 1.0 / (2.0 * (Dpar + 2.0*Dper))
                cdp.diff_tensor.Da = Dpar - Dper

            # The geometric parameter set {Diso, Dratio}.
            elif geo_params.count('Diso') == 1 and geo_params.count('Dratio') == 1:
                # The parameters.
                Diso = geo_values[geo_params.index('Diso')]
                Dratio = geo_values[geo_params.index('Dratio')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = 1.0 / (6.0 * Diso)
                cdp.diff_tensor.Da = 3.0 * Diso * (Dratio - 1.0) / (Dratio + 2.0)

            # Unknown parameter combination.
            else:
                raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)

        # More than two geometric parameters.
        elif len(geo_params) > 2:
            raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


        # Orientational parameters.
        ###########################

        # A single orientational parameter.
        if len(orient_params) == 1:
            # The single parameter theta.
            if orient_params[0] == 'theta':
                cdp.diff_tensor.theta = orient_values[orient_params.index('theta')]

            # The single parameter phi.
            elif orient_params[0] == 'phi':
                cdp.diff_tensor.phi = orient_values[orient_params.index('phi')]

        # Two orientational parameters.
        elif len(orient_params) == 2:
            # The orientational parameter set {theta, phi}.
            if orient_params.count('theta') == 1 and orient_params.count('phi') == 1:
                cdp.diff_tensor.theta = orient_values[orient_params.index('theta')]
                cdp.diff_tensor.phi = orient_values[orient_params.index('phi')]

            # Unknown parameter combination.
            else:
                raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

        # More than two orientational parameters.
        elif len(orient_params) > 2:
            raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)


    # Ellipsoidal diffusion.
    ########################

    elif cdp.diff_tensor.type == 'ellipsoid':
        # Geometric parameters.
        #######################

        # A single geometric parameter.
        if len(geo_params) == 1:
            # The single parameter tm.
            if geo_params[0] == 'tm':
                cdp.diff_tensor.tm = geo_values[0]

            # The single parameter Diso.
            elif geo_params[0] == 'Diso':
                cdp.diff_tensor.tm = 1.0 / (6.0 * geo_values[0])

            # The single parameter Da.
            elif geo_params[0] == 'Da':
                cdp.diff_tensor.Da = geo_values[0]

            # The single parameter Dr.
            elif geo_params[0] == 'Dr':
                cdp.diff_tensor.Dr = geo_values[0]

            # Cannot set the single parameter.
            else:
                raise RelaxError, "The geometric diffusion parameter " + `geo_params[0]` + " cannot be set."

        # Two geometric parameters.
        elif len(geo_params) == 2:
            # The geometric parameter set {tm, Da}.
            if geo_params.count('tm') == 1 and geo_params.count('Da') == 1:
                # The parameters.
                tm = geo_values[geo_params.index('tm')]
                Da = geo_values[geo_params.index('Da')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = tm
                cdp.diff_tensor.Da = Da

            # The geometric parameter set {tm, Dr}.
            elif geo_params.count('tm') == 1 and geo_params.count('Dr') == 1:
                # The parameters.
                tm = geo_values[geo_params.index('tm')]
                Dr = geo_values[geo_params.index('Dr')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = tm
                cdp.diff_tensor.Dr = Dr

            # The geometric parameter set {Diso, Da}.
            elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1:
                # The parameters.
                Diso = geo_values[geo_params.index('Diso')]
                Da = geo_values[geo_params.index('Da')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = 1.0 / (6.0 * Diso)
                cdp.diff_tensor.Da = Da

            # The geometric parameter set {Diso, Dr}.
            elif geo_params.count('Diso') == 1 and geo_params.count('Dr') == 1:
                # The parameters.
                Diso = geo_values[geo_params.index('Diso')]
                Dr = geo_values[geo_params.index('Dr')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = 1.0 / (6.0 * Diso)
                cdp.diff_tensor.Dr = Dr

            # The geometric parameter set {Da, Dr}.
            elif geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                # The parameters.
                Da = geo_values[geo_params.index('Da')]
                Dr = geo_values[geo_params.index('Dr')]

                # Set the internal parameter values.
                cdp.diff_tensor.Da = Da
                cdp.diff_tensor.Da = Dr

            # Unknown parameter combination.
            else:
                raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)

        # Three geometric parameters.
        elif len(geo_params) == 3:
            # The geometric parameter set {tm, Da, Dr}.
            if geo_params.count('tm') == 1 and geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                # The parameters.
                tm = geo_values[geo_params.index('tm')]
                Da = geo_values[geo_params.index('Da')]
                Dr = geo_values[geo_params.index('Dr')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = tm
                cdp.diff_tensor.Da = Da
                cdp.diff_tensor.Dr = Dr

            # The geometric parameter set {Diso, Da, Dr}.
            elif geo_params.count('Diso') == 1 and geo_params.count('Da') == 1 and geo_params.count('Dr') == 1:
                # The parameters.
                Diso = geo_values[geo_params.index('Diso')]
                Da = geo_values[geo_params.index('Da')]
                Dr = geo_values[geo_params.index('Dr')]

                # Set the internal parameter values.
                cdp.diff_tensor.tm = 1.0 / (6.0 * Diso)
                cdp.diff_tensor.Da = Da
                cdp.diff_tensor.Dr = Dr

            # The geometric parameter set {Dx, Dy, Dz}.
            elif geo_params.count('Dx') == 1 and geo_params.count('Dy') == 1 and geo_params.count('Dz') == 1:
                # The parameters.
                Dx = geo_values[geo_params.index('Dx')]
                Dy = geo_values[geo_params.index('Dy')]
                Dz = geo_values[geo_params.index('Dz')]

                # Set the internal tm value.
                if Dx + Dy + Dz == 0.0:
                    cdp.diff_tensor.tm = 1e99
                else:
                    cdp.diff_tensor.tm = 0.5 / (Dx + Dy + Dz)

                # Set the internal Da value.
                cdp.diff_tensor.Da = Dz - 0.5*(Dx + Dy)

                # Set the internal Dr value.
                if cdp.diff_tensor.Da == 0.0:
                    cdp.diff_tensor.Dr = (Dy - Dx) * 1e99
                else:
                    cdp.diff_tensor.Dr = (Dy - Dx) / (2.0*cdp.diff_tensor.Da)

            # Unknown parameter combination.
            else:
                raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


        # More than three geometric parameters.
        elif len(geo_params) > 3:
            raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


        # Orientational parameters.
        ###########################

        # A single orientational parameter.
        if len(orient_params) == 1:
            # The single parameter alpha.
            if orient_params[0] == 'alpha':
                cdp.diff_tensor.alpha = orient_values[orient_params.index('alpha')]

            # The single parameter beta.
            elif orient_params[0] == 'beta':
                cdp.diff_tensor.beta = orient_values[orient_params.index('beta')]

            # The single parameter gamma.
            elif orient_params[0] == 'gamma':
                cdp.diff_tensor.gamma = orient_values[orient_params.index('gamma')]

        # Two orientational parameters.
        elif len(orient_params) == 2:
            # The orientational parameter set {alpha, beta}.
            if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
                cdp.diff_tensor.alpha = orient_values[orient_params.index('alpha')]
                cdp.diff_tensor.beta = orient_values[orient_params.index('beta')]

            # The orientational parameter set {alpha, gamma}.
            if orient_params.count('alpha') == 1 and orient_params.count('gamma') == 1:
                cdp.diff_tensor.alpha = orient_values[orient_params.index('alpha')]
                cdp.diff_tensor.gamma = orient_values[orient_params.index('gamma')]

            # The orientational parameter set {beta, gamma}.
            if orient_params.count('beta') == 1 and orient_params.count('gamma') == 1:
                cdp.diff_tensor.beta = orient_values[orient_params.index('beta')]
                cdp.diff_tensor.gamma = orient_values[orient_params.index('gamma')]

            # Unknown parameter combination.
            else:
                raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

        # Three orientational parameters.
        elif len(orient_params) == 3:
            # The orientational parameter set {alpha, beta, gamma}.
            if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
                cdp.diff_tensor.alpha = orient_values[orient_params.index('alpha')]
                cdp.diff_tensor.beta = orient_values[orient_params.index('beta')]
                cdp.diff_tensor.gamma = orient_values[orient_params.index('gamma')]

            # Unknown parameter combination.
            else:
                raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

        # More than three orientational parameters.
        elif len(orient_params) > 3:
            raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)


    # Fold the angles in.
    #####################

    if orient_params:
        fold_angles()


def sphere(params=None, time_scale=None, param_types=None):
    """Function for setting up a spherical diffusion tensor.
    
    @param params:      The diffusion tensor parameter.
    @type params:       float
    @param time_scale:  The correlation time scaling value.
    @type time_scale:   float
    @param param_types: The type of parameter supplied.  If 0, then the parameter is tm.  If 1, then
                        the parameter is Diso.
    @type param_types:  int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # The diffusion type.
    cdp.diff_tensor.type = 'sphere'

    # tm.
    if param_types == 0:
        # Scaling.
        tm = params * time_scale

        # Set the parameters.
        set(value=[tm], param=['tm'])

    # Diso
    elif param_types == 1:
        # Scaling.
        Diso = params * d_scale

        # Set the parameters.
        set(value=[Diso], param=['Diso'])

    # Unknown parameter combination.
    else:
        raise RelaxUnknownParamCombError, ('param_types', param_types)


def spheroid(self):
    """Function for setting up spheroidal diffusion."""

    # The diffusion type.
    cdp.diff_tensor.type = 'spheroid'

    # Spheroid diffusion type.
    allowed_types = [None, 'oblate', 'prolate']
    if self.spheroid_type not in allowed_types:
        raise RelaxError, "The 'spheroid_type' argument " + `self.spheroid_type` + " should be 'oblate', 'prolate', or None."
    cdp.diff_tensor.spheroid_type = self.spheroid_type

    # (tm, Da, theta, phi).
    if self.param_types == 0:
        # Unpack the tuple.
        tm, Da, theta, phi = self.params

        # Scaling.
        tm = tm * self.time_scale
        Da = Da * self.d_scale

        # Set the parameters.
        self.set(run=self.run, value=[tm, Da], param=['tm', 'Da'])

    # (Diso, Da, theta, phi).
    elif self.param_types == 1:
        # Unpack the tuple.
        Diso, Da, theta, phi = self.params

        # Scaling.
        Diso = Diso * self.d_scale
        Da = Da * self.d_scale

        # Set the parameters.
        self.set(run=self.run, value=[Diso, Da], param=['Diso', 'Da'])

    # (tm, Dratio, theta, phi).
    elif self.param_types == 2:
        # Unpack the tuple.
        tm, Dratio, theta, phi = self.params

        # Scaling.
        tm = tm * self.time_scale

        # Set the parameters.
        self.set(run=self.run, value=[tm, Dratio], param=['tm', 'Dratio'])

    # (Dpar, Dper, theta, phi).
    elif self.param_types == 3:
        # Unpack the tuple.
        Dpar, Dper, theta, phi = self.params

        # Scaling.
        Dpar = Dpar * self.d_scale
        Dper = Dper * self.d_scale

        # Set the parameters.
        self.set(run=self.run, value=[Dpar, Dper], param=['Dpar', 'Dper'])

    # (Diso, Dratio, theta, phi).
    elif self.param_types == 4:
        # Unpack the tuple.
        Diso, Dratio, theta, phi = self.params

        # Scaling.
        Diso = Diso * self.d_scale

        # Set the parameters.
        self.set(run=self.run, value=[Diso, Dratio], param=['Diso', 'Dratio'])

    # Unknown parameter combination.
    else:
        raise RelaxUnknownParamCombError, ('param_types', self.param_types)

    # Convert the angles to radians.
    if self.angle_units == 'deg':
        theta = (theta / 360.0) * 2.0 * pi
        phi = (phi / 360.0) * 2.0 * pi

    # Set the orientational parameters.
    self.set(run=self.run, value=[theta, phi], param=['theta', 'phi'])


def test_params(self, num_params):
    """Function for testing the validity of the input parameters."""

    # An allowable error to account for machine precision, optimisation quality, etc.
    error = 1e-4

    # tm.
    tm = cdp.diff_tensor.tm
    if tm <= 0.0 or tm > 1e-6:
        raise RelaxError, "The tm value of " + `tm` + " should be between zero and one microsecond."

    # Spheroid.
    if num_params == 4:
        # Parameters.
        Diso = 1.0 / (6.0 * cdp.diff_tensor.tm)
        Da = cdp.diff_tensor.Da

        # Da.
        if Da < (-1.5*Diso - error*Diso) or Da > (3.0*Diso + error*Diso):
            raise RelaxError, "The Da value of " + `Da` + " should be between -3/2 * Diso and 3Diso."

    # Ellipsoid.
    if num_params == 6:
        # Parameters.
        Diso = 1.0 / (6.0 * cdp.diff_tensor.tm)
        Da = cdp.diff_tensor.Da
        Dr = cdp.diff_tensor.Dr

        # Da.
        if Da < (0.0 - error*Diso) or Da > (3.0*Diso + error*Diso):
            raise RelaxError, "The Da value of " + `Da` + " should be between zero and 3Diso."

        # Dr.
        if Dr < (0.0 - error) or Dr > (1.0 + error):
            raise RelaxError, "The Dr value of " + `Dr` + " should be between zero and one."


def unit_axes(self):
    """Function for calculating the unit axes of the diffusion tensor.

    Spheroid
    ~~~~~~~~

    The unit Dpar vector is

                 | sin(theta) * cos(phi) |
        Dpar  =  | sin(theta) * sin(phi) |
                 |      cos(theta)       |


    Ellipsoid
    ~~~~~~~~~

    The unit Dx vector is

               | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Dx  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |
               |                    cos(alpha) * sin(beta)                      |

    The unit Dy vector is

               | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Dy  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |
               |                   sin(alpha) * sin(beta)                      |

    The unit Dz vector is

               | -sin(beta) * cos(gamma) |
        Dz  =  |  sin(beta) * sin(gamma) |
               |        cos(beta)        |

    """

    # Spheroid.
    if cdp.diff_tensor.type == 'spheroid':
        # Initialise.
        Dpar = zeros(3, Float64)

        # Trig.
        sin_theta = sin(cdp.diff_tensor.theta)
        cos_theta = cos(cdp.diff_tensor.theta)
        sin_phi = sin(cdp.diff_tensor.phi)
        cos_phi = cos(cdp.diff_tensor.phi)

        # Unit Dpar axis.
        Dpar[0] = sin_theta * cos_phi
        Dpar[1] = sin_theta * sin_phi
        Dpar[2] = cos_theta

        # Return the vector.
        return Dpar

    # Ellipsoid.
    if cdp.diff_tensor.type == 'ellipsoid':
        # Initialise.
        Dx = zeros(3, Float64)
        Dy = zeros(3, Float64)
        Dz = zeros(3, Float64)

        # Trig.
        sin_alpha = sin(cdp.diff_tensor.alpha)
        cos_alpha = cos(cdp.diff_tensor.alpha)
        sin_beta = sin(cdp.diff_tensor.beta)
        cos_beta = cos(cdp.diff_tensor.beta)
        sin_gamma = sin(cdp.diff_tensor.gamma)
        cos_gamma = cos(cdp.diff_tensor.gamma)

        # Unit Dx axis.
        Dx[0] = -sin_alpha * sin_gamma  +  cos_alpha * cos_beta * cos_gamma
        Dx[1] = -sin_alpha * cos_gamma  -  cos_alpha * cos_beta * sin_gamma
        Dx[2] =  cos_alpha * sin_beta

        # Unit Dy axis.
        Dx[0] = cos_alpha * sin_gamma  +  sin_alpha * cos_beta * cos_gamma
        Dx[1] = cos_alpha * cos_gamma  -  sin_alpha * cos_beta * sin_gamma
        Dx[2] = sin_alpha * sin_beta

        # Unit Dz axis.
        Dx[0] = -sin_beta * cos_gamma
        Dx[1] =  sin_beta * sin_gamma
        Dx[2] =  cos_beta

        # Return the vectors.
        return Dx, Dy, Dz
