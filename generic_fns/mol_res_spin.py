###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2008 Edward d'Auvergne                        #
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
"""Module for the manipulation of the molecule-residue-spin data structures in the relax data store.

The functionality of this module is diverse:
    - Documentation for the spin identification string.
    - Functions for parsing or generating spin identification strings.
    - The mol-res-spin selection object (derived from the Selection class).
    - Generator functions for looping over molecules, residues, or spins.
    - Functions for returning MoleculeContainer, ResidueContainer, and SpinContainer objects or
    information about these.
    - Functions for copying, creating, deleting, displaying, naming, and numbering
    MoleculeContainer, ResidueContainer, and SpinContainer objects in the relax data store.
    - Functions for counting spins or testing their existence.
"""

# Python module imports.
from re import split
from string import strip
from textwrap import fill
from warnings import warn

# relax module imports.
from data.mol_res_spin import MoleculeContainer, ResidueContainer, SpinContainer
from generic_fns import pipes
from generic_fns import relax_re
from relax_errors import RelaxError, RelaxNoSpinError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError
from relax_warnings import RelaxWarning


id_string_doc = """
Identification string documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The identification string is composed of three components: the molecule id token beginning with the '#' character, the residue id token beginning with the ':' character, and the atom or spin system id token beginning with the '@' character.  Each token can be composed of multiple elements separated by the ',' character and each individual element can either be a number (which must be an integer, in string format), a name, or a range of numbers separated by the '-' character.  Negative numbers are supported.  The full id string specification is

    #<mol_name> :<res_id>[, <res_id>[, <res_id>, ...]] @<atom_id>[, <atom_id>[, <atom_id>, ...]],

where the token elements are

    <mol_name>, the name of the molecule,
    <res_id>, the residue identifier which can be a number, name, or range of numbers,
    <atom_id>, the atom or spin system identifier which can be a number, name, or range of numbers.

If one of the tokens is left out then all elements will be assumed to match.  For example if the string does not contain the '#' character then all molecules will match the string.

Regular expression can be used to select spins.  For example the string '@H*' will select the protons 'H', 'H2', 'H98'.
"""

# Wrap the id string doc.
string = ''
for line in split('\n', id_string_doc):
    string = string + fill(line, width=100, initial_indent=8*' ', subsequent_indent=8*' ') + '\n'
id_string_doc = string



