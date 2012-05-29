###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""A module of special objects used within the specific function API."""

# Python module imports.
from types import FunctionType, MethodType

# relax module imports.
from relax_errors import RelaxError


class Param_list:
    """A special object for handling global and spin parameters."""

    def __init__(self, min_stats=False):
        """Set up the class.

        @keyword min_stats:     A flag which if True will include the parameters 'chi2', 'iter', 'f_count', 'g_count', 'h_count', 'warning' in the list.
        @type min_stats:        bool
        """

        # Store the flags.
        self.min_stats = min_stats

        # Initialise the lists and dictionaries for the parameter info.
        self._names = []
        self._string = {}
        self._defaults = {}
        self._units = {}
        self._desc = {}
        self._py_types = {}
        self._conv_factor = {}
        self._grace_string = {}
        self._err = {}
        self._sim = {}


    def add(self, name, string=None, default=None, units=None, desc=None, py_type=None, conv_factor=None, grace_string=None, param=False, err=False, sim=False):
        """Add a parameter to the list.

        @param name:            The name of the parameter.  This will be used as the variable name.
        @type name:             str
        @keyword string:        The string representation of the parameter.
        @type string:           None or str
        @keyword default:       The default value of the parameter.
        @type default:          anything
        @keyword units:         A string representing the parameters units.
        @type units:            None or str
        @keyword desc:          The text description of the parameter.
        @type desc:             None or str
        @keyword py_type:          The Python type that this parameter should be.
        @type py_type:             Python type object
        @keyword conv_factor:   The factor of conversion between different parameter units.
        @type conv_factor:      None, float or func
        @keyword grace_string:  The string used for the axes in Grace plots of the data.
        @type grace_string:     None or str
        @keyword param:         A flag which if True will set this to an analysis specific parameter belonging to the 'params' set.  If False, then the parameter will belong to the 'generic' set.
        @keyword err:           A flag which if True indicates that the parameter name + '_err' error data structure can exist.
        @type err:              bool
        @keyword sim:           A flag which if True indicates that the parameter name + '_sim' Monte Carlo simulation data structure can exist.
        @type sim:              bool
        """

        # Add the values.
        self._names.append(name)
        self._defaults[name] = default
        self._units[name] = units
        self._desc[name] = desc
        self._conv_factor[name] = conv_factor
        self._py_types[name] = py_type
        self._param[name] = param
        self._err[name] = err
        self._sim[name] = sim

        # The parameter string.
        if string:
            self._string[name] = string
        else:
            self._string[name] = name

        # The Grace string.
        if grace_string:
            self._grace_string[name] = grace_string
        else:
            self._grace_string[name] = name


    def contains(self, name):
        """Determine if the given name is within the parameter list.

        @param name:    The name of the parameter to search for.
        @type name:     str
        @return:        True if the parameter is within the list, False otherwise.
        @rtype:         bool
        """

        # Check.
        if name in self._names:
            return True

        # No match.
        return False


    def get_conv_factor(self, name):
        """Return the conversion factor.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The conversion factor.
        @rtype:         float
        """

        # Check.
        if name not in self._names:
            return 1.0

        # No factor.
        if self._conv_factor[name] == None:
            return 1.0

        # Function.
        if isinstance(self._conv_factor[name], FunctionType) or isinstance(self._conv_factor[name], MethodType):
            return self._conv_factor[name]()

        # Value.
        return self._conv_factor[name]


    def get_default(self, name):
        """Return the default value of the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The default value.
        @rtype:         None or str
        """

        # Check.
        if name not in self._names:
            return None

        # Return the default value.
        return self._defaults[name]


    def get_desc(self, name):
        """Return the description of the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The description.
        @rtype:         None or str
        """

        # Check.
        if name not in self._names:
            return None

        # Return the description.
        return self._desc[name]


    def get_err(self, name):
        """Return the error flag for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The error flag for the parameter.
        @rtype:         bool
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)

        # Return the type.
        return self._err[name]


    def get_grace_string(self, name):
        """Return the Grace string for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Grace string.
        @rtype:         str
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)

        # Return the value.
        return self._grace_string[name]


    def get_sim(self, name):
        """Return the Monte Carlo simulation flag for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Monte Carlo simulation flag for the parameter.
        @rtype:         bool
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)

        # Return the type.
        return self._sim[name]


    def get_type(self, name):
        """Return the Python type for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The Python type.
        @rtype:         Python type object
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)

        # Return the Python type.
        return self._py_types[name]


    def get_units(self, name):
        """Return the units string for the parameter.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        The units string.
        @rtype:         str
        """

        # Check.
        if name not in self._names:
            raise RelaxError("The parameter '%s' does not exist." % name)

        # Function.
        if isinstance(self._conv_factor[name], FunctionType) or isinstance(self._conv_factor[name], MethodType):
            return self._units[name]()

        # Return the value.
        return self._units[name]
