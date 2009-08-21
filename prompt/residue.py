###############################################################################
#                                                                             #
# Copyright (C) 2007, 2009 Edward d'Auvergne                                  #
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
"""Module containing the 'residue' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from base_class import User_fn_class
import check
from generic_fns.mol_res_spin import copy_residue, create_residue, delete_residue, display_residue, id_string_doc, name_residue, number_residue
from relax_errors import RelaxIntError, RelaxNoneStrError, RelaxStrError


class Residue(User_fn_class):
    """Class for manipulating the residue data."""

    def copy(self, pipe_from=None, res_from=None, pipe_to=None, res_to=None):
        """Function for copying all data associated with a residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The data pipe containing the residue from which the data will be copied.  This
            defaults to the current data pipe.

        res_from:  The residue identifier string of the residue to copy the data from.

        pipe_to:  The data pipe to copy the data to.  This defaults to the current data pipe.

        res_to:  The residue identifier string of the residue to copy the data to.


        Description
        ~~~~~~~~~~~

        This function will copy all the data associated with the identified residue to the new,
        non-existent residue.  The new residue must not already exist.


        Examples
        ~~~~~~~~

        To copy the residue data from residue 1 to the new residue 2, type:

        relax> residue.copy(res_from=':1', res_to=':2')


        To copy residue 1 of the molecule 'Old mol' to residue 5 of the molecule 'New mol', type:

        relax> residue.copy(res_from='#Old mol:1', res_to='#New mol:5')


        To copy the residue data of residue 1 from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> residue.copy(res_from=':1', pipe_to='m2')
        relax> residue.copy(pipe_from='m1', res_from=':1', pipe_to='m2', res_to=':1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", res_from=" + repr(res_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", res_to=" + repr(res_to) + ")"
            print(text)

        # The argument checks.
        check.is_str(pipe_from, 'pipe from', can_be_none=True)
        check.is_str(res_from, 'residue from')
        check.is_str(pipe_to, 'pipe to', can_be_none=True)
        check.is_str(res_to, 'residue to', can_be_none=True)

        # Execute the functional code.
        copy_residue(pipe_from=pipe_from, res_from=res_from, pipe_to=pipe_to, res_to=res_to)


    def create(self, res_num=None, res_name=None, mol_name=None):
        """Function for creating a new residue.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_num:  The residue number.

        res_name:  The name of the residue.

        mol_name:  The name of the molecule to add the residue to.


        Description
        ~~~~~~~~~~~

        Using this function a new sequence can be generated without using the sequence user
        functions.  However if the sequence already exists, the new residue will be added to the end
        of the residue list (the residue numbers of this list need not be sequential).  The same
        residue number cannot be used more than once.  A corresponding single spin system will be
        created for this residue.  The spin system number and name or additional spin systems can be
        added later if desired.


        Examples
        ~~~~~~~~

        The following sequence of commands will generate the sequence 1 ALA, 2 GLY, 3 LYS:

        relax> residue.create(1, 'ALA')
        relax> residue.create(2, 'GLY')
        relax> residue.create(3, 'LYS')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.create("
            text = text + "res_num=" + repr(res_num)
            text = text + ", res_name=" + repr(res_name)
            text = text + ", mol_name=" + repr(mol_name) + ")"
            print(text)

        # The argument checks.
        check.is_int(res_num, 'residue number')
        check.is_str(res_name, 'residue name', can_be_none=True)
        check.is_str(mol_name, 'molecule name', can_be_none=True)

        # Execute the functional code.
        create_residue(res_num=res_num, res_name=res_name, mol_name=mol_name)


    def delete(self, res_id=None):
        """Function for deleting residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of residues.  See the identification
        string documentation below for more information.  If spin system/atom ids are included a
        RelaxError will be raised.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.delete("
            text = text + "res_id=" + repr(res_id) + ")"
            print(text)

        # The argument checks.
        check.is_str(res_id, 'residue identification string')

        # Execute the functional code.
        delete_residue(res_id=res_id)


    def display(self, res_id=None):
        """Function for displaying information about the residue(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.display("
            text = text + "res_id=" + repr(res_id) + ")"
            print(text)

        # The argument checks.
        check.is_str(res_id, 'residue identification string', can_be_none=True)

        # Execute the functional code.
        display_residue(res_id=res_id)


    def name(self, res_id=None, name=None, force=False):
        """Function for naming residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identification string corresponding to one or more residues.

        name:  The new name.

        force:  A flag which if True will cause the residue to be renamed.


        Description
        ~~~~~~~~~~~

        This function simply allows residues to be named (or renamed).


        Examples
        ~~~~~~~~

        The following sequence of commands will rename the sequence {1 ALA, 2 GLY, 3 LYS} to {1 XXX,
        2 XXX, 3 XXX}:

        relax> residue.name(':1', 'XXX', force=True)
        relax> residue.name(':2', 'XXX', force=True)
        relax> residue.name(':3', 'XXX', force=True)

        Alternatively:

        relax> residue.name(':1,2,3', 'XXX', force=True)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.name("
            text = text + "res_id=" + repr(res_id)
            text = text + ", name=" + repr(name)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        check.is_str(res_id, 'residue identification string')
        check.is_str(name, 'new residue name')
        check.is_bool(force, 'force flag')

        # Execute the functional code.
        name_residue(res_id=res_id, name=name, force=force)


    def number(self, res_id=None, number=None, force=False):
        """Function for numbering residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identification string corresponding to a single residue.

        number:  The new residue number.

        force:  A flag which if True will cause the residue to be renumbered.


        Description
        ~~~~~~~~~~~

        This function simply allows residues to be numbered.  The new number cannot correspond to
        an existing residue.


        Examples
        ~~~~~~~~

        The following sequence of commands will renumber the sequence {1 ALA, 2 GLY, 3 LYS} to
        {101 ALA, 102 GLY, 103 LYS}:

        relax> residue.number(':1', 101, force=True)
        relax> residue.number(':2', 102, force=True)
        relax> residue.number(':3', 103, force=True)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.number("
            text = text + "res_id=" + repr(res_id)
            text = text + ", number=" + repr(number)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        check.is_str(res_id, 'residue identification string')
        check.is_int(number, 'new residue number')
        check.is_bool(force, 'force flag')

        # Execute the functional code.
        number_residue(res_id=res_id, number=number, force=force)



    # Docstring modification.
    #########################

    # Add the residue identification string description.
    copy.__doc__ = copy.__doc__ + "\n\n" + id_string_doc + "\n"
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
    display.__doc__ = display.__doc__ + "\n\n" + id_string_doc + "\n"
    name.__doc__ = name.__doc__ + "\n\n" + id_string_doc + "\n"
    number.__doc__ = number.__doc__ + "\n\n" + id_string_doc + "\n"
