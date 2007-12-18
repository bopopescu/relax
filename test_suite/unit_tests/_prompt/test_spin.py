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
from data import Data as relax_data_store
from prompt.spin import Spin
from relax_errors import RelaxError, RelaxIntError, RelaxNoPipeError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.spin_testing_base import Spin_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_spin(Spin_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.spin' module."""

    # Instantiate the user function class.
    spin_fns = Spin(fake_relax.fake_instance())


    def test_copy_argfail_pipe_from(self):
        """Test the proper failure of the spin.copy() user function for the pipe_from argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spin_fns.copy, pipe_from=data[1], spin_from='#Old mol:1@111', spin_to='#Old mol:2')


    def test_copy_argfail_spin_from(self):
        """Test the proper failure of the spin.copy() user function for the spin_from argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spin_fns.copy, spin_from=data[1], spin_to='#Old mol:2')


    def test_copy_argfail_pipe_to(self):
        """Test the proper failure of the spin.copy() user function for the pipe_to argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spin_fns.copy, pipe_to=data[1], spin_from='#Old mol:1@111', spin_to='#Old mol:2')


    def test_copy_argfail_spin_to(self):
        """Test the proper failure of the spin.copy() user function for the spin_to argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or  data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spin_fns.copy, spin_from='#Old mol:1@111', spin_to=data[1])


    def test_create_argfail_spin_num(self):
        """Test the proper failure of the spin.create() user function for the spin_num argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.spin_fns.create, spin_num=data[1], spin_name='NH')


    def test_create_argfail_spin_name(self):
        """Test the proper failure of the spin.create() user function for the spin_name argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spin_fns.create, spin_name=data[1], spin_num=1)


    def test_create_argfail_res_id(self):
        """Test the proper failure of the spin.create() user function for the res_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spin_fns.create, res_id=data[1], spin_num=1, spin_name='NH')


    def test_delete_argfail_spin_id(self):
        """Test the proper failure of the spin.delete() user function for the spin_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spin_fns.delete, spin_id=data[1])


    def test_display_argfail_spin_id(self):
        """Test the proper failure of the spin.display() user function for the spin_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.spin_fns.display, spin_id=data[1])


    def test_rename_argfail_spin_id(self):
        """Test the proper failure of the spin.rename() user function for the spin_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spin_fns.rename, spin_id=data[1])


    def test_rename_argfail_new_name(self):
        """Test the proper failure of the spin.rename() user function for the new_name argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spin_fns.rename, new_name=data[1])


    def test_renumber_argfail_spin_id(self):
        """Test the proper failure of the spin.renumber() user function for the spin_id argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.spin_fns.renumber, spin_id=data[1])


    def test_renumber_argfail_new_number(self):
        """Test the proper failure of the spin.renumber() user function for the new_number argument."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.spin_fns.renumber, spin_id='@111', new_number=data[1])
