###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
from os import F_OK, access
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from generic_fns import molmol
from generic_fns.selection import exists_mol_res_spin_data, return_molecule, return_residue, return_spin, spin_loop
from generic_fns.structure.scientific import Scientific_data
from relax_errors import RelaxError, RelaxFileError, RelaxNoPipeError, RelaxNoSequenceError, RelaxPdbError
from relax_io import get_file_path
from relax_warnings import RelaxNoPDBFileWarning



def load_spins(spin_id=None):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:   The molecule, residue, and spin identifier string.
    @type spin_id:      str
    """

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Print out.
    print "Generating the spins from the loaded structure.\n"

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Loop over all atoms of the spin_id selection.
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(atom_id=spin_id, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True):
        # Initialise the identification string.
        id = ''

        # Get the molecule container corresponding to the molecule name.
        if mol_name:
            # Update the ID string.
            id = id + '#' + mol_name

            # The container.
            mol_cont = return_molecule(id)

        # The is only one molecule and it is unnamed.
        elif cdp.mol[0].name == None and len(cdp.mol) == 1:
            mol_cont = cdp.mol[0]

        # Add the molecule if it doesn't exist.
        if mol_name and mol_cont == None:
            # Add the molecule.
            cdp.mol.add_item(mol_name=mol_name)

            # Get the container.
            mol_cont = cdp.mol[-1]

        # Add the residue number to the ID string (residue name is ignored because only the number is unique).
        id = id + ':' + `res_num`

        # Get the corresponding residue container.
        res_cont = return_residue(id)

        # Add the residue if it doesn't exist.
        if res_num and res_name and res_cont == None:
            # Add the residue.
            mol_cont.res.add_item(res_name=res_name, res_num=res_num)

            # Get the container.
            res_cont = mol_cont.res[-1]

        # Add the atom number to the ID string (atom name is ignored because only the number is unique).
        id = id + '@' + `atom_num`

        # Get the corresponding spin container.
        spin_cont = return_spin(id)

        # Add the spin if it doesn't exist.
        if atom_name and spin_cont == None:
            # Add the spin.
            res_cont.spin.add_item(spin_name=atom_name, spin_num=atom_num)

            # Get the container.
            spin_cont = res_cont.spin[-1]

        # Add the position vector to the spin container.
        spin_cont.pos = pos


def read_pdb(file=None, dir=None, model=None, parser='scientific', fail=True, verbosity=1):
    """The PDB loading function.

    Parsers
    =======

    Currently only the Scientific Python parser is available for reading PDB files.  This parser is
    selected only if the parser keyword argument is set to 'scientific'.


    @keyword file:          The name of the PDB file to read.
    @type file:             str
    @keyword dir:           The directory where the PDB file is located.  If set to None, then the
                            file will be searched for in the current directory.
    @type dir:              str or None
    @keyword model:         The PDB model to extract from the file.  If set to None, then all models
                            will be loaded.
    @type model:            int or None
    @keyword parser:        The parser to be used to read the PDB file.
    @type parser:           str
    @keyword fail:          A flag which, if True, will cause a RelaxError to be raised if the PDB
                            file does not exist.  If False, then a RelaxWarning will be trown
                            instead.
    @type fail:             bool
    @keyword verbosity:     The amount of information to print to screen.  Zero corresponds to
                            minimal output while higher values increase the amount of output.  The
                            default value is 1.
    @type verbosity:        int
    @raise RelaxFileError:  If the fail flag is set, then a RelaxError is raised if the PDB file
                            does not exist.
    """

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if structural data already exists.
    if hasattr(cdp, 'struct'):
        raise RelaxPdbError

    # The file path.
    file_path = get_file_path(file, dir)

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError, ('PDB', file_path)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return

    # Place the Scientific Python structural object into the relax data store.
    if parser == 'scientific':
        cdp.structure = Scientific_data()

    # Load the structures.
    cdp.structure.load_structures(file_path, model, verbosity)

    # Load into Molmol (if running).
    molmol.open_pdb()


def set_vector(spin=None, xh_vect=None):
    """Place the XH unit vector into the spin container object.

    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword xh_vect:   The unit vector parallel to the XH bond.
    @type xh_vect:      array of len 3
    """

    # Place the XH unit vector into the container.
    spin.xh_vect = xh_vect


def vectors(heteronuc=None, proton=None, spin_id=None, verbosity=1):
    """Function for calculating/extracting the XH unit vector from the loaded structure.

    @param heteronuc:   The name of the heteronucleus.
    @type heteronuc:    str
    @param proton:      The name of the proton.
    @type proton:       str
    @param spin_id:     The molecule, residue, and spin identifier string.
    @type spin_id:      str
    @param verbosity:   The higher the value, the more information is printed to screen.
    @type verbosity:    int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test that the nuclei have been correctly set.
    if heteronuc == proton:
        raise RelaxError, "The proton and heteronucleus are set to the same atom."

    # Number of structures.
    num_str = len(cdp.structure.structures)

    # Print out.
    if verbosity:
        if num_str > 1:
            print "\nCalculating and averaging the unit XH vectors from all structures."
        else:
            print "\nCalculating the unit XH vectors from the structure."

    # Loop over the sequence.
    for spin in spin_loop(spin_id):
        # Skip unselected residues.
        if not spin.select:
            continue

        # Set the proton and heteronucleus names.
        spin.proton = proton
        spin.heteronuc = heteronuc

        # Calculate the vector.
        vector = xh_vector(spin)

        # Set the vector and deselect the spin if the vector doesn't exist.
        if vector != None:
            spin.xh_vect = vector    
        else:
            spin.select = False