class Selection(object):
    """An object containing mol-res-spin selections.

    A Selection object represents either a set of selected molecules, residues and spins, or the
    union or intersection of two other Selection objects.
    """

    def __init__(self, select_string):
        """Initialise a Selection object.

        @param select_string:   A mol-res-spin selection string.
        @type select_string:    string
        """

        self._union = None
        self._intersect = None

        self.molecules = []
        self.residues = []
        self.spins = []

        if not select_string:
            return

        # Read boolean symbols from right to left:
        and_index = select_string.rfind('&')
        or_index = select_string.rfind('|')

        if and_index > or_index:
            sel0 = Selection(select_string[:and_index].strip())
            sel1 = Selection(select_string[and_index+1:].strip())
            self.intersection(sel0, sel1)

        elif or_index > and_index:
            sel0 = Selection(select_string[:or_index].strip())
            sel1 = Selection(select_string[or_index+1:].strip())
            self.union(sel0, sel1)

        # No booleans, so parse as simple selection:
        else:
            mol_token, res_token, spin_token = tokenise(select_string)
            self.molecules = parse_token(mol_token)
            self.residues = parse_token(res_token)
            self.spins = parse_token(spin_token)


    def __contains__(self, obj):
        """Replacement function for determining if an object matches the selection.

        @param obj:     The data object.  This can be a MoleculeContainer, ResidueContainer, or
                        SpinContainer instance or a type of these instances.  If a tuple, only one
                        type of object can be in the tuple.
        @type obj:      instance or type of instances.
        @return:        The answer of whether the object matches the selection.
        @rtype:         bool
        """

        # The selection object is a union.
        if self._union:
            return (obj in self._union[0]) or (obj in self._union[1])

        # The selection object is an intersection.
        elif self._intersect:
            return (obj in self._intersect[0]) and (obj in self._intersect[1])

        # Simple spin identification string.
        if type(obj) == str:
            return self.__contains_spin_id(obj)

        # Comparison of data containers to this selection object.
        else:
            return self.__contains_mol_res_spin_containers(obj)


    def __contains_mol_res_spin_containers(self, obj):
        """Are the MoleculeContainer, ResidueContainer, and/or SpinContainer in the selection.

        @param obj:     The data object.  This can be a MoleculeContainer, ResidueContainer, or
                        SpinContainer instance or a type of these instances.  If a tuple, only one
                        type of object can be in the tuple.
        @type obj:      instance or type of instances.
        @return:        The answer of whether the objects are found within the selection object.
        @rtype:         bool
        """

        # Initialise the molecule, residue, and spin objects.
        mol = None
        res = None
        spin = None

        # The object is not a tuple, so lets turn it into one.
        if type(obj) != tuple:
            obj = (obj,)

        # Max 3 objects (cannot match, so False).
        if len(obj) > 3:
            return False

        # Loop over the objects.
        for i in range(len(obj)):
            # The object is a molecule.
            if isinstance(obj[i], MoleculeContainer):
                # Error.
                if mol != None:
                    raise RelaxError, "Comparing two molecular containers simultaneously with the selection object is not supported."

                # Unpack.
                mol = obj[i]

            # The object is a residue.
            elif isinstance(obj[i], ResidueContainer):
                # Error.
                if res != None:
                    raise RelaxError, "Comparing two residue containers simultaneously with the selection object is not supported."

                # Unpack.
                res = obj[i]

            # The object is a spin.
            elif isinstance(obj[i], SpinContainer):
                # Error.
                if spin != None:
                    raise RelaxError, "Comparing two spin containers simultaneously with the selection object is not supported."

                # Unpack.
                spin = obj[i]

            # Unknown object (so return False).
            else:
                return False

        # Selection flags.
        select_mol = False
        select_res = False
        select_spin = False

        # Molecule container.
        if mol:
            # No molecules in selection object, therefore default to a match.
            if not self.molecules:
                select_mol = True

            # A true match.
            elif relax_re.search(self.molecules, mol.name):
                select_mol = True
        else:
            # No molecule container sent in, therefore the molecule is assumed to match.
            select_mol = True

        # Residue container.
        if res:
            # No residues in selection object, therefore default to a match.
            if not self.residues:
                select_res = True

            # A true match.
            elif relax_re.search(self.residues, res.name) or res.num in self.residues:
                select_res = True
        else:
            # No residue container sent in, therefore the residue is assumed to match.
            select_res = True

        # Spin container.
        if spin:
            # No spins in selection object, therefore default to a match.
            if not self.spins:
                select_spin = True

            # A true match.
            elif relax_re.search(self.spins, spin.name) or spin.num in self.spins:
                select_spin = True
        else:
            # No spin container sent in, therefore the spin is assumed to match.
            select_spin = True

        # Return the selection status.
        return select_mol and select_res and select_spin


    def __contains_spin_id(self, spin_id):
        """Is the molecule, residue, and/or spin of the spin_id string located in the selection.

        Only the simple selections allowed by the tokenise function are currently supported.


        @param spin_id: The spin identification string.
        @type spin_id:  str
        @return:        The answer of whether the molecule, residue, and/or spin corresponding to
                        the spin_id string found within the selection object.
        @rtype:         bool
        """

        # Parse the spin_id string.
        try:
            mol_token, res_token, spin_token = tokenise(spin_id)
            molecules = parse_token(mol_token)
            residues = parse_token(res_token)
            spins = parse_token(spin_token)
        except RelaxError:
            warn(RelaxWarning("The spin identification string " + `spin_id` + " is too complex for the selection object."))


    def contains_mol(self, mol=None):
        """Determine if the molecule name, in string form, is contained in this selection object.

        @keyword mol:   The name of the molecule.
        @type mol:      str or None
        @return:        The answer of whether the molecule is contained withing the selection
                        object.
        @rtype:         bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].contains_mol(mol) or self._union[1].contains_mol(mol)

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].contains_mol(mol) and self._intersect[1].contains_mol(mol)

        # The check.
        if relax_re.search(self.molecules, mol):
            return True

        # Nothingness.
        if not self.molecules:
            return True

        # No match.
        return False


    def contains_res(self, res_num=None, res_name=None, mol=None):
        """Determine if the residue name, in string form, is contained in this selection object.

        @keyword res_num:   The residue number.
        @type res_num:      int or None
        @keyword res_name:  The residue name.
        @type res_name:     str or None
        @keyword mol:       The molecule name.
        @type mol:          str or None
        @return:            The answer of whether the molecule is contained withing the selection
                            object.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].contains_res(res_num, res_name, mol) or self._union[1].contains_res(res_num, res_name, mol)

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].contains_res(res_num, res_name, mol) and self._intersect[1].contains_res(res_num, res_name, mol)

        # Does it contain the molecule.
        select_mol = self.contains_mol(mol)

        # Residue selection flag.
        select_res = False

        # The residue checks.
        if res_num in self.residues or relax_re.search(self.residues, res_name):
            select_res = True

        # Nothingness.
        if not self.residues:
            select_res = True

        # Return the result.
        return select_res and select_mol


    def contains_spin(self, spin_num=None, spin_name=None, res_num=None, res_name=None, mol=None):
        """Determine if the spin is contained in this selection object.

        @keyword spin_num:  The spin number.
        @type spin_num:     int or None
        @keyword spin_name: The spin name.
        @type spin_name:    str or None
        @keyword res_num:   The residue number.
        @type res_num:      int or None
        @keyword res_name:  The residue name.
        @type res_name:     str or None
        @keyword mol:       The molecule name.
        @type mol:          str or None
        @return:            The answer of whether the spin is contained withing the selection
                            object.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].contains_spin(spin_num, spin_name, res_num, res_name, mol) or self._union[1].contains_spin(spin_num, spin_name, res_num, res_name, mol)

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].contains_spin(spin_num, spin_name, res_num, res_name, mol) and self._intersect[1].contains_spin(spin_num, spin_name, res_num, res_name, mol)

        # Does it contain the molecule.
        select_mol = self.contains_mol(mol)

        # Does it contain the residue.
        select_res = self.contains_res(res_num, res_name, mol)

        # Spin selection flag.
        select_spin = False

        # The spin checks.
        if spin_num in self.spins or relax_re.search(self.spins, spin_name):
            select_spin = True

        # Nothingness.
        if not self.spins:
            select_spin = True

        # Return the result.
        return select_spin and select_res and select_mol


    def has_molecules(self):
        """Determine if the selection object contains molecules.

        @return:            The answer of whether the selection contains molecules.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].has_molecules() or self._union[1].has_molecules()

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].has_molecules() and self._intersect[1].has_molecules()

        # Molecules are present.
        if self.molecules:
            return True


    def has_residues(self):
        """Determine if the selection object contains residues.

        @return:            The answer of whether the selection contains residues.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].has_residues() or self._union[1].has_residues()

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].has_residues() and self._intersect[1].has_residues()

        # Residues are present.
        if self.residues:
            return True


    def has_spins(self):
        """Determine if the selection object contains spins.

        @return:            The answer of whether the selection contains spins.
        @rtype:             bool
        """

        # The selection object is a union.
        if self._union:
            return self._union[0].has_spins() or self._union[1].has_spins()

        # The selection object is an intersection.
        elif self._intersect:
            return self._intersect[0].has_spins() and self._intersect[1].has_spins()

        # Spins are present.
        if self.spins:
            return True


    def intersection(self, select_obj0, select_obj1):
        """Make this Selection object the intersection of two other Selection objects.

        @param select_obj0: First Selection object in intersection.
        @type select_obj0:  Selection instance.
        @param select_obj1: First Selection object in intersection.
        @type select_obj1:  Selection instance.
        """

        # Check that nothing is set.
        if self._union or self._intersect or self.molecules or self.residues or self.spins:
            raise RelaxError, "Cannot define multiple Boolean relationships between Selection objects"

        # Create the intersection.
        self._intersect = (select_obj0, select_obj1)


    def union(self, select_obj0, select_obj1):
        """Make this Selection object the union of two other Selection objects.

        @param select_obj0: First Selection object in intersection.
        @type select_obj0:  Selection instance.
        @param select_obj1: First Selection object in intersection.
        @type select_obj1:  Selection instance.
        """

        # Check that nothing is set.
        if self._union or self._intersect or self.molecules or self.residues or self.spins:
            raise RelaxError, "Cannot define multiple Boolean relationships between Selection objects"

        # Create the union.
        self._union = (select_obj0, select_obj1)



def __linear_ave(positions):
    """Perform linear averaging of the atomic positions.

    @param positions:   The atomic positions.  The first index is that of the positions to be
                        averaged over.  The second, optionally, can be the different models if
                        present.  The last index is over the x, y, and z coordinates.
    @type positions:    rank-2 list of floats or rank-3 list of floats
    @return:            The averaged positions.  Either a single vector or an list of vectors.
    @rtype:             rank-1 list of floats or rank-2 list of floats
    """

    # Multi-model averaging.
    multi_model = False
    if type(positions[0][0]) == list:
        multi_model = True

    # Convert a rank-2 list into a rank-3 list (avoid code duplication).
    if not multi_model:
        for i in range(len(positions)):
            positions[i] = [positions[i]]

    # Loop over the multiple models.
    ave = []
    for model_index in range(len(positions[0])):
        # Append an empty vector.
        ave.append([0.0, 0.0, 0.0])

        # Loop over the x, y, and z coordinates.
        for coord_index in range(3):
            # Loop over the atomic positions.
            for atom_index in range(len(positions)):
                ave[model_index][coord_index] = ave[model_index][coord_index] + positions[atom_index][model_index][coord_index]

            # Average.
            ave[model_index][coord_index] = ave[model_index][coord_index] / len(positions)

    # Return the averaged positions.
    return ave


def copy_molecule(pipe_from=None, mol_from=None, pipe_to=None, mol_to=None):
    """Copy the contents of a molecule container to a new molecule.

    For copying to be successful, the mol_from identification string must match an existent molecule.

    @param pipe_from:   The data pipe to copy the molecule data from.  This defaults to the current
                        data pipe.
    @type pipe_from:    str
    @param mol_from:    The molecule identification string for the structure to copy the data from.
    @type mol_from:     str
    @param pipe_to:     The data pipe to copy the molecule data to.  This defaults to the current
                        data pipe.
    @type pipe_to:      str
    @param mol_to:      The molecule identification string for the structure to copy the data to.
    @type mol_to:       str
    """

    # The current data pipe.
    if pipe_from == None:
        pipe_from = pipes.cdp_name()
    if pipe_to == None:
        pipe_to = pipes.cdp_name()

    # The second pipe does not exist.
    pipes.test(pipe_to)

    # Split up the selection string.
    mol_from_token, res_from_token, spin_from_token = tokenise(mol_from)
    mol_to_token, res_to_token, spin_to_token = tokenise(mol_to)

    # Disallow spin selections.
    if spin_from_token != None or spin_to_token != None:
        raise RelaxSpinSelectDisallowError

    # Disallow residue selections.
    if res_from_token != None or res_to_token != None:
        raise RelaxResSelectDisallowError

    # Parse the molecule token for renaming.
    mol_name_to = return_single_molecule_info(mol_to_token)

    # Test if the molecule name already exists.
    mol_to_cont = return_molecule(mol_to, pipe_to)
    if mol_to_cont and not mol_to_cont.is_empty():
        raise RelaxError, "The molecule " + `mol_to` + " already exists in the " + `pipe_to` + " data pipe."

    # Get the single molecule data container.
    mol_from_cont = return_molecule(mol_from, pipe_from)

    # No molecule to copy data from.
    if mol_from_cont == None:
        raise RelaxError, "The molecule " + `mol_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Get the target pipe.
    pipe = pipes.get_pipe(pipe_to)

    # Copy the data.
    if pipe.mol[0].name == None and len(pipe.mol) == 1:
        pipe.mol[0] = mol_from_cont.__clone__()
    else:
        pipe.mol.append(mol_from_cont.__clone__())

    # Change the new molecule name.
    if mol_name_to != None:
        pipe.mol[-1].name = mol_name_to


def copy_residue(pipe_from=None, res_from=None, pipe_to=None, res_to=None):
    """Copy the contents of the residue structure from one residue to a new residue.

    For copying to be successful, the res_from identification string must match an existent residue.
    The new residue number must be unique.

    @param pipe_from:   The data pipe to copy the residue from.  This defaults to the current data
                        pipe.
    @type pipe_from:    str
    @param res_from:    The residue identification string for the structure to copy the data from.
    @type res_from:     str
    @param pipe_to:     The data pipe to copy the residue to.  This defaults to the current data
                        pipe.
    @type pipe_to:      str
    @param res_to:      The residue identification string for the structure to copy the data to.
    @type res_to:       str
    """

    # The current data pipe.
    if pipe_from == None:
        pipe_from = pipes.cdp_name()
    if pipe_to == None:
        pipe_to = pipes.cdp_name()

    # The second pipe does not exist.
    pipes.test(pipe_to)

    # Get the target pipe.
    pipe = pipes.get_pipe(pipe_to)

    # Split up the selection string.
    mol_from_token, res_from_token, spin_from_token = tokenise(res_from)
    mol_to_token, res_to_token, spin_to_token = tokenise(res_to)

    # Disallow spin selections.
    if spin_from_token != None or spin_to_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the residue token for renaming and renumbering.
    res_num_to, res_name_to = return_single_residue_info(res_to_token)

    # Test if the residue number already exists.
    res_to_cont = return_residue(res_to, pipe_to)
    if res_to_cont and not res_to_cont.is_empty():
        raise RelaxError, "The residue " + `res_to` + " already exists in the " + `pipe_to` + " data pipe."

    # Get the single residue data container.
    res_from_cont = return_residue(res_from, pipe_from)

    # No residue to copy data from.
    if res_from_cont == None:
        raise RelaxError, "The residue " + `res_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Get the single molecule data container to copy the residue to (default to the first molecule).
    mol_to_container = return_molecule(res_to, pipe_to)
    if mol_to_container == None:
        mol_to_container = pipe.mol[0]

    # Copy the data.
    if mol_to_container.res[0].num == None and mol_to_container.res[0].name == None and len(mol_to_container.res) == 1:
        mol_to_container.res[0] = res_from_cont.__clone__()
    else:
        mol_to_container.res.append(res_from_cont.__clone__())

    # Change the new residue number and name.
    if res_num_to != None:
        mol_to_container.res[-1].num = res_num_to
    if res_name_to != None:
        mol_to_container.res[-1].name = res_name_to


def copy_spin(pipe_from=None, spin_from=None, pipe_to=None, spin_to=None):
    """Copy the contents of the spin structure from one spin to a new spin.

    For copying to be successful, the spin_from identification string must match an existent spin.
    The new spin number must be unique.

    @param pipe_from:   The data pipe to copy the spin from.  This defaults to the current data
                        pipe.
    @type pipe_from:    str
    @param spin_from:   The spin identification string for the structure to copy the data from.
    @type spin_from:    str
    @param pipe_to:     The data pipe to copy the spin to.  This defaults to the current data
                        pipe.
    @type pipe_to:      str
    @param spin_to:     The spin identification string for the structure to copy the data to.
    @type spin_to:      str
    """

    # The current data pipe.
    if pipe_from == None:
        pipe_from = pipes.cdp_name()
    if pipe_to == None:
        pipe_to = pipes.cdp_name()

    # The second pipe does not exist.
    pipes.test(pipe_to)

    # Get the target pipe.
    pipe = pipes.get_pipe(pipe_to)

    # Split up the selection string.
    mol_to_token, res_to_token, spin_to_token = tokenise(spin_to)

    # Test if the spin number already exists.
    if spin_to_token:
        spin_to_cont = return_spin(spin_to, pipe_to)
        if spin_to_cont and not spin_to_cont.is_empty():
            raise RelaxError, "The spin " + `spin_to` + " already exists in the " + `pipe_from` + " data pipe."

    # No residue to copy data from.
    if not return_residue(spin_from, pipe_from):
        raise RelaxError, "The residue in " + `spin_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # No spin to copy data from.
    spin_from_cont = return_spin(spin_from, pipe_from)
    if spin_from_cont == None:
        raise RelaxError, "The spin " + `spin_from` + " does not exist in the " + `pipe_from` + " data pipe."

    # Get the single residue data container to copy the spin to (default to the first molecule, first residue).
    res_to_cont = return_residue(spin_to, pipe_to)
    if res_to_cont == None and spin_to:
        # No residue to copy data to.
        raise RelaxError, "The residue in " + `spin_to` + " does not exist in the " + `pipe_from` + " data pipe."
    if res_to_cont == None:
        res_to_cont = pipe.mol[0].res[0]

    # Copy the data.
    if res_to_cont.spin[0].num == None and res_to_cont.spin[0].name == None and len(res_to_cont.spin) == 1:
        res_to_cont.spin[0] = spin_from_cont.__clone__()
    else:
        res_to_cont.spin.append(spin_from_cont.__clone__())

    # Parse the spin token for renaming and renumbering.
    spin_num_to, spin_name_to = return_single_spin_info(spin_to_token)

    # Change the new spin number and name.
    if spin_num_to != None:
        res_to_cont.spin[-1].num = spin_num_to
    if spin_name_to != None:
        res_to_cont.spin[-1].name = spin_name_to


def count_molecules(selection=None):
    """Count the number of molecules for which there is data.

    @param selection:   The selection string.
    @type selection:    str
    @return:            The number of non-empty molecules.
    @rtype:             int
    """

    # No data, hence no molecules.
    if not exists_mol_res_spin_data():
        return 0

    # Init.
    mol_num = 0

    # Spin loop.
    for mol in molecule_loop(selection):
        mol_num = mol_num + 1

    # Return the number of molecules.
    return mol_num


def count_residues(selection=None):
    """Count the number of residues for which there is data.

    @param selection:   The selection string.
    @type selection:    str
    @return:            The number of non-empty residues.
    @rtype:             int
    """

    # No data, hence no residues.
    if not exists_mol_res_spin_data():
        return 0

    # Init.
    res_num = 0

    # Spin loop.
    for res in residue_loop(selection):
        res_num = res_num + 1

    # Return the number of residues.
    return res_num


def count_spins(selection=None, skip_desel=True):
    """Function for counting the number of spins for which there is data.

    @param selection:   The selection string.
    @type selection:    str
    @return:            The number of non-empty spins.
    @rtype:             int
    """

    # No data, hence no spins.
    if not exists_mol_res_spin_data():
        return 0

    # Init.
    spin_num = 0

    # Spin loop.
    for spin in spin_loop(selection):
        # Skip deselected spins.
        if skip_desel and not spin.select:
            continue

        spin_num = spin_num + 1

    # Return the number of spins.
    return spin_num


def create_molecule(mol_name=None):
    """Function for adding a molecule into the relax data store."""

    # Test if the current data pipe exists.
    pipes.test()

    # Alias the current data pipe.
    cdp = pipes.get_pipe()

    # Test if the molecule name already exists.
    for i in xrange(len(cdp.mol)):
        if cdp.mol[i].name == mol_name:
            raise RelaxError, "The molecule '" + `mol_name` + "' already exists in the relax data store."


    # Append the molecule.
    cdp.mol.add_item(mol_name=mol_name)


def create_residue(res_num=None, res_name=None, mol_id=None):
    """Function for adding a residue into the relax data store.

    @param res_num:     The identification number of the new residue.
    @type res_num:      int
    @param res_name:    The name of the new residue.
    @type res_name:     str
    @param mol_id:      The molecule identification string.
    @type mol_id:       str
    """

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(mol_id)

    # Disallowed selections.
    if res_token != None:
        raise RelaxResSelectDisallowError
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Test if the current data pipe exists.
    pipes.test()

    # Get the molecule container to add the residue to.
    if mol_id:
        mol_to_cont = return_molecule(mol_id)
        if mol_to_cont == None:
            raise RelaxError, "The molecule in " + `mol_id` + " does not exist in the current data pipe."
    else:
        mol_to_cont = cdp.mol[0]

    # Add the residue.
    mol_to_cont.res.add_item(res_num=res_num, res_name=res_name)


def create_pseudo_spin(spin_name=None, spin_num=None, res_id=None, members=None, averaging=None):
    """Add a pseudo-atom spin container into the relax data store.
    
    @param spin_name:   The name of the new pseudo-spin.
    @type spin_name:    str
    @param spin_num:    The identification number of the new spin.
    @type spin_num:     int
    @param res_id:      The molecule and residue identification string.
    @type res_id:       str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Get the residue container to add the spin to.
    if res_id:
        res_to_cont = return_residue(res_id)
        if res_to_cont == None:
            raise RelaxError, "The residue in " + `res_id` + " does not exist in the current data pipe."
    else:
        res_to_cont = cdp.mol[0].res[0]

    # Check the averaging technique.
    if averaging not in ['linear']:
        raise RelaxError, "The '%s' averaging technique is unknown." % averaging

    # Get the spin positions.
    positions = []
    for atom in members:
        # Get the spin container.
        spin = return_spin(atom)

        # Test that the spin exists.
        if spin == None:
            raise RelaxNoSpinError, atom

        # Test the position.
        if not hasattr(spin, 'pos') or not spin.pos:
            raise RelaxError, "Positional information is not available for the atom '%s'." % atom

        # Store the position.
        positions.append(spin.pos)

    # Add the spin.
    res_to_cont.spin.add_item(spin_num=spin_num, spin_name=spin_name)
    spin = res_to_cont.spin[-1]

    # Set the pseudo-atom spin container attributes.
    spin.averaging = averaging
    if averaging == 'linear':
        spin.pos = __linear_ave(positions)


