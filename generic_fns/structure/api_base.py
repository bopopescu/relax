###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
"""The API for accessing, creating, and modifying structural information.

The full API is documented within this base class object.  Each available API call is given as a
prototype method stub (or functional method) with all arguments, raised errors, and return values
documented.
"""

# Python module imports.
from os import sep
from types import MethodType
from warnings import warn

# relax module import.
from data.relax_xml import fill_object_contents, xml_to_object
from relax_errors import RelaxError, RelaxFileError, RelaxImplementError
from relax_io import file_root
from relax_warnings import RelaxWarning


class Base_struct_API:
    """The structural object base class.

    All API methods are prototyped here as stub methods.
    """

    # Identification string.
    id = 'API'


    def __init__(self):
        """Initialise the structural object."""

        # Initialise the variables used to keep track of multiple structures.
        self.num = 0
        self.name = []
        self.model = []
        self.file = []
        self.path = []
        self.structural_data = ModelList()


    def add_molecule(self, name=None, model=None):
        """Prototype method stub for adding the given molecule to the store.

        @keyword name:          The molecule identification string.
        @type name:             str
        @keyword model:         The number of the model to add the molecule to.
        @type model:            int or None
        """

        # Raise the error.
        raise RelaxImplementError


    def atom_loop(self, atom_id=None, str_id=None, model_num_flag=False, mol_name_flag=False, res_num_flag=False, res_name_flag=False, atom_num_flag=False, atom_name_flag=False, element_flag=False, pos_flag=False, ave=False):
        """Prototype generator method stub for looping over all atoms in the structural data object.

        This method should be designed as a generator (http://www.python.org/dev/peps/pep-0255/).
        It should loop over all atoms of the system yielding the following atomic information, if
        the corresponding flag is True, in tuple form:

            1.  Model number.
            2.  Molecule name.
            3.  Residue number.
            4.  Residue name.
            5.  Atom number.
            6.  Atom name.
            7.  The element name (its atomic symbol and optionally the isotope, e.g. 'N', 'Mg',
                '17O', '13C', etc).
            8.  The position of the atom in Euclidean space.


        @keyword atom_id:           The molecule, residue, and atom identifier string.  Only atoms
                                    matching this selection will be yielded.
        @type atom_id:              str
        @keyword str_id:            The structure identifier.  This can be the file name, model
                                    number, or structure number.  If None, then all structures will
                                    be looped over.
        @type str_id:               str, int, or None
        @keyword model_num_flag:    A flag which if True will cause the model number to be yielded.
        @type model_num_flag:       bool
        @keyword mol_name_flag:     A flag which if True will cause the molecule name to be yielded.
        @type mol_name_flag:        bool
        @keyword res_num_flag:      A flag which if True will cause the residue number to be
                                    yielded.
        @type res_num_flag:         bool
        @keyword res_name_flag:     A flag which if True will cause the residue name to be yielded.
        @type res_name_flag:        bool
        @keyword atom_num_flag:     A flag which if True will cause the atom number to be yielded.
        @type atom_num_flag:        bool
        @keyword atom_name_flag:    A flag which if True will cause the atom name to be yielded.
        @type atom_name_flag:       bool
        @keyword element_flag:      A flag which if True will cause the element name to be yielded.
        @type element_flag:         bool
        @keyword pos_flag:          A flag which if True will cause the atomic position to be
                                    yielded.
        @type pos_flag:             bool
        @keyword ave:               A flag which if True will result in this method returning the
                                    average atom properties across all loaded structures.
        @type ave:                  bool
        @return:                    A tuple of atomic information, as described in the docstring.
        @rtype:                     tuple consisting of optional molecule name (str), residue number
                                    (int), residue name (str), atom number (int), atom name(str),
                                    element name (str), and atomic position (array of len 3).
        """

        # Raise the error.
        raise RelaxImplementError


    def attached_atom(self, atom_id=None, attached_atom=None, model=None):
        """Prototype method stub for finding the atom 'attached_atom' bonded to the atom 'atom_id'.

        @keyword atom_id:       The molecule, residue, and atom identifier string.  This must
                                correspond to a single atom in the system.
        @type atom_id:          str
        @keyword attached_atom: The name of the attached atom to return.
        @type attached_atom:    str
        @keyword model:         The model to return the positional information from.  If not
                                supplied and multiple models exist, then the returned atomic
                                position will be a list of the positions in each model.
        @type model:            None or int
        @return:                A tuple of information about the bonded atom.
        @rtype:                 tuple consisting of the atom number (int), atom name (str), element
                                name (str), and atomic positions for each model (list of numpy
                                arrays)
        """

        # Raise the error.
        raise RelaxImplementError


    def bond_vectors(self, atom_id=None, attached_atom=None, model_num=None, return_name=False, return_warnings=False):
        """Prototype method stub for finding the bond vectors between 'attached_atom' and 'atom_id'.

        @keyword atom_id:           The molecule, residue, and atom identifier string.  This must
                                    correspond to a single atom in the system.
        @type atom_id:              str
        @keyword attached_atom:     The name of the bonded atom.
        @type attached_atom:        str
        @keyword model_num:         The model of which to return the vectors from.  If not supplied
                                    and multiple models exist, then vectors from all models will be
                                    returned.
        @type model_num:            None or int
        @keyword return_name:       A flag which if True will cause the name of the attached atom to
                                    be returned together with the bond vectors.
        @type return_name:          bool
        @keyword return_warnings:   A flag which if True will cause warning messages to be returned.
        @type return_warnings:      bool
        @return:                    The list of bond vectors for each model.
        @rtype:                     list of numpy arrays
        """

        # Raise the error.
        raise RelaxImplementError


    def from_xml(self, str_node, dir=None):
        """Recreate the structural object from the XML structural object node.

        @param str_node:    The structural object XML node.
        @type str_node:     xml.dom.minicompat.Element instance
        @keyword dir:       The name of the directory containing the results file.
        @type dir:          str
        """

        # Recreate all the data structures.
        xml_to_object(str_node, self)

        # Loop over the structures and load them.
        for i in xrange(self.num):
            # Load the structure from file and path.
            if self.path[i]:
                try:
                    loaded = self.load_pdb(file_path=self.path[i] + sep + self.file[i], model=None, struct_index=i)
                except RelaxError:
                    loaded = False
            else:
                loaded = False

            # Try without the path to search for the file in the current directory.
            if not loaded:
                try:
                    loaded = self.load_pdb(file_path=self.file[i], model=None, struct_index=i)
                except RelaxError:
                    loaded = False

            # Try in the path of the results file.
            if not loaded:
                try:
                    loaded = self.load_pdb(file_path=dir + sep + self.file[i], model=None, struct_index=i)
                except RelaxError:
                    loaded = False

            # Can't load the file.
            if not loaded:
                if self.path[i]:
                    warn(RelaxWarning("The structure file " + `self.file[i]` + " cannot be found in the current directory, the directory of the results file or in the directory" + `self.path[i]` + "."))
                else:
                    warn(RelaxWarning("The structure file " + `self.file[i]` + " cannot be found in the current directory or the directory of the results file."))


    def get_model(self, model):
        """Return or create the model.

        @param model:   The model number.
        @type model:    int or None
        @return:        The ModelContainer corresponding to the model number or that newly created.
        @rteyp:         ModelContainer instance
        """

        # Check if the target is a single model.
        if model == None and self.num_models() > 1:
            raise RelaxError, "The target model cannot be determined as there are %s models already present." % self.num_modes()

        # No model specified.
        if model == None:
            # Create the first model, if necessary.
            if self.num_models():
                self.structural_data.add_item()

            # Alias the first model.
            model_cont = self.structural_data[0]

        # The model has been specified.
        else:
            # Get the preexisting model.
            found = False
            for model_cont in self.structural_data:
                if model_cont.num == model:
                    found = True
                    break

            # Add the model if it doesn't exist.
            if not found:
                self.structural_data.add_item(model)
                model_cont = self.structural_data[-1]


    def load_pdb(self, file_path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, verbosity=False):
        """Prototype method stub for loading structures from a PDB file.

        This inherited prototype method is a stub which, if the functionality is desired, should be
        overwritten by the derived class.


        @param file_path:       The full path of the PDB file.
        @type file_path:        str
        @keyword read_mol:      The molecule(s) to read from the file, independent of model.  The
                                molecules are determined differently by the different parsers, but
                                are numbered consecutively from 1.  If set to None, then all
                                molecules will be loaded.
        @type read_mol:         None, int, or list of int
        @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None,
                                then the molecules will be automatically labelled based on the file
                                name or other information.
        @type set_mol_name:     None, str, or list of str
        @keyword read_model:    The PDB model to extract from the file.  If set to None, then all
                                models will be loaded.
        @type read_model:       None, int, or list of int
        @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then
                                the PDB model numbers will be preserved, if they exist.
        @type set_model_num:    None, int, or list of int
        @keyword verbosity:     A flag which if True will cause messages to be printed.
        @type verbosity:        bool
        @return:                The status of the loading of the PDB file.
        @rtype:                 bool
        """

        # Raise the error.
        raise RelaxImplementError


    def num_models(self):
        """Method for returning the number of models.

        @return:    The number of models in the structural object.
        @rtype:     int
        """

        return len(self.structural_data)


    def num_molecules(self):
        """Method for returning the number of molecules.

        @return:    The number of molecules in the structural object.
        @rtype:     int
        """

        # Validate the structural object.
        self.validate()

        # Return the number.
        return len(self.structural_data[0].mol)


    def pack_structs(self, data_matrix, orig_model_num=None, set_model_num=None, orig_mol_num=None, set_mol_name=None, file_name=None, file_path=None):
        """From the given structural data, expand the structural data data structure.

        @param data_matrix:         A matrix of structural objects.
        @type data_matrix:          list of lists of structural objects
        @keyword orig_model_num:    The original model numbers (for storage).
        @type orig_model_num:       list of int
        @keyword set_model_num:     The new model numbers (for model renumbering).
        @type set_model_num:        list of int
        @keyword orig_mol_num:      The original molecule numbers (for storage).
        @type orig_mol_num:         list of int
        @keyword mol_name:          The molecule ID string.
        @type mol_name:             str
        @keyword file_name:         The name of the file from which the molecular data has been
                                    extracted.
        @type file_name:            None or str
        @keyword file_path:         The full path to the file specified by 'file_name'.
        @type file_path:            None or str
        """

        # Test the number of models.
        if len(orig_model_num) != len(data_matrix):
            raise RelaxError, "Structural data mismatch, %s original models verses %s in the structural data." % (len(orig_model_num), len(data_matrix))

        # Test the number of molecules.
        if len(orig_mol_num) != len(data_matrix[0]):
            raise RelaxError, "Structural data mismatch, %s original molecules verses %s in the structural data." % (len(orig_mol_num), len(data_matrix[0]))

        # Model numbers do not change.
        if not set_model_num:
            set_model_num = orig_model_num

        # Test the model mapping.
        if len(set_model_num) != len(data_matrix):
            raise RelaxError, "Failure of the mapping of new model numbers, %s new model numbers verses %s models in the structural data." % (len(set_model_num), len(data_matrix))

        # Test the molecule mapping.
        if len(set_mol_name) != len(data_matrix[0]):
            raise RelaxError, "Failure of the mapping of new molecule names, %s new molecule names verses %s molecules in the structural data." % (len(set_mol_name), len(data_matrix[0]))

        # Test that the target models and structures are absent, and get the already existing model numbers.
        current_models = []
        for i in range(len(self.structural_data)):
            # Create a list of current models.
            current_models.append(self.structural_data[i].num)

            # Loop over the structures.
            for j in range(len(self.structural_data[i].mol)):
                if self.structural_data[i].num in set_model_num and self.structural_data[i].mol[j].name in set_mol_name:
                    raise RelaxError, "The molecule '%s' of model %s already exists." % (self.structural_data[i].mol[j].name, self.structural_data[i].num)

        # Loop over the models.
        for i in range(len(set_model_num)):
            # The model doesn't currently exist.
            if set_model_num[i] not in current_models:
                # Create the model.
                self.structural_data.add_item(set_model_num[i])

                # Add the model number to the current_models list.
                current_models.append(set_model_num[i])

                # Get the model.
                model = self.structural_data[-1]

            # Otherwise get the pre-existing model.
            else:
                model = self.structural_data[current_models.index(set_model_num[i])]

            # Loop over the molecules.
            for j in range(len(set_mol_name)):
                # Print out.
                print "Adding molecule '%s' to model %s (from the original molecule number %s of model %s)" % (set_mol_name[j], set_model_num[i], orig_mol_num[j], orig_model_num[i])

                # Pack the structures.
                model.mol.add_item(mol_name=set_mol_name[j], mol_cont=data_matrix[i][j])

                # Set the molecule name and store the structure file info. 
                model.mol[-1].mol_name = set_mol_name[j]
                model.mol[-1].file_name = file_name
                model.mol[-1].file_path = file_path
                model.mol[-1].file_mol_num = orig_mol_num[j]
                model.mol[-1].file_model = orig_model_num[j]



    def target_mol_name(self, set=None, target=None, index=None, mol_num=None, file=None):
        """Add the new molecule name to the target data structure.

        @keyword set:       The list of new molecule names.  If not supplied, the names will be
                            generated from the file name.
        @type set:          None or list of str
        @keyword target:    The target molecule name data structure to which the new name will be
                            appended.
        @type target:       list
        @keyword index:     The molecule index, matching the set argument.
        @type index:        int
        @keyword mol_num:   The molecule number.
        @type mol_num:      int
        @keyword file:      The name of the file, excluding all directories.
        @type file:         str
        """

        # Set the target molecule name.
        if set:
            target.append(set[index])
        else:
            # Set the name to the file name plus the structure number.
            target.append(file_root(file) + '_mol' + `mol_num`)


    def to_xml(self, doc, element):
        """Prototype method for converting the structural object to an XML representation.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the alignment tensors XML element to.
        @type element:  XML element object
        """

        # Create the structural element and add it to the higher level element.
        str_element = doc.createElement('structure')
        element.appendChild(str_element)

        # Set the structural attributes.
        str_element.setAttribute('desc', 'Structural information')
        str_element.setAttribute('id', self.id)

        # Blacklist methods.
        blacklist = []
        for name in dir(self):
            # Get the object.
            obj = getattr(self, name)

            # Add methods to the list.
            if isinstance(obj, MethodType):
                blacklist.append(name)

        # Add all simple python objects within the PipeContainer to the pipe element.
        fill_object_contents(doc, str_element, object=self, blacklist=blacklist + ['structural_data'] + self.__class__.__dict__.keys())


    def write_pdb(self, file, struct_index=None):
        """Prototype method stub for the creation of a PDB file from the structural data.

        The PDB records
        ===============

        The following information about the PDB records has been taken from the "Protein Data Bank
        Contents Guide: Atomic Coordinate Entry Format Description" version 3.1, February 11, 2008.

        HET record
        ----------

        The HET record describes non-standard residues.  The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "HET   "     |                                                |
         |  8 - 10 | LString(3)   | hetID        | Het identifier, right-justified.               |
         | 13      | Character    | ChainID      | Chain identifier.                              |
         | 14 - 17 | Integer      | seqNum       | Sequence number.                               |
         | 18      | AChar        | iCode        | Insertion code.                                |
         | 21 - 25 | Integer      | numHetAtoms  | Number of HETATM records for the group present |
         |         |              |              | in the entry.                                  |
         | 31 - 70 | String       | text         | Text describing Het group.                     |
         |_________|______________|______________|________________________________________________|


        HETNAM record
        -------------

        The HETNAM associates a chemical name with the hetID from the HET record.  The format is of
        the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "HETNAM"     |                                                |
         |  9 - 10 | Continuation | continuation | Allows concatenation of multiple records.      |
         | 12 - 14 | LString(3)   | hetID        | Het identifier, right-justified.               |
         | 16 - 70 | String       | text         | Chemical name.                                 |
         |_________|______________|______________|________________________________________________|


        FORMUL record
        -------------

        The chemical formula for non-standard groups. The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "FORMUL"     |                                                |
         |  9 - 10 | Integer      | compNum      | Component number.                              |
         | 13 - 15 | LString(3)   | hetID        | Het identifier.                                |
         | 17 - 18 | Integer      | continuation | Continuation number.                           |
         | 19      | Character    | asterisk     | "*" for water.                                 |
         | 20 - 70 | String       | text         | Chemical formula.                              |
         |_________|______________|______________|________________________________________________|


        MODEL record
        ------------

        The model number, for multiple structures.  The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "MODEL "     |                                                |
         | 11 - 14 | Integer      | serial       | Model serial number.                           |
         |_________|______________|______________|________________________________________________|


        ATOM record
        -----------

        The ATOM record contains the atomic coordinates for atoms belonging to standard residues.
        The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "ATOM"       |                                                |
         |  7 - 11 | Integer      | serial       | Atom serial number.                            |
         | 13 - 16 | Atom         | name         | Atom name.                                     |
         | 17      | Character    | altLoc       | Alternate location indicator.                  |
         | 18 - 20 | Residue name | resName      | Residue name.                                  |
         | 22      | Character    | chainID      | Chain identifier.                              |
         | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
         | 27      | AChar        | iCode        | Code for insertion of residues.                |
         | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X in Angstroms.     |
         | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y in Angstroms.     |
         | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z in Angstroms.     |
         | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                     |
         | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                            |
         | 73 - 76 | LString(4)   | segID        | Segment identifier, left-justified.            |
         | 77 - 78 | LString(2)   | element      | Element symbol, right-justified.               |
         | 79 - 80 | LString(2)   | charge       | Charge on the atom.                            |
         |_________|______________|______________|________________________________________________|


        HETATM record
        -------------

        The HETATM record contains the atomic coordinates for atoms belonging to non-standard
        groups.  The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "HETATM"     |                                                |
         |  7 - 11 | Integer      | serial       | Atom serial number.                            |
         | 13 - 16 | Atom         | name         | Atom name.                                     |
         | 17      | Character    | altLoc       | Alternate location indicator.                  |
         | 18 - 20 | Residue name | resName      | Residue name.                                  |
         | 22      | Character    | chainID      | Chain identifier.                              |
         | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
         | 27      | AChar        | iCode        | Code for insertion of residues.                |
         | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X.                  |
         | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y.                  |
         | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z.                  |
         | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                     |
         | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                            |
         | 73 - 76 | LString(4)   | segID        | Segment identifier; left-justified.            |
         | 77 - 78 | LString(2)   | element      | Element symbol; right-justified.               |
         | 79 - 80 | LString(2)   | charge       | Charge on the atom.                            |
         |_________|______________|______________|________________________________________________|


        TER record
        ----------

        The end of the ATOM and HETATM records for a chain.  According to the draft atomic
        coordinate entry format description:

        I{"The TER record has the same residue name, chain identifier, sequence number and insertion
        code as the terminal residue. The serial number of the TER record is one number greater than
        the serial number of the ATOM/HETATM preceding the TER."}

        The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "TER   "     |                                                |
         |  7 - 11 | Integer      | serial       | Serial number.                                 |
         | 18 - 20 | Residue name | resName      | Residue name.                                  |
         | 22      | Character    | chainID      | Chain identifier.                              |
         | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
         | 27      | AChar        | iCode        | Insertion code.                                |
         |_________|______________|______________|________________________________________________|


        CONECT record
        -------------

        The connectivity between atoms.  This is required for all HET groups and for non-standard
        bonds.  The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "CONECT"     |                                                |
         |  7 - 11 | Integer      | serial       | Atom serial number                             |
         | 12 - 16 | Integer      | serial       | Serial number of bonded atom                   |
         | 17 - 21 | Integer      | serial       | Serial number of bonded atom                   |
         | 22 - 26 | Integer      | serial       | Serial number of bonded atom                   |
         | 27 - 31 | Integer      | serial       | Serial number of bonded atom                   |
         | 32 - 36 | Integer      | serial       | Serial number of hydrogen bonded atom          |
         | 37 - 41 | Integer      | serial       | Serial number of hydrogen bonded atom          |
         | 42 - 46 | Integer      | serial       | Serial number of salt bridged atom             |
         | 47 - 51 | Integer      | serial       | Serial number of hydrogen bonded atom          |
         | 52 - 56 | Integer      | serial       | Serial number of hydrogen bonded atom          |
         | 57 - 61 | Integer      | serial       | Serial number of salt bridged atom             |
         |_________|______________|______________|________________________________________________|


        ENDMDL record
        -------------

        The end of model record, for multiple structures.  The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "ENDMDL"     |                                                |
         |_________|______________|______________|________________________________________________|



        MASTER record
        -------------

        The control record for bookkeeping.  The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "MASTER"     |                                                |
         | 11 - 15 | Integer      | numRemark    | Number of REMARK records                       |
         | 16 - 20 | Integer      | "0"          |                                                |
         | 21 - 25 | Integer      | numHet       | Number of HET records                          |
         | 26 - 30 | Integer      | numHelix     | Number of HELIX records                        |
         | 31 - 35 | Integer      | numSheet     | Number of SHEET records                        |
         | 36 - 40 | Integer      | numTurn      | Number of TURN records                         |
         | 41 - 45 | Integer      | numSite      | Number of SITE records                         |
         | 46 - 50 | Integer      | numXform     | Number of coordinate transformation records    |
         |         |              |              | (ORIGX+SCALE+MTRIX)                            |
         | 51 - 55 | Integer      | numCoord     | Number of atomic coordinate records            |
         |         |              |              | (ATOM+HETATM)                                  |
         | 56 - 60 | Integer      | numTer       | Number of TER records                          |
         | 61 - 65 | Integer      | numConect    | Number of CONECT records                       |
         | 66 - 70 | Integer      | numSeq       | Number of SEQRES records                       |
         |_________|______________|______________|________________________________________________|


        END record
        ----------

        The end of the PDB file.  The format of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "END   "     |                                                |
         |_________|______________|______________|________________________________________________|


        @param file:            The PDB file object.  This object must be writable.
        @type file:             file object
        @param struct_index:    The index of the structural container to write.  If None, all
                                structures will be written.
        @type struct_index:     int
        """

        # Raise the error.
        raise RelaxImplementError


    def validate(self):
        """Check the integrity of the structural data.

        The number of molecules must be the same in all models.
        """

        # Reference number of molecules.
        num_mols = len(self.structural_data[0].mol)

        # Loop over all other models.
        for i in range(1, len(self.structural_data)):
            if num_mols != len(self.structural_data[i].mol):
                raise RelaxError, "The structural object is not valid - the number of molecules is not the same for all models."



