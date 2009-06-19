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
"""Module for the specific methods of the Frame Order theories."""

# Python module imports.
from math import pi

# relax module imports.
from generic_fns import pipes
from relax_errors import RelaxNoModelError
from specific_fns.base_class import Common_functions


class Frame_order(Common_functions):
    """Class containing the specific methods of the Frame Order theories."""

    def __update_model(self):
        """Update the model parameters as necessary."""

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Initialise the list of model parameters.
        if not hasattr(cdp, 'params'):
            cdp.params = []

        # Set up the parameter arrays.
        if not len(cdp.params):
            # Isotropic cone parameters.
            if cdp.model == 'iso cone':
                cdp.params.append('alpha')
                cdp.params.append('beta')
                cdp.params.append('gamma')
                cdp.params.append('theta')


    def grid_search(self, lower, upper, inc, constraints=False, verbosity=0, sim_index=None):
        """Perform a grid search.

        @param lower:       The lower bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          int or array of int
        @param constraints: If True, constraints are applied during the grid search (eliminating
                            parts of the grid).  If False, no constraints are used.
        @type constraints:  bool
        @param verbosity:   A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the Frame Order model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError, 'Frame Order'

        # The number of parameters.
        n = len(cdp.params)

        # If inc is an int, convert it into an array of that value.
        if type(inc) == int:
            inc = [inc]*n

        # Initialise the grid_ops structure.
        grid_ops = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension has the elements: 0, the number of increments in that
        dimension; 1, the lower limit of the grid; 2, the upper limit of the grid."""

        # Set the grid search options.
        for i in xrange(n):
            # Euler angles.
            if cdp.params[i] in ['alpha', 'gamma']:
                grid_ops.append([inc[i], 0.0, 2*pi])
            if cdp.params[i] == 'beta':
                grid_ops.append([inc[i], 0.0, pi])

            # The cone angle.
            if cdp.params[i] == 'theta':
                grid_ops.append([inc[i], 0.0, pi])

            # Lower bound (if supplied).
            if lower:
                grid_ops[i][1] = lower[i]

            # Upper bound (if supplied).
            if upper:
                grid_ops[i][1] = upper[i]

        # Minimisation.
        self.minimise(min_algor='grid', min_options=grid_ops, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def select_model(self, model=None):
        """Select the Frame Order model.

        @param model:   The Frame Order model.  As of yet, this can only be 'iso cone'.
        @type model:    str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the model is already setup.
        if hasattr(cdp, 'model'):
            raise RelaxModelError, 'Frame Order'

        # Test if the model name exists.
        if not model in ['iso cone']:
            raise RelaxError, "The model name " + `model` + " is invalid."

        # Set the model
        cdp.model = model

        # Initialise the list of model parameters.
        cdp.params = []

        # Update the model.
        self.__update_model()