def create_spin(spin_num=None, spin_name=None, res_id=None):
    """Function for adding a spin into the relax data store.
    
    @param spin_num:    The identification number of the new spin.
    @type spin_num:     int
    @param spin_name:   The name of the new spin.
    @type spin_name:    str
    @param res_id:      The molecule and residue identification string.
    @type res_id:       str
    """

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Test if the current data pipe exists.
    pipes.test()

    # Get the residue container to add the spin to.
    if res_id:
        res_to_cont = return_residue(res_id)
        if res_to_cont == None:
            raise RelaxError, "The residue in " + `res_id` + " does not exist in the current data pipe."
    else:
        res_to_cont = cdp.mol[0].res[0]

    # Add the spin.
    res_to_cont.spin.add_item(spin_num=spin_num, spin_name=spin_name)


def convert_from_global_index(global_index=None, pipe=None):
    """Convert the global index into the molecule, residue, and spin indices.

    @param global_index:        The global spin index, spanning the molecule and residue containers.
    @type global_index:         int
    @param pipe:                The data pipe containing the spin.  Defaults to the current data
                                pipe.
    @type pipe:                 str
    @return:                    The corresponding molecule, residue, and spin indices.
    @rtype:                     tuple of int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Loop over the spins.
    spin_num = 0
    for mol_index, res_index, spin_index in spin_index_loop(pipe=pipe):
        # Match to the global index.
        if spin_num == global_index:
            return mol_index, res_index, spin_index

        # Increment the spin number.
        spin_num = spin_num + 1


def delete_molecule(mol_id=None):
    """Function for deleting molecules from the current data pipe.

    @param mol_id:  The molecule identifier string.
    @type mol_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(mol_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Disallow residue selections.
    if res_token != None:
        raise RelaxResSelectDisallowError

    # Parse the token.
    molecules = parse_token(mol_token)

    # Alias the current data pipe.
    cdp = pipes.get_pipe()

    # List of indices to delete.
    indices = []

    # Loop over the molecules.
    for i in xrange(len(cdp.mol)):
        # Remove the residue is there is a match.
        if cdp.mol[i].name in molecules:
            indices.append(i)

    # Reverse the indices.
    indices.reverse()

    # Delete the molecules.
    for index in indices:
        cdp.mol.pop(index)

    # Create an empty residue container if no residues remain.
    if len(cdp.mol) == 0:
        cdp.mol.add_item()


def delete_residue(res_id=None):
    """Function for deleting residues from the current data pipe.

    @param res_id:  The molecule and residue identifier string.
    @type res_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Parse the tokens.
    residues = parse_token(res_token)

    # Molecule loop.
    for mol in molecule_loop(mol_token):
        # List of indices to delete.
        indices = []

        # Loop over the residues of the molecule.
        for i in xrange(len(mol.res)):
            # Remove the residue is there is a match.
            if mol.res[i].num in residues or mol.res[i].name in residues:
                indices.append(i)

        # Reverse the indices.
        indices.reverse()

        # Delete the residues.
        for index in indices:
            mol.res.pop(index)

        # Create an empty residue container if no residues remain.
        if len(mol.res) == 0:
            mol.res.add_item()


def delete_spin(spin_id=None):
    """Function for deleting spins from the current data pipe.

    @param spin_id: The molecule, residue, and spin identifier string.
    @type spin_id:  str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(spin_id)

    # Parse the tokens.
    spins = parse_token(spin_token)

    # Residue loop.
    for res in residue_loop(spin_id):
        # List of indices to delete.
        indices = []

        # Loop over the spins of the residue.
        for i in xrange(len(res.spin)):
            # Store the spin indices for deletion.
            if res.spin[i].num in spins or res.spin[i].name in spins:
                indices.append(i)

        # Reverse the indices.
        indices.reverse()

        # Delete the spins.
        for index in indices:
            res.spin.pop(index)

        # Create an empty spin container if no spins remain.
        if len(res.spin) == 0:
            res.spin.add_item()


def display_molecule(mol_id=None):
    """Function for displaying the information associated with the molecule.

    @param mol_id:  The molecule identifier string.
    @type mol_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(mol_id)

    # Disallowed selections.
    if res_token != None:
        raise RelaxResSelectDisallowError
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # The molecule selection string.
    if mol_token:
        mol_sel = '#' + mol_token
    else:
        mol_sel = None

    # Print a header.
    print "\n\n%-15s %-15s" % ("Molecule", "Number of residues")

    # Molecule loop.
    for mol in molecule_loop(mol_sel):
        # Print the molecule data.
        print "%-15s %-15s" % (mol.name, `len(mol.res)`)


def display_residue(res_id=None):
    """Function for displaying the information associated with the residue.

    @param res_id:  The molecule and residue identifier string.
    @type res_id:   str
    """

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(res_id)

    # Disallow spin selections.
    if spin_token != None:
        raise RelaxSpinSelectDisallowError

    # Print a header.
    print "\n\n%-15s %-15s %-15s %-15s" % ("Molecule", "Res number", "Res name", "Number of spins")

    # Residue loop.
    for res, mol_name in residue_loop(res_id, full_info=True):
        print "%-15s %-15s %-15s %-15s" % (mol_name, `res.num`, res.name, `len(res.spin)`)


def display_spin(spin_id=None):
    """Function for displaying the information associated with the spin.

    @param spin_id: The molecule and residue identifier string.
    @type spin_id:  str
    """

    # Print a header.
    print "\n\n%-15s %-15s %-15s %-15s %-15s" % ("Molecule", "Res number", "Res name", "Spin number", "Spin name")

    # Spin loop.
    for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
        # Print the residue data.
        print "%-15s %-15s %-15s %-15s %-15s" % (mol_name, `res_num`, res_name, `spin.num`, spin.name)


def exists_mol_res_spin_data(pipe=None):
    """Function for determining if any molecule-residue-spin data exists.

    @keyword pipe:      The data pipe in which the molecule-residue-spin data will be checked for.
    @type pipe:         str
    @return:            The answer to the question about the existence of data.
    @rtype:             bool
    """

    # The current data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # The molecule, residue, spin object stack is empty.
    if dp.mol.is_empty():
        return False

    # Otherwise.
    return True


def find_index(selection=None, pipe=None, global_index=True):
    """Find and return the spin index or indices for the selection string.

    @keyword selection:     The spin selection identifier.
    @type selection:        str
    @keyword pipe:          The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:             str
    @keyword global_index:  A flag which if True will cause the global index to be returned.  If
                            False, then the molecule, residue, and spin indices will be returned.
    @type global_index:     bool
    @return:                The global spin index or the molecule, residue, and spin indices.
    @rtype:                 int or tuple of 3 int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Init the mol and global index.
    global_i = -1
    mol_index = -1

    # Loop over the molecules.
    for mol in dp.mol:
        # Increment the molecule index.
        mol_index = mol_index + 1

        # Init the residue index.
        res_index = -1

        # Loop over the residues.
        for res in mol.res:
            # Increment the residue index.
            res_index = res_index + 1

            # Init the residue index.
            spin_index = -1

            # Loop over the spins.
            for spin in res.spin:
                # Increment the spin and global index.
                spin_index = spin_index + 1
                global_i = global_i + 1

                # Stop if the spin matches the selection.
                if (mol, res, spin) in select_obj:
                    # Return the indices.
                    if global_index:
                        return global_i
                    else:
                        return mol_index, res_index, spin_index


def first_residue_num(selection=None):
    """Determine the first residue number.

    @return:    The number of the first residue.
    @rtype:     int
    """

    # Get the molecule.
    mol = return_molecule(selection)

    # The first residue number.
    return mol.res[0].num


def generate_spin_id(mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
    """Generate the spin selection string.

    @param mol_name:    The molecule name.
    @type mol_name:     str or None
    @param res_num:     The residue number.
    @type res_num:      int or None
    @param res_name:    The residue name.
    @type res_name:     str or None
    @param spin_num:    The spin number.
    @type spin_num:     int or None
    @param spin_name:   The spin name.
    @type spin_name:    str or None
    @return:            The spin identification string.
    @rtype:             str
    """

    # Init.
    id = ""

    # Molecule name.
    if mol_name != None:
        id = id + "#" + mol_name

    # Residue data.
    if res_num != None:
        id = id + ":" + str(res_num)
    if res_num != None and res_name != None:
        id = id + "&:" + res_name
    elif res_name != None:
        id = id + ":" + res_name

    # Spin data.
    if spin_num != None:
        id = id + "@" + str(spin_num)
    if spin_num != None and spin_name != None:
        id = id + "&@" + spin_name
    elif spin_name != None:
        id = id + "@" + spin_name

    # Return the spin id string.
    return id


def generate_spin_id_data_array(data=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None):
    """Generate the spin selection string from the given data array.

    @param data:            An array containing the molecule, residue, and/or spin data.
    @type data:             list of str
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    @return:                The spin identification string.
    @rtype:                 str
    """

    # Init.
    id = ""

    # Molecule data.
    if mol_name_col != None and data[mol_name_col]:
        id = id + "#" + data[mol_name_col]

    # Residue data.
    if res_num_col != None and data[res_num_col] != None:
        id = id + ":" + str(data[res_num_col])
    if (res_num_col != None and data[res_num_col] != None) and (res_name_col != None and data[res_name_col]):
        id = id + "&:" + data[res_name_col]
    elif res_name_col != None and data[res_name_col]:
        id = id + ":" + data[res_name_col]

    # Spin data.
    if spin_num_col != None and data[spin_num_col] != None:
        id = id + "@" + str(data[spin_num_col])
    if (spin_num_col != None and data[spin_num_col] != None) and (spin_name_col != None and data[spin_name_col]):
        id = id + "&@" + data[spin_name_col]
    elif spin_name_col != None and data[spin_name_col]:
        id = id + "@" + data[spin_name_col]

    # Return the spin id string.
    return id


def last_residue_num(selection=None):
    """Determine the last residue number.

    @return:    The number of the last residue.
    @rtype:     int
    """

    # Get the molecule.
    mol = return_molecule(selection)

    # The last residue number.
    return mol.res[-1].num


def molecule_loop(selection=None, pipe=None):
    """Generator function for looping over all the molecules of the given selection.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the molecule.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The molecule specific data container.
    @rtype:             instance of the MoleculeContainer class.
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data():
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Disallowed selections.
    if select_obj.residues:
        raise RelaxResSelectDisallowError
    if select_obj.spins:
        raise RelaxSpinSelectDisallowError

    # Loop over the molecules.
    for mol in dp.mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
            continue

        # Yield the molecule data container.
        yield mol


def name_molecule(mol_id, name=None):
    """Name the molecules.

    @param mol_id:      The molecule identification string.
    @type mol_id:       str
    @param name:        The new molecule name.
    @type name:         str
    """

    # Get the single molecule data container.
    mol = return_molecule(mol_id)

    # Disallow residue and spin selections.
    select_obj = Selection(mol_id)
    if select_obj.has_residues():
        raise RelaxResSelectDisallowError
    if select_obj.has_spins():
        raise RelaxSpinSelectDisallowError

    # Name the molecule is there is a single match.
    if mol:
        mol.name = name
        

def name_residue(res_id, name=None):
    """Name the residues.

    @param res_id:      The residue identification string.
    @type res_id:       str
    @param name:        The new residue name.
    @type name:         str
    """

    # Disallow spin selections.
    select_obj = Selection(res_id)
    if select_obj.has_spins():
        raise RelaxSpinSelectDisallowError

    # Rename the matching residues.
    for res in residue_loop(res_id):
        res.name = name


def name_spin(spin_id=None, name=None):
    """Name the spins.

    @param spin_id:     The spin identification string.
    @type spin_id:      str
    @param name:        The new spin name.
    @type name:         str
    """

    # Rename the matching spins.
    for spin in spin_loop(spin_id):
        spin.name = name


def number_residue(res_id, number=None):
    """Number the residues.

    @param res_id:      The residue identification string.
    @type res_id:       str
    @param number:      The new residue number.
    @type number:       int
    """

    # Catch multiple numberings!
    i = 0
    for res in residue_loop(res_id):
        i = i + 1

    # Fail if multiple residues are numbered.
    if i > 1:
        raise RelaxError, "The numbering of multiple residues is disallowed, each residue requires a unique number."

    # Disallow spin selections.
    select_obj = Selection(res_id)
    if select_obj.has_spins():
        raise RelaxSpinSelectDisallowError

    # Rename the residue.
    for res in residue_loop(res_id):
        res.num = number


def number_spin(spin_id=None, number=None):
    """Number the spins.

    @param spin_id:     The spin identification string.
    @type spin_id:      str
    @param number:      The new spin number.
    @type number:       int
    """

    # Catch multiple renumberings!
    i = 0
    for spin in spin_loop(spin_id):
        i = i + 1

    # Fail if multiple spins are numbered.
    if number != None and i > 1:
        raise RelaxError, "The numbering of multiple spins is disallowed, as each spin requires a unique number."

    # Rename the spin.
    for spin in spin_loop(spin_id):
        spin.num = number


def parse_token(token, verbosity=False):
    """Parse the token string and return a list of identifying numbers and names.

    Firstly the token is split by the ',' character into its individual elements and all whitespace
    stripped from the elements.  Numbers are converted to integers, names are left as strings, and
    ranges are converted into the full list of integers.

    @param token:       The identification string, the elements of which are separated by commas.
                        Each element can be either a single number, a range of numbers (two numbers
                        separated by '-'), or a name.
    @type token:        str
    @keyword verbosity: A flag which if True will cause a number of print outs to be activated.
    @type verbosity:    bool
    @return:            A list of identifying numbers and names.
    @rtype:             list of int and str
    """

    # No token.
    if token == None:
        return []

    # Split by the ',' character.
    elements = split(',', token)

    # Loop over the elements.
    list = []
    for element in elements:
        # Strip all leading and trailing whitespace.
        element = strip(element)

        # Find all '-' characters (ignoring the first character, i.e. a negative number).
        indices= []
        for i in xrange(1,len(element)):
            if element[i] == '-':
                indices.append(i)

        # Range.
        valid_range = True
        if indices:
            # Invalid range element, only one range char '-' and one negative sign is allowed.
            if len(indices) > 2:
                if verbosity:
                    print "The range element " + `element` + " is invalid.  Assuming the '-' character does not specify a range."
                valid_range = False

            # Convert the two numbers to integers.
            try:
                start = int(element[:indices[0]])
                end = int(element[indices[0]+1:])
            except ValueError:
                if verbosity:
                    print "The range element " + `element` + " is invalid as either the start or end of the range are not integers.  Assuming the '-' character does not specify a range."
                valid_range = False

            # Test that the starting number is less than the end.
            if valid_range and start >= end:
                if verbosity:
                    print "The starting number of the range element " + `element` + " needs to be less than the end number.  Assuming the '-' character does not specify a range."
                valid_range = False

            # Create the range and append it to the list.
            if valid_range:
                for i in range(start, end+1):
                    list.append(i)

            # Just append the string (even though it might be junk).
            else:
                list.append(element)

        # Number or name.
        else:
            # Try converting the element into an integer.
            try:
                element = int(element)
            except ValueError:
                pass

            # Append the element.
            list.append(element)

    # Sort the list.
    list.sort()

    # Return the identifying list.
    return list


def residue_loop(selection=None, pipe=None, full_info=False):
    """Generator function for looping over all the residues of the given selection.

    @param selection:   The residue selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the residue.  Defaults to the current data pipe.
    @type pipe:         str
    @param full_info:   A flag specifying if the amount of information to be returned.  If false,
                        only the data container is returned.  If true, the molecule name, residue
                        number, and residue name is additionally returned.
    @type full_info:    boolean
    @return:            The residue specific data container and, if full_info=True, the molecule
                        name.
    @rtype:             instance of the ResidueContainer class.  If full_info=True, the type is the
                        tuple (ResidueContainer, str).
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data():
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol in dp.mol:
        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if (mol, res) not in select_obj:
                continue

            # Yield the residue data container.
            if full_info:
                yield res, mol.name
            else:
                yield res


def return_molecule(selection=None, pipe=None):
    """Function for returning the molecule data container of the given selection.

    @param selection:   The molecule selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the molecule.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The molecule specific data container.
    @rtype:             instance of the MoleculeContainer class.
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    mol_num = 0
    mol_container = None
    for mol in dp.mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
            continue

        # Skip named molecules if the selection is None.
        if selection == None and mol.name != None:
            continue

        # Store the molecule container.
        mol_container = mol

        # Increment the molecule number counter.
        mol_num = mol_num + 1

    # No unique identifier.
    if mol_num > 1:
        raise RelaxError, "The identifier " + `selection` + " corresponds to more than a single molecule in the " + `pipe` + " data pipe."

    # Return the molecule container.
    return mol_container


def return_residue(selection=None, pipe=None):
    """Function for returning the residue data container of the given selection.

    @param selection:   The residue selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the residue.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The residue specific data container.
    @rtype:             instance of the ResidueContainer class.
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    res = None
    res_num = 0
    res_container = None
    for mol in dp.mol:
        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if (mol, res) not in select_obj:
                continue

            # Store the residue container.
            res_container = res

            # Increment the residue number counter.
            res_num = res_num + 1

    # No unique identifier.
    if res_num > 1:
        raise RelaxError, "The identifier " + `selection` + " corresponds to more than a single residue in the " + `pipe` + " data pipe."

    # Return the residue container.
    return res_container


def return_spin(selection=None, pipe=None, full_info=False):
    """Function for returning the spin data container of the given selection.

    @param selection:   The spin selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @param full_info:   A flag specifying if the amount of information to be returned.  If false,
                        only the data container is returned.  If true, the molecule name, residue
                        number, and residue name is additionally returned.
    @type full_info:    boolean
    @return:            The spin system specific data container and, if full_info=True, the molecule
                        name, residue number, and residue name.
    @rtype:             instance of the SpinContainer class.  If full_info=True, the type is the
                        tuple (SpinContainer, str, int, str).
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    spin = None
    spin_num = 0
    spin_container = None
    for mol in dp.mol:
        # Loop over the residues.
        for res in mol.res:
            # Loop over the spins.
            for spin in res.spin:
                # Skip the spin if there is no match to the selection.
                if (mol, res, spin) not in select_obj:
                    continue

                # Store all containers.
                mol_container = mol
                res_container = res
                spin_container = spin

                # Increment the spin number counter.
                spin_num = spin_num + 1

    # No unique identifier.
    if spin_num > 1:
        raise RelaxError, "The identifier " + `selection` + " corresponds to more than a single spin in the " + `pipe` + " data pipe."

    # Return the spin container.
    if full_info:
        return mol_container.name, res_container.num, res_container.name, spin_container
    else:
        return spin_container


def return_spin_from_index(global_index=None, pipe=None, return_spin_id=False):
    """Function for returning the spin data container corresponding to the global index.

    @param global_index:        The global spin index, spanning the molecule and residue containers.
    @type global_index:         int
    @param pipe:                The data pipe containing the spin.  Defaults to the current data
                                pipe.
    @type pipe:                 str
    @keyword return_spin_id:    A flag which if True will cause both the spin container and spin
                                identification string to be returned.
    @type return_spin_id:       bool
    @return:                    The spin specific data container (additionally the spin
                                identification string if return_spin_id is set).
    @rtype:                     instance of the SpinContainer class (or tuple of SpinContainer and
                                str)
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Loop over the spins.
    spin_num = 0
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Match to the global index.
        if spin_num == global_index:
            # Return the spin and the spin_id string.
            if return_spin_id:
                # The spin identification string.
                spin_id = generate_spin_id(mol_name, res_num, res_name, spin.num, spin.name)

                # Return both objects.
                return spin, spin_id

            # Return the spin by itself.
            else:
                return spin

        # Increment the spin number.
        spin_num = spin_num + 1


def return_single_molecule_info(molecule_token):
    """Return the single molecule name corresponding to the molecule token.

    @param molecule_token:  The molecule identification string.
    @type molecule_token:   str
    @return:                The molecule name.
    @rtype:                 str
    """

    # Parse the molecule token for renaming and renumbering.
    molecule_info = parse_token(molecule_token)

    # Determine the molecule name.
    mol_name = None
    for info in molecule_info:
        # A molecule name identifier.
        if mol_name == None:
            mol_name = info
        else:
            raise RelaxError, "The molecule identifier " + `molecule_token` + " does not correspond to a single molecule."

    # Return the molecule name.
    return mol_name


def return_single_residue_info(residue_token):
    """Return the single residue number and name corresponding to the residue token.

    @param residue_token:   The residue identification string.
    @type residue_token:    str
    @return:                A tuple containing the residue number and the residue name.
    @rtype:                 (int, str)
    """

    # Parse the residue token for renaming and renumbering.
    residue_info = parse_token(residue_token)

    # Determine the residue number and name.
    res_num = None
    res_name = None
    for info in residue_info:
        # A residue name identifier.
        if type(info) == str:
            if res_name == None:
                res_name = info
            else:
                raise RelaxError, "The residue identifier " + `residue_token` + " does not correspond to a single residue."

        # A residue number identifier.
        if type(info) == int:
            if res_num == None:
                res_num = info
            else:
                raise RelaxError, "The residue identifier " + `residue_token` + " does not correspond to a single residue."

    # Return the residue number and name.
    return res_num, res_name


def return_single_spin_info(spin_token):
    """Return the single spin number and name corresponding to the spin token.

    @param spin_token:  The spin identification string.
    @type spin_token:   str
    @return:            A tuple containing the spin number and the spin name.
    @rtype:             (int, str)
    """

    # Parse the spin token for renaming and renumbering.
    spin_info = parse_token(spin_token)

    # Determine the spin number and name.
    spin_num = None
    spin_name = None
    for info in spin_info:
        # A spin name identifier.
        if type(info) == str:
            if spin_name == None:
                spin_name = info
            else:
                raise RelaxError, "The spin identifier " + `spin_token` + " does not correspond to a single spin."

        # A spin number identifier.
        if type(info) == int:
            if spin_num == None:
                spin_num = info
            else:
                raise RelaxError, "The spin identifier " + `spin_token` + " does not correspond to a single spin."

    # Return the spin number and name.
    return spin_num, spin_name


def same_sequence(pipe1, pipe2):
    """Test if the sequence data in both pipes are the same.

    @param pipe1:       The first data pipe.
    @type pipe1:        str
    @param pipe2:       The second data pipe.
    @type pipe2:        str
    @return:            True if the sequence data matches, False otherwise.
    @rtype:             bool
    """

    # Test the data pipes.
    pipes.test(pipe1)
    pipes.test(pipe2)

    # Get the data pipes.
    pipe1 = pipes.get_pipe(pipe1)
    pipe2 = pipes.get_pipe(pipe2)

    # Different number of molecules.
    if len(pipe1.mol) != len(pipe2.mol):
        return False

    # Loop over the molecules.
    for i in xrange(len(pipe1.mol)):
        # Different number of residues.
        if len(pipe1.mol[i].res) != len(pipe2.mol[i].res):
            return False

        # Loop over the residues.
        for j in xrange(len(pipe1.mol[i].res)):
            # Different number of spins.
            if len(pipe1.mol[i].res[j].spin) != len(pipe2.mol[i].res[j].spin):
                return False

            # Loop over the spins.
            for k in xrange(len(pipe1.mol[i].res[j].spin)):
                # Different spin numbers.
                if pipe1.mol[i].res[j].spin[k].num != pipe2.mol[i].res[j].spin[k].num:
                    return False

                # Different spin names.
                if pipe1.mol[i].res[j].spin[k].name != pipe2.mol[i].res[j].spin[k].name:
                    return False

    # The sequence is the same.
    return True


def spin_in_list(spin_list, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
    """Function for determining if the spin is located within the list of spins.

    @param spin_list:       The list of spins.  The first dimension corresponds to different spins,
                            the second corresponds to the spin information columns.
    @type spin_list:        list of lists of str
    @keyword mol_name_col:  The column containing the molecule name information.
    @type mol_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.
    @type res_num_col:      int or None
    @keyword res_name_col:  The column containing the residue name information.
    @type res_name_col:     int or None
    @keyword spin_num_col:  The column containing the spin number information.
    @type spin_num_col:     int or None
    @keyword spin_name_col: The column containing the spin name information.
    @type spin_name_col:    int or None
    @keyword mol_name:      The molecule name.
    @type mol_name:         str or None
    @keyword res_num:       The residue number.
    @type res_num:          int or None
    @keyword res_name:      The residue name.
    @type res_name:         str or None
    @keyword spin_num:      The spin number.
    @type spin_num:         int or None
    @keyword spin_name:     The spin name.
    @type spin_name:        str or None
    @return:                The answer of whether the spin is within the list.
    @rtype:                 bool
    """

    # Create a selection object based on the spin.
    select_obj = Selection(generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name))

    # Loop over the spins.
    for spin in spin_list:
        # Generate the spin identification string.
        spin_id = generate_spin_id_data_array(data=file_data[i], mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

        # There is a hit.
        if spin_id in select_obj:
            return True

    # Not in the list.
    return False


def spin_index_loop(selection=None, pipe=None):
    """Generator function for looping over all selected spins, returning the mol-res-spin indices.

    @param selection:   The spin system selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The molecule, residue, and spin index.
    @rtype:             tuple of 3 int
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data():
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol_index in xrange(len(dp.mol)):
        # Alias the molecule container.
        mol = dp.mol[mol_index]

        # Loop over the residues.
        for res_index in xrange(len(dp.mol[mol_index].res)):
            # Alias the residue container.
            res = dp.mol[mol_index].res[res_index]

            # Loop over the spins.
            for spin_index in xrange(len(dp.mol[mol_index].res[res_index].spin)):
                # Alias the spin container.
                spin = dp.mol[mol_index].res[res_index].spin[spin_index]

                # Skip the spin if there is no match to the selection.
                if (mol, res, spin) not in select_obj:
                    continue

                # Yield the spin system specific indices.
                yield mol_index, res_index, spin_index


def spin_loop(selection=None, pipe=None, full_info=False, return_id=False):
    """Generator function for looping over all the spin systems of the given selection.

    @keyword selection: The spin system selection identifier.
    @type selection:    str
    @keyword pipe:      The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @keyword full_info: A flag which if True will cause the the molecule name, residue number, and
                        residue name to be returned in addition to the spin container.
    @type full_info:    bool
    @keyword return_id: A flag which if True will cause the spin identification string of the
                        current spin to be returned in addition to the spin container.
    @type return_id:    bool
    @return:            The spin system specific data container.  If full_info is True, a tuple of
                        the spin container, the molecule name, residue number, and residue name.  If
                        return_id is True, a tuple of the spin container and spin id.  If both flags
                        are True, then a tuple of the spin container, the molecule name, residue
                        number, residue name, and spin id.
    @rtype:             If full_info and return_id are False, SpinContainer instance.  If full_info
                        is True and return_id is false, a tuple of (SpinContainer instance, str,
                        int, str).  If full_info is False and return_id is True, a tuple of
                        (SpinContainer instance, str).  If full_info and return_id are False, a
                        tuple of (SpinContainer instance, str, int, str, str)
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data(pipe):
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol in dp.mol:
        # Loop over the residues.
        for res in mol.res:
            # Loop over the spins.
            for spin in res.spin:
                # Skip the spin if there is no match to the selection.
                if (mol, res, spin) not in select_obj:
                    continue

                # Generate the spin id.
                if return_id:
                    spin_id = generate_spin_id(mol.name, res.num, res.name, spin.num, spin.name)

                # Yield the data.
                if full_info and return_id:
                    yield spin, mol.name, res.num, res.name, spin_id
                elif full_info:
                    yield spin, mol.name, res.num, res.name
                elif return_id:
                    yield spin, spin_id
                else:
                    yield spin


def tokenise(selection):
    """Split the input selection string returning the mol_token, res_token, and spin_token strings.

    The mol_token is identified as the text from the '#' to either the ':' or '@' characters or the
    end of the string.

    The res_token is identified as the text from the ':' to either the '@' character or the end of
    the string.

    The spin_token is identified as the text from the '@' to the end of the string.

    @param selection:   The selection identifier.
    @type selection:    str
    @return:            The mol_token, res_token, and spin_token.
    @rtype:             3-tuple of str or None
    """

    # No selection.
    if selection == None:
        return None, None, None


    # Atoms.
    ########

    # Split by '@'.
    atom_split = split('@', selection)

    # Test that only one '@' character was supplied.
    if len(atom_split) > 2:
        raise RelaxError, "Only one '@' character is allowed within the selection identifier string."

    # No atom identifier.
    if len(atom_split) == 1:
        spin_token = None
    else:
        # Test for out of order identifiers.
        if ':' in atom_split[1]:
            raise RelaxError, "The atom identifier '@' must come after the residue identifier ':'."
        elif '#' in atom_split[1]:
            raise RelaxError, "The atom identifier '@' must come after the molecule identifier '#'."

        # The token.
        spin_token = atom_split[1]


    # Residues.
    ###########

    # Split by ':'.
    res_split = split(':', atom_split[0])

    # Test that only one ':' character was supplied.
    if len(res_split) > 2:
        raise RelaxError, "Only one ':' character is allowed within the selection identifier string."

    # No residue identifier.
    if len(res_split) == 1:
        res_token = None
    else:
        # Test for out of order identifiers.
        if '#' in res_split[1]:
            raise RelaxError, "The residue identifier ':' must come after the molecule identifier '#'."

        # The token.
        res_token = res_split[1]



    # Molecules.
    ############

    # Split by '#'.
    mol_split = split('#', res_split[0])

    # Test that only one '#' character was supplied.
    if len(mol_split) > 2:
        raise RelaxError, "Only one '#' character is allowed within the selection identifier string."

    # No molecule identifier.
    if len(mol_split) == 1:
        mol_token = None
    else:
        mol_token = mol_split[1]


    # Improper selection string.
    if mol_token == None and res_token == None and spin_token == None:
        raise RelaxError, "The selection string " + `selection` + " is invalid."

    # Return the three tokens.
    return mol_token, res_token, spin_token