class ModelList(list):
    """List type data container for the different structural models.

    Here different models are defined as the same molecule but with different conformations.
    """

    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        text = "Models.\n\n"
        text = text + "%-8s%-8s" % ("Index", "Model number") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s" % (i, self[i].num) + "\n"
        return text


    def add_item(self, model_num=None):
        """Append an empty ModelContainer to the ModelList.

        @keyword model_num: The model number.
        @type model_num:    int
        """

        # If no model data exists, replace the empty first model with this model (just a renumbering).
        if self.is_empty():
            self[0].num = model_num

        # Otherwise append an empty ModelContainer.
        else:
            # Test if the model number already exists.
            for i in xrange(len(self)):
                if self[i].num == model_num:
                    raise RelaxError, "The model '" + `model_num` + "' already exists."

            # Append an empty ModelContainer.
            self.append(ModelContainer(model_num))


    def is_empty(self):
        """Method for testing if this ModelList object is empty.

        @return:    True if this list only has one ModelContainer and the model name has not
                    been set, False otherwise.
        @rtype:     bool
        """

        # There is only one ModelContainer and it is empty.
        if len(self) == 1 and self[0].is_empty():
            return True

        # Otherwise.
        return False


    def from_xml(self, model_nodes):
        """Recreate a model list data structure from the XML model nodes.

        @param model_nodes: The model XML nodes.
        @type model_nodes:  xml.dom.minicompat.NodeList instance
        """

        # Test if empty.
        if not self.is_empty():
            raise RelaxFromXMLNotEmptyError, self.__class__.__name__

        # Loop over the models.
        for model_node in model_nodes:
            # Get the model details and add the model to the ModelList structure.
            num = eval(model_node.getAttribute('num'))
            if num == 'None':
                num = None
            self.add_item(model_num=num)

            # Get the molecule nodes.
            mol_nodes = model_node.getElementsByTagName('mol')

            # Recreate the molecule data structures for the current model.
            self[-1].mol.from_xml(mol_nodes)


    def to_xml(self, doc, element):
        """Create XML elements for each model.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the model XML elements to.
        @type element:  XML element object
        """

        # Loop over the models.
        for i in xrange(len(self)):
            # Create an XML element for this model and add it to the higher level element.
            model_element = doc.createElement('model')
            element.appendChild(model_element)

            # Set the model attributes.
            model_element.setAttribute('desc', 'Model container')
            model_element.setAttribute('num', str(self[i].num))

            # Add all simple python objects within the ModelContainer to the XML element.
            fill_object_contents(doc, model_element, object=self[i], blacklist=['num', 'mol'] + self[i].__class__.__dict__.keys())

            # Add the molecule data.
            self[i].mol.to_xml(doc, model_element)



