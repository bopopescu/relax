###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

import sys
from types import FunctionType

from doc_string import regexp_doc
import help
from generic_fns.diffusion_tensor import Diffusion_tensor
from specific_fns.model_free import Model_free


class OpenDX:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with OpenDX."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def execute(self, file="map", dir="dx", dx_exe="dx", vp_exec=1):
        """Function for running OpenDX.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The file name prefix.  For example if file is set to 'temp', then the OpenDX program
        temp.net will be loaded.

        dir:  The directory to change to for running OpenDX.  If this is set to 'None', OpenDX will
        be run in the current directory.

        dx_exe:  The OpenDX executable file.

        vp_exec:  A flag specifying whether to execute the visual program automatically at
        start-up.  The default is 1 which turns execution on.  Setting the value to zero turns
        execution off.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "dx("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", dx_exe=" + `dx_exe`
            text = text + ", vp_exec=" + `vp_exec` + ")"
            print text

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory name.
        if dir == None:
            pass
        elif type(dir) != str:
            raise RelaxNoneStrError, ('file name', file)

        # The OpenDX executable file.
        if type(dx_exe) != str:
            raise RelaxStrError, ('OpenDX executable file name', dx_exe)

        # Visual program execution flag.
        if type(vp_exec) != int or (vp_exec != 0 and vp_exec != 1):
            raise RelaxBinError, ('visual program execution flag', vp_exec)

        # Execute the functional code.
        self.__relax__.generic.opendx.run(file=file, dir=dir, dx_exe=dx_exe, vp_exec=vp_exec)


    def map(self, run=None, params=None, map_type="Iso3D", res_num=None, inc=20, lower=None, upper=None, file="map", dir="dx", point=None, point_file="point", remap=None):
        """Function for creating a map of the given space in OpenDX format.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        params:  The parameters to be mapped.  This argument should be an array of strings, values
        of which are described below.

        map_type:  The type of map to create.  For example the default, a 3D isosurface, the type is
        'Iso3D'.  See below for more details.

        res_num:  The residue number.

        inc:  The number of increments to map in each dimension.  This value controls the resolution
        of the map.

        lower:  The lower bounds of the space.  If you wish to change the lower bounds of the map
        then supply an array of length equal to the number of parameters in the model.  A lower
        bound for each parameter must be supplied.  If nothing is supplied then the defaults will
        be used.

        upper:  The upper bounds of the space.  If you wish to change the upper bounds of the map
        then supply an array of length equal to the number of parameters in the model.  A upper
        bound for each parameter must be supplied.  If nothing is supplied then the defaults will
        be used.

        file:  The file name.  All the output files are prefixed with this name.  The main file
        containing the data points will be called the value of 'file'.  The OpenDX program will be
        called 'file.net' and the OpenDX import file will be called 'file.general'.

        dir:  The directory to output files to.  Set this to 'None' if you do not want the files to
        be placed in subdirectory.  If the directory does not exist, it will be created.

        point:  An array of parameter values where a point in the map, shown as a red sphere, will
        be placed.  The length must be equal to the number of parameters.

        point_file:  The name of that the point output files will be prefixed with.

        remap:  A user supplied remapping function.  This function will receive the parameter array
        and must return an array of equal length.


        Map type
        ~~~~~~~~

        The map type can be changed by supplying the 'map_type' keyword argument.  Here is a list of
        currently supported map types:
        _____________________________________________________________________________
        |                                           |                               |
        | Surface type                              | Pattern                       |
        |___________________________________________|_______________________________|
        |                                           |                               |
        | 3D isosurface                             | '^[Ii]so3[Dd]'                |
        |___________________________________________|_______________________________|

        Pattern syntax is simply regular expression syntax where square brackets '[]' means any
        character within the brackets, '^' means the start of the string, etc.


        Examples
        ~~~~~~~~

        The following commands will generate a map of the extended model-free space defined as run
        'm5' which consists of the parameters {S2, S2f, ts}.  Files will be output into the
        directory 'dx' and will be prefixed by 'map'.  The residue, in this case, is number 6.

        relax> dx.map('m5', ['S2', 'S2f', 'ts'], 6)
        relax> dx.map('m5', ['S2', 'S2f', 'ts'], 6, 20, 'map', 'dx')
        relax> dx.map('m5', ['S2', 'S2f', 'ts'], res_num=6, file='map', dir='dx')
        relax> dx.map(run='m5', params=['S2', 'S2f', 'ts'], res_num=6, inc=20, file='map', dir='dx')
        relax> dx.map(run='m5', params=['S2', 'S2f', 'ts'], res_num=6, type='Iso3D', inc=20,
                      swap=[0, 1, 2], file='map', dir='dx')


        To map the model-free space 'm4' defined by the parameters {S2, te, Rex}, name the results
        'test', and not place the files in a subdirectory, use the following commands (assuming
        residue 2).

        relax> dx.map('m4', ['S2', 'te', 'Rex'], res_num=2, file='test', dir=None)
        relax> dx.map(run='m4', params=['S2', 'te', 'Rex'], res_num=2, inc=100, file='test',
                      dir=None)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "map("
            text = text + "run=" + `run`
            text = text + ", params=" + `params`
            text = text + ", map_type=" + `map_type`
            text = text + ", res_num=" + `res_num`
            text = text + ", inc=" + `inc`
            text = text + ", lower=" + `lower`
            text = text + ", upper=" + `upper`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", point=" + `point`
            text = text + ", point_file=" + `point_file`
            text = text + ", remap=" + `remap` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The parameters to map.
        if type(params) != list:
            raise RelaxListError, ('parameters', params)
        num_params = len(params)
        for i in xrange(num_params):
            if type(params[i]) != str:
                raise RelaxListStrError, ('parameters', params)

        # Space type.
        if type(map_type) != str:
            raise RelaxStrError, ('map type', map_type)

        # The residue number.
        if type(res_num) != int:
            raise RelaxIntError, ('residue number', res_num)

        # Increment.
        if type(inc) != int:
            raise RelaxIntError, ('increment', inc)
        elif inc <= 1:
            raise RelaxError, "The increment value needs to be greater than 1."

        # Lower bounds.
        if lower != None:
            if type(lower) != list:
                raise RelaxListError, ('lower bounds', lower)
            if len(lower) != num_params:
                raise RelaxLenError, ('lower bounds', num_params)
            for i in xrange(len(lower)):
                if type(lower[i]) != int and type(lower[i]) != float:
                    raise RelaxListNumError, ('lower bounds', lower)

        # Upper bounds.
        if upper != None:
            if type(upper) != list:
                raise RelaxListError, ('upper bounds', upper)
            if len(upper) != num_params:
                raise RelaxLenError, ('upper bounds', num_params)
            for i in xrange(len(upper)):
                if type(upper[i]) != int and type(upper[i]) != float:
                    raise RelaxListNumError, ('upper bounds', upper)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory name.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Point.
        if point != None:
            if type(point) != list:
                raise RelaxListError, ('point', point)
            if len(point) != num_params:
                raise RelaxLenError, ('point', point)
            if type(point_file) != str:
                raise RelaxStrError, ('point file name', point_file)
            for i in xrange(len(point)):
                if type(point[i]) != int and type(point[i]) != float:
                    raise RelaxListNumError, ('point', point)

        # Remap function.
        if remap != None and type(remap) is not FunctionType:
            raise RelaxFunctionError, ('remap function', remap)

        # Execute the functional code.
        self.__relax__.generic.opendx.map(run=run, params=params, map_type=map_type, res_num=res_num, inc=inc, lower=lower, upper=upper, file=file, dir=dir, point=point, point_file=point_file, remap=remap)


    # Docstring modification.
    #########################

    # Write function.
    map.__doc__ = map.__doc__ + "\n\n" + regexp_doc() + "\n"
    map.__doc__ = map.__doc__ + Diffusion_tensor.return_data_name.__doc__ + "\n\n"
    map.__doc__ = map.__doc__ + Model_free.return_data_name.__doc__ + "\n\n"
