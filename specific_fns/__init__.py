###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2007 Edward d'Auvergne                             #
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

# Package docstring.
"""This package consists of modules which are specific to the type of the data pipe."""



# relax module imports.
from specific_fns.hybrid import Hybrid
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.model_free import Model_free
from specific_fns.n_state_model import N_state_model
from specific_fns.noe import Noe
from specific_fns.relax_fit import Relax_fit
from relax_errors import RelaxError, RelaxFuncSetupError


# The available modules.
__all__ = [ 'base_class',
            'hybrid',
            'jw_mapping',
            'model_free',
            'n_state_model',
            'noe',
            'relax_data',
            'relax_fit']

# Instantiate all classes.
hybrid_obj = Hybrid()
jw_mapping_obj = Jw_mapping()
model_free_obj = Model_free()
noe_obj = Noe()
n_state_model_obj = N_state_model()
relax_fit_obj = Relax_fit()


# The function for returning the requested specific function.
def get_specific_fn(eqi, function_type, raise_error=1):
    """The function for returning the requested specific function."""

    # Initialise.
    function = None

    # Get the class instance corresponding to function_type.
    inst = get_instance(function_type)

    # Attempt to retrieve the function.
    try:
        # Back-calculate function.
        if eqi == 'back_calc':
            function = inst.back_calc

        # Calculate function.
        if eqi == 'calculate':
            function = inst.calculate

        # Copy function.
        if eqi == 'copy':
            function = inst.copy

        # Create Monte Carlo data function.
        if eqi == 'create_mc_data':
            function = inst.create_mc_data

        # Data structure initialisation function.
        if eqi == 'data_init':
            function = inst.data_init

        # Default parameter value returning function.
        if eqi == 'default_value':
            function = inst.default_value

        # Duplicate data function.
        if eqi == 'duplicate_data':
            function = inst.duplicate_data

        # Eliminate models.
        if eqi == 'eliminate':
            function = inst.eliminate

        # Grid search function.
        if eqi == 'grid_search':
            function = inst.grid_search

        # Initial Monte Carlo parameter value search function.
        if eqi == 'init_sim_values':
            function = inst.sim_init_values

        # Map bounds function.
        if eqi == 'map_bounds':
            function = inst.map_bounds

        # Minimise function.
        if eqi == 'minimise':
            function = inst.minimise

        # Model statistics.
        if eqi == 'model_stats':
            function = inst.model_statistics

        # Molmol macro creation.
        if eqi == 'molmol_macro':
            function = inst.molmol.macro

        # Number of instances.
        if eqi == 'num_instances':
            function = inst.num_instances

        # Overfit deselect.
        if eqi == 'overfit_deselect':
            function = inst.overfit_deselect

        # Pack Monte Carlo simulation data function.
        if eqi == 'pack_sim_data':
            function = inst.sim_pack_data

        # Parameter names function.
        if eqi == 'param_names':
            function = inst.get_param_names

        # Parameter values function.
        if eqi == 'param_values':
            function = inst.get_param_values

        # Read results file function (Columnar format).
        if eqi == 'read_columnar_results':
            function = inst.read_columnar_results

        # Read results file function (XML format).
        #if eqi == 'read_xml_results':
        #    function = inst.read_xml_results

        # Data returning function.
        if eqi == 'return_data':
            function = inst.return_data

        # Data or parameter name returning function.
        if eqi == 'return_data_name':
            function = inst.return_data_name

        # Data error returning function.
        if eqi == 'return_error':
            function = inst.return_error

        # Factor of conversion between different parameter units returning function.
        if eqi == 'return_conversion_factor':
            function = inst.return_conversion_factor

        # Grace string returning function.
        if eqi == 'return_grace_string':
            function = inst.return_grace_string

        # Selected simulation array returning function.
        if eqi == 'return_selected_sim':
            function = inst.sim_return_selected

        # Simulation chi-squared array returning function.
        if eqi == 'return_sim_chi2':
            function = inst.sim_return_chi2

        # Simulation parameter array returning function.
        if eqi == 'return_sim_param':
            function = inst.sim_return_param

        # String of the external parameter units returning function.
        if eqi == 'return_units':
            function = inst.return_units

        # Value and error returning function.
        if eqi == 'return_value':
            function = inst.return_value

        # Set error function.
        if eqi == 'set_error':
            function = inst.set_error

        # Set non-spin specific parameters function.
        if eqi == 'set_non_spin_params':
            function = inst.set_non_spin_params

        # Set the selected simulations array.
        if eqi == 'set_selected_sim':
            function = inst.set_selected_sim

        # Set update function.
        if eqi == 'set_update':
            function = inst.set_update

        # Skip function.
        if eqi == 'skip_function':
            function = inst.skip_function

        # Unselect function.
        if eqi == 'unselect':
            function = inst.unselect

        # Write results function (Columnar format).
        if eqi == 'write_columnar_results':
            function = inst.write_columnar_results

        # Write results function (XML format).
        #if eqi == 'write_xml_results':
        #    function = inst.write_xml_results

    # Catch if the function is missing.
    except AttributeError:
        function = None

    # Raise an error if the function doesn't exist.
    if raise_error and function == None:
        # Raise the error.
        raise RelaxFuncSetupError, get_string(function_type)

    # Return the function.
    return function


def get_instance(function_type):
    """Function for returning the class instance corresponding to the function type."""

    # NOE calculation.
    if function_type == 'noe':
        return noe_obj

    # The N-state model.
    if function_type == 'N-state':
        return n_state_model_obj

    # Relaxation curve fitting.
    if function_type == 'relax_fit':
        return relax_fit_obj

    # Reduced spectral density mapping.
    if function_type == 'jw':
        return jw_mapping_obj

    # Model-free analysis.
    if function_type == 'mf':
        return model_free_obj

    # Hybrid models.
    if function_type == 'hybrid':
        return hybrid_obj

    # Unknown analysis.
    raise RelaxError, "The function_type " + `function_type` + " is unknown."


def get_string(function_type):
    """Function for returning a string corresponding to the function type."""

    # NOE calculation.
    if function_type == 'noe':
        return "NOE calculations"

    # The N-state model.
    if function_type == 'N-state':
        return "the N-state model"

    # Relaxation curve fitting.
    if function_type == 'relax_fit':
        return "relaxation curve fitting"

    # Reduced spectral density mapping.
    if function_type == 'jw':
        return "reduced spectral density mapping"

    # Model-free analysis.
    if function_type == 'mf':
        return "Model-free analysis"

    # Hybrid models.
    if function_type == 'hybrid':
        return "hybrid models"

    # Unknown analysis.
    raise RelaxError, "The function_type " + `function_type` + " is unknown."
