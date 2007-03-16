###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007 Edward d'Auvergne                             #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoRunError




class Eliminate:
    def __init__(self, relax):
        """Class containing the function for model elimination."""

        self.relax = relax


    def eliminate(self, run=None, function=None, args=None):
        """Function for model elimination."""

        # Create the list of runs.
        self.runs = self.relax.generic.runs.list_of_runs(run)

        # Loop over the runs.
        for self.run in self.runs:
            # Test if the run exists.
            if not self.run in relax_data_store.run_names:
                raise RelaxNoRunError, self.run

            # Function type.
            function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]

            # Specific eliminate, parameter names, parameter values, number of instances, and unselect function setup.
            eliminate = self.relax.specific_setup.setup('eliminate', function_type)
            param_names = self.relax.specific_setup.setup('param_names', function_type)
            param_values = self.relax.specific_setup.setup('param_values', function_type)
            num_instances = self.relax.specific_setup.setup('num_instances', function_type)
            unselect = self.relax.specific_setup.setup('unselect', function_type)

            # Get the number of instances and loop over them.
            for i in xrange(num_instances(self.run)):
                # Determine if simulations are active for the run.
                if hasattr(relax_data_store, 'sim_state') and relax_data_store.sim_state.has_key(self.run) and relax_data_store.sim_state[self.run] == 1:
                    sim_state = 1
                else:
                    sim_state = 0


                # Model elimination.
                ####################

                if sim_state == 0:
                    # Get the parameter names and values.
                    names = param_names(self.run, i)
                    values = param_values(self.run, i)

                    # No data.
                    if names == None or values == None:
                        continue

                    # Test that the names and values vectors are of equal length.
                    if len(names) != len(values):
                        raise RelaxError, "The names vector " + `names` + " is of a different length to the values vector " + `values` + "."

                    # Loop over the parameters.
                    flag = 0
                    for j in xrange(len(names)):
                        # Eliminate function.
                        if eliminate(names[j], values[j], self.run, i, args):
                            flag = 1

                    # Unselect.
                    if flag:
                        unselect(self.run, i)


                # Simulation elimination.
                #########################

                else:
                    # Loop over the simulations.
                    for j in xrange(relax_data_store.sim_number[self.run]):
                        # Get the parameter names and values.
                        names = param_names(self.run, i)
                        values = param_values(self.run, i, sim_index=j)

                        # No data.
                        if names == None or values == None:
                            continue

                        # Test that the names and values vectors are of equal length.
                        if len(names) != len(values):
                            raise RelaxError, "The names vector " + `names` + " is of a different length to the values vector " + `values` + "."

                        # Loop over the parameters.
                        flag = 0
                        for k in xrange(len(names)):
                            # Eliminate function.
                            if eliminate(names[k], values[k], self.run, i, args):
                                flag = 1

                        # Unselect.
                        if flag:
                            unselect(self.run, i, sim_index=j)
