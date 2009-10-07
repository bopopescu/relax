###############################################################################
#                                                                             #
# Copyright (C) 2007-2009 Edward d'Auvergne                                   #
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
"""Module for the specific analysis of the N-state dynamic model."""

# Python module imports.
from math import acos, cos, pi, sqrt
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import array, dot, float64, identity, ones, zeros
from numpy.linalg import inv, norm
from re import search
from warnings import warn

# relax module imports.
from float import isNaN, isInf
import generic_fns
from generic_fns.mol_res_spin import return_spin, spin_loop
from generic_fns import pipes
import generic_fns.structure.geometric
from generic_fns.structure.internal import Internal
import generic_fns.structure.mass
from maths_fns.n_state_model import N_state_opt
from maths_fns.potential import quad_pot
from maths_fns.rotation_matrix import two_vect_to_R, euler_zyz_to_R
from physical_constants import dipolar_constant, g1H, pcs_constant, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxInfError, RelaxModelError, RelaxNaNError, RelaxNoModelError, RelaxNoTensorError
from relax_io import open_write_file
from relax_warnings import RelaxWarning
from specific_fns.base_class import Common_functions


class N_state_model(Common_functions):
    """Class containing functions for the N-state model."""

    def __assemble_param_vector(self, sim_index=None):
        """Assemble all the parameters of the model into a single array.

        @param sim_index:       The index of the simulation to optimise.  This should be None if
                                normal optimisation is desired.
        @type sim_index:        None or int
        @return:                The parameter vector used for optimisation.
        @rtype:                 numpy array
        """

        # Test if the model is selected.
        if not hasattr(cdp, 'model') or not isinstance(cdp.model, str):
            raise RelaxNoModelError

        # Determine the data type.
        data_types = self.__base_data_types()

        # Initialise the parameter vector.
        param_vector = []

        # A RDC or PCS data type requires the alignment tensors to be at the start of the parameter vector.
        if 'rdc' in data_types or 'pcs' in data_types:
            # Loop over the alignments, adding the alignment tensor parameters to the parameter vector.
            for i in xrange(len(cdp.align_tensors)):
                param_vector = param_vector + list(cdp.align_tensors[i].tensor_5D)

        # Monte Carlo simulation data structures.
        if sim_index != None:
            # Populations.
            if cdp.model in ['2-domain', 'population']:
                probs = cdp.probs_sim[sim_index]

            # Euler angles.
            if cdp.model == '2-domain':
                alpha = cdp.alpha_sim[sim_index]
                beta = cdp.beta_sim[sim_index]
                gamma = cdp.gamma_sim[sim_index]

        # Normal data structures.
        else:
            # Populations.
            if cdp.model in ['2-domain', 'population']:
                probs = cdp.probs

            # Euler angles.
            if cdp.model == '2-domain':
                alpha = cdp.alpha
                beta = cdp.beta
                gamma = cdp.gamma

        # The probabilities (exclude that of state N).
        if cdp.model in ['2-domain', 'population']:
            param_vector = param_vector + probs[0:-1]

        # The Euler angles.
        if cdp.model == '2-domain':
            for i in xrange(cdp.N):
                param_vector.append(alpha[i])
                param_vector.append(beta[i])
                param_vector.append(gamma[i])

        # Convert all None values to zero (to avoid conversion to NaN).
        for i in xrange(len(param_vector)):
            if param_vector[i] == None:
                param_vector[i] = 0.0

        # Return a numpy arrary.
        return array(param_vector, float64)


    def __assemble_scaling_matrix(self, data_types=None, scaling=True):
        """Create and return the scaling matrix.

        @keyword data_types:    The base data types used in the optimisation.  This list can contain
                                the elements 'rdc', 'pcs' or 'tensor'.
        @type data_types:       list of str
        @keyword scaling:       If False, then the identity matrix will be returned.
        @type scaling:          bool
        @return:                The square and diagonal scaling matrix.
        @rtype:                 numpy rank-2 array
        """

        # Initialise.
        scaling_matrix = identity(self.param_num(), float64)

        # Return the identity matrix.
        if not scaling:
            return scaling_matrix

        # Starting point of the populations.
        pop_start = 0
        if 'rdc' in data_types or 'pcs' in data_types:
            pop_start = pop_start + 5*len(cdp.align_tensors)

        # Loop over the populations, and set the scaling factor.
        if cdp.model in ['2-domain', 'population']:
            factor = 100.0
            for i in xrange(pop_start, pop_start + (cdp.N-1)):
                scaling_matrix[i, i] = factor

        # Return the matrix.
        return scaling_matrix


    def __base_data_types(self):
        """Determine all the base data types.

        The base data types can include::
            - 'rdc', residual dipolar couplings.
            - 'pcs', pseudo-contact shifts.
            - 'noesy', NOE restraints.
            - 'tensor', alignment tensors.

        @return:    A list of all the base data types.
        @rtype:     list of str
        """

        # Array of data types.
        list = []

        # RDC search.
        for spin in spin_loop():
            if hasattr(spin, 'rdc'):
                list.append('rdc')
                break

        # PCS search.
        for spin in spin_loop():
            if hasattr(spin, 'pcs'):
                list.append('pcs')
                break

        # Alignment tensor search.
        if not ('rdc' in list or 'pcs' in list) and hasattr(cdp, 'align_tensors'):
            list.append('tensor')

        # NOESY data search.
        if hasattr(cdp, 'noe_restraints'):
            list.append('noesy')

        # No data is present.
        if not list:
            raise RelaxError("Neither RDC, PCS, NOESY nor alignment tensor data is present.")

        # Return the list.
        return list


    def __disassemble_param_vector(self, param_vector=None, data_types=None, sim_index=None):
        """Disassemble the parameter vector and place the values into the relevant variables.

        For the 2-domain N-state model, the parameters are stored in the probability and Euler angle
        data structures.  For the population N-state model, only the probabilities are stored.  If
        RDCs are present and alignment tensors are optimised, then these are stored as well.

        @keyword data_types:    The base data types used in the optimisation.  This list can contain
                                the elements 'rdc', 'pcs' or 'tensor'.
        @type data_types:       list of str
        @keyword param_vector:  The parameter vector returned from optimisation.
        @type param_vector:     numpy array
        @keyword sim_index:     The index of the simulation to optimise.  This should be None if
                                normal optimisation is desired.
        @type sim_index:        None or int
        """

        # Test if the model is selected.
        if not hasattr(cdp, 'model') or not isinstance(cdp.model, str):
            raise RelaxNoModelError

        # Unpack and strip off the alignment tensor parameters.
        if 'rdc' in data_types or 'pcs' in data_types:
            # Loop over the alignments, adding the alignment tensor parameters to the tensor data container.
            for i in xrange(len(cdp.align_tensors)):
                cdp.align_tensors[i].Axx = param_vector[5*i]
                cdp.align_tensors[i].Ayy = param_vector[5*i+1]
                cdp.align_tensors[i].Axy = param_vector[5*i+2]
                cdp.align_tensors[i].Axz = param_vector[5*i+3]
                cdp.align_tensors[i].Ayz = param_vector[5*i+4]

            # Create a new parameter vector without the tensors.
            param_vector = param_vector[5*len(cdp.align_tensors):]

        # Monte Carlo simulation data structures.
        if sim_index != None:
            # Populations.
            if cdp.model in ['2-domain', 'population']:
                probs = cdp.probs_sim[sim_index]

            # Euler angles.
            if cdp.model == '2-domain':
                alpha = cdp.alpha_sim[sim_index]
                beta = cdp.beta_sim[sim_index]
                gamma = cdp.gamma_sim[sim_index]

        # Normal data structures.
        else:
            # Populations.
            if cdp.model in ['2-domain', 'population']:
                probs = cdp.probs

            # Euler angles.
            if cdp.model == '2-domain':
                alpha = cdp.alpha
                beta = cdp.beta
                gamma = cdp.gamma

        # The probabilities for states 0 to N-1.
        if cdp.model in ['2-domain', 'population']:
            for i in xrange(cdp.N-1):
                probs[i] = param_vector[i]

            # The probability for state N.
            probs[-1] = 1 - sum(probs[0:-1])

        # The Euler angles.
        if cdp.model == '2-domain':
            for i in xrange(cdp.N):
                alpha[i] = param_vector[cdp.N-1 + 3*i]
                beta[i] = param_vector[cdp.N-1 + 3*i + 1]
                gamma[i] = param_vector[cdp.N-1 + 3*i + 2]


    def __linear_constraints(self, data_types=None, scaling_matrix=None):
        """Function for setting up the linear constraint matrices A and b.

        Standard notation
        =================

        The N-state model constraints are::

            0 <= pc <= 1,

        where p is the probability and c corresponds to state c.


        Matrix notation
        ===============

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are::

            | 1  0  0 |                   |    0    |
            |         |                   |         |
            |-1  0  0 |                   |   -1    |
            |         |                   |         |
            | 0  1  0 |                   |    0    |
            |         |     |  p0  |      |         |
            | 0 -1  0 |     |      |      |   -1    |
            |         |  .  |  p1  |  >=  |         |
            | 0  0  1 |     |      |      |    0    |
            |         |     |  p2  |      |         |
            | 0  0 -1 |                   |   -1    |
            |         |                   |         |
            |-1 -1 -1 |                   |   -1    |
            |         |                   |         |
            | 1  1  1 |                   |    0    |

        This example is for a 4-state model, the last probability pn is not included as this
        parameter does not exist (because the sum of pc is equal to 1).  The Euler angle parameters
        have been excluded here but will be included in the returned A and b objects.  These
        parameters simply add columns of zero to the A matrix and have no effect on b.  The last two
        rows correspond to the inequality::

            0 <= pN <= 1.

        As::
                    N-1
                    \
            pN = 1 - >  pc,
                    /__
                    c=1

        then::

            -p1 - p2 - ... - p(N-1) >= -1,

             p1 + p2 + ... + p(N-1) >= 0.


        @keyword data_types:        The base data types used in the optimisation.  This list can
                                    contain the elements 'rdc', 'pcs' or 'tensor'.
        @type data_types:           list of str
        @keyword scaling_matrix:    The diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 square matrix
        @return:                    The matrices A and b.
        @rtype:                     tuple of len 2 of a numpy rank-2, size NxM matrix and numpy
                                    rank-1, size N array
        """

        # Starting point of the populations.
        pop_start = 0
        if 'rdc' in data_types or 'pcs' in data_types:
            pop_start = pop_start + 5*len(cdp.align_tensors)

        # Initialisation (0..j..m).
        A = []
        b = []
        zero_array = zeros(self.param_num(), float64)
        i = pop_start
        j = 0

        # Probability parameters.
        if cdp.model in ['2-domain', 'population']:
            # Loop over the prob parameters (N - 1, because the sum of pc is 1).
            for k in xrange(cdp.N - 1):
                # 0 <= pc <= 1.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0)
                b.append(-1.0 / scaling_matrix[i, i])
                j = j + 2

                # Increment i.
                i = i + 1

            # Add the inequalities for pN.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            for i in xrange(pop_start, self.param_num()):
                A[-2][i] = -1.0
                A[-1][i] = 1.0
            b.append(-1.0)
            b.append(0.0)

        # Convert to numpy data structures.
        A = array(A, float64)
        b = array(b, float64)

        # Return the constraint objects.
        return A, b


    def __minimise_bc_data(self, model):
        """Extract and unpack the back calculated data.

        @param model:   The instantiated class containing the target function.
        @type model:    class instance
        """

        # Loop over each alignment.
        for i in xrange(model.num_align):
            # Spin loop.
            data_index = 0
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Spins with PCS data.
                if hasattr(spin, 'pcs'):
                    # Initialise the data structure if necessary.
                    if not hasattr(spin, 'pcs_bc'):
                        spin.pcs_bc = [None]*model.num_align

                    # Append the back calculated PCS (in ppm).
                    spin.pcs_bc[i] = model.deltaij_theta[i, data_index] * 1e6

                # Spins with RDC data.
                if hasattr(spin, 'rdc') and (hasattr(spin, 'xh_vect') or hasattr(spin, 'bond_vect')):
                    # Initialise the data structure if necessary.
                    if not hasattr(spin, 'rdc_bc'):
                        spin.rdc_bc = [None] * model.num_align

                    # Append the back calculated PCS.
                    spin.rdc_bc[i] = model.Dij_theta[i, data_index]

                # Increment the spin index if it contains data.
                if hasattr(spin, 'pcs') or (hasattr(spin, 'rdc') and (hasattr(spin, 'xh_vect') or hasattr(spin, 'bond_vect'))):
                    data_index = data_index + 1


    def __minimise_setup_pcs(self):
        """Set up the data structures for optimisation using PCSs as base data sets.

        @return:    The assembled data structures for using PCSs as the base data for optimisation.
                    These include:
                        - the PCS values.
                        - the unit vectors connecting the paramagnetic centre (the electron spin) to
                        the nuclear spin.
                        - the pseudocontact shift constants.
        @rtype:     tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array, numpy
                    rank-1 array, numpy rank-1 array)
        """

        # Data setup tests.
        if not hasattr(cdp, 'paramagnetic_centre'):
            raise RelaxError("The paramagnetic centre has not yet been specified.")
        if not hasattr(cdp, 'temperature'):
            raise RelaxError("The experimental temperatures have not been set.")
        if not hasattr(cdp, 'frq'):
            raise RelaxError("The spectrometer frequencies of the experiments have not been set.")

        # Initialise.
        pcs = []
        pcs_err = []
        unit_vect = []
        r = []
        pcs_const = []

        # Spin loop.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins without PCS data.
            if not hasattr(spin, 'pcs'):
                continue

            # Append the PCSs to the list.
            pcs.append(spin.pcs)

            # Append the PCS errors (or a list of None).
            if hasattr(spin, 'pcs_err'):
                pcs_err.append(spin.pcs_err)
            else:
                pcs_err.append([None]*len(spin.pcs))

            # Add empty lists to the r and unit_vector lists.
            unit_vect.append([])
            r.append([])

            # The position list.
            if type(spin.pos[0]) in [float, float64]:
                pos = [spin.pos]
            else:
                pos = spin.pos

            # Loop over the states, and calculate the paramagnetic centre to nucleus unit vectors.
            for c in range(cdp.N):
                # Calculate the electron spin to nuclear spin vector.
                vect = pos[c] - cdp.paramagnetic_centre

                # The length.
                r[-1].append(norm(vect))

                # Append the unit vector.
                unit_vect[-1].append(vect/norm(vect))

        # Convert the distances from Angstrom to meters.
        r = array(r, float64) * 1e-10

        # Loop over experiments.
        for i in xrange(len(cdp.align_tensors)):
            # Append an empty array to the PCS constant structure.
            pcs_const.append([])

            # Get the temperature and spectrometer frequency for the PCS constant.
            id = cdp.align_tensors[i].name
            temp = cdp.temperature[id]
            frq = cdp.frq[id]

            # Convert the frequency of Hertz into a field strength in Tesla units.
            frq = frq * 2.0 * pi / g1H

            # Spin loop.
            j = 0
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins without PCS data.
                if not hasattr(spin, 'pcs'):
                    continue

                # Append an empty array to the PCS constant structure.
                pcs_const[i].append([])

                # Loop over the states, and calculate the PCS constant for each (the distance changes each time).
                for c in range(cdp.N):
                    pcs_const[i][-1].append(pcs_constant(temp, frq, r[j][c]))

                # Spin index.
                j = j + 1

        # Initialise the numpy objects (the pcs matrix is transposed!).
        pcs_numpy = zeros((len(pcs[0]), len(pcs)), float64)
        pcs_err_numpy = zeros((len(pcs[0]), len(pcs)), float64)
        unit_vect_numpy = zeros((len(unit_vect), len(unit_vect[0]), 3), float64)

        # Loop over the spins.
        for spin_index in xrange(len(pcs)):
            # Loop over the alignments.
            for align_index in xrange(len(pcs[spin_index])):
                # Transpose and store the PCS value and error.
                pcs_numpy[align_index, spin_index] = pcs[spin_index][align_index]
                pcs_err_numpy[align_index, spin_index] = pcs_err[spin_index][align_index]

            # Loop over the N states.
            for state_index in xrange(len(unit_vect[spin_index])):
                # Store the unit vector.
                unit_vect_numpy[spin_index, state_index] = unit_vect[spin_index][state_index]

        # Convert the PCS from ppm to no units.
        pcs_numpy = pcs_numpy * 1e-6
        pcs_err_numpy = pcs_err_numpy * 1e-6

        # Return the data structures.
        return pcs_numpy, pcs_err_numpy, unit_vect_numpy, array(pcs_const)


    def __minimise_setup_rdcs(self, param_vector=None, scaling_matrix=None):
        """Set up the data structures for optimisation using RDCs as base data sets.

        @return:    The assembled data structures for using RDCs as the base data for optimisation.
                    These include:
                        - rdcs, the RDC values.
                        - vectors, the heteronucleus to proton vectors.
                        - dj, the dipolar constants.
        @rtype:     tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array)
        """

        # Initialise.
        rdcs = []
        rdc_err = []
        vectors = []
        dj = []

        # Spin loop.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins without RDC data or unit XH bond vectors.
            if not hasattr(spin, 'rdc'):
                # Add rows of None if other data exists.
                if hasattr(spin, 'pcs'):
                    rdcs.append([None]*len(cdp.align_tensors))
                    rdc_err.append([None]*len(cdp.align_tensors))
                    vectors.append([None]*3)
                    dj.append(None)

                # Jump to the next spin.
                continue

            # RDC data exists but the XH bond vectors are missing?
            if not hasattr(spin, 'xh_vect') and not hasattr(spin, 'bond_vect'):
                # Throw a warning.
                warn(RelaxWarning("RDC data exists but the XH bond vectors are missing, skipping spin " + spin_id))

                # Add rows of None if other data exists.
                if hasattr(spin, 'pcs'):
                    rdcs.append([None]*len(cdp.align_tensors))
                    rdc_err.append([None]*len(cdp.align_tensors))
                    vectors.append([None]*3)
                    dj.append(None)

                # Jump to the next spin.
                continue

            # Append the RDC and XH vectors to the lists.
            if hasattr(spin, 'xh_vect'):
                obj = getattr(spin, 'xh_vect')
            else:
                obj = getattr(spin, 'bond_vect')
            rdcs.append(spin.rdc)
            if isinstance(obj[0], float):
                vectors.append([obj])
            else:
                vectors.append(obj)

            # Append the PCS errors (or a list of None).
            if hasattr(spin, 'rdc_err'):
                rdc_err.append(spin.rdc_err)
            else:
                rdc_err.append([None]*len(cdp.align_tensors))

            # Gyromagnetic ratios.
            gx = return_gyromagnetic_ratio(spin.heteronuc_type)
            gh = return_gyromagnetic_ratio(spin.proton_type)

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            dj.append(3.0/(2.0*pi) * dipolar_constant(gx, gh, spin.r))

        # Initialise the numpy objects (the rdc matrix is transposed!).
        rdcs_numpy = zeros((len(rdcs[0]), len(rdcs)), float64)
        rdc_err_numpy = zeros((len(rdcs[0]), len(rdcs)), float64)
        vect_numpy = zeros((len(vectors), len(vectors[0]), 3), float64)

        # Loop over the spins.
        for spin_index in xrange(len(rdcs)):
            # Loop over the alignments.
            for align_index in xrange(len(rdcs[spin_index])):
                # Transpose and store the RDC value and error.
                rdcs_numpy[align_index, spin_index] = rdcs[spin_index][align_index]
                rdc_err_numpy[align_index, spin_index] = rdc_err[spin_index][align_index]

            # Loop over the N states.
            for state_index in xrange(len(vectors[spin_index])):
                # Store the unit vector.
                vect_numpy[spin_index, state_index] = vectors[spin_index][state_index]

        # Return the data structures.
        return rdcs_numpy, rdc_err_numpy, vect_numpy, array(dj, float64)


    def __minimise_setup_tensors(self, sim_index=None):
        """Set up the data structures for optimisation using alignment tensors as base data sets.

        @keyword sim_index: The index of the simulation to optimise.  This should be None if
                            normal optimisation is desired.
        @type sim_index:    None or int
        @return:            The assembled data structures for using alignment tensors as the base
                            data for optimisation.  These include:
                                - full_tensors, the data of the full alignment tensors.
                                - red_tensor_elem, the tensors as concatenated rank-1 5D arrays.
                                - red_tensor_err, the tensor errors as concatenated rank-1 5D
                                arrays.
                                - full_in_ref_frame, flags specifying if the tensor in the reference
                                frame is the full or reduced tensor.
        @rtype:             tuple of (list, numpy rank-1 array, numpy rank-1 array, numpy rank-1
                            array)
        """

        # Initialise.
        n = len(cdp.align_tensors.reduction)
        full_tensors = zeros(n*5, float64)
        red_tensors  = zeros(n*5, float64)
        red_err = ones(n*5, float64) * 1e-5
        full_in_ref_frame = zeros(n, float64)

        # Loop over the full tensors.
        for i, tensor in self.__tensor_loop(red=False):
            # The full tensor.
            full_tensors[5*i + 0] = tensor.Axx
            full_tensors[5*i + 1] = tensor.Ayy
            full_tensors[5*i + 2] = tensor.Axy
            full_tensors[5*i + 3] = tensor.Axz
            full_tensors[5*i + 4] = tensor.Ayz

            # The full tensor corresponds to the frame of reference.
            if cdp.ref_domain == tensor.domain:
                full_in_ref_frame[i] = 1

        # Loop over the reduced tensors.
        for i, tensor in self.__tensor_loop(red=True):
            # The reduced tensor (simulation data).
            if sim_index != None:
                red_tensors[5*i + 0] = tensor.Axx_sim[sim_index]
                red_tensors[5*i + 1] = tensor.Ayy_sim[sim_index]
                red_tensors[5*i + 2] = tensor.Axy_sim[sim_index]
                red_tensors[5*i + 3] = tensor.Axz_sim[sim_index]
                red_tensors[5*i + 4] = tensor.Ayz_sim[sim_index]

            # The reduced tensor.
            else:
                red_tensors[5*i + 0] = tensor.Axx
                red_tensors[5*i + 1] = tensor.Ayy
                red_tensors[5*i + 2] = tensor.Axy
                red_tensors[5*i + 3] = tensor.Axz
                red_tensors[5*i + 4] = tensor.Ayz

            # The reduced tensor errors.
            if hasattr(tensor, 'Axx_err'):
                red_err[5*i + 0] = tensor.Axx_err
                red_err[5*i + 1] = tensor.Ayy_err
                red_err[5*i + 2] = tensor.Axy_err
                red_err[5*i + 3] = tensor.Axz_err
                red_err[5*i + 4] = tensor.Ayz_err

        # Return the data structures.
        return full_tensors, red_tensors, red_err, full_in_ref_frame


    def __tensor_loop(self, red=False):
        """Generator method for looping over the full or reduced tensors.

        @keyword red:   A flag which if True causes the reduced tensors to be returned, and if False
                        the full tensors are returned.
        @type red:      bool
        @return:        The tensor index and the tensor.
        @rtype:         (int, AlignTensorData instance)
        """

        # Number of tensor pairs.
        n = len(cdp.align_tensors.reduction)

        # Alias.
        data = cdp.align_tensors
        list = data.reduction

        # Full or reduced index.
        if red:
            index = 1
        else:
            index = 0

        # Loop over the reduction list.
        for i in range(n):
            yield i, data[list[i][index]]


    def __q_factors_rdc(self):
        """Calculate the Q-factors for the RDC data."""

        # Q-factor list.
        cdp.q_factors_rdc = []
        cdp.q_factors_rdc_norm2 = []

        # Loop over the alignments.
        for i in xrange(len(cdp.align_tensors)):
            # Init.
            D2_sum = 0.0
            sse = 0.0

            # Spin loop.
            dj = None
            N = 0
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins without RDC data.
                if not hasattr(spin, 'rdc') or not hasattr(spin, 'rdc_bc') or spin.rdc[i] == None:
                    continue

                # Sum of squares.
                sse = sse + (spin.rdc[i] - spin.rdc_bc[i])**2

                # Sum the RDCs squared (for one type of normalisation).
                D2_sum = D2_sum + spin.rdc[i]**2

                # Gyromagnetic ratios.
                gx = return_gyromagnetic_ratio(spin.heteronuc_type)
                gh = return_gyromagnetic_ratio(spin.proton_type)

                # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
                dj_new = 3.0/(2.0*pi) * dipolar_constant(gx, gh, spin.r)
                if dj and dj_new != dj:
                    raise RelaxError("All the RDCs must come from the same nucleus type.")
                else:
                    dj = dj_new

                # Increment the number of data sets.
                N = N + 1

            # Normalisation factor of 2Da^2(4 + 3R)/5.
            D = dj * cdp.align_tensors[i].tensor_diag
            Da = 1.0/3.0 * (D[2, 2] - (D[0, 0]+D[1, 1])/2.0)
            Dr = 1.0/3.0 * (D[0, 0] - D[1, 1])
            R = Dr / Da
            norm = 2.0 * (Da)**2 * (4.0 + 3.0*R**2)/5.0
            if Da == 0.0:
                norm = 1e-15

            # The Q-factor for the alignment.
            Q = sqrt(sse / N / norm)
            cdp.q_factors_rdc.append(Q)
            cdp.q_factors_rdc_norm2.append(sqrt(sse / D2_sum))

        # The total Q-factor.
        cdp.q_rdc = 0.0
        cdp.q_rdc_norm2 = 0.0
        for Q in cdp.q_factors_rdc:
            cdp.q_rdc = cdp.q_rdc + Q**2
        for Q in cdp.q_factors_rdc_norm2:
            cdp.q_rdc_norm2 = cdp.q_rdc_norm2 + Q**2
        cdp.q_rdc = sqrt(cdp.q_rdc / len(cdp.q_factors_rdc))
        cdp.q_rdc_norm2 = sqrt(cdp.q_rdc_norm2 / len(cdp.q_factors_rdc_norm2))


    def __q_factors_pcs(self):
        """Calculate the Q-factors for the PCS data."""

        # Q-factor list.
        cdp.q_factors_pcs = []

        # Loop over the alignments.
        for i in xrange(len(cdp.align_tensors)):
            # Init.
            pcs2_sum = 0.0
            sse = 0.0

            # Spin loop.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins without PCS data.
                if not hasattr(spin, 'pcs') or not hasattr(spin, 'pcs_bc') or spin.pcs[i] == None:
                    continue

                # Sum of squares.
                sse = sse + (spin.pcs[i] - spin.pcs_bc[i])**2

                # Sum the PCSs squared (for normalisation).
                pcs2_sum = pcs2_sum + spin.pcs[i]**2

            # The Q-factor for the alignment.
            Q = sqrt(sse / pcs2_sum)
            cdp.q_factors_pcs.append(Q)

        # The total Q-factor.
        cdp.q_pcs = 0.0
        for Q in cdp.q_factors_pcs:
            cdp.q_pcs = cdp.q_pcs + Q**2
        cdp.q_pcs = cdp.q_pcs / len(cdp.q_factors_pcs)
        cdp.q_pcs = sqrt(cdp.q_pcs)


    def __update_model(self):
        """Update the model parameters as necessary."""

        # Initialise the list of model parameters.
        if not hasattr(cdp, 'params'):
            cdp.params = []

        # Determine the number of states (loaded as structural models), if not already set.
        if not hasattr(cdp, 'N'):
            # Set the number.
            if hasattr(cdp, 'structure'):
                cdp.N = cdp.structure.num_models()

            # Otherwise return as the rest cannot be updated without N.
            else:
                return

        # Set up the parameter arrays.
        if not cdp.params:
            # Add the probability or population weight parameters.
            if cdp.model in ['2-domain', 'population']:
                for i in xrange(cdp.N-1):
                    cdp.params.append('p' + repr(i))

            # Add the Euler angle parameters.
            if cdp.model == '2-domain':
                for i in xrange(cdp.N):
                    cdp.params.append('alpha' + repr(i))
                    cdp.params.append('beta' + repr(i))
                    cdp.params.append('gamma' + repr(i))

        # Initialise the probability and Euler angle arrays.
        if cdp.model in ['2-domain', 'population']:
            if not hasattr(cdp, 'probs'):
                cdp.probs = [None] * cdp.N
        if cdp.model == '2-domain':
            if not hasattr(cdp, 'alpha'):
                cdp.alpha = [None] * cdp.N
            if not hasattr(cdp, 'beta'):
                cdp.beta = [None] * cdp.N
            if not hasattr(cdp, 'gamma'):
                cdp.gamma = [None] * cdp.N

        # Determine the data type.
        data_types = self.__base_data_types()

        # Set up alignment tensors for each alignment.
        ids = []
        if 'rdc' in data_types:
            ids = ids+cdp.rdc_ids
        if 'pcs' in data_types:
            ids = ids+cdp.pcs_ids

        # Set up tensors for each alignment.
        for id in ids:
            # No tensors initialised.
            if not hasattr(cdp, 'align_tensors'):
                generic_fns.align_tensor.init(tensor=id, params=[0.0, 0.0, 0.0, 0.0, 0.0])

            # Find if the tensor corresponding to the id exists.
            exists = False
            for tensor in cdp.align_tensors:
                if id == tensor.name:
                    exists = True

            # Initialise the tensor.
            if not exists:
                generic_fns.align_tensor.init(tensor=id, params=[0.0, 0.0, 0.0, 0.0, 0.0])


    def calc_ave_dist(self, atom1, atom2, exp=1):
        """Calculate the average distances.

        The formula used is::

                      _N_
                  / 1 \                  \ 1/exp
            <r> = | -  > |p1i - p2i|^exp |
                  \ N /__                /
                       i

        where i are the members of the ensemble, N is the total number of structural models, and p1
        and p2 at the two atom positions.


        @param atom1:   The atom identification string of the first atom.
        @type atom1:    str
        @param atom2:   The atom identification string of the second atom.
        @type atom2:    str
        @keyword exp:   The exponent used for the averaging, e.g. 1 for linear averaging and -6 for
                        r^-6 NOE averaging.
        @type exp:      int
        @return:        The average distance between the two atoms.
        @rtype:         float
        """

        # Get the spin containers.
        spin1 = return_spin(atom1)
        spin2 = return_spin(atom2)

        # Loop over each model.
        num_models = len(spin1.pos)
        ave_dist = 0.0
        for i in range(num_models):
            # Distance to the minus sixth power.
            dist = norm(spin1.pos[i] - spin2.pos[i])
            ave_dist = ave_dist + dist**(exp)

        # Average.
        ave_dist = ave_dist / num_models

        # The exponent.
        ave_dist = ave_dist**(1.0/exp)

        # Return the average distance.
        return ave_dist


    def calculate(self, verbosity=1):
        """Calculation function.

        Currently this function simply calculates the NOESY flat-bottom quadratic energy potential,
        if NOE restraints are available.

        @param verbosity:       A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        """

        # Test if the N-state model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('N-state')

        # Init some numpy arrays.
        num_restraints = len(cdp.noe_restraints)
        dist = zeros(num_restraints, float64)
        pot = zeros(num_restraints, float64)
        lower = zeros(num_restraints, float64)
        upper = zeros(num_restraints, float64)

        # Loop over the NOEs.
        for i in range(num_restraints):
            # Create arrays of the NOEs.
            lower[i] = cdp.noe_restraints[i][2]
            upper[i] = cdp.noe_restraints[i][3]

            # Calculate the average distances, using -6 power averaging.
            dist[i] = self.calc_ave_dist(cdp.noe_restraints[i][0], cdp.noe_restraints[i][1], exp=-6)

        # Calculate the quadratic potential.
        quad_pot(dist, pot, lower, upper) 

        # Store the distance and potential information.
        cdp.ave_dist = []
        cdp.quad_pot = []
        for i in range(num_restraints):
            cdp.ave_dist.append([cdp.noe_restraints[i][0], cdp.noe_restraints[i][1], dist[i]])
            cdp.quad_pot.append([cdp.noe_restraints[i][0], cdp.noe_restraints[i][1], pot[i]])


    def CoM(self, pivot_point=None, centre=None):
        """Centre of mass analysis.

        This function does an analysis of the centre of mass (CoM) of the N states.  This includes
        calculating the order parameter associated with the pivot-CoM vector, and the associated
        cone of motions.  The pivot_point argument must be supplied.  If centre is None, then the
        CoM will be calculated from the selected parts of the loaded structure.  Otherwise it will
        be set to the centre arg.

        @param pivot_point: The pivot point in the structural file(s).
        @type pivot_point:  list of float of length 3
        @param centre:      The optional centre of mass vector.
        @type centre:       list of float of length 3
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Set the pivot point.
        cdp.pivot_point = pivot_point

        # The centre has been supplied.
        if centre:
            cdp.CoM = centre

        # Calculate from the structure file.
        else:
            cdp.CoM = generic_fns.structure.mass.centre_of_mass()

        # Calculate the vector between the pivot and CoM points.
        cdp.pivot_CoM = array(cdp.CoM, float64) - array(cdp.pivot_point, float64)

        # Calculate the unit vector between the pivot and CoM points.
        unit_vect = cdp.pivot_CoM / norm(cdp.pivot_CoM)

        # Initilise some data structures.
        R = zeros((3, 3), float64)
        vectors = zeros((cdp.N, 3), float64)

        # Loop over the N states.
        for c in xrange(cdp.N):
            # Generate the rotation matrix.
            euler_zyz_to_R(cdp.alpha[c], cdp.beta[c], cdp.gamma[c], R)

            # Rotate the unit vector.
            vectors[c] = dot(R, unit_vect)

            # Multiply by the probability.
            vectors[c] = vectors[c] * cdp.probs[c]

        # Average of the unit vectors.
        cdp.ave_unit_pivot_CoM = sum(vectors)

        # The length reduction.
        cdp.ave_pivot_CoM_red = norm(cdp.ave_unit_pivot_CoM)

        # The aveage pivot-CoM vector.
        cdp.ave_pivot_CoM = norm(cdp.pivot_CoM) * cdp.ave_unit_pivot_CoM

        # The full length rotated pivot-CoM vector.
        cdp.full_ave_pivot_CoM = cdp.ave_pivot_CoM / cdp.ave_pivot_CoM_red

        # The cone angle for diffusion on an axially symmetric cone.
        cdp.theta_diff_on_cone = acos(cdp.ave_pivot_CoM_red)
        cdp.S_diff_on_cone = (3.0*cos(cdp.theta_diff_on_cone)**2 - 1.0) / 2.0

        # The cone angle and order parameter for diffusion in an axially symmetric cone.
        cdp.theta_diff_in_cone = acos(2.*cdp.ave_pivot_CoM_red - 1.)
        cdp.S_diff_in_cone = cos(cdp.theta_diff_in_cone) * (1 + cos(cdp.theta_diff_in_cone)) / 2.0

        # Print out.
        print(("\n%-40s %-20s" % ("Pivot point:", repr(cdp.pivot_point))))
        print(("%-40s %-20s" % ("Moving domain CoM (prior to rotation):", repr(cdp.CoM))))
        print(("%-40s %-20s" % ("Pivot-CoM vector", repr(cdp.pivot_CoM))))
        print(("%-40s %-20s" % ("Pivot-CoM unit vector:", repr(unit_vect))))
        print(("%-40s %-20s" % ("Average of the unit pivot-CoM vectors:", repr(cdp.ave_unit_pivot_CoM))))
        print(("%-40s %-20s" % ("Average of the pivot-CoM vector:", repr(cdp.ave_pivot_CoM))))
        print(("%-40s %-20s" % ("Full length rotated pivot-CoM vector:", repr(cdp.full_ave_pivot_CoM))))
        print(("%-40s %-20s" % ("Length reduction from unity:", repr(cdp.ave_pivot_CoM_red))))
        print(("%-40s %.5f rad (%.5f deg)" % ("Cone angle (diffusion on a cone)", cdp.theta_diff_on_cone, cdp.theta_diff_on_cone / (2*pi) *360.)))
        print(("%-40s S_cone = %.5f (S^2 = %.5f)" % ("S_cone (diffusion on a cone)", cdp.S_diff_on_cone, cdp.S_diff_on_cone**2)))
        print(("%-40s %.5f rad (%.5f deg)" % ("Cone angle (diffusion in a cone)", cdp.theta_diff_in_cone, cdp.theta_diff_in_cone / (2*pi) *360.)))
        print(("%-40s S_cone = %.5f (S^2 = %.5f)" % ("S_cone (diffusion in a cone)", cdp.S_diff_in_cone, cdp.S_diff_in_cone**2)))
        print("\n\n")


    def cone_pdb(self, cone_type=None, scale=1.0, file=None, dir=None, force=False):
        """Create a PDB file containing a geometric object representing the various cone models.

        Currently the only cone types supported are 'diff in cone' and 'diff on cone'.


        @param cone_type:   The type of cone model to represent.
        @type cone_type:    str
        @param scale:       The size of the geometric object is eqaul to the average pivot-CoM
                            vector length multiplied by this scaling factor.
        @type scale:        float
        @param file:        The name of the PDB file to create.
        @type file:         str
        @param dir:         The name of the directory to place the PDB file into.
        @type dir:          str
        @param force:       Flag which if set to True will cause any pre-existing file to be
                            overwritten.
        @type force:        int
        """

        # Test if the cone models have been determined.
        if cone_type == 'diff in cone':
            if not hasattr(cdp, 'S_diff_in_cone'):
                raise RelaxError("The diffusion in a cone model has not yet been determined.")
        elif cone_type == 'diff on cone':
            if not hasattr(cdp, 'S_diff_on_cone'):
                raise RelaxError("The diffusion on a cone model has not yet been determined.")
        else:
            raise RelaxError("The cone type " + repr(cone_type) + " is unknown.")

        # The number of increments for the filling of the cone objects.
        inc = 20

        # The rotation matrix.
        R = zeros((3, 3), float64)
        two_vect_to_R(array([0, 0, 1], float64), cdp.ave_pivot_CoM/norm(cdp.ave_pivot_CoM), R)

        # Create the structural object.
        structure = Internal()

        # Add a structure.
        structure.add_struct(name='cone')

        # Alias the single molecule from the single model.
        mol = structure.structural_data[0].mol[0]

        # Add the pivot point.
        mol.atom_add(pdb_record='HETATM', atom_num=1, atom_name='R', res_name='PIV', res_num=1, pos=cdp.pivot_point, element='C')

        # Generate the average pivot-CoM vectors.
        print("\nGenerating the average pivot-CoM vectors.")
        sim_vectors = None
        if hasattr(cdp, 'ave_pivot_CoM_sim'):
            sim_vectors = cdp.ave_pivot_CoM_sim
        res_num = generic_fns.structure.geometric.generate_vector_residues(mol=mol, vector=cdp.ave_pivot_CoM, atom_name='Ave', res_name_vect='AVE', sim_vectors=sim_vectors, res_num=2, origin=cdp.pivot_point, scale=scale)

        # Generate the cone outer edge.
        print("\nGenerating the cone outer edge.")
        if cone_type == 'diff in cone':
            angle = cdp.theta_diff_in_cone
        elif cone_type == 'diff on cone':
            angle = cdp.theta_diff_on_cone
        cap_start_atom = mol.atom_num[-1]+1
        generic_fns.structure.geometric.cone_edge(mol=mol, res_name='CON', res_num=3, apex=cdp.pivot_point, R=R, angle=angle, length=norm(cdp.pivot_CoM), inc=inc)

        # Generate the cone cap, and stitch it to the cone edge.
        if cone_type == 'diff in cone':
            print("\nGenerating the cone cap.")
            cone_start_atom = mol.atom_num[-1]+1
            generic_fns.structure.geometric.generate_vector_dist(mol=mol, res_name='CON', res_num=3, centre=cdp.pivot_point, R=R, max_angle=angle, scale=norm(cdp.pivot_CoM), inc=inc)
            generic_fns.structure.geometric.stitch_cap_to_cone(mol=mol, cone_start=cone_start_atom, cap_start=cap_start_atom+1, max_angle=angle, inc=inc)

        # Create the PDB file.
        print("\nGenerating the PDB file.")
        pdb_file = open_write_file(file, dir, force=force)
        structure.write_pdb(pdb_file)
        pdb_file.close()


    default_value_doc = """
        N-state model default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ______________________________________________________________________________________
        |                             |                             |                        |
        | Data type                   | Object name                 | Value                  |
        |_____________________________|_____________________________|________________________|
        |                             |                             |                        |
        | Probabilities               | 'p0', 'p1', 'p2', ..., 'pN' | 1/N                    |
        |                             |                             |                        |
        | Euler angle alpha           | 'alpha0', 'alpha1', ...     | (c+1) * pi / (N+1)     |
        |                             |                             |                        |
        | Euler angle beta            | 'beta0', 'beta1', ...       | (c+1) * pi / (N+1)     |
        |                             |                             |                        |
        | Euler angle gamma           | 'gamma0', 'gamma1', ...     | (c+1) * pi / (N+1)     |
        |_____________________________|_____________________________|________________________|

        In this table, N is the total number of states and c is the index of a given state ranging
        from 0 to N-1.  The default probabilities are all set to be equal whereas the angles are
        given a range of values so that no 2 states are equal at the start of optimisation.

        Note that setting the probability for state N will do nothing as it is equal to one minus
        all the other probabilities.
        """

    def default_value(self, param):
        """The default N-state model parameter values.

        @param param:   The N-state model parameter.
        @type param:    str
        @return:        The default value.
        @rtype:         float
        """

        # Split the parameter into its base name and index.
        name, index = self.return_data_name(param, index=True)

        # The number of states as a float.
        N = float(cdp.N)

        # Probability.
        if name == 'probs':
            return 1.0 / N

        # Euler angles.
        elif name == 'alpha' or name == 'beta' or name == 'gamma':
            return (float(index)+1) * pi / (N+1.0)


    def grid_search(self, lower, upper, inc, constraints=False, verbosity=0, sim_index=None):
        """The grid search function.

        @param lower:       The lower bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          array of int
        @param constraints: If True, constraints are applied during the grid search (elinating parts
                            of the grid).  If False, no constraints are used.
        @type constraints:  bool
        @param verbosity:   A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        """

        # Test if the N-state model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('N-state')

        # The number of parameters.
        n = self.param_num()

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            print("Cannot run a grid search on a model with zero parameters, skipping the grid search.")
            return

        # Test the grid search options.
        self.test_grid_ops(lower=lower, upper=upper, inc=inc, n=n)

        # If inc is a single int, convert it into an array of that value.
        if isinstance(inc, int):
            inc = [inc]*n

        # Setup the default bounds.
        if not lower:
            # Init.
            lower = []
            upper = []

            # Loop over the parameters.
            for i in range(n):
                # i is in the parameter array.
                if i < len(cdp.params):
                    # Probabilities (default values).
                    if search('^p', cdp.params[i]):
                        lower.append(0.0)
                        upper.append(1.0)

                    # Angles (default values).
                    if search('^alpha', cdp.params[i]) or search('^gamma', cdp.params[i]):
                        lower.append(0.0)
                        upper.append(2*pi)
                    elif search('^beta', cdp.params[i]):
                        lower.append(0.0)
                        upper.append(pi)
    
                # Otherwise this must be an alignment tensor component.
                else:
                    lower.append(-1e-3)
                    upper.append(1e-3)

        # Minimisation.
        self.minimise(min_algor='grid', min_options=[inc, lower, upper], constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        False
        @rtype:         bool
        """

        # Spin specific parameters.
        if name in ['bond_length', 'heteronucleus', 'proton']:
            return True

        # All other parameters are global.
        return False


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None):
        """Minimisation function.

        @param min_algor:       The minimisation algorithm to use.
        @type min_algor:        str
        @param min_options:     An array of options to be used by the minimisation algorithm.
        @type min_options:      array of str
        @param func_tol:        The function tolerance which, when reached, terminates optimisation.
                                Setting this to None turns of the check.
        @type func_tol:         None or float
        @param grad_tol:        The gradient tolerance which, when reached, terminates optimisation.
                                Setting this to None turns of the check.
        @type grad_tol:         None or float
        @param max_iterations:  The maximum number of iterations for the algorithm.
        @type max_iterations:   int
        @param constraints:     If True, constraints are used during optimisation.
        @type constraints:      bool
        @param scaling:         If True, diagonal scaling is enabled during optimisation to allow
                                the problem to be better conditioned.
        @type scaling:          bool
        @param verbosity:       A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @param sim_index:       The index of the simulation to optimise.  This should be None if
                                normal optimisation is desired.
        @type sim_index:        None or int
        """

        # Test if the N-state model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('N-state')

        # '2-domain' model setup tests.
        if cdp.model == '2-domain':
            # The number of states.
            if not hasattr(cdp, 'N'):
                raise RelaxError("The number of states has not been set.")

            # The reference domain.
            if not hasattr(cdp, 'ref_domain'):
                raise RelaxError("The reference domain has not been set.")

        # Right, constraints cannot be used for the 'fixed' model.
        if constraints and cdp.model == 'fixed':
            warn(RelaxWarning("Turning constraints off.  These cannot be used for the 'fixed' model."))
            constraints = False

            # Pop out the Method of Multipliers algorithm.
            if min_algor == 'Method of Multipliers':
                min_algor = min_options[0]
                min_options = min_options[1:]

        # Update the model parameters if necessary.
        self.__update_model()

        # Create the initial parameter vector.
        param_vector = self.__assemble_param_vector(sim_index=sim_index)

        # Determine if alignment tensors or RDCs are to be used.
        data_types = self.__base_data_types()

        # Diagonal scaling.
        scaling_matrix = self.__assemble_scaling_matrix(data_types=data_types, scaling=scaling)
        param_vector = dot(inv(scaling_matrix), param_vector)

        # Linear constraints.
        if constraints:
            A, b = self.__linear_constraints(data_types=data_types, scaling_matrix=scaling_matrix)
        else:
            A, b = None, None

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, red_tensor_elem, red_tensor_err, full_in_ref_frame = None, None, None, None
        if 'tensor' in data_types:
            full_tensors, red_tensor_elem, red_tensor_err, full_in_ref_frame = self.__minimise_setup_tensors(sim_index=sim_index)

        # Get the data structures for optimisation using PCSs as base data sets.
        pcs, pcs_err, pcs_vect, pcs_dj = None, None, None, None
        if 'pcs' in data_types:
            pcs, pcs_err, pcs_vect, pcs_dj = self.__minimise_setup_pcs()

        # Get the data structures for optimisation using RDCs as base data sets.
        rdcs, rdc_err, xh_vect, rdc_dj = None, None, None, None
        if 'rdc' in data_types:
            rdcs, rdc_err, xh_vect, rdc_dj = self.__minimise_setup_rdcs()

        # Set up the class instance containing the target function.
        model = N_state_opt(model=cdp.model, N=cdp.N, init_params=param_vector, full_tensors=full_tensors, red_data=red_tensor_elem, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame, pcs=pcs, rdcs=rdcs, pcs_errors=pcs_err, rdc_errors=rdc_err, pcs_vect=pcs_vect, xh_vect=xh_vect, pcs_const=pcs_dj, dip_const=rdc_dj, scaling_matrix=scaling_matrix)

        # Grid search.
        if search('^[Gg]rid', min_algor):
            results = grid(func=model.func, args=(), num_incs=min_options[0], lower=min_options[1], upper=min_options[2], A=A, b=b, verbosity=verbosity)

            # Unpack the results.
            param_vector, func, iter_count, warning = results
            f_count = iter_count
            g_count = 0.0
            h_count = 0.0

        # Minimisation.
        else:
            results = generic_minimise(func=model.func, dfunc=model.dfunc, d2func=model.d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)

            # Unpack the results.
            if results == None:
                return
            param_vector, func, iter_count, f_count, g_count, h_count, warning = results

        # Catch infinite chi-squared values.
        if isInf(func):
            raise RelaxInfError('chi-squared')

        # Catch chi-squared values of NaN.
        if isNaN(func):
            raise RelaxNaNError('chi-squared')

        # Scaling.
        if scaling:
            param_vector = dot(scaling_matrix, param_vector)

        # Disassemble the parameter vector.
        self.__disassemble_param_vector(param_vector=param_vector, data_types=data_types, sim_index=sim_index)

        # Monte Carlo minimisation statistics.
        if sim_index != None:
            # Chi-squared statistic.
            cdp.chi2_sim[sim_index] = func

            # Iterations.
            cdp.iter_sim[sim_index] = iter_count

            # Function evaluations.
            cdp.f_count_sim[sim_index] = f_count

            # Gradient evaluations.
            cdp.g_count_sim[sim_index] = g_count

            # Hessian evaluations.
            cdp.h_count_sim[sim_index] = h_count

            # Warning.
            cdp.warning_sim[sim_index] = warning

        # Normal statistics.
        else:
            # Chi-squared statistic.
            cdp.chi2 = func

            # Iterations.
            cdp.iter = iter_count

            # Function evaluations.
            cdp.f_count = f_count

            # Gradient evaluations.
            cdp.g_count = g_count

            # Hessian evaluations.
            cdp.h_count = h_count

            # Warning.
            cdp.warning = warning

        # Statistical analysis.
        if 'rdc' in data_types or 'pcs' in data_types:
            # Get the final back calculated data (for the Q-factor and
            self.__minimise_bc_data(model)

            # Calculate the RDC Q-factors.
            if 'rdc' in data_types:
                self.__q_factors_rdc()

            # Calculate the PCS Q-factors.
            if 'pcs' in data_types:
                self.__q_factors_pcs()


    def model_statistics(self, instance=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword instance:      This is the optimisation instance index.  This should always be the
                                value of 1 for the N-state model.  As it is ignored, this arg can be
                                anything.
        @type instance:         None or int
        @keyword spin_id:       The spin identification string.  This is ignored in the N-state
                                model.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are
                                returned.  For the N-state model, this argument is ignored.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of
                                parameters (k), the number of data points (n), and the chi-squared
                                value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Return the values.
        return self.param_num(), self.num_data_points(), cdp.chi2


    def num_data_points(self):
        """Determine the number of data points used in the model.

        @return:    The number, n, of data points in the model.
        @rtype:     int
        """

        # Determine the data type.
        data_types = self.__base_data_types()

        # Init.
        n = 0

        # Spin loop.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # RDC data (skipping array elements set to None).
            if 'rdc' in data_types:
                if hasattr(spin, 'rdc'):
                    for rdc in spin.rdc:
                        if isinstance(rdc, float):
                            n = n + 1

            # PCS data (skipping array elements set to None).
            if 'pcs' in data_types:
                if hasattr(spin, 'pcs'):
                    for pcs in spin.pcs:
                        if isinstance(pcs, float):
                            n = n + 1

        # Alignment tensors.
        if 'tensor' in data_types:
            n = n + 5*len(cdp.align_tensors)

        # Return the value.
        return n


    def number_of_states(self, N=None):
        """Set the number of states in the N-state model.

        @param N:   The number of states.
        @type N:    int
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test if the model is setup.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('N-state')

        # Set the value of N.
        cdp.N = N

        # Update the model.
        self.__update_model()


    def ref_domain(self, ref=None):
        """Set the reference domain for the '2-domain' N-state model.

        @param ref: The reference domain.
        @type ref:  str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test if the model is setup.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('N-state')

        # Test that the correct model is set.
        if cdp.model != '2-domain':
            raise RelaxError("Setting the reference domain is only possible for the '2-domain' N-state model.")

        # Test if the reference domain exists.
        exists = False
        for tensor_cont in cdp.align_tensors:
            if tensor_cont.domain == ref:
                exists = True
        if not exists:
            raise RelaxError("The reference domain cannot be found within any of the loaded tensors.")

        # Set the reference domain.
        cdp.ref_domain = ref

        # Update the model.
        self.__update_model()


    def param_num(self):
        """Determine the number of parameters in the model.

        @return:    The number of model parameters.
        @rtype:     int
        """

        # Determine the data type.
        data_types = self.__base_data_types()

        # Init.
        num = 0

        # Alignment tensor params.
        if 'rdc' in data_types or 'pcs' in data_types:
            num = num + 5*len(cdp.align_tensors)

        # Populations.
        if cdp.model in ['2-domain', 'population']:
            num = num + (cdp.N - 1)

        # Euler angles.
        if cdp.model == '2-domain':
            num = num + 3*cdp.N

        # Return the param number.
        return num


    return_data_name_doc = """
        N-state model data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |                             |                                   |
        | Data type              | Object name                 | Patterns                          |
        |________________________|_____________________________|___________________________________|
        |                        |                             |                                   |
        | Probabilities          | 'probs'                     | 'p0', 'p1', 'p2', ..., 'pN'       |
        |                        |                             |                                   |
        | Euler angle alpha      | 'alpha'                     | 'alpha0', 'alpha1', ...           |
        |                        |                             |                                   |
        | Euler angle beta       | 'beta'                      | 'beta0', 'beta1', ...             |
        |                        |                             |                                   |
        | Euler angle gamma      | 'gamma'                     | 'gamma0', 'gamma1', ...           |
        |                        |                             |                                   |
        | Bond length            | 'r'                         | '^r$' or '[Bb]ond[ -_][Ll]ength'  |
        |                        |                             |                                   |
        | Heteronucleus type     | 'heteronuc_type'            | '^[Hh]eteronucleus$'              |
        |                        |                             |                                   |
        | Proton type            | 'proton_type'               | '^[Pp]roton$'                     |
        |________________________|_____________________________|___________________________________|

        The objects corresponding to the object names are lists (or arrays) with each element
        corrsponding to each state.
        """

    def return_data_name(self, name, index=None):
        """Return a unique identifying string for the N-state model parameter.

        @param name:    The N-state model parameter.
        @type name:     str
        @keyword index: The probability parameter index.
        @type index:    None or int
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # Probability.
        if search('^p[0-9]*$', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[1:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'probs', i
            else:
                return 'probs'

        # Alpha Euler angle.
        if search('^alpha', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[5:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'alpha', i
            else:
                return 'alpha'

        # Beta Euler angle.
        if search('^beta', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[4:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'beta', i
            else:
                return 'beta'

        # Gamma Euler angle.
        if search('^gamma', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[5:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'gamma', i
            else:
                return 'gamma'


        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            if index:
                return 'r', None
            else:
                return 'r'

        # Heteronucleus type.
        if search('^[Hh]eteronucleus$', name):
            if index:
                return 'heteronuc_type', None
            else:
                return 'heteronuc_type'

        # Proton type.
        if search('^[Pp]roton$', name):
            if index:
                return 'proton_type', None
            else:
                return 'proton_type'

        # Return nothing.
        if index:
            return None, None
        else:
            return None


    def select_model(self, model=None):
        """Select the N-state model type.

        @param model:   The N-state model type.  Can be one of '2-domain', 'population', or 'fixed'.
        @type model:    str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test if the model is setup.
        if hasattr(cdp, 'model'):
            raise RelaxModelError('N-state')

        # Test if the model name exists.
        if not model in ['2-domain', 'population', 'fixed']:
            raise RelaxError("The model name " + repr(model) + " is invalid.")

        # Set the model
        cdp.model = model

        # Initialise the list of model parameters.
        cdp.params = []

        # Update the model.
        self.__update_model()


    set_doc = """
        N-state model set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~

        Setting parameters for the N-state model is a little different from the other type of
        analyses as each state has a set of parameters with the same names as the other states.
        To set the parameters for a specific state c (ranging from 0 for the first to N-1 for the
        last, the number c should be added to the end of the parameter name.  So the Euler angle
        gamma of the third state is specified using the string 'gamma2'.

        """


    def set_non_spin_params(self, value=None, param=None):
        """Function for setting all the N-state model parameter values.

        @param value:   The parameter values (for defaults supply [None]).
        @type value:    list of numbers or [None]
        @param param:   The parameter names.
        @type param:    None, str, or list of str
        """

        # Get the model parameters if param is None.
        if param == None:
            param = cdp.params

        # Test that the parameter and value lists are the same size.
        if isinstance(param, list) and value[0] != None and len(param) != len(value):
            raise RelaxError("The length of " + repr(len(value)) + " of the value array must be equal to the length of the parameter array, " + repr(param) + ".")

        # Convert param to a list (if it is a string).
        if isinstance(param, str):
            param = [param]

        # If no value is supplied (i.e. value == [None]), then get the default values.
        if value == [None]:
            value = []
            for i in xrange(len(param)):
                value.append(self.default_value(param[i]))

        # Set the parameter values.
        for i in xrange(len(param)):
            # Get the object name and the parameter index.
            object_name, index = self.return_data_name(param[i], index=True)
            if not object_name:
                raise RelaxError("The data type " + repr(param[i]) + " does not exist.")

            # Simple objects (not a list).
            if index == None:
                setattr(cdp, object_name, value[i])

            # List objects.
            else:
                # Get the object.
                object = getattr(cdp, object_name)

                # Set the parameter value.
                object[index] = value[i]
