###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2007 Edward d'Auvergne                        #
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
from re import compile, match, search, split
from string import strip
from textwrap import fill

# relax module imports.
from data import Data as relax_data_store
from data.mol_res_spin import MoleculeContainer, ResidueContainer, SpinContainer
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoSequenceError, RelaxRegExpError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError
from generic_fns import pipes


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
"""

# Wrap the id string doc.
string = ''
for line in split('\n', id_string_doc):
    string = string + fill(line, width=100, initial_indent=8*' ', subsequent_indent=8*' ') + '\n'
id_string_doc = string



class Selection(object):
    """An object containing mol-res-spin selections.

    A Selection object represents either a set of selected
    molecules, residues and spins, or the union or intersection
    of two other Selection objects."""

    def __init__(self, select_string):
        """Initialise a Selection object.

        @type select_string: string
        @param select_string: a mol-res-spin selection string"""

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

        @param obj:     The data object.
        @type obj:      MoleculeContainer, ResidueContainer, or SpinContainer object.
        @return:        The answer of whether the object matches the selection.
        @rtype:         Boolean
        """

        # The selection object is a union.
        if self._union:
            return (obj in self._union[0]) or (obj in self._union[1])

        # The selection object is an intersection.
        elif self._intersect:
            return (obj in self._intersect[0]) and (obj in self._intersect[1])

        # The object is a molecule.
        elif isinstance(obj, MoleculeContainer):
            if not self.molecules:
                return True
            elif obj.name in self.molecules:
                return True

        # The object is a residue.
        elif isinstance(obj, ResidueContainer):
            if not self.residues:
                return True
            elif obj.name in self.residues or obj.num in self.residues:
                return True

        # The object is a spin.
        elif isinstance(obj, SpinContainer):
            if not self.spins:
                return True
            elif obj.name in self.spins or obj.num in self.spins:
                return True

        # No match.
        return False


    def intersection(self, select_obj0, select_obj1):
        """Make a Selection object the intersection of two Selection objects

        @type select_obj0: Instance of class Selection
        @param select_obj0: First Selection object in intersection
        @type select_obj1: Instance of class Selection
        @param select_obj1: First Selection object in intersection"""

        if self._union or self._intersect or self.molecules or self.residues or self.spins:
            raise RelaxError, "Cannot define multiple Boolean relationships between Selection objects"
        self._intersect = (select_obj0, select_obj1)


    def union(self, select_obj0, select_obj1):
        """Make a Selection object the union of two Selection objects

        @type select_obj0: Instance of class Selection
        @param select_obj0: First Selection object in union
        @type select_obj1: Instance of class Selection
        @param select_obj1: First Selection object in union"""

        if self._union or self._intersect or self.molecules or self.residues or self.spins:
            raise RelaxError, "Cannot define multiple Boolean relationships between Selection objects"
        self._union = (select_obj0, select_obj1)


def count_spins(selection=None):
    """Function for counting the number of spins for which there is data.

    @param selection:   The selection string.
    @type selection:    str
    @return:            The number of non-empty spins.
    @return type:       int
    """

    # No data, hence no spins.
    if not exists_mol_res_spin_data():
        return 0

    # Init.
    spin_num = 0

    # Spin loop.
    for spin in spin_loop(selection):
        spin_num = spin_num + 1

    # Return the number of spins.
    return spin_num


def desel_all(self, run=None):
    """Function for deselecting all residues."""

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence and set the selection flag to 0.
        for i in xrange(len(relax_data_store.res[self.run])):
            relax_data_store.res[self.run][i].select = 0


def desel_read(self, run=None, file=None, dir=None, change_all=None, column=None):
    """Function for deselecting the residues contained in a file."""

    # Extract the data from the file.
    file_data = self.relax.IO.extract_data(file, dir)

    # Count the number of header lines.
    header_lines = 0
    for i in xrange(len(file_data)):
        try:
            int(file_data[i][column])
        except:
            header_lines = header_lines + 1
        else:
            break

    # Remove the header.
    file_data = file_data[header_lines:]

    # Strip the data.
    file_data = self.relax.IO.strip(file_data)

    # Create the list of residues to deselect.
    deselect = []
    for i in xrange(len(file_data)):
        try:
            deselect.append(int(file_data[i][column]))
        except:
            raise RelaxError, "Improperly formatted file."

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    no_match = 1
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Select all residues.
            if change_all:
                data.select = 1

            # Unselect the residue if it is in the list deselect.
            if data.num in deselect:
                data.select = 0

            # Match flag.
            no_match = 0

    # No residue matched.
    if no_match:
        print "No residues match."


