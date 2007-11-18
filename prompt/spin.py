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
import sys

# relax module imports.
import help
from generic_fns import residue
from generic_fns.selection import id_string_doc
from relax_errors import RelaxIntError, RelaxStrError


class Spin:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the spin data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, pipe_from=None, spin_from=None, pipe_to=None, spin_to=None):
        """Function for copying all data associated with a spin.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The data pipe containing the spin from which the data will be copied.  This
            defaults to the current data pipe.

        spin_from:  The spin identifier string of the spin to copy the data from.

        pipe_to:  The data pipe to copy the data to.  This defaults to the current data pipe.

        spin_to:  The spin identifier string of the spin to copy the data to.


        Description
        ~~~~~~~~~~~

        This function will copy all the data associated with the identified spin to the new,
        non-existent spin.  The new spin must not already exist.


        Examples
        ~~~~~~~~

        To copy the spin data from spin 1 to the new spin 2, type:

        relax> spin.copy(spin_from='@1', spin_to='@2')


        To copy spin 1 of the molecule 'Old mol' to spin 5 of the molecule 'New mol', type:

        relax> spin.copy(spin_from='#Old mol@1', spin_to='#New mol@5')


        To copy the spin data of spin 1 from the data pipe 'm1' to 'm2', assuming the current
        data pipe is 'm1', type:

        relax> spin.copy(spin_from='@1', pipe_to='m2')
        relax> spin.copy(pipe_from='m1', spin_from='@1', pipe_to='m2', spin_to='@1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.copy("
            text = text + "pipe_from=" + `pipe_from`
            text = text + "spin_from=" + `spin_from`
            text = text + "pipe_to=" + `pipe_to`
            text = text + ", spin_to=" + `spin_to` + ")"
            print text

        # The data pipe from argument.
        if pipe_from != None and type(pipe_from) != str:
            raise RelaxNoneStrError, ('data pipe from', pipe_from)

        # The spin from argument.
        if type(spin_from) != str:
            raise RelaxStrError, ('spin from', spin_from)

        # The data pipe to argument.
        if pipe_to != None and type(pipe_to) != str:
            raise RelaxNoneStrError, ('data pipe to', pipe_to)

        # The spin to argument.
        if spin_to != None and type(spin_to) != str:
            raise RelaxNoneStrError, ('spin to', spin_to)

        # Execute the functional code.
        spin.copy(pipe_from=pipe_from, spin_from=spin_from, pipe_to=pipe_to, spin_to=spin_to)


    def create(self, spin_num=None, spin_name=None, res_id=None):
        """Function for creating a new spin.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_num:  The spin number.

        spin_name:  The name of the spin.

        res_id:  The residue ID string identifying the residue to add the spin to.


        Description
        ~~~~~~~~~~~

        This function will add a new spin data container to the relax data storage object.  The same
        spin number cannot be used more than once.


        Examples
        ~~~~~~~~

        The following sequence of commands will generate the sequence 1 C4, 2 C9, 3 C15:

        relax> spin.create(1, 'C4')
        relax> spin.create(2, 'C9')
        relax> spin.create(3, 'C15')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.create("
            text = text + ", spin_num=" + `spin_num`
            text = text + ", spin_name=" + `spin_name`
            text = text + ", res_id=" + `res_id` + ")"
            print text

        # Spin number.
        if type(spin_num) != int:
            raise RelaxIntError, ('spin number', spin_num)

        # Spin name.
        if type(spin_name) != str:
            raise RelaxStrError, ('spin name', spin_name)

        # The residue ID.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identification string', res_id)

        # Execute the functional code.
        spin.create(spin_num=spin_num, spin_name=spin_name, res_id=res_id)


    def delete(self, spin_id=None):
        """Function for deleting spins.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of spins.  See the identification
        string documentation below for more information.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.delete("
            text = text + "spin_id=" + `spin_id` + ")"
            print text

        # The spin identifier argument.
        if type(spin_id) != str:
            raise RelaxStrError, ('spin identifier', spin_id)

        # Execute the functional code.
        spin.delete(spin_id=spin_id)


    def display(self, spin_id=None):
        """Function for displaying information about the spin(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.display("
            text = text + "spin_id=" + `spin_id` + ")"
            print text

        # The spin_id argument.
        if type(spin_id) != str:
            raise RelaxStrError, ('spin identification string', spin_id)

        # Execute the functional code.
        spin.display(spin_id=spin_id)


    def rename(self, spin_id=None, new_name=None):
        """Function for renaming an existent spin(s).

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string corresponding to one or more spins.

        new_name:  The new name.


        Description
        ~~~~~~~~~~~

        This function simply allows spins to be renamed.


        Examples
        ~~~~~~~~

        The following sequence of commands will rename the sequence {1 C1, 2 C2, 3 C3} to {1 C11,
        2 C12, 3 C13}:

        relax> spin.rename('@1', 'C11')
        relax> spin.rename('@2', 'C12')
        relax> spin.rename('@3', 'C13')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.rename("
            text = text + ", spin_id=" + `spin_id`
            text = text + ", new_name=" + `new_name` + ")"
            print text

        # Spin identification string.
        if type(spin_id) != int:
            raise RelaxIntError, ('spin identification string', spin_id)

        # New spin name.
        if type(new_name) != str:
            raise RelaxStrError, ('new spin name', new_name)

        # Execute the functional code.
        spin.create(spin_num=spin_num, new_name=new_name)


    def renumber(self, spin_id=None, new_number=None):
        """Function for renumbering an existent spin.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string corresponding to a single spin.

        new_number:  The new spin number.


        Description
        ~~~~~~~~~~~

        This function simply allows spins to be renumbered.  The new number cannot correspond to
        an existing spin number (for that residue or that molecule).


        Examples
        ~~~~~~~~

        The following sequence of commands will renumber the sequence {1 C1, 2 C2, 3 C3} to
        {-1 C1, -2 C2, -3 C3}:

        relax> spin.renumber('@1', -1)
        relax> spin.renumber('@2', -2)
        relax> spin.renumber('@3', -3)

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "spin.renumber("
            text = text + ", spin_id=" + `spin_id`
            text = text + ", new_number=" + `new_number` + ")"
            print text

        # Spin identification string.
        if type(spin_id) != str:
            raise RelaxStrError, ('spin identification string', spin_id)

        # New spin number.
        if type(new_number) != int:
            raise RelaxIntError, ('new spin number', new_number)

        # Execute the functional code.
        spin.create(spin_num=spin_num, new_number=new_number)



    # Docstring modification.
    #########################

    # Add the identification string description.
    copy.__doc__ = copy.__doc__ + "\n\n" + id_string_doc + "\n"
    create.__doc__ = create.__doc__ + "\n\n" + id_string_doc + "\n"
    delete.__doc__ = delete.__doc__ + "\n\n" + id_string_doc + "\n"
    display.__doc__ = display.__doc__ + "\n\n" + id_string_doc + "\n"
    rename.__doc__ = rename.__doc__ + "\n\n" + id_string_doc + "\n"
    renumber.__doc__ = renumber.__doc__ + "\n\n" + id_string_doc + "\n"
