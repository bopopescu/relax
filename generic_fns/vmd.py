###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007 Edward d'Auvergne                             #
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
from Scientific.Visualization import VMD

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxNoPdbError


# The relax data storage object.



class Vmd:
    def __init__(self, relax):
        """Class containing the functions for viewing molecules."""

        self.relax = relax


    def view(self, run):
        """Function for viewing the collection of molecules using VMD."""

        # Test if the PDB file has been loaded.
        if not relax_data_store.pdb.has_key(run):
            raise RelaxNoPdbError, run

        # Create an empty scene.
        relax_data_store.vmd_scene = VMD.Scene()

        # Add the molecules to the scene.
        for i in xrange(len(relax_data_store.pdb[run].structures)):
            relax_data_store.vmd_scene.addObject(VMD.Molecules(relax_data_store.pdb[run].structures[i]))

        # View the scene.
        relax_data_store.vmd_scene.view()