def desel_res(self, run=None, num=None, name=None, change_all=None):
    """Function for deselecting specific residues."""

    # Test if the residue number is a valid regular expression.
    if type(num) == str:
        try:
            compile(num)
        except:
            raise RelaxRegExpError, ('residue number', num)

    # Test if the residue name is a valid regular expression.
    if name:
        try:
            compile(name)
        except:
            raise RelaxRegExpError, ('residue name', name)

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    no_match = 1
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Select all residues.
            if change_all:
                data.select = 1

            # Skip the residue if there is no match to 'num'.
            if type(num) == int:
                if not data.num == num:
                    continue
            if type(num) == str:
                if not match(num, `data.num`):
                    continue

            # Skip the residue if there is no match to 'name'.
            if name != None:
                if not match(name, data.name):
                    continue

            # Unselect the residue.
            data.select = 0

            # Match flag.
            no_match = 0

    # No residue matched.
    if no_match:
        print "No residues match."


def exists_mol_res_spin_data():
    """Function for determining if any molecule-residue-spin data exists.

    @return:            The answer to the question about the existence of data.
    @rtype:             bool
    """

    # Test the data pipe.
    pipes.test(relax_data_store.current_pipe)

    # Alias the data pipe container.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # More than 1 molecule (hence data exists).
    if len(cdp.mol) > 1:
        return True

    # The single molecule has been named.
    if cdp.mol[0].name != None:
        return True

    # More than 1 residue (hence data exists).
    if len(cdp.mol[0].res) > 1:
        return True

    # The single residue has been named or numbered.
    if cdp.mol[0].res[0].name != None or cdp.mol[0].res[0].num != None:
        return True

    # More than 1 spin (hence data exists).
    if len(cdp.mol[0].res[0].spin) > 1:
        return True

    # The single spin has been named or numbered.
    if cdp.mol[0].res[0].spin[0].name != None or cdp.mol[0].res[0].spin[0].num != None:
        return True

    # The object names in an empty spin container.
    white_list = ['name', 'num', 'select'] 

    # Loop over the objects in the spin container.
    for name in dir(cdp.mol[0].res[0].spin[0]):
        # Skip white listed objects.
        if name in white_list:
            continue

        # Skip objects beginning with '__'.
        if search('^__', name):
            continue

        # Found an object not in the white list (hence the spin container has been modified).
        return True

    # No data!
    return False


