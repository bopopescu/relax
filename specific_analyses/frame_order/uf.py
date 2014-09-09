###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""Module for all of the frame order specific user functions."""

# Python module imports.
from numpy import array, float64, transpose, zeros
from warnings import warn

# relax module imports.
from lib.arg_check import is_float_array
from lib.check_types import is_float
from lib.errors import RelaxError
from lib.geometry.rotations import euler_to_R_zyz, R_to_euler_zyz
from lib.warnings import RelaxWarning
from pipe_control import pipes
from specific_analyses.frame_order.geometric import create_ave_pos, create_distribution, create_geometric_rep
from specific_analyses.frame_order.parameters import update_model
from specific_analyses.frame_order.variables import MODEL_LIST, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID


def num_int_pts(num=200000):
    """Set the number of integration points to use in the quasi-random Sobol' sequence.

    @keyword num:   The number of integration points.
    @type num:      int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Throw a warning to the user if not enough points are being used.
    if num < 1000:
        warn(RelaxWarning("To obtain reliable results in a frame order analysis, the number of integration points should be greater than 1000."))
 
    # Store the value.
    cdp.num_int_pts = num


def pdb_model(ave_pos="ave_pos", rep="frame_order", dist="domain_distribution", dir=None, compress_type=0, size=30.0, inc=36, force=False):
    """Create 3 different PDB files for representing the frame order dynamics of the system.

    @keyword ave_pos:       The file root for the average molecule structure.
    @type ave_pos:          str or None
    @keyword rep:           The file root of the PDB representation of the frame order dynamics to create.
    @type rep:              str or None
    @keyword dist:          The file root which will contain multiple models spanning the full dynamics distribution of the frame order model.
    @type dist:             str or None
    @keyword dir:           The name of the directory to place the PDB file into.
    @type dir:              str
    @keyword compress_type: The compression type.  The integer values correspond to the compression type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @keyword size:          The size of the geometric object in Angstroms.
    @type size:             float
    @keyword inc:           The number of increments for the filling of the cone objects.
    @type inc:              int
    @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:            bool
    """

    # Check that at least one PDB file name is given.
    if not ave_pos and not rep and not dist:
        raise RelaxError("Minimally one PDB file name must be supplied.")

    # Test if the current data pipe exists.
    pipes.test()

    # Create the average position structure.
    if ave_pos:
        create_ave_pos(file=ave_pos, dir=dir, compress_type=compress_type, force=force)

    # Nothing more to do for the rigid model.
    if cdp.model == MODEL_RIGID:
        return

    # Create the geometric representation.
    if rep:
        create_geometric_rep(file=rep, dir=dir, compress_type=compress_type, size=size, inc=inc, force=force)

    # Create the distribution.
    if dist:
        create_distribution(file=dist, dir=dir, compress_type=compress_type, force=force)


def permute_axes():
    """Permute the axes of the motional eigenframe to switch between local minima."""

    # Check that the model is valid.
    if cdp.model not in [MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS]:
        raise RelaxError("The permutation of the motional eigenframe is only valid for the '%s' and '%s' frame order models." % (MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS))

    # Check that the model parameters are setup.
    if not hasattr(cdp, 'cone_theta_y') or not is_float(cdp.cone_theta_y):
        raise RelaxError("The parameter values are not set up.")

    # The angles.  Note that cone_theta_x corresponds to a rotation about the y-axis!
    cone_sigma_max = 0.0
    if cdp.model == MODEL_PSEUDO_ELLIPSE:
        cone_sigma_max = cdp.cone_sigma_max
    angles = array([cdp.cone_theta_y, cdp.cone_theta_x, cone_sigma_max], float64)

    # Generate the eigenframe of the motion.
    frame = zeros((3, 3), float64)
    euler_to_R_zyz(cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma, frame)

    # The permutation with the condition that cone_theta_x <= cone_theta_y.
    if angles[1] <= angles[2]:
        perm = [2, 0, 1]
    else:
        perm = [1, 2, 0]

    # Permute the angles.
    cdp.cone_theta_y = angles[perm[0]]
    cdp.cone_theta_x = angles[perm[1]]
    if cdp.model == MODEL_PSEUDO_ELLIPSE:
        cdp.cone_sigma_max = angles[perm[2]]

    # Permute the axes.
    frame_new = transpose(array([frame[:, perm[0]], frame[:, perm[1]], frame[:, perm[2]]], float64))

    # Convert the permuted frame to Euler angles and store them.
    cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma = R_to_euler_zyz(frame_new)


def pivot(pivot=None, order=1, fix=False):
    """Set the pivot point for the 2 body motion.

    @keyword pivot: The pivot point of the two bodies (domains, etc.) in the structural coordinate system.
    @type pivot:    list of num
    @keyword order: The ordinal number of the pivot point.  The value of 1 is for the first pivot point, the value of 2 for the second pivot point, and so on.
    @type order:    int
    @keyword fix:   A flag specifying if the pivot point should be fixed during optimisation.
    @type fix:      bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Store the fixed flag.
    cdp.pivot_fixed = fix

    # No pivot given, so update the model if needed and quit.
    if pivot == None:
        if hasattr(cdp, 'model'):
            update_model()
        return

    # Convert the pivot to a numpy array.
    pivot = array(pivot, float64)

    # Check the pivot validity.
    is_float_array(pivot, name='pivot point', size=3)

    # Store the pivot point and fixed flag.
    if order == 1:
        cdp.pivot_x = pivot[0]
        cdp.pivot_y = pivot[1]
        cdp.pivot_z = pivot[2]
    else:
        # The variable names.
        name_x = 'pivot_x_%i' % order
        name_y = 'pivot_y_%i' % order
        name_z = 'pivot_z_%i' % order

        # Store the variables.
        setattr(cdp, name_x, pivot[0])
        setattr(cdp, name_y, pivot[1])
        setattr(cdp, name_z, pivot[2])

    # Update the model.
    if hasattr(cdp, 'model'):
        update_model()


def ref_domain(ref=None):
    """Set the reference domain for the frame order, multi-domain models.

    @param ref: The reference domain.
    @type ref:  str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Check that the domain is defined.
    if not hasattr(cdp, 'domain') or ref not in list(cdp.domain.keys()):
        raise RelaxError("The domain '%s' has not been defined.  Please use the domain user function." % ref)

    # Test if the reference domain exists.
    exists = False
    for tensor_cont in cdp.align_tensors:
        if hasattr(tensor_cont, 'domain') and tensor_cont.domain == ref:
            exists = True
    if not exists:
        raise RelaxError("The reference domain cannot be found within any of the loaded tensors.")

    # Set the reference domain.
    cdp.ref_domain = ref

    # Update the model.
    if hasattr(cdp, 'model'):
        update_model()


def select_model(model=None):
    """Select the Frame Order model.

    @param model:   The Frame Order model.  This can be one of 'pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor', 'iso cone', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor', 'rigid', 'free rotor', 'double rotor'.
    @type model:    str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the model name exists.
    if not model in MODEL_LIST:
        raise RelaxError("The model name '%s' is invalid, it must be one of %s." % MODEL_LIST)

    # Set the model
    cdp.model = model

    # Initialise the list of model parameters.
    cdp.params = []

    # Update the model.
    update_model()
