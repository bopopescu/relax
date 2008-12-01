###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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
"""The relaxation curve fitting specific code."""

# Python module imports.
from math import sqrt
from numpy import array, average, dot, float64, identity, zeros
from numpy.linalg import inv
from re import match, search
import sys

# relax module imports.
from dep_check import C_module_exp_fn
from base_class import Common_functions
from generic_fns import pipes
from generic_fns.mol_res_spin import count_spins, exists_mol_res_spin_data, generate_spin_id, return_spin, spin_loop
from minfx.generic import generic_minimise
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxLenError, RelaxNoModelError, RelaxNoSequenceError

# C modules.
if C_module_exp_fn:
    from maths_fns.relax_fit import setup, func, dfunc, d2func, back_calc_I


class Relax_fit(Common_functions):
    """Class containing functions for relaxation curve fitting."""

    def assemble_param_vector(self, spin=None, sim_index=None):
        """Assemble the exponential curve parameter vector (as a numpy array).

        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        @return:                An array of the parameter values of the exponential model.
        @rtype:                 numpy array
        """

        # Initialise.
        param_vector = []

        # Loop over the model parameters.
        for i in xrange(len(spin.params)):
            # Relaxation rate.
            if spin.params[i] == 'Rx':
                if sim_index != None:
                    param_vector.append(spin.rx_sim[sim_index])
                elif spin.rx == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.rx)

            # Initial intensity.
            elif spin.params[i] == 'I0':
                if sim_index != None:
                    param_vector.append(spin.i0_sim[sim_index])
                elif spin.i0 == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.i0)

            # Intensity at infinity.
            elif spin.params[i] == 'Iinf':
                if sim_index != None:
                    param_vector.append(spin.iinf_sim[sim_index])
                elif spin.iinf == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.iinf)

        # Return a numpy array.
        return array(param_vector, float64)


    def assemble_scaling_matrix(self, spin=None, scaling=True):
        """Create and return the scaling matrix.

        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword scaling:       A flag which if false will cause the identity matrix to be returned.
        @type scaling:          bool
        @return:                The diagonal and square scaling matrix.
        @rtype:                 numpy diagonal matrix
        """

        # Initialise.
        scaling_matrix = identity(len(spin.params), float64)
        i = 0

        # No diagonal scaling.
        if not scaling:
            return scaling_matrix

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Loop over the parameters.
        for i in xrange(len(spin.params)):
            # Relaxation rate.
            if spin.params[i] == 'Rx':
                pass

            # Intensity scaling.
            elif search('^i', spin.params[i]):
                # Find the position of the first time point.
                pos = cdp.relax_times.index(min(cdp.relax_times))

                # Scaling.
                scaling_matrix[i, i] = 1.0 / average(spin.intensities[pos])

            # Increment i.
            i = i + 1

        # Return the scaling matrix.
        return scaling_matrix


    def back_calc(self, spin=None, relax_time_index=None):
        """Back-calculation of peak intensity for the given relaxation time.

        @keyword spin:              The spin container.
        @type spin:                 SpinContainer instance
        @keyword relax_time_index:  The index for the desired relaxation time.
        @type relax_time_index:     int
        @return:                    The peak intensity for the desired relaxation time.
        @rtype:                     float
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Create the initial parameter vector.
        param_vector = self.assemble_param_vector(spin=spin)

        # Create a scaling matrix.
        scaling_matrix = self.assemble_scaling_matrix(spin=spin, scaling=False)

        # Initialise the relaxation fit functions.
        setup(num_params=len(spin.params), num_times=len(cdp.relax_times), values=spin.intensities, sd=spin.intensity_err, relax_times=cdp.relax_times, scaling_matrix=scaling_matrix)

        # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
        func(param_vector)

        # Get the data back.
        results = back_calc_I()

        # Return the correct peak height.
        return results[relax_time_index]


    def create_mc_data(self, spin_id):
        """Create the Monte Carlo peak intensity data.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator
                        method.
        @type spin_id:  str
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # Initialise the MC data data structure.
        mc_data = []

        # Get the spin container.
        spin = return_spin(spin_id)

        # Skip deselected spins.
        if not spin.select:
            return

        # Skip spins which have no data.
        if not hasattr(spin, 'intensities'):
            return

        # Test if the model is set.
        if not hasattr(spin, 'model') or not spin.model:
            raise RelaxNoModelError

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Loop over the spectral time points.
        for j in xrange(len(cdp.relax_times)):
            # Back calculate the value.
            value = self.back_calc(spin=spin, relax_time_index=j)

            # Append the value.
            mc_data.append(value)

        # Return the MC data.
        return mc_data


    def data_init(self, spin):
        """Initialise the spin specific data structures.

        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        """

        # Loop over the data structure names.
        for name in self.data_names():
            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Otherwise initialise the data structure to None.
            else:
                init_data = None

            # If the name is not in 'spin', add it.
            if not hasattr(spin, name):
                setattr(spin, name, init_data)


    def data_names(self, set='all', error_names=False, sim_names=False):
        """Function for returning a list of names of data structures.

        Description
        ===========

        The names are as follows:

            - 'params', an array of the parameter names associated with the model.
            - 'rx', either the R1 or R2 relaxation rate.
            - 'i0', the initial intensity.
            - 'iinf', the intensity at infinity.
            - 'chi2', chi-squared value.
            - 'iter', iterations.
            - 'f_count', function count.
            - 'g_count', gradient count.
            - 'h_count', hessian count.
            - 'warning', minimisation warning.


        @keyword set:           The set of object names to return.  This can be set to 'all' for all
                                names, to 'generic' for generic object names, 'params' for
                                model-free parameter names, or to 'min' for minimisation specific
                                object names.
        @type set:              str
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object
                                names as well.
        @type sim_names:        bool
        @return:                The list of object names.
        @rtype:                 list of str
        """

        # Initialise.
        names = []

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('rx')
            names.append('i0')
            names.append('iinf')

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        # Parameter errors.
        if error_names and (set == 'all' or set == 'params'):
            names.append('rx_err')
            names.append('i0_err')
            names.append('iinf_err')

        # Parameter simulation values.
        if sim_names and (set == 'all' or set == 'params'):
            names.append('rx_sim')
            names.append('i0_sim')
            names.append('iinf_sim')

        # Return the names.
        return names


    def default_value(self, param):
        """
        Relaxation curve fitting default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        These values are completely arbitrary as peak heights (or volumes) are extremely variable
        and the Rx value is a compensation for both the R1 and R2 values.
        ___________________________________________________________________
        |                        |               |                        |
        | Data type              | Object name   | Value                  |
        |________________________|_______________|________________________|
        |                        |               |                        |
        | Relaxation rate        | 'rx'          | 8.0                    |
        |                        |               |                        |
        | Initial intensity      | 'i0'          | 10000.0                |
        |                        |               |                        |
        | Intensity at infinity  | 'iinf'        | 0.0                    |
        |                        |               |                        |
        |________________________|_______________|________________________|

        """

        # Relaxation rate.
        if param == 'rx':
            return 8.0

        # Initial intensity.
        if param == 'i0':
            return 10000.0

        # Intensity at infinity.
        if param == 'iinf':
            return 0.0


    def disassemble_param_vector(self, param_vector=None, spin=None, sim_index=None):
        """Disassemble the parameter vector.

        @keyword param_vector:  The parameter vector.
        @type param_vector:     numpy array
        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Monte Carlo simulations.
        if sim_index != None:
            # The relaxation rate.
            spin.rx_sim[sim_index] = param_vector[0]

            # Initial intensity.
            spin.i0_sim[sim_index] = param_vector[1]

            # Intensity at infinity.
            if cdp.curve_type == 'inv':
                spin.iinf_sim[sim_index] = param_vector[2]

        # Parameter values.
        else:
            # The relaxation rate.
            spin.rx = param_vector[0]

            # Initial intensity.
            spin.i0 = param_vector[1]

            # Intensity at infinity.
            if cdp.curve_type == 'inv':
                spin.iinf = param_vector[2]


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The exponential curve fitting grid search function.

        @keyword lower:         The lower bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.
                                The number of elements in the array must equal to the number of
                                parameters in the model.
        @type inc:              array of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating
                                parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The index of the simulation to apply the grid search to.  If None,
                                the normal model is optimised.
        @type sim_index:        int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def grid_search_setup(self, spin=None, param_vector=None, lower=None, upper=None, inc=None, scaling_matrix=None):
        """The grid search setup function.

        @keyword spin:              The spin data container.
        @type spin:                 SpinContainer instance
        @keyword param_vector:      The parameter vector.
        @type param_vector:         numpy array
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is
                                    only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is
                                    only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid
                                    search.  The number of elements in the array must equal to the
                                    number of parameters in the model.  This argument is only used
                                    when doing a grid search.
        @type inc:                  array of int
        @keyword scaling_matrix:    The scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @return:                    A tuple of the grid size and the minimisation options.  For the
                                    minimisation options, the first dimension corresponds to the
                                    model parameter.  The second dimension is a list of the number
                                    of increments, the lower bound, and upper bound.
        @rtype:                     (int, list of lists [int, float, float])
        """

        # The length of the parameter array.
        n = len(param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError, "Cannot run a grid search on a model with zero parameters."

        # Lower bounds.
        if lower != None:
            if len(lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if upper != None:
            if len(upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Increment.
        if type(inc) == list:
            if len(inc) != n:
                raise RelaxLenError, ('increment', n)
            inc = inc
        elif type(inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(inc)
            inc = temp

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Minimisation options initialisation.
        min_options = []
        j = 0

        # Loop over the parameters.
        for i in xrange(len(spin.params)):
            # Relaxation rate (from 0 to 20 s^-1).
            if spin.params[i] == 'Rx':
                min_options.append([inc[j], 0.0, 20.0])

            # Intensity
            elif search('^I', spin.params[i]):
                # Find the position of the first time point.
                pos = cdp.relax_times.index(min(cdp.relax_times))

                # Scaling.
                min_options.append([inc[j], 0.0, average(spin.intensities[pos])])

            # Increment j.
            j = j + 1

        # Set the lower and upper bounds if these are supplied.
        if lower != None:
            for j in xrange(n):
                if lower[j] != None:
                    min_options[j][1] = lower[j]
        if upper != None:
            for j in xrange(n):
                if upper[j] != None:
                    min_options[j][2] = upper[j]

        # Test if the grid is too large.
        grid_size = 1
        for i in xrange(len(min_options)):
            grid_size = grid_size * min_options[i][0]
        if type(grid_size) == long:
            raise RelaxError, "A grid search of size " + `grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / scaling_matrix[j, j]

        return grid_size, min_options


    def linear_constraints(self, spin=None, scaling_matrix=None):
        """Set up the relaxation curve fitting linear constraint matrices A and b.

        Standard notation
        =================

        The relaxation rate constraints are::

            Rx >= 0

        The intensity constraints are::

            I0 >= 0
            Iinf >= 0


        Matrix notation
        ===============

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are::

            | 1  0  0 |     |  Rx  |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |  .  |  I0  |  >=  |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     | Iinf |      |    0    |


        @keyword spin:              The spin data container.
        @type spin:                 SpinContainer instance
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(spin.params)
        zero_array = zeros(n, float64)
        i = 0
        j = 0

        # Loop over the parameters.
        for k in xrange(len(spin.params)):
            # Relaxation rate.
            if spin.params[k] == 'Rx':
                # Rx >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Intensity parameter.
            elif search('^I', spin.params[k]):
                # I0, Iinf >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Increment i.
            i = i + 1

        # Convert to numpy data structures.
        A = array(A, float64)
        b = array(b, float64)

        return A, b


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Relaxation curve fitting function.

        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerence which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerence which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow
                                    the problem to be better conditioned.
        @type scaling:              bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the
                                    greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if
                                    normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.
                                    The number of elements in the array must equal to the number of
                                    parameters in the model.  This argument is only used when doing a
                                    grid search.
        @type inc:                  array of int
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over the sequence.
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins which have no data.
            if not hasattr(spin, 'intensities'):
                continue

            # Create the initial parameter vector.
            param_vector = self.assemble_param_vector(spin=spin)

            # Diagonal scaling.
            scaling_matrix = self.assemble_scaling_matrix(spin=spin, scaling=scaling)
            if len(scaling_matrix):
                param_vector = dot(inv(scaling_matrix), param_vector)

            # Get the grid search minimisation options.
            if match('^[Gg]rid', min_algor):
                grid_size, min_options = self.grid_search_setup(spin=spin, param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

            # Linear constraints.
            if constraints:
                A, b = self.linear_constraints(spin=spin, scaling_matrix=scaling_matrix)

            # Print out.
            if verbosity >= 1:
                # Get the spin id string.
                spin_id = generate_spin_id(mol_name, res_num, res_name, spin.num, spin.name)

                # Individual spin print out.
                if verbosity >= 2:
                    print "\n\n"

                string = "Fitting to spin " + `spin_id`
                print "\n\n" + string
                print len(string) * '~'

                # Grid search print out.
                if match('^[Gg]rid', min_algor):
                    print "Unconstrained grid search size: " + `grid_size` + " (constraints may decrease this size).\n"


            # Initialise the function to minimise.
            ######################################

            if sim_index == None:
                values = spin.ave_intensities
            else:
                values = spin.sim_intensities[sim_index]

            setup(num_params=len(spin.params), num_times=len(cdp.relax_times), values=values, sd=cdp.sigma_I, relax_times=cdp.relax_times, scaling_matrix=scaling_matrix)


            # Setup the minimisation algorithm when constraints are present.
            ################################################################

            if constraints and not match('^[Gg]rid', min_algor):
                algor = min_options[0]
            else:
                algor = min_algor


            # Levenberg-Marquardt minimisation.
            ###################################

            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                # Reconstruct the error data structure.
                lm_error = zeros(len(spin.relax_times), float64)
                index = 0
                for k in xrange(len(spin.relax_times)):
                    lm_error[index:index+len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.relax_fit.lm_dri, lm_error)


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)
            else:
                results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=True, print_flag=verbosity)
            if results == None:
                return
            param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

            # Scaling.
            if scaling:
                param_vector = dot(scaling_matrix, param_vector)

            # Disassemble the parameter vector.
            self.disassemble_param_vector(param_vector=param_vector, spin=spin, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Chi-squared statistic.
                spin.chi2_sim[sim_index] = chi2

                # Iterations.
                spin.iter_sim[sim_index] = iter_count

                # Function evaluations.
                spin.f_count_sim[sim_index] = f_count

                # Gradient evaluations.
                spin.g_count_sim[sim_index] = g_count

                # Hessian evaluations.
                spin.h_count_sim[sim_index] = h_count

                # Warning.
                spin.warning_sim[sim_index] = warning


            # Normal statistics.
            else:
                # Chi-squared statistic.
                spin.chi2 = chi2

                # Iterations.
                spin.iter = iter_count

                # Function evaluations.
                spin.f_count = f_count

                # Gradient evaluations.
                spin.g_count = g_count

                # Hessian evaluations.
                spin.h_count = h_count

                # Warning.
                spin.warning = warning


    def model_setup(self, model, params):
        """Update various model specific data structures.

        @param model:   The exponential curve type.
        @type model:    str
        @param params:  A list consisting of the model parameters.
        @type params:   list of str
        """

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Set the model.
        cdp.curve_type = model

        # Loop over the sequence.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Initialise the data structures (if needed).
            self.data_init(spin)

            # The model and parameter names.
            spin.model = model
            spin.params = params


    def overfit_deselect(self):
        """Deselect spins which have insufficient data to support minimisation."""

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        for spin in spin_loop():
            # Check if data exists.
            if not hasattr(spin, 'intensities'):
                spin.select = False
                continue

            # Require 3 or more data points.
            if len(spin.intensities) < 3:
                spin.select = False
                continue


    def relax_time(self, time=0.0, spectrum_id=None):
        """Set the relaxation time period associated with a given spectrum.

        @keyword time:          The time, in seconds, of the relaxation period.
        @type time:             float
        @keyword spectrum_id:   The spectrum identification string.
        @type spectrum_id:      str
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the spectrum id exists.
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxError, "The peak heights corresponding to spectrum id '%s' have not been loaded." % spectrum_id

        # Store the relaxation time in the class instance.
        self.__relax_time = float(time)

        # The index.
        index = cdp.spectrum_ids.index(spectrum_id)

        # Initialise the global relaxation time data structure if needed.
        if not hasattr(cdp, 'relax_times'):
            cdp.relax_times = [None] * len(cdp.spectrum_ids)

        # Index not present in the global relaxation time data structure.
        while 1:
            if index > len(cdp.relax_times) - 1:
                cdp.relax_times.append(None)
            else:
                break

        # Add the time at the correct position.
        cdp.relax_times[index] = time


    def return_data(self, spin):
        """Function for returning the peak intensity data structure.

        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        @return:        The peak intensity data structure.
        @rtype:         list of float
        """

        return spin.intensities


    def return_error(self, spin_id):
        """Return the standard deviation data structure.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator
                        method.
        @type spin_id:  str
        @return:        The standard deviation data structure.
        @rtype:         list of float
        """

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        return cdp.sigma_I


    def return_data_name(self, name):
        """
        Relaxation curve fitting data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        __________________________________________________________________________________________
        |                                   |                      |                             |
        | Data type                         | Object name          | Patterns                    |
        |___________________________________|______________________|_____________________________|
        |                                   |                      |                             |
        | Relaxation rate                   | 'rx'                 | '^[Rr]x$'                   |
        |                                   |                      |                             |
        | Average peak intensities (series) | 'ave_intensities'    | '^[Aa]ve[ -_][Ii]nt$'       |
        |                                   |                      |                             |
        | Initial intensity                 | 'i0'                 | '^[Ii]0$'                   |
        |                                   |                      |                             |
        | Intensity at infinity             | 'iinf'               | '^[Ii]inf$'                 |
        |                                   |                      |                             |
        | Relaxation period times (series)  | 'relax_times'        | '^[Rr]elax[ -_][Tt]imes$'   |
        |___________________________________|______________________|_____________________________|

        """

        # Relaxation rate.
        if match('^[Rr]x$', name):
            return 'rx'

        # Average peak intensities (series)
        if match('^[Aa]ve[ -_][Ii]nt$', name):
            return 'ave_intensities'

        # Initial intensity.
        if match('^[Ii]0$', name):
            return 'i0'

        # Intensity at infinity.
        if match('^[Ii]inf$', name):
            return 'iinf'

        # Relaxation period times (series).
        if match('^[Rr]elax[ -_][Tt]imes$', name):
            return 'relax_times'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Relaxation rate.
        if object_name == 'rx':
            grace_string = '\\qR\\sx\\Q'

        # Average peak intensities.
        elif object_name == 'ave_intensities':
            grace_string = '\\qAverage peak intensities\\Q'

        # Initial intensity.
        elif object_name == 'i0':
            grace_string = '\\qI\\s0\\Q'

        # Intensity at infinity.
        elif object_name == 'iinf':
            grace_string = '\\qI\\sinf\\Q'

        # Intensity at infinity.
        elif object_name == 'relax_times':
            grace_string = '\\qRelaxation time period (s)\\Q'

        # Return the Grace string.
        return grace_string


    def return_units(self, stat_type):
        """Dummy function which returns None as the stats have no units."""

        return None


    def select_model(self, model='exp'):
        """Function for selecting the model of the exponential curve.

        @keyword model: The exponential curve type.  Can be one of 'exp' or 'inv'.
        @type model:    str
        """

        # Test if the current pipe exists.
        pipes.test()

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the pipe type is set to 'relax_fit'.
        function_type = cdp.pipe_type
        if function_type != 'relax_fit':
            raise RelaxFuncSetupError, specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Two parameter exponential fit.
        if model == 'exp':
            print "Two parameter exponential fit."
            params = ['Rx', 'I0']

        # Three parameter inversion recovery fit.
        elif model == 'inv':
            print "Three parameter inversion recovery fit."
            params = ['Rx', 'I0', 'Iinf']

        # Invalid model.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(model, params)


    def set_doc(self):
        """
        Relaxation curve fitting set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Only three parameters can be set, the relaxation rate (Rx), the initial intensity (I0), and
        the intensity at infinity (Iinf).  Setting the parameter Iinf has no effect if the chosen
        model is that of the exponential curve which decays to zero.
        """


    def sim_pack_data(self, spin_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param spin_id:     The spin identification string, as yielded by the base_data_loop()
                            generator method.
        @type spin_id:      str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Test if the simulation data already exists.
        if hasattr(spin, 'sim_intensities'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        spin.sim_intensities = sim_data
