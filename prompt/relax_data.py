###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2007-2009 Edward d'Auvergne                         #
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
"""Module containing the 'relax_data' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from base_class import User_fn_class
import check
from generic_fns import relax_data
from relax_errors import RelaxError


class Relax_data(User_fn_class):
    """Class for manipulating R1, R2, and NOE relaxation data."""

    def back_calc(self, ri_label=None, frq_label=None, frq=None):
        """Function for back calculating relaxation data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.

        frq:  The spectrometer frequency in Hz.

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.back_calc("
            text = text + "ri_label=" + repr(ri_label)
            text = text + ", frq_label=" + repr(frq_label)
            text = text + ", frq=" + repr(frq) + ")"
            print(text)

        # The argument checks.
        check.is_str(ri_label, 'relaxation label')
        check.is_str(frq_label, 'frequency label')
        check.is_num(frq, 'frequency')

        # Execute the functional code.
        relax_data.back_calc(ri_label=ri_label, frq_label=frq_label, frq=frq)


    def copy(self, pipe_from=None, pipe_to=None, ri_label=None, frq_label=None):
        """Function for copying relaxation data from pipe_from to pipe_to.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the pipe to copy the relaxation data from.

        pipe_to:  The name of the pipe to copy the relaxation data to.

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.


        Description
        ~~~~~~~~~~~

        This function will copy relaxation data from 'pipe_from' to 'pipe_to'.  If ri_label and frq_label
        are not given then all relaxation data will be copied, otherwise only a specific data set
        will be copied.


        Examples
        ~~~~~~~~

        To copy all relaxation data from pipe 'm1' to pipe 'm9', type one of:

        relax> relax_data.copy('m1', 'm9')
        relax> relax_data.copy(pipe_from='m1', pipe_to='m9')
        relax> relax_data.copy('m1', 'm9', None, None)
        relax> relax_data.copy(pipe_from='m1', pipe_to='m9', ri_label=None, frq_label=None)

        To copy only the NOE relaxation data with the frq_label of '800' from 'm3' to 'm6', type one
        of:

        relax> relax_data.copy('m3', 'm6', 'NOE', '800')
        relax> relax_data.copy(pipe_from='m3', pipe_to='m6', ri_label='NOE', frq_label='800')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", ri_label=" + repr(ri_label)
            text = text + ", frq_label=" + repr(frq_label) + ")"
            print(text)

        # The argument checks.
        check.is_str(pipe_from, 'pipe from', can_be_none=True)
        check.is_str(pipe_to, 'pipe to', can_be_none=True)
        check.is_str(ri_label, 'relaxation label', can_be_none=True)
        check.is_str(frq_label, 'frequency label', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        relax_data.copy(pipe_from=pipe_from, pipe_to=pipe_to, ri_label=ri_label, frq_label=frq_label)


    def delete(self, ri_label=None, frq_label=None):
        """Function for deleting the relaxation data corresponding to ri_label and frq_label.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.


        Examples
        ~~~~~~~~

        To delete the relaxation data corresponding to ri_label='NOE', frq_label='600', type:

        relax> relax_data.delete('NOE', '600')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.delete("
            text = text + "ri_label=" + repr(ri_label)
            text = text + ", frq_label=" + repr(frq_label) + ")"
            print(text)

        # The argument checks.
        check.is_str(ri_label, 'relaxation label')
        check.is_str(frq_label, 'frequency label')

        # Execute the functional code.
        relax_data.delete(ri_label=ri_label, frq_label=frq_label)


    def display(self, ri_label=None, frq_label=None):
        """Function for displaying the relaxation data corresponding to ri_label and frq_label.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.


        Examples
        ~~~~~~~~

        To display the NOE relaxation data at 600 MHz, type:

        relax> relax_data.display('NOE', '600')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.display("
            text = text + "ri_label=" + repr(ri_label)
            text = text + ", frq_label=" + repr(frq_label) + ")"
            print(text)

        # The argument checks.
        check.is_str(ri_label, 'relaxation label')
        check.is_str(frq_label, 'frequency label')

        # Execute the functional code.
        relax_data.display(ri_label=ri_label, frq_label=frq_label)


    def read(self, ri_label=None, frq_label=None, frq=None, file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None):
        """Function for reading R1, R2, or NOE relaxation data from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.

        frq:  The spectrometer frequency in Hz.

        file:  The name of the file containing the relaxation data.

        dir:  The directory where the file is located.

        mol_name_col:  The molecule name column (this defaults to no column).

        res_num_col:  The residue number column (the default is 0, i.e. the first column).

        res_name_col:  The residue name column (the default is 1, i.e. the second column).

        spin_num_col:  The spin number column (this defaults to no column).

        spin_name_col:  The spin name column (this defaults to no column).

        data_col:  The relaxation data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).


        Description
        ~~~~~~~~~~~

        The frequency label argument can be anything as long as data collected at the same field
        strength have the same label.


        Examples
        ~~~~~~~~

        The following commands will read the protein NOE relaxation data collected at 600 MHz out of
        a file called 'noe.600.out' where the residue numbers, residue names, data, errors are in
        the first, second, third, and forth columns respectively.

        relax> relax_data.read('NOE', '600', 599.7 * 1e6, 'noe.600.out')
        relax> relax_data.read(ri_label='NOE', frq_label='600', frq=600.0 * 1e6, file='noe.600.out')


        The following commands will read the R2 data out of the file 'r2.out' where the residue
        numbers, residue names, data, errors are in the second, third, fifth, and sixth columns
        respectively.  The columns are separated by commas.

        relax> relax_data.read('R2', '800 MHz', 8.0 * 1e8, 'r2.out', 1, 2, 4, 5, ',')
        relax> relax_data.read(ri_label='R2', frq_label='800 MHz', frq=8.0*1e8, file='r2.out',
                               res_num_col=1, res_name_col=2, data_col=4, error_col=5, sep=',')


        The following commands will read the R1 data out of the file 'r1.out' where the columns are
        separated by the symbol '%'

        relax> relax_data.read('R1', '300', 300.1 * 1e6, 'r1.out', sep='%')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.read("
            text = text + "ri_label=" + repr(ri_label)
            text = text + ", frq_label=" + repr(frq_label)
            text = text + ", frq=" + repr(frq)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", data_col=" + repr(data_col)
            text = text + ", error_col=" + repr(error_col)
            text = text + ", sep=" + repr(sep) + ")"
            print(text)

        # The argument checks.
        check.is_str(ri_label, 'relaxation label')
        check.is_str(frq_label, 'frequency label')
        check.is_num(frq, 'frequency')
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        check.is_int(res_num_col, 'residue number column', can_be_none=True)
        check.is_int(res_name_col, 'residue name column', can_be_none=True)
        check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        check.is_int(data_col, 'data column')
        check.is_int(error_col, 'error column')
        check.is_str(sep, 'column separator', can_be_none=True)

        # Execute the functional code.
        relax_data.read(ri_label=ri_label, frq_label=frq_label, frq=frq, file=file, dir=dir, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep)


    def write(self, ri_label=None, frq_label=None, file=None, dir=None, force=False):
        """Function for writing R1, R2, or NOE relaxation data to a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ri_label:  The relaxation data type, ie 'R1', 'R2', or 'NOE'.

        frq_label:  The field strength label.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which if True will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        The 'ri_label' and 'frq_label' arguments are required for selecting which relaxation data
        to write to file.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_data.write("
            text = text + "ri_label=" + repr(ri_label)
            text = text + ", frq_label=" + repr(frq_label)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        check.is_str(ri_label, 'relaxation label')
        check.is_str(frq_label, 'frequency label')
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_bool(force, 'force flag')

        # Execute the functional code.
        relax_data.write(ri_label=ri_label, frq_label=frq_label, file=file, dir=dir, force=force)
