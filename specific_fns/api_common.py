###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2009 Edward d'Auvergne                             #
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
"""API methods in common between different analysis types."""

# Python module imports.
from copy import deepcopy

# relax module imports.
import arg_check
from data.mol_res_spin import SpinContainer
from generic_fns.mol_res_spin import count_spins, exists_mol_res_spin_data, return_spin, spin_loop
from relax_errors import RelaxError, RelaxLenError, RelaxNoSequenceError


class API_common:
    """Base class containing API methods common to multiple analysis types."""

    def _base_data_loop_spin(self):
        """Generator method for looping over the base data of the specific analysis type (spin system specific).

        This method simply loops over the spins, returning the spin identification string.

        @return:    The spin identification string
        @rtype:     str
        """

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Yield the spin id string.
            yield spin_id


    def _data_init_dummy(self, data_cont, sim=False):
        """Dummy method for initialising data structures.

        This method does nothing!


        @param data_cont:   The data container.
        @type data_cont:    instance
        @keyword sim:       The unused Monte Carlo simulation flag.
        @type sim:          bool
        """


    def _eliminate_false(self, name, value, model_info, args, sim=None):
        """Dummy method for model elimination.

        This simply returns False to signal that no model elimination is to be performed.


        @param name:        The parameter name.
        @type name:         str
        @param value:       The parameter value.
        @type value:        float
        @param model_info:  The model index from model_info().
        @type model_info:   int
        @param args:        The elimination constant overrides.
        @type args:         None or tuple of float
        @keyword sim:       The Monte Carlo simulation index.
        @type sim:          int
        @return:            False to prevent model elimination.
        @rtype:             bool
        """

        # Don't eliminate.
        return False


    def _has_errors_spin(self):
        """Testing if errors exist for the current data pipe (spin system specific).

        @return:    The answer to the question of whether errors exist.
        @rtype:     bool
        """

        # Diffusion tensor errors.
        if hasattr(cdp, 'diff'):
            for object_name in dir(cdp.diff):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(cdp.diff, object_error):
                    return True

        # Loop over the sequence.
        for spin in spin_loop():
            # Parameter errors.
            for object_name in dir(spin):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(spin, object_error):
                    return True

        # No errors found.
        return False


    def _is_spin_param_true(self, name):
        """Dummy method stating that the parameter is spin specific.

        This method always returns true, hence all parameters will be considered residents of a SpinContainer object unless this method is overwritten.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        True
        @rtype:         bool
        """

        # Return the default of True.
        return True


    def _model_loop_spin(self):
        """Default generator method for looping over the models, where each spin has a separate model.

        In this case only a single model per spin system is assumed.  Hence the yielded data is the spin container object.


        @return:    The spin container.
        @rtype:     SpinContainer instance
        """

        # Loop over the sequence.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Yield the spin container.
            yield spin


    def _num_instances_spin(self):
        """Return the number of instances, equal to the number of selected spins.

        @return:    The number of instances (equal to the number of spins).
        @rtype:     int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Return the number of spins.
        return count_spins()


    def _overfit_deselect_dummy(self):
        """Dummy method, normally for deselecting spins with insufficient data for minimisation."""

        # Print out.
        print("\n\nOver-fit spin deselection.\n")


    def _return_no_conversion_factor(self, param, spin=None, spin_id=None):
        """Method for returning 1.0.

        @param param:       The parameter name.
        @type param:        str
        @param spin:        Spin container.
        @type spin:         SpinContainer instance
        @return:            A conversion factor of 1.0.
        @rtype:             float
        """

        return 1.0


    def _return_data_relax_data(self, spin):
        """Return the Ri data structure for the given spin.

        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer instance
        @return:        The array of relaxation data values.
        @rtype:         list of float
        """

        return spin.relax_data


    def _return_error_relax_data(self, spin_id):
        """Return the Ri error structure for the corresponding spin.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator method.
        @type spin_id:  str
        @return:        The array of relaxation data error values.
        @rtype:         list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Return the data.
        return spin.relax_error


    def _return_value_general(self, spin, param, sim=None):
        """Return the value and error corresponding to the parameter 'param'.

        If sim is set to an integer, return the value of the simulation and None.  The values are taken from the given SpinContainer object.


        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        @param param:   The name of the parameter to return values for.
        @type param:    str
        @param sim:     The Monte Carlo simulation index.
        @type sim:      None or int
        @return:        The value and error corresponding to
        @rtype:         tuple of length 2 of floats or None
        """

        # Initialise.
        index = None

        # Get the object name.
        object_name = self.return_data_name(param)

        # The error and simulation names.
        if object_name:
            object_error = object_name + '_err'
            object_sim = object_name + '_sim'

        # The data type does not exist.
        else:
            # Is it a spectrum id?
            if param in cdp.spectrum_ids:
                index = cdp.spectrum_ids.index(param)
                object_name = 'intensities'
                object_error = 'intensity_err'
                object_sim = 'intensity_sim'

            # Unknown data type.
            else:
                raise RelaxError("The parameter " + repr(param) + " does not exist.")

        # Initial values.
        value = None
        error = None

        # Value and error.
        if sim == None:
            # Get the value.
            if hasattr(spin, object_name):
                value = getattr(spin, object_name)
                if index != None:
                    value = value[index]
            elif hasattr(cdp, object_name):
                value = getattr(cdp, object_name)
                if index != None:
                    value = value[index]

            # Get the error.
            if hasattr(spin, object_error):
                error = getattr(spin, object_error)
                if index != None:
                    error = error[index]
            elif hasattr(cdp, object_error):
                error = getattr(cdp, object_error)
                if index != None:
                    error = error[index]

        # Simulation value.
        else:
            # Get the value.
            if hasattr(spin, object_sim):
                object = getattr(spin, object_sim)
                if index != None:
                    object = object[index]
                value = object[sim]
            elif hasattr(cdp, object_sim):
                object = getattr(cdp, object_sim)
                if index != None:
                    object = object[index]
                value = object[sim]

        # Return the data.
        return value, error


    def _set_error_spin(self, model_info, index, error):
        """Set the parameter errors (spin system specific).

        @param model_info:  The spin container originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
        """

        # The spin container.
        if not isinstance(model_info, SpinContainer):
            raise RelaxError("The model information argument is not a spin container.")
        spin = model_info

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                setattr(spin, param + "_err", error)

            # Increment.
            inc = inc + 1


    def _set_param_values_global(self, param=None, value=None, spin_id=None, force=True):
        """Set the global parameter values in the top layer of the data pipe.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword spin_id:   The spin identification string (unused).
        @type spin_id:      None
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        arg_check.is_str_list(param, 'parameter name')
        arg_check.is_list(value, 'parameter value')
        arg_check.is_none(spin_id, 'spin ID string')

        # Loop over the parameters.
        for i in range(len(param)):
            # Get the object's name.
            obj_name = self.return_data_name(param[i])

            # Is the parameter is valid?
            if not obj_name:
                raise RelaxError("The parameter '%s' is not valid for this data pipe type." % param[i])

            # Is the parameter already set.
            if not force and hasattr(cdp, obj_name) and getattr(cdp, obj_name) != None:
                raise RelaxError("The parameter '%s' already exists, set the force flag to True to overwrite." % param[i])

            # Set the parameter.
            setattr(cdp, obj_name, value[i])


    def _set_param_values_spin(self, param=None, value=None, spin_id=None, force=True):
        """Set the spin specific parameter values.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword spin_id:   The spin identification string, only used for spin specific parameters.
        @type spin_id:      None or str
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        arg_check.is_str_list(param, 'parameter name')
        arg_check.is_list(value, 'parameter value')

        # Loop over the parameters.
        for i in range(len(param)):
            # Get the object's name.
            obj_name = self.return_data_name(param[i])

            # Is the parameter is valid?
            if not obj_name:
                raise RelaxError("The parameter '%s' is not valid for this data pipe type." % param[i])

            # Spin loop.
            for spin in spin_loop(spin_id):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Set the parameter.
                setattr(spin, obj_name, value[i])


    def _set_selected_sim_spin(self, model_info, select_sim):
        """Set the simulation selection flag (spin system specific).

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param select_sim:  The selection flag for the simulations.
        @type select_sim:   bool
        """

        # The spin container.
        if not isinstance(model_info, SpinContainer):
            raise RelaxError("The model information argument is not a spin container.")
        spin = model_info

        # Set the array.
        spin.select_sim = deepcopy(select_sim)


    def _set_update(self, param, spin):
        """Dummy method to do nothing!

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """


    def _sim_init_values_spin(self):
        """Initialise the Monte Carlo parameter values (spin system specific)."""

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Loop over the spins.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Loop over all the parameter names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(spin, sim_object_name):
                    raise RelaxError("Monte Carlo parameter values have already been set.")


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the residues.
        for spin in spin_loop():
            # Skip deselected residues.
            if not spin.select:
                continue

            # Loop over all the data names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(spin, sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(spin, sim_object_name)

                # Loop over the simulations.
                for j in xrange(cdp.sim_number):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(spin, object_name)))

            # Loop over all the minimisation object names.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(spin, sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(spin, sim_object_name)

                # Loop over the simulations.
                for j in xrange(cdp.sim_number):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(spin, object_name)))


    def _sim_return_chi2_spin(self, model_info, index=None):
        """Return the simulation chi-squared values (spin system specific).

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @keyword index:     The optional simulation index.
        @type index:        int
        @return:            The list of simulation chi-squared values.  If the index is supplied, only a single value will be returned.
        @rtype:             list of float or float
        """

        # The spin container.
        if not isinstance(model_info, SpinContainer):
            raise RelaxError("The model information argument is not a spin container.")
        spin = model_info

        # Index.
        if index != None:
            return spin.chi2_sim[index]

        # List of vals.
        else:
            return spin.chi2_sim


    def _sim_return_param_spin(self, model_info, index):
        """Return the array of simulation parameter values (spin system specific).

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
        """

        # The spin container.
        if not isinstance(model_info, SpinContainer):
            raise RelaxError("The model information argument is not a spin container.")
        spin = model_info

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                return getattr(spin, param + "_sim")

            # Increment.
            inc = inc + 1


    def _sim_return_selected_spin(self, model_info):
        """Return the array of selected simulation flags (spin system specific).

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # The spin container.
        if not isinstance(model_info, SpinContainer):
            raise RelaxError("The model information argument is not a spin container.")
        spin = model_info

        # Return the array.
        return spin.select_sim


    def _test_grid_ops_general(self, lower=None, upper=None, inc=None, n=None):
        """Test that the grid search options are reasonable.

        @param lower:   The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:    array of numbers
        @param upper:   The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:    array of numbers
        @param inc:     The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
        @type inc:      array of int
        @param n:       The number of parameters in the model.
        @type n:        int
        """

        # Lower bounds test.
        if lower != None:
            if len(lower) != n:
                raise RelaxLenError('lower bounds', n)

        # Upper bounds.
        if upper != None:
            if len(upper) != n:
                raise RelaxLenError('upper bounds', n)

        # Increment.
        if isinstance(inc, list):
            if len(inc) != n:
                raise RelaxLenError('increment', n)