def generate_spin_id(data=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None):
    """Function for generating the spin selection string from the given data.

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
    @type return:           str
    """

    # Init.
    id = ""

    # Molecule data.
    if mol_name_col != None:
        id = id + "#" + data[mol_name_col]

    # Residue data.
    if res_num_col != None:
        id = id + ":" + data[res_num_col]
    if  res_num_col != None and res_name_col != None:
        id = id + "&" + data[res_name_col]
    elif res_name_col != None:
        id = id + ":" + data[res_name_col]

    # Spin data.
    if spin_num_col != None:
        id = id + "@" + data[spin_num_col]
    if  spin_num_col != None and spin_name_col != None:
        id = id + "&" + data[spin_name_col]
    elif spin_name_col != None:
        id = id + "@" + data[spin_name_col]

    # Return the spin id string.
    return id


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
        pipe = relax_data_store.current_pipe

    # Test the data pipe.
    pipes.test(pipe)

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
    for mol in relax_data_store[pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
            continue

        # Yield the molecule data container.
        yield mol


def parse_token(token):
    """Parse the token string and return a list of identifying numbers and names.

    Firstly the token is split by the ',' character into its individual elements and all whitespace
    stripped from the elements.  Numbers are converted to integers, names are left as strings, and
    ranges are converted into the full list of integers.

    @param token:   The identification string, the elements of which are separated by commas.  Each
        element can be either a single number, a range of numbers (two numbers separated by '-'), or
        a name.
    @type token:    str
    @return:        A list of identifying numbers and names.
    @rtype:         list of int and str
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
        indecies= []
        for i in xrange(1,len(element)):
            if element[i] == '-':
                indecies.append(i)

        # Range.
        if indecies:
            # Invalid range element, only one range char '-' and one negative sign is allowed.
            if len(indecies) > 2:
                raise RelaxError, "The range element " + `element` + " is invalid."

            # Convert the two numbers to integers.
            try:
                start = int(element[:indecies[0]])
                end = int(element[indecies[0]+1:])
            except ValueError:
                raise RelaxError, "The range element " + `element` + " is invalid as either the start or end of the range are not integers."

            # Test that the starting number is less than the end.
            if start >= end:
                raise RelaxError, "The starting number of the range element " + `element` + " needs to be less than the end number."

            # Create the range and append it to the list.
            for i in range(start, end+1):
                list.append(i)

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
        pipe = relax_data_store.current_pipe

    # Test the data pipe.
    pipes.test(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data():
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol in relax_data_store[pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
            continue

        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if res not in select_obj:
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
        pipe = relax_data_store.current_pipe

    # Test the data pipe.
    pipes.test(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # No selection.
    if len(select_obj.molecules) == 0:
        return None

    # Loop over the molecules.
    mol_num = 0
    mol_container = None
    for mol in relax_data_store[pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
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
        pipe = relax_data_store.current_pipe

    # Test the data pipe.
    pipes.test(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # No selection.
    if len(select_obj.residues) == 0:
        return None

    # Loop over the molecules.
    res = None
    res_num = 0
    res_container = None
    for mol in relax_data_store[pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
            continue

        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if res not in select_obj:
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


def return_spin(selection=None, pipe=None):
    """Function for returning the spin data container of the given selection.

    @param selection:   The spin selection identifier.
    @type selection:    str
    @param pipe:        The data pipe containing the spin.  Defaults to the current data pipe.
    @type pipe:         str
    @return:            The spin specific data container.
    @rtype:             instance of the ResidueContainer class.
    """

    # The data pipe.
    if pipe == None:
        pipe = relax_data_store.current_pipe

    # Test the data pipe.
    pipes.test(pipe)

    # Parse the selection string.
    select_obj = Selection(selection)

    # No selection.
    if len(select_obj.spins) == 0:
        return None

    # Loop over the molecules.
    spin = None
    spin_num = 0
    spin_container = None
    for mol in relax_data_store[pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
            continue

        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if res not in select_obj:
                continue

            # Loop over the spins.
            for spin in res.spin:
                # Skip the spin if there is no match to the selection.
                if spin not in select_obj:
                    continue

                # Store the spin container.
                spin_container = spin

                # Increment the spin number counter.
                spin_num = spin_num + 1

    # No unique identifier.
    if spin_num > 1:
        raise RelaxError, "The identifier " + `selection` + " corresponds to more than a single spin in the " + `pipe` + " data pipe."

    # Return the spin container.
    return spin_container


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


def reverse(selection=None):
    """Function for the reversal of the spin system selection."""

    # Loop over the spin systems and reverse the selection flag.
    for spin in spin_loop(selection):
        # Reverse the selection.
        if spin.select:
            spin.select = 0
        else:
            spin.select = 1


def sel_all(self, run=None):
    """Function for selecting all residues."""

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence and set the selection flag to 1.
        for i in xrange(len(relax_data_store.res[self.run])):
            relax_data_store.res[self.run][i].select = 1


def sel_read(self, run=None, file=None, dir=None, boolean='OR', change_all=0, column=None):
    """Select the residues contained in the given file.

    @param run:         The run name.
    @type run:          str
    @param file:        The name of the file.
    @type file:         str
    @param dir:         The directory containing the file.
    @type dir:          str
    @param boolean:     The boolean operator used to select the spin systems with.  It can be
        one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
    @type boolean:      str
    @param change_all:  A flag which if set will set the selection to solely those of the file.
    @type change_all:   int
    @param column:      The whitespace separated column in which the residue numbers are
        located.
    @type column:       int
    """

    # Extract the data from the file.
    file_data = self.relax.IO.extract_data(file, dir)

    # Count the number of header lines.
    header_lines = 0
    for i in xrange(len(file_data)):
        try:
            int(file_data[i][column])
        except:
            header_lines = header_lines + 1
        else:
            break

    # Remove the header.
    file_data = file_data[header_lines:]

    # Strip the data.
    file_data = self.relax.IO.strip(file_data)

    # Create the list of residues to select.
    select = []
    for i in xrange(len(file_data)):
        try:
            select.append(int(file_data[i][column]))
        except:
            raise RelaxError, "Improperly formatted file."

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # The spin system is in the new selection list.
            if data.num in select:
                new_select = 1
            else:
                new_select = 0

            # Select just the residues in the file.
            if change_all:
                data.select = new_select

            # Boolean selections.
            if boolean == 'OR':
                data.select = data.select or new_select
            elif boolean == 'NOR':
                data.select = not (data.select or new_select)
            elif boolean == 'AND':
                data.select = data.select and new_select
            elif boolean == 'NAND':
                data.select = not (data.select and new_select)
            elif boolean == 'XOR':
                data.select = not (data.select and new_select) and (data.select or new_select)
            elif boolean == 'XNOR':
                data.select = (data.select and new_select) or not (data.select or new_select)
            else:
                raise RelaxError, "Unknown boolean operator " + `boolean`


def sel_res(self, run=None, num=None, name=None, boolean='OR', change_all=0):
    """Select specific residues.

    @param run:         The run name.
    @type run:          str
    @param num:         The residue number.
    @type num:          int or regular expression str
    @param name:        The residue name.
    @type name:         regular expression str
    @param boolean:     The boolean operator used to select the spin systems with.  It can be
        one of 'OR', 'NOR', 'AND', 'NAND', 'XOR', or 'XNOR'.
    @type boolean:      str
    @param change_all:  A flag which if set will set the selection to solely those residues
        specified.
    @type change_all:   int
    """

    # Test if the residue number is a valid regular expression.
    if type(num) == str:
        try:
            compile(num)
        except:
            raise RelaxRegExpError, ('residue number', num)

    # Test if the residue name is a valid regular expression.
    if name:
        try:
            compile(name)
        except:
            raise RelaxRegExpError, ('residue name', name)

    # Create the list of runs.
    self.runs = self.relax.generic.runs.list_of_runs(run)

    # Loop over the runs.
    no_match = 1
    for self.run in self.runs:
        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not len(relax_data_store.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Initialise the new selection flag.
            new_select = 0

            # Set the new selection flag if the residue matches 'num'.
            if type(num) == int:
                if data.num == num:
                    new_select = 1
            elif type(num) == str:
                if match(num, `data.num`):
                    new_select = 1

            # Set the new selection flag if the residue matches 'name'.
            if name != None:
                if match(name, data.name):
                    new_select = 1

            # Select just the specified residues.
            if change_all:
                data.select = new_select

            # Boolean selections.
            if boolean == 'OR':
                data.select = data.select or new_select
            elif boolean == 'NOR':
                data.select = not (data.select or new_select)
            elif boolean == 'AND':
                data.select = data.select and new_select
            elif boolean == 'NAND':
                data.select = not (data.select and new_select)
            elif boolean == 'XOR':
                data.select = not (data.select and new_select) and (data.select or new_select)
            elif boolean == 'XNOR':
                data.select = (data.select and new_select) or not (data.select or new_select)
            else:
                raise RelaxError, "Unknown boolean operator " + `boolean`

            # Match flag.
            if new_select:
                no_match = 0

    # No residue matched.
    if no_match:
        print "No residues match."


def spin_loop(selection=None, pipe=None, full_info=False):
    """Generator function for looping over all the spin systems of the given selection.

    @param selection:   The spin system selection identifier.
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
        pipe = relax_data_store.current_pipe

    # Test the data pipe.
    pipes.test(pipe)

    # Test for the presence of data, and end the execution of this function if there is none.
    if not exists_mol_res_spin_data():
        return

    # Parse the selection string.
    select_obj = Selection(selection)

    # Loop over the molecules.
    for mol in relax_data_store[pipe].mol:
        # Skip the molecule if there is no match to the selection.
        if mol not in select_obj:
            continue

        # Loop over the residues.
        for res in mol.res:
            # Skip the residue if there is no match to the selection.
            if res not in select_obj:
                continue

            # Loop over the spins.
            for spin in res.spin:
                # Skip the spin if there is no match to the selection.
                if spin not in select_obj:
                    continue

                # Yield the spin system data container.
                if full_info:
                    yield spin, mol.name, res.num, res.name
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

