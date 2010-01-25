###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2007-2010 Edward d'Auvergne                         #
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
"""Module containing the 'rdc' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import rdc
from relax_errors import RelaxError


class RDC(User_fn_class):
    """Class for handling residual dipolar coulpings."""

    def back_calc(self, align_id=None):
        """Back calculate RDCs.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        align_id:  The alignment ID string.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "rdc.back_calc("
            text = text + "align_id=" + repr(align_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(align_id, 'alignment ID string')

        # Execute the functional code.
        rdc.back_calc(align_id=align_id)


    def copy(self, pipe_from=None, pipe_to=None, align_id=None):
        """Copy RDC data from pipe_from to pipe_to.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the pipe to copy the RDC data from.

        pipe_to:  The name of the pipe to copy the RDC data to.

        align_id:  The alignment ID string.


        Description
        ~~~~~~~~~~~

        This function will copy RDC data from 'pipe_from' to 'pipe_to'.  If align_id is not given
        then all RDC data will be copied, otherwise only a specific data set will be.


        Examples
        ~~~~~~~~

        To copy all RDC data from pipe 'm1' to pipe 'm9', type one of:

        relax> rdc.copy('m1', 'm9')
        relax> rdc.copy(pipe_from='m1', pipe_to='m9')
        relax> rdc.copy('m1', 'm9', None)
        relax> rdc.copy(pipe_from='m1', pipe_to='m9', align_id=None)

        To copy only the 'Th' RDC data from 'm3' to 'm6', type one of:

        relax> rdc.copy('m3', 'm6', 'Th')
        relax> rdc.copy(pipe_from='m3', pipe_to='m6', align_id='Th')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "rdc.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", align_id=" + repr(align_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)
        arg_check.is_str(align_id, 'alignment ID string', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        rdc.copy(pipe_from=pipe_from, pipe_to=pipe_to, align_id=align_id)


    def delete(self, align_id=None):
        """Delete the RDC data corresponding to the alignment ID.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        align_id:  The alignment ID string.


        Examples
        ~~~~~~~~

        To delete the RDC data corresponding to align_id='PH_gel', type:

        relax> rdc.delete('PH_gel')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "rdc.delete("
            text = text + "align_id=" + repr(align_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(align_id, 'alignment ID string')

        # Execute the functional code.
        rdc.delete(align_id=align_id)


    def display(self, align_id=None):
        """Display the RDC data corresponding to the alignment ID.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        align_id:  The alignment ID string.


        Examples
        ~~~~~~~~

        To display the 'phage' RDC data, type:

        relax> rdc.display('phage')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "rdc.display("
            text = text + "align_id=" + repr(align_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(align_id, 'alignment ID string')

        # Execute the functional code.
        rdc.display(align_id=align_id)


    def read(self, align_id=None, file=None, dir=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
        """Read the RDC data from file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        align_id:  The alignment ID string.

        file:  The name of the file containing the RDC data.

        dir:  The directory where the file is located.

        spin_id_col:  The spin ID string column (an alternative to the mol, res, and spin name and
            number columns).

        mol_name_col:  The molecule name column (alternative to the spin_id_col).

        res_num_col:  The residue number column (alternative to the spin_id_col).

        res_name_col:  The residue name column (alternative to the spin_id_col).

        spin_num_col:  The spin number column (alternative to the spin_id_col).

        spin_name_col:  The spin name column (alternative to the spin_id_col).

        data_col:  The RDC data column.

        error_col:  The experimental error column.

        sep:  The column separator (the default is white space).

        spin_id:  The spin ID string to restrict the loading of data to certain spin subsets.


        Description
        ~~~~~~~~~~~

        The spin system can be identified in the file using two different formats.  The first is the
        spin ID string column which can include the molecule name, the residue name and number, and
        the spin name and number.  Alternatively the mol_name_col, res_num_col, res_name_col,
        spin_num_col, and/or spin_name_col arguments can be supplied allowing this information to be
        in separate columns.  Note that the numbering of columns starts at one.  The spin_id
        argument can be used to restrict the reading to certain spin types, for example only 15N
        spins when only residue information is in the file.


        Examples
        ~~~~~~~~

        The following commands will read the RDC data out of the file 'Tb.txt' where the columns are
        separated by the symbol ',', and store the RDCs under the ID 'Tb'.

        relax> rdc.read('Tb', 'Tb.txt', sep=',')


        If the individual spin RDC errors are located in the file 'rdc_err.txt' in column number 5,
        then to read these values into relax, type one of:

        relax> rdc.read('phage', 'rdc_err.txt', error_col=5)
        relax> rdc.read(align_id='phage', file='rdc_err.txt', error_col=5)


        If the RDCs correspond to the 'N' spin and other spin types such as 1H, 13C, etc. are loaded
        into relax, then type:

        relax> rdc.read('Tb', 'Tb.txt', spin_id='@N')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "rdc.read("
            text = text + "align_id=" + repr(align_id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spin_id_col=" + repr(spin_id_col)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", data_col=" + repr(data_col)
            text = text + ", error_col=" + repr(error_col)
            text = text + ", sep=" + repr(sep)
            text = text + ", spin_id=" + repr(spin_id) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(align_id, 'alignment ID string')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_int(spin_id_col, 'spin ID string column', can_be_none=True)
        arg_check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        arg_check.is_int(res_num_col, 'residue number column', can_be_none=True)
        arg_check.is_int(res_name_col, 'residue name column', can_be_none=True)
        arg_check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        arg_check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        arg_check.is_int(data_col, 'data column', can_be_none=True)
        arg_check.is_int(error_col, 'error column', can_be_none=True)
        arg_check.is_str(sep, 'column separator', can_be_none=True)
        arg_check.is_str(spin_id, 'spin ID string', can_be_none=True)

        # Execute the functional code.
        rdc.read(align_id=align_id, file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep, spin_id=spin_id)


    def write(self, align_id=None, file=None, dir=None, force=False):
        """Write the RDC data to file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        align_id:  The alignment ID string.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which if True will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        The 'align_id' argument are required for selecting which RDC data set will be written to file.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "rdc.write("
            text = text + "align_id=" + repr(align_id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(align_id, 'alignment ID string')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        rdc.write(align_id=align_id, file=file, dir=dir, force=force)
