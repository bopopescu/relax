###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
from prompt.structure import Structure
from relax_errors import RelaxBinError, RelaxFloatError, RelaxNoneIntError, RelaxNoneStrError, RelaxNumError, RelaxStrError
from test_suite.unit_tests.structure_testing_base import Structure_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_structure(Structure_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.structure' module."""

    # Instantiate the user function class.
    structure_fns = Structure(fake_relax.fake_instance())


    def test_create_diff_tensor_pdb_argfail_scale(self):
        """The scale arg test of the structure.create_diff_tensor_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float and int arguments, and skip them.
            if data[0] == 'float' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.structure_fns.create_diff_tensor_pdb, scale=data[1])


    def test_create_diff_tensor_pdb_argfail_file(self):
        """The file arg test of the structure.create_diff_tensor_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.structure_fns.create_diff_tensor_pdb, file=data[1])


    def test_create_diff_tensor_pdb_argfail_dir(self):
        """The dir arg test of the structure.create_diff_tensor_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.structure_fns.create_diff_tensor_pdb, dir=data[1])


    def test_create_diff_tensor_pdb_argfail_force(self):
        """The force arg test of the structure.create_diff_tensor_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin arguments, and skip them.
            if data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxBinError, self.structure_fns.create_diff_tensor_pdb, force=data[1])


    def test_create_vector_dist_argfail_length(self):
        """The length arg test of the structure.create_vector_dist() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float arguments, and skip them.
            if data[0] == 'float':
                continue

            # The argument test.
            self.assertRaises(RelaxFloatError, self.structure_fns.create_vector_dist, length=data[1])


    def test_create_vector_dist_argfail_symmetry(self):
        """The symmetry arg test of the structure.create_vector_dist() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin arguments, and skip them.
            if data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxBinError, self.structure_fns.create_vector_dist, symmetry=data[1])


    def test_create_vector_dist_argfail_file(self):
        """The file arg test of the structure.create_vector_dist() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.structure_fns.create_vector_dist, file=data[1])


    def test_create_vector_dist_argfail_dir(self):
        """The dir arg test of the structure.create_vector_dist() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.structure_fns.create_vector_dist, dir=data[1])


    def test_create_vector_dist_argfail_force(self):
        """The force arg test of the structure.create_vector_dist() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin arguments, and skip them.
            if data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxBinError, self.structure_fns.create_vector_dist, force=data[1])


    def test_read_pdb_argfail_file(self):
        """The file arg test of the structure.read_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.structure_fns.read_pdb, file=data[1])


    def test_read_pdb_argfail_dir(self):
        """The dir arg test of the structure.read_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.structure_fns.read_pdb, file='test.pdb', dir=data[1])


    def test_read_pdb_argfail_model(self):
        """The model arg test of the structure.read_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and int arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneIntError, self.structure_fns.read_pdb, file='test.pdb', model=data[1])


    def test_read_pdb_argfail_load_seq(self):
        """The load_seq arg test of the structure.read_pdb() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the bin arguments, and skip them.
            if data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxBinError, self.structure_fns.read_pdb, file='test.pdb', load_seq=data[1])


    def test_vectors_argfail_heteronuc(self):
        """The heteronuc arg test of the structure.vectors() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.structure_fns.vectors, heteronuc=data[1])


    def test_vectors_argfail_proton(self):
        """The proton arg test of the structure.vectors() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.structure_fns.vectors, proton=data[1])


    def test_vectors_argfail_spin_id(self):
        """The spin_id arg test of the structure.vectors() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.structure_fns.vectors, spin_id=data[1])


