###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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

from copy import deepcopy
from math import sqrt
from Numeric import ones
from random import gauss

from relax_errors import RelaxError, RelaxNoRunError, RelaxNoSequenceError


class Monte_carlo:
    def __init__(self, relax):
        """Class containing functions for Monte Carlo simulations."""

        self.relax = relax


    def create_data(self, run=None, method=None):
        """Function for creating simulation data.

        It is assumed that all data types are residue specific.
        """

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `self.run` + " have not been set up."

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test the method argument.
        valid_methods = ['back_calc', 'direct']
        if method not in valid_methods:
            raise RelaxError, "The simulation creation method " + `method` + " is not valid."

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific Monte Carlo data creation, data return, and error return function setup.
        create_mc_data = self.relax.specific_setup.setup('create_mc_data', function_type)
        return_data = self.relax.specific_setup.setup('return_data', function_type)
        return_error = self.relax.specific_setup.setup('return_error', function_type)
        pack_sim_data = self.relax.specific_setup.setup('pack_sim_data', function_type)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # Create the Monte Carlo data.
            if method == 'back_calc':
                data = create_mc_data(self.run, i)

            # Get the original data.
            else:
                data = return_data(self.run, i)

            # Get the errors.
            error = return_error(self.run, i)

            # Loop over the Monte Carlo simulations.
            random = []
            for j in xrange(self.relax.data.sim_number[self.run]):
                # Randomise the data.
                random.append([])
                for k in xrange(len(data)):
                    # No data or errors.
                    if data[k] == None or error[k] == None:
                        random[j].append(None)
                        continue

                    # Gaussian randomisation.
                    random[j].append(gauss(data[k], error[k]))

            # Pack the simulation data.
            pack_sim_data(self.run, i, random)


    def error_analysis(self, run=None, prune=0.0):
        """Function for calculating errors from the Monte Carlo simulations.

        The standard deviation formula used to calculate the errors is the square root of the
        bias-corrected variance, given by the formula:

                       ____________________________
                      /   1
            sd  =    /  ----- * sum({Xi - Xav}^2)]
                   \/   n - 1

        where:
            n is the total number of simulations.
            Xi is the parameter value for simulation i.
            Xav is the mean parameter value for all simulations.
        """

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `self.run` + " have not been set up."

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific number of instances, return simulation chi2 array, return selected simulation array, return simulation parameter array, and set error functions.
        count_num_instances = self.relax.specific_setup.setup('num_instances', function_type)
        if prune > 0.0:
            return_sim_chi2 = self.relax.specific_setup.setup('return_sim_chi2', function_type)
        return_selected_sim = self.relax.specific_setup.setup('return_selected_sim', function_type)
        return_sim_param = self.relax.specific_setup.setup('return_sim_param', function_type)
        set_error = self.relax.specific_setup.setup('set_error', function_type)

        # Count the number of instances.
        num_instances = count_num_instances(self.run)

        # Loop over the instances.
        for instance in xrange(num_instances):
            # Get the selected simulation array.
            select_sim = return_selected_sim(self.run, instance)

            # Initialise an array of indecies to prune (an empty array means no prunning).
            indecies_to_skip = []

            # Pruning.
            if prune > 0.0:
                # Get the array of simulation chi-squared values.
                chi2_array = return_sim_chi2(self.run, instance)

                # The total number of simulations.
                n = len(chi2_array)

                # Create a sorted array of chi-squared values.
                chi2_sorted = deepcopy(chi2_array)
                chi2_sorted.sort()

                # Number of indecies to remove from one side of the chi2 distribution.
                num = int(float(n) * 0.5 * prune)

                # Remove the lower tail.
                for i in xrange(num):
                    indecies_to_skip.append(chi2_array.index(chi2_sorted[i]))

                # Remove the upper tail.
                for i in xrange(n-num, n):
                    indecies_to_skip.append(chi2_array.index(chi2_sorted[i]))

            # Loop over the parameters.
            index = 0
            while 1:
                # Get the array of simulation parameters for the index.
                param_array = return_sim_param(self.run, instance, index)

                # Break (no more parameters).
                if param_array == None:
                    break

                # Simulation parameters with values (ie not None).
                if param_array[0] != None:
                    # The total number of simulations.
                    n = 0
                    for i in xrange(len(param_array)):
                        # Skip unselected simulations.
                        if not select_sim[i]:
                            continue

                        # Prune.
                        if i in indecies_to_skip:
                            continue

                        # Increment n.
                        n = n + 1

                    # Calculate the sum of the parameter value for all simulations.
                    Xsum = 0.0
                    for i in xrange(len(param_array)):
                        # Skip unselected simulations.
                        if not select_sim[i]:
                            continue

                        # Prune.
                        if i in indecies_to_skip:
                            continue

                        # Sum.
                        Xsum = Xsum + param_array[i]

                    # Calculate the mean parameter value for all simulations.
                    Xav = Xsum / float(n)

                    # Calculate the sum part of the standard deviation.
                    sd = 0.0
                    for i in xrange(len(param_array)):
                        # Skip unselected simulations.
                        if not select_sim[i]:
                            continue

                        # Prune.
                        if i in indecies_to_skip:
                            continue

                        # Sum.
                        sd = sd + (param_array[i] - Xav)**2

                    # Calculate the standard deviation.
                    sd = sqrt(sd / (float(n) - 1.0))

                # Simulation parameters with the value None.
                else:
                    sd = None

                # Set the parameter error.
                set_error(self.run, instance, index, sd)

                # Increment the parameter index.
                index = index + 1


    def initial_values(self, run=None):
        """Function for setting the initial simulation parameter values."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `self.run` + " have not been set up."

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific initial Monte Carlo parameter value function setup.
        init_sim_values = self.relax.specific_setup.setup('init_sim_values', function_type)

        # Set the initial parameter values.
        init_sim_values(self.run)


    def off(self, run=None):
        """Function for turning simulations off."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `self.run` + " have not been set up."

        # Turn simulations off.
        self.relax.data.sim_state[self.run] = 0


    def on(self, run=None):
        """Function for turning simulations on."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `self.run` + " have not been set up."

        # Turn simulations on.
        self.relax.data.sim_state[self.run] = 1


    def select_all_sims(self, number=None, all_select_sim=None):
        """Function for setting the select flag of all simulations of all instances to one."""

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific number of instances and set the selected simulation array functions.
        count_num_instances = self.relax.specific_setup.setup('num_instances', function_type)
        set_selected_sim = self.relax.specific_setup.setup('set_selected_sim', function_type)

        # Count the number of instances.
        num_instances = count_num_instances(self.run)

        # Create the selected simulation array with all simulations selected.
        if all_select_sim == None:
            select_sim = ones(number)

        # Loop over the instances.
        for instance in xrange(num_instances):
            # Set up the selected simulation array.
            if all_select_sim != None:
                select_sim = all_select_sim[instance].tolist()

            # Set the selected simulation array.
            set_selected_sim(self.run, instance, select_sim)


    def setup(self, run=None, number=None, all_select_sim=None):
        """Function for setting up Monte Carlo simulations.
        
        @param run:             The name of the run.
        @type run:              str
        @param number:          The number of Monte Carlo simulations to set up.
        @type number:           int
        @params all_select_sim: The selection status of the Monte Carlo simulations.  The first
            dimension of this matrix corresponds to the simulation and the second corresponds to the
            instance.
        @type all_select_sim:   Numeric matrix (int)
        """

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if Monte Carlo simulations have already been set up for the given run.
        if hasattr(self.relax.data, 'sim_number') and self.relax.data.sim_number.has_key(self.run):
            raise RelaxError, "Monte Carlo simulations for the run " + `self.run` + " have already been set up."

        # Create the data structure 'sim_number' if it doesn't exist.
        if not hasattr(self.relax.data, 'sim_number'):
            self.relax.data.sim_number = {}

        # Add the simulation number.
        self.relax.data.sim_number[self.run] = number

        # Create the data structure 'sim_state'.
        if not hasattr(self.relax.data, 'sim_state'):
            self.relax.data.sim_state = {}

        # Turn simulations on.
        self.relax.data.sim_state[self.run] = 1

        # Select all simulations.
        self.select_all_sims(number=number, all_select_sim=all_select_sim)
