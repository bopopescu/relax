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
import sys

# relax module imports.
from data import Data as relax_data_store
from data_types import return_data_types
from generic_fns import residue
from prompt.molecule import Molecule
from relax_errors import RelaxError, RelaxIntError, RelaxNoPipeError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.molecule_testing_base import Molecule_base_class

# Set the variable sys.ps3 (this is required by the user functions).
sys.ps3 = 'relax> '


# A class to act as a container.
class Container:
    pass

# Fake normal relax usage of the user function class.
relax = Container()
relax.interpreter = Container()
relax.interpreter.intro = True


class Test_molecule(Molecule_base_class, TestCase):
    """Unit tests for the functions of the 'generic_fns.molecule' module."""

    # Instantiate the user function class.
    molecule_fns = Molecule(relax)
    residue_fns = residue


    def test_copy_argfail_pipe_from(self):
        """Test the proper failure of the molecule.copy() user function for the pipe_from argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.copy, pipe_from=data[1], mol_from='#Old mol', mol_to='#Old mol')


    def test_copy_argfail_mol_from(self):
        """Test the proper failure of the molecule.copy() user function for the mol_from argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.copy, mol_from=data[1], mol_to='#Old mol')


    def test_copy_argfail_pipe_to(self):
        """Test the proper failure of the molecule.copy() user function for the pipe_to argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.copy, pipe_to=data[1], mol_from='#Old mol', mol_to='#New mol2')


    def test_copy_argfail_mol_to(self):
        """Test the proper failure of the molecule.copy() user function for the mol_to argument."""

        # Set up some data.
        self.setup_data()

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.copy, mol_from='#Old mol', mol_to=data[1])


    def test_create_argfail_mol_name(self):
        """Test the proper failure of the molecule.create() user function for the mol_name argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.create, mol_name=data[1])


    def test_delete_argfail_mol_id(self):
        """Test the proper failure of the molecule.delete() user function for the mol_id argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.delete, mol_id=data[1])


    def test_display_argfail_mol_id(self):
        """Test the proper failure of the molecule.display() user function for the mol_id argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.molecule_fns.display, mol_id=data[1])


    def test_rename_argfail_mol_id(self):
        """Test the proper failure of the molecule.rename() user function for the mol_id argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.rename, mol_id=data[1])


    def test_rename_argfail_new_name(self):
        """Test the proper failure of the molecule.rename() user function for the new_name argument."""

        # Loop over the data types.
        for data in return_data_types():
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.molecule_fns.rename, new_name=data[1])