class ModelContainer(object):
    """Class containing all the model specific data."""

    def __init__(self, model_num=None):
        """Set up the default objects of the model data container."""

        # The model number.
        self.num = model_num

        # The empty molecule list.
        self.mol = MolList()


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing the data for model %s.\n" % self.num

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Molecule list.
            if name == 'mol':
                text = text + "  mol: The list of %s molecules within the model.\n" % len(self.mol)
                continue

            # Skip the ModelContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


    def is_empty(self):
        """Method for testing if this ModelContainer object is empty.

        @return:    True if this container is empty and the model number has not been set, False
                    otherwise.
        @rtype:     bool
        """

        # The model num has been set.
        if self.num != None:
            return False

        # An object has been added to the container.
        for name in dir(self):
            # Skip the objects initialised in __init__().
            if name == 'num' or name == 'mol':
                continue

            # Skip the ModelContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The molecule list is not empty.
        if not self.mol.is_empty():
            return False

        # The ModelContainer is unmodified.
        return True



class MolList(list):
    """List type data container for holding the different molecules of one model."""

    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        text = "Molecules.\n\n"
        text = text + "%-8s%-8s" % ("Index", "Name") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s" % (i, self[i].name) + "\n"
        return text


    def add_item(self, mol_name=None, mol_cont=None):
        """Append the given MolContainer instance to the MolList.

        @keyword mol_name:	The molecule number.
        @type mol_name:      	int
        @keyword mol_cont:   	The data structure for the molecule.
        @type mol_cont:      	MolContainer instance
        """

        # If no molecule data exists, replace the empty first molecule with this molecule (just a renaming).
        if self.is_empty():
            self[0].name = mol_name

        # Otherwise append an empty MolContainer.
        else:
            # Test if the molecule already exists.
            for i in xrange(len(self)):
                if self[i].name == mol_name:
                    raise RelaxError, "The molecule '" + `mol_name` + "' already exists."

            # Append an empty MolContainer.
            self.append(mol_cont)


    def is_empty(self):
        """Method for testing if this MolList object is empty.

        @return:    True if this list only has one MolContainer and the molecule name has not
                    been set, False otherwise.
        @rtype:     bool
        """

        # There is only one MolContainer and it is empty.
        if len(self) == 1 and hasattr(self[0], 'is_empty') and self[0].is_empty():
            return True

        # Otherwise.
        return False


    def from_xml(self, mol_nodes):
        """Recreate a molecule list data structure from the XML molecule nodes.

        @param mol_nodes:    The molecule XML nodes.
        @type mol_nodes:     xml.dom.minicompat.NodeList instance
        """

        # Test if empty.
        if not self.is_empty():
            raise RelaxFromXMLNotEmptyError, self.__class__.__name__

        # Loop over the molecules.
        for mol_node in mol_nodes:
            # Get the molecule details and add the molecule to the MolList structure.
            name = eval(mol_node.getAttribute('name'))
            if name == 'None':
                name = None
            self.add_item(mol_name=name)

            # Get the molecule nodes.
            mol_nodes = mol_node.getElementsByTagName('mol')

            # Recreate the molecule data structures for the current molecule.
            self[-1].mol.from_xml(mol_nodes)


    def to_xml(self, doc, element):
        """Create XML elements for each molecule.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the molecule XML elements to.
        @type element:  XML element object
        """

        # Loop over the molecules.
        for i in xrange(len(self)):
            # Create an XML element for this molecule and add it to the higher level element.
            mol_element = doc.createElement('mol')
            element.appendChild(mol_element)

            # Set the molecule attributes.
            mol_element.setAttribute('desc', 'Molecule container')
            mol_element.setAttribute('name', str(self[i].name))

            # Add all simple python objects within the MolContainer to the XML element.
            fill_object_contents(doc, mol_element, object=self[i], blacklist=['name'] + self[i].__class__.__dict__.keys())

            # Add the molecule data.
            self[i].mol.to_xml(doc, mol_element)
