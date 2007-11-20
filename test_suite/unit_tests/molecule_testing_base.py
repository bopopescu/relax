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

# relax module imports.
from data import Data as relax_data_store
from generic_fns import molecule, residue
from relax_errors import RelaxError, RelaxNoPipeError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError



class Molecule_base_class:
    """Base class for the tests of both the 'prompt.molecule' and 'generic_fns.molecule' modules.

    This base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the molecule unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        relax_data_store.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        relax_data_store.current_pipe = 'orig'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def setup_data(self):
        """Function for setting up some data for the unit tests."""

        # Create the first residue and add some data to its spin container.
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1
        relax_data_store['orig'].mol[0].name = 'Old mol'

        # Create a second molecule.
        relax_data_store['orig'].mol.add_item('New mol')

        # Copy the residue to the new molecule.
        residue.copy(res_from=':1', res_to='#New mol')
        residue.copy(res_from='#Old mol:1', res_to='#New mol:5')

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2


    def test_copy_between_pipes(self):
        """Test the copying of the molecule data between different data pipes.

        The function tested is both generic_fns.molecule.copy() and prompt.molecule.copy().
        """

        # Create the first molecule and residue and add some data to its spin container.
        self.molecule_fns.create('Old mol')
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the molecule to the second data pipe.
        self.molecule_fns.copy(mol_from='#Old mol', pipe_to='test')
        self.molecule_fns.copy(pipe_from='orig', mol_from='#Old mol', pipe_to='test', mol_to='#New mol')

        # Change the first molecule's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Test the original molecule.
        self.assertEqual(relax_data_store['orig'].mol[0].name, 'Old mol')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new molecule.
        self.assertEqual(relax_data_store['test'].mol[0].name, 'Old mol')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].x, 1)

        # Test the second new molecule.
        self.assertEqual(relax_data_store['test'].mol[1].name, 'New mol')
        self.assertEqual(relax_data_store['test'].mol[1].res[0].num, 1)
        self.assertEqual(relax_data_store['test'].mol[1].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['test'].mol[1].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[1].res[0].spin[0].x, 1)


    def test_copy_between_pipes_fail_no_pipe(self):
        """Test the failure of copying of the molecule data between different data pipes.

        The function tested is both generic_fns.molecule.copy() and prompt.molecule.copy().
        """

        # Create the first molecule and residue and add some data to its spin container.
        self.molecule_fns.create('Old mol')
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the molecule to the second data pipe.
        self.assertRaises(RelaxNoPipeError, self.molecule_fns.copy, mol_from='#Old mol', pipe_to='test2')


    def test_copy_within_pipe(self):
        """Test the copying of the molecule data within a single data pipe.

        The function tested is both generic_fns.molecule.copy() and prompt.molecule.copy().
        """

        # Create the first molecule and residue and add some data to its spin container.
        self.molecule_fns.create('Old mol')
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the molecule a few times.
        self.molecule_fns.copy(mol_from='#Old mol', mol_to='#2')
        self.molecule_fns.copy(mol_from='#Old mol', pipe_to='orig', mol_to='#3')

        # Change the first molecule's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Copy the molecule once more.
        self.molecule_fns.copy(mol_from='#Old mol', mol_to='#4')

        # Test the original molecule.
        self.assertEqual(relax_data_store['orig'].mol[0].name, 'Old mol')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new molecule 2.
        self.assertEqual(relax_data_store['orig'].mol[1].name, 2)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].x, 1)

        # Test the new molecule 3.
        self.assertEqual(relax_data_store['orig'].mol[2].name, 3)
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].spin[0].x, 1)

        # Test the new molecule 4.
        self.assertEqual(relax_data_store['orig'].mol[3].name, 4)
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].spin[0].x, 2)


    def test_copy_within_pipe_fail(self):
        """Test the failure of the copying of the molecule data within a molecule.

        The function tested is both generic_fns.molecule.copy() and prompt.molecule.copy().
        """

        # Create a few molecules.
        self.molecule_fns.create('GST')
        self.molecule_fns.create('GB1')

        # Copy a non-existent molecule (MBP).
        self.assertRaises(RelaxError, self.molecule_fns.copy, mol_from='#MBP', mol_to='#IL4')

        # Copy a molecule to one which already exists.
        self.assertRaises(RelaxError, self.molecule_fns.copy, mol_from='#GST', mol_to='#GB1')


    def test_creation(self):
        """Test the creation of a molecule data structure.

        The function tested is both generic_fns.molecule.create() and prompt.molecule.create().
        """

        # Create a few new molecules.
        self.molecule_fns.create('Ap4Aase')
        self.molecule_fns.create('ATP')
        self.molecule_fns.create(mol_name='MgF4')

        # Test that the molecule names are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].name, 'Ap4Aase')
        self.assertEqual(relax_data_store['orig'].mol[1].name, 'ATP')
        self.assertEqual(relax_data_store['orig'].mol[2].name, 'MgF4')


    def test_creation_fail(self):
        """Test the failure of molecule creation by supplying two molecules with the same name.

        The function tested is both generic_fns.molecule.create() and prompt.molecule.create().
        """

        # Create the first molecule.
        self.molecule_fns.create('CaM')

        # Assert that a RelaxError occurs when the next added molecule has the same name as the first.
        self.assertRaises(RelaxError, self.molecule_fns.create, 'CaM')


    def test_delete(self):
        """Test molecule deletion.

        The function tested is both generic_fns.molecule.delete() and prompt.molecule.delete().
        """

        # Set up some data.
        self.setup_data()

        # Delete the first molecule.
        self.molecule_fns.delete(mol_id='#Old mol')

        # Test that the first molecule is now 'New mol'.
        self.assertEqual(relax_data_store['orig'].mol[0].name, 'New mol')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[0].spin[0], 'x'))
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 5)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[1].spin[0], 'x'))


    def test_delete_all(self):
        """Test the deletion of all molecules.

        The function tested is both generic_fns.molecule.delete() and prompt.molecule.delete().
        """

        # Set up some data.
        self.setup_data()

        # Delete all molecules.
        self.molecule_fns.delete(mol_id='#Old mol')
        self.molecule_fns.delete(mol_id='#New mol')

        # Test that the first molecule defaults back to the empty container.
        self.assertEqual(relax_data_store['orig'].mol[0].name, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, None)


    def test_delete_fail(self):
        """Test the failure of molecule deletion when a residue or spin id is supplied.

        The function tested is both generic_fns.molecule.delete() and prompt.molecule.delete().
        """

        # Supply a spin id.
        self.assertRaises(RelaxSpinSelectDisallowError, self.molecule_fns.delete, mol_id='@2')

        # Supply a residue id.
        self.assertRaises(RelaxResSelectDisallowError, self.molecule_fns.delete, mol_id=':1')


    def test_display(self):
        """Test the display of molecular information.

        The function tested is both generic_fns.molecule.display() and prompt.molecule.display().
        """

        # Set up some data.
        self.setup_data()

        # The following should all work without error.
        self.molecule_fns.display()
        self.molecule_fns.display('#Old mol')
        self.molecule_fns.display(mol_id='#New mol')


    def test_display_fail(self):
        """Test the failure of the display of molecule information.

        The function tested is both generic_fns.molecule.display() and prompt.molecule.display().
        """

        # Set up some data.
        self.setup_data()

        # The following should fail.
        self.assertRaises(RelaxSpinSelectDisallowError, self.molecule_fns.display, '@N')
        self.assertRaises(RelaxResSelectDisallowError, self.molecule_fns.display, ':1')


    def test_rename(self):
        """Test the renaming of a molecule.

        The function tested is both generic_fns.molecule.rename() and prompt.molecule.rename().
        """

        # Set up some data.
        self.setup_data()

        # Rename the molecule.
        self.molecule_fns.rename(mol_id='#New mol', new_name='K')

        # Test that the molecule has been renamed.
        self.assertEqual(relax_data_store['orig'].mol[1].name, 'K')


    def test_rename_fail(self):
        """Test the failure of renaming a molecule when a residue or spin id is given.

        The function tested is both generic_fns.molecule.rename() and prompt.molecule.rename().
        """

        # Try renaming using a spin id.
        self.assertRaises(RelaxSpinSelectDisallowError, self.molecule_fns.rename, mol_id='@111', new_name='K')

        # Try renaming using a residue id.
        self.assertRaises(RelaxResSelectDisallowError, self.molecule_fns.rename, mol_id=':1', new_name='K')


    def test_rename_many_fail(self):
        """Test the failure of the renaming of multiple molecules to the same name.

        The function tested is both generic_fns.molecule.rename() and prompt.molecule.rename().
        """

        # Set up some data.
        self.setup_data()

        # Test for the failure.
        self.assertRaises(RelaxError, self.molecule_fns.rename, mol_id='#Old mol,New mol', new_name='K')
