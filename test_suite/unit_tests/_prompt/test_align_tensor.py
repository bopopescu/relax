###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from unittest import TestCase

# relax module imports.
from prompt.align_tensor import Align_tensor
from relax_errors import RelaxBinError, RelaxIntError, RelaxNumTupleError
from test_suite.unit_tests.align_tensor_testing_base import Align_tensor_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_align_tensor(Align_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.align_tensor' module."""

    # Instantiate the user function class.
    align_tensor_fns = Align_tensor(fake_relax.fake_instance())


    def test_init_argfail_params(self):
        """Test the proper failure of the align_tensor.init() user function for the params argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float list arguments, and skip them.
            if data[0] == 'float tuple':
                continue

            # The argument test.
            self.assertRaises(RelaxNumTupleError, self.align_tensor_fns.init, params=data[1])


    def test_init_argfail_param_types(self):
        """The proper failure of the align_tensor.init() user function for the param_types argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.align_tensor_fns.init, params=(0.0, 0.0, 0.0, 0.0, 0.0), param_types=data[1])


    def test_init_argfail_errors(self):
        """The proper failure of the align_tensor.init() user function for the errors argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin arguments, and skip them.
            if data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxBinError, self.align_tensor_fns.init, params=(0.0, 0.0, 0.0, 0.0, 0.0), errors=data[1])



