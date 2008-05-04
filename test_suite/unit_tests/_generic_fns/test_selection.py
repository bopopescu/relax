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
from generic_fns import selection
from relax_errors import RelaxError, RelaxNoPipeError


class Test_selection(TestCase):
    """Unit tests for the functions of the 'generic_fns.selection' module."""

    def setUp(self):
        """Set up some residues and spins for testing their selection and deselection."""

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Name the first molecule.
        cdp.mol[0].name = 'Ap4Aase'

        # Add a second molecule to the system.
        cdp.mol.add_item(mol_name='RNA')

        # Add two more residues to the first molecule (and set the residue number of the first).
        cdp.mol[0].res[0].num = 1
        cdp.mol[0].res.add_item(res_num=2, res_name='Glu')
        cdp.mol[0].res.add_item(res_num=4, res_name='Pro')

        # Add some spin info to this molecule.
        cdp.mol[0].res[0].spin[0].name = 'NH'
        cdp.mol[0].res[0].spin[0].num = 60
        cdp.mol[0].res[1].spin[0].name = 'NH'
        cdp.mol[0].res[1].spin[0].num = 63

        # Add one more residue to the second molecule (and set the residue number of the first).
        cdp.mol[1].res[0].num = -5
        cdp.mol[1].res.add_item(res_num=-4)

        # Add a second set of spins to the second molecule (naming the first set first).
        cdp.mol[1].res[0].spin[0].name = 'C8'
        cdp.mol[1].res[1].spin[0].name = 'C8'
        cdp.mol[1].res[0].spin.add_item(spin_name='N5')
        cdp.mol[1].res[1].spin.add_item(spin_name='N5')

        # Deselect a number of spins.
        cdp.mol[0].res[0].spin[0].select = 0
        cdp.mol[0].res[2].spin[0].select = 0
        cdp.mol[1].res[0].spin[0].select = 0
        cdp.mol[1].res[1].spin[1].select = 0


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset.
        relax_data_store.__reset__()
