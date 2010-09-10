# Script for checking the parametric restriction of the isotropic cone to the free rotor isotropic cone frame order model.

# Python module imports.
import __main__
from numpy import array, cross, float64, zeros
from numpy.linalg import norm
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from maths_fns.rotation_matrix import R_to_euler_zyz


def get_angle(index, incs=None, deg=False):
    """Return the angle corresponding to the incrementation index."""

    # The angle of one increment.
    inc_angle = pi / incs

    # The angle of the increment.
    angle = inc_angle * (index+1)

    # Return.
    if deg:
        return angle / (2*pi) * 360
    else:
        return angle


# Init.
INC = 18

# Generate 3 orthogonal vectors.
vect_z = array([2, 1, 3], float64)
vect_x = cross(vect_z, array([1, 1, 1], float64))
vect_y = cross(vect_z, vect_x)

# Normalise.
vect_x = vect_x / norm(vect_x)
vect_y = vect_y / norm(vect_y)
vect_z = vect_z / norm(vect_z)

# Build the frame.
EIG_FRAME = zeros((3, 3), float64)
EIG_FRAME[:,0] = vect_x
EIG_FRAME[:,1] = vect_y
EIG_FRAME[:,2] = vect_z
a, b, g = R_to_euler_zyz(EIG_FRAME)

# Load the tensors.
execfile(__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors'+sep+'iso_cone_free_rotor_axis2_1_3_tensors_beta78.75.py')

# Data stores.
ds.chi2 = []
ds.angles = []

# Loop over the cones.
for i in range(INC):
    # Switch data pipes.
    ds.angles.append(get_angle(i, incs=INC, deg=True))
    pipe.switch('cone_%s_deg' % ds.angles[-1])

    # Data init.
    cdp.ave_pos_alpha  = cdp.ave_pos_alpha2  = 0.0
    cdp.ave_pos_beta   = cdp.ave_pos_beta2   = 78.75 / 360.0 * 2.0 * pi
    cdp.ave_pos_gamma  = cdp.ave_pos_gamma2  = 0.0
    cdp.eigen_alpha    = cdp.eigen_alpha2    = a
    cdp.eigen_beta     = cdp.eigen_beta2     = b
    cdp.eigen_gamma    = cdp.eigen_gamma2    = g
    cdp.cone_theta     = cdp.cone_theta2     = get_angle(i, incs=INC, deg=False)
    cdp.cone_sigma_max = cdp.cone_sigma_max2 = pi

    # Select the Frame Order model.
    frame_order.select_model(model='iso cone')

    # Set the reference domain.
    frame_order.ref_domain('full')

    # Calculate the chi2.
    calc()
    #cdp.chi2b = cdp.chi2
    #minimise('simplex')
    ds.chi2.append(cdp.chi2)

# Save the program state.
#state.save("iso_cone_to_iso_cone_free_rotor", force=True)

print "\n\n"
for i in range(INC):
    print("Cone %3i deg, chi2: %s" % (ds.angles[i], ds.chi2[i]))
