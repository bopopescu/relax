###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module for the manipulation of relaxation data."""

# Python module imports.
import sys

# relax module imports.
from generic_fns.interatomic import create_interatom, interatomic_loop, return_interatom
from generic_fns.mol_res_spin import Selection, return_spin, spin_loop
from relax_errors import RelaxError
from relax_io import write_data



def define(spin_id1=None, spin_id2=None, direct_bond=False):
    """Set up the magnetic dipole-dipole interaction.

    @keyword spin_id1:      The spin identifier string of the first spin of the pair.
    @type spin_id1:         str
    @keyword spin_id2:      The spin identifier string of the second spin of the pair.
    @type spin_id2:         str
    @keyword direct_bond:   A flag specifying if the two spins are directly bonded.
    @type direct_bond:      bool
    """

    # Loop over both spin selections.
    ids = []
    for spin, id1 in spin_loop(spin_id1, return_id=True):
        for spin, id2 in spin_loop(spin_id2, return_id=True):
            # Directly bonded atoms.
            if direct_bond and hasattr(cdp, 'structure') and not cdp.structure.are_bonded(atom_id1=id1, atom_id2=id2):
                continue

            # Get the interatomic data object, if it exists.
            interatom = return_interatom(id1, id2)

            # Check that this has not already been set up.
            if hasattr(interatom, 'dipole_pair') and interatom.dipole_pair:
                raise RelaxError("The magnetic dipole-dipole interaction already exists between the spins '%s' and '%s'." % (id1, id2))

            # Create the container if needed.
            if not interatom:
                interatom = create_interatom(spin_id1=id1, spin_id2=id2)

            # Set a flag indicating that a dipole-dipole interaction is present.
            interatom.dipole_pair = True

            # Store the IDs for the print out.
            ids.append([repr(id1), repr(id2)])

    # Print out.
    write_data(out=sys.stdout, headings=["Spin_ID_1", "Spin_ID_2"], data=ids)


def set_dist(spin_id1=None, spin_id2=None, ave_dist=None):
    """Set up the magnetic dipole-dipole interaction.

    @keyword spin_id1:      The spin identifier string of the first spin of the pair.
    @type spin_id1:         str
    @keyword spin_id2:      The spin identifier string of the second spin of the pair.
    @type spin_id2:         str
    @keyword ave_dist:      The r^-3 averaged interatomic distance.
    @type ave_dist:         float
    """

    # Generate the selection objects.
    sel_obj1 = Selection(spin_id1)
    sel_obj2 = Selection(spin_id2)

    # Loop over the interatomic containers.
    data = []
    for interatom in interatomic_loop():
        # Get the spin info.
        mol_name1, res_num1, res_name1, spin1 = return_spin(interatom.spin_id1, full_info=True)
        mol_name2, res_num2, res_name2, spin2 = return_spin(interatom.spin_id2, full_info=True)

        # No match, either way.
        if not (sel_obj1.contains_spin(spin_num=spin1.num, spin_name=spin1.name, res_num=res_num1, res_name=res_name1, mol=mol_name1) and sel_obj2.contains_spin(spin_num=spin2.num, spin_name=spin2.name, res_num=res_num2, res_name=res_name2, mol=mol_name2)) and not (sel_obj2.contains_spin(spin_num=spin1.num, spin_name=spin1.name, res_num=res_num1, res_name=res_name1, mol=mol_name1) and sel_obj1.contains_spin(spin_num=spin2.num, spin_name=spin2.name, res_num=res_num2, res_name=res_name2, mol=mol_name2)):
            continue

        # Store the averaged distance.
        interatom.r = ave_dist

        # Store the data for the print out.
        data.append([repr(interatom.spin_id1), repr(interatom.spin_id2), repr(ave_dist)])

    # Print out.
    write_data(out=sys.stdout, headings=["Spin_ID_1", "Spin_ID_2", "Ave_distance"], data=data)
