###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2008 Edward d'Auvergne                             #
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
import colour
import help
from relax_errors import RelaxBinError, RelaxListNumError, RelaxNoneStrError, RelaxNoneStrListError, RelaxStrError
from specific_fns.model_free.molmol import Molmol


class Molmol:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with Molmol."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def clear_history(self):
        """Function for clearing the Molmol command history."""

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.clear_history()"
            print text

        # Execute the functional code.
        self.__relax__.generic.molmol.clear_history()


    def command(self, run=None, command=None):
        """Function for executing a user supplied Molmol command.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        command:  The Molmol command to execute.


        Description
        ~~~~~~~~~~~

        This user function allows you to pass Molmol commands to the program.  This can be useful
        for automation or scripting.


        Example
        ~~~~~~~

        To reinitialise the Molmol instance for the run 'aic', type:

        relax> molmol.command("aic", "InitAll yes")
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.command("
            text = text + "run=" + `run`
            text = text + ", command=" + `command` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The command argument.
        if type(command) != str:
            raise RelaxStrError, ('command', command)

        # Execute the functional code.
        self.__relax__.generic.molmol.command(run=run, command=command)


    def macro_exec(self, run=None, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
        """Function for executing Molmol macros.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The data type to map to the structure.

        style:  The style of the macro.

        colour_start:  The starting colour, either an array or string, of the linear colour
        gradient.

        colour_end:  The ending colour, either an array or string, of the linear colour gradient.

        colour_list:  The list of colours to match the start and end strings.


        Description
        ~~~~~~~~~~~

        This function allows residues specific values to be mapped to a structure through Molmol
        macros.  Currently only the 'classic' style, which is described below, is availible.


        Colour
        ~~~~~~

        The values are coloured based on a linear colour gradient which is specified through the
        'colour_start' and 'colour_end' arguments.  These arguments can either be a string to
        identify one of the RGB (red, green, blue) colour arrays listed in the tables below, or you
        can give the RGB vector itself.  For example, colour_start='white' and
        colour_start=[1.0, 1.0, 1.0] both select the same colour.  Leaving both arguments at None
        will select the default colour gradient which for each type of analysis is described below.

        When supplying the colours as strings, two lists of colours can be selected from which to
        match the strings.  These are the default Molmol colour list and the X11 colour list, both
        of which are described in the tables below.  The default behaviour is to first search the
        Molmol list and then the X11 colour list, raising an error if neither contain the string.
        To explicitly select these lists, set the 'colour_list' argument to either 'molmol' or
        'x11'.


        Examples
        ~~~~~~~~

        To map the order parameter values, S2, of the run 'final' onto the structure using the
        classic style, type:

        relax> molmol.macro_exec('final', 'S2')
        relax> molmol.macro_exec('final', data_type='S2')
        relax> molmol.macro_exec('final', data_type='S2', style="classic")
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.macro_exec("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", style=" + `style`
            text = text + ", colour_start=" + `colour_start`
            text = text + ", colour_end=" + `colour_end`
            text = text + ", colour_list=" + `colour_list` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data type for mapping to the structure.
        if type(data_type) != str:
            raise RelaxStrError, ('data type', data_type)

        # The style.
        if type(style) != str:
            raise RelaxStrError, ('style', style)

        # The starting colour of the linear gradient.
        if colour_start != None and type(colour_start) != str and type(colour_start) != list:
            raise RelaxNoneStrListError, ('starting colour of the linear gradient', colour_start)
        if type(colour_start) == list:
            for i in xrange(len(colour_start)):
                if type(colour_start[i]) != float and type(colour_start[i]) != int:
                    raise RelaxListNumError, ('starting colour of the linear gradient', colour_start)

        # The ending colour of the linear gradient.
        if colour_end != None and type(colour_end) != str and type(colour_end) != list:
            raise RelaxNoneStrListError, ('ending colour of the linear gradient', colour_end)
        if type(colour_end) == list:
            for i in xrange(len(colour_end)):
                if type(colour_end[i]) != float and type(colour_end[i]) != int:
                    raise RelaxListNumError, ('ending colour of the linear gradient', colour_end)

        # Execute the functional code.
        self.__relax__.generic.molmol.macro_exec(run=run, data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)


    def ribbon(self, run=None):
        """Apply the Molmol ribbon style.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.


        Description
        ~~~~~~~~~~~

        This function applies the Molmol ribbon style which is equivalent to clicking on 'ribbon' in
        the Molmol side menu.  To do this, the following commands are executed:

            CalcAtom 'H'
            CalcAtom 'HN'
            CalcSecondary
            XMacStand ribbon.mac


        Example
        ~~~~~~~

        To apply the ribbon style to the PDB file loaded for the run 'final', type:

        relax> molmol.ribbon("final")
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.ribbon("
            text = text + "run=" + `run` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.molmol.ribbon(run=run)


    def tensor_pdb(self, run=None, file=None):
        """Function displaying the diffusion tensor PDB geometric object over the loaded PDB.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the PDB file containing the tensor geometric object.


        Description
        ~~~~~~~~~~~

        In executing this user function, a PDB file must have previously been loaded into this run,
        a geometric object or polygon representing the Brownian rotational diffusion tensor will be
        overlain with the loaded PDB file and displayed within Molmol.  The PDB file containing the
        geometric object must be created using the complementary 'pdb.create_diff_tensor_pdb()' user
        function.

        To display the diffusion tensor, the multiple commands will be executed.  To overlay the
        structure with the diffusion tensor, everything will be selected and reoriented and moved to
        their original PDB frame positions:

            SelectAtom ''
            SelectBond ''
            SelectAngle ''
            SelectDist ''
            SelectPrim ''
            RotateInit
            MoveInit

        Next the tensor PDB file is read in, selected, and the covalent bonds of the PDB CONECT
        records calculated:

            ReadPdb file
            SelectMol '@file'
            CalcBond 1 1 1

        Then only the atoms and bonds of the geometric object are selected and the 'ball/stick'
        style applied:

            SelectAtom '0'
            SelectBond '0'
            SelectAtom ':TNS'
            SelectBond ':TNS'
            XMacStand ball_stick.mac

        The appearance is finally touched up:

            RadiusAtom 1
            SelectAtom ':TNS@C*'
            RadiusAtom 1.5
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.tensor_pdb("
            text = text + "run=" + `run`
            text = text + ", file=" + `file` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Execute the functional code.
        self.__relax__.generic.molmol.tensor_pdb(run=run, file=file)


    def view(self, run=None):
        """Function for viewing the collection of molecules extracted from the PDB file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run which the PDB belongs to.


        Example
        ~~~~~~~

        relax> molmol.view('m1')
        relax> molmol.view(run='pdb')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.view("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.molmol.view(run=run)


    def write(self, run=None, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir='molmol', force=0):
        """Function for creating Molmol macros.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The data type to map to the structure.

        style:  The style of the macro.

        colour_start:  The starting colour, either an array or string, of the linear colour
        gradient.

        colour_end:  The ending colour, either an array or string, of the linear colour gradient.

        colour_list:  The list of colours to match the start and end strings.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        This function allows residues specific values to be mapped to a structure through the
        creation of a Molmol '*.mac' macro which can be executed in Molmol by clicking on 'File,
        Macro, Execute User...'.  Currently only the 'classic' style, which is described below, is
        availible.


        Colour
        ~~~~~~

        The values are coloured based on a linear colour gradient which is specified through the
        'colour_start' and 'colour_end' arguments.  These arguments can either be a string to
        identify one of the RGB (red, green, blue) colour arrays listed in the tables below, or you
        can give the RGB vector itself.  For example, colour_start='white' and
        colour_start=[1.0, 1.0, 1.0] both select the same colour.  Leaving both arguments at None
        will select the default colour gradient which for each type of analysis is described below.

        When supplying the colours as strings, two lists of colours can be selected from which to
        match the strings.  These are the default Molmol colour list and the X11 colour list, both
        of which are described in the tables below.  The default behaviour is to first search the
        Molmol list and then the X11 colour list, raising an error if neither contain the string.
        To explicitly select these lists, set the 'colour_list' argument to either 'molmol' or
        'x11'.


        Examples
        ~~~~~~~~

        To create a Molmol macro mapping the order parameter values, S2, of the run 'final' onto the
        structure using the classic style, type:

        relax> molmol.write('final', 'S2')
        relax> molmol.write('final', data_type='S2')
        relax> molmol.write('final', data_type='S2', style="classic", file='s2.mac', dir='molmol')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.write("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", style=" + `style`
            text = text + ", colour_start=" + `colour_start`
            text = text + ", colour_end=" + `colour_end`
            text = text + ", colour_list=" + `colour_list`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data type for mapping to the structure.
        if type(data_type) != str:
            raise RelaxStrError, ('data type', data_type)

        # The style.
        if type(style) != str:
            raise RelaxStrError, ('style', style)

        # The starting colour of the linear gradient.
        if colour_start != None and type(colour_start) != str and type(colour_start) != list:
            raise RelaxNoneStrListError, ('starting colour of the linear gradient', colour_start)
        if type(colour_start) == list:
            for i in xrange(len(colour_start)):
                if type(colour_start[i]) != float and type(colour_start[i]) != int:
                    raise RelaxListNumError, ('starting colour of the linear gradient', colour_start)

        # The ending colour of the linear gradient.
        if colour_end != None and type(colour_end) != str and type(colour_end) != list:
            raise RelaxNoneStrListError, ('ending colour of the linear gradient', colour_end)
        if type(colour_end) == list:
            for i in xrange(len(colour_end)):
                if type(colour_end[i]) != float and type(colour_end[i]) != int:
                    raise RelaxListNumError, ('ending colour of the linear gradient', colour_end)

        # File.
        if file != None and type(file) != str:
            raise RelaxNoneStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.generic.molmol.write(run=run, data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, file=file, dir=dir, force=force)



    # Docstring modification.
    #########################

    # Write function.
    write.__doc__ = write.__doc__ + "\n\n" + Molmol.molmol_classic_style.__doc__ + "\n\n"

    # Molmol RGB colour list.
    write.__doc__ = write.__doc__ + "\n\n" + colour.molmol_colours.__doc__ + "\n\n"

    # X11 RGB colour list.
    write.__doc__ = write.__doc__ + "\n\n" + colour.x11_colours.__doc__ + "\n\n"
