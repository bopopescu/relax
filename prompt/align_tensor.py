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
from generic_fns import align_tensor
from relax_errors import RelaxError, RelaxBinError, RelaxFloatError, RelaxIntError, RelaxNoneStrError, RelaxNumTupleError, RelaxStrError


class Align_tensor:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the alignment tensor."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, tensor_from=None, pipe_from=None, tensor_to=None, pipe_to=None):
        """Function for copying alignment tensor data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor_from:  The identification string of the alignment tensor to copy the data from.

        pipe_from:  The name of the data pipe to copy the alignment tensor data from.

        tensor_to:  The identification string of the alignment tensor to copy the data to.

        pipe_to:  The name of the data pipe to copy the alignment tensor data to.


        Description
        ~~~~~~~~~~~

        This function will copy the alignment tensor data to a new tensor or a new data pipe.  The
        destination data pipe must not contain any alignment tensor data corresponding to the
        tensor_to label.  If the pipe_from or pipe_to arguments are not supplied, then both will
        default to the current data pipe.  Both the tensor_from and tensor_to arguments must be
        supplied.


        Examples
        ~~~~~~~~

        To copy the alignment tensor data corresponding to 'Pf1' from the data pipe 'old' to the
        current data pipe, type one of:

        relax> align_tensor.copy('Pf1', 'old')
        relax> align_tensor.copy(tensor_from='Pf1', pipe_from='old')


        To copy the alignment tensor data corresponding to 'Otting' from the current data pipe to
        the data pipe new, type one of:

        relax> align_tensor.copy('Otting', pipe_to='new')
        relax> align_tensor.copy(tensor_from='Otting', pipe_to='new')


        To copy the alignment tensor data of 'Otting' to that of 'Otting new', type one of:

        relax> align_tensor.copy('Otting', tensor_to='Otting new')
        relax> align_tensor.copy(tensor_from='Pf1', tensor_to='Otting new')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.copy("
            text = text + "tensor_from=" + `tensor_from`
            text = text + ", pipe_from=" + `pipe_from`
            text = text + ", tensor_to=" + `tensor_to`
            text = text + ", pipe_to=" + `pipe_to` + ")"
            print text

        # The tensor_from argument.
        if type(tensor_from) != str:
            raise RelaxStrError, ('tensor from', tensor_from)

        # The pipe_from argument.
        if pipe_from != None and type(pipe_from) != str:
            raise RelaxNoneStrError, ('pipe from', pipe_from)

        # The tensor_to argument.
        if type(tensor_to) != str:
            raise RelaxStrError, ('tensor to', tensor_to)

        # The pipe_to argument.
        if pipe_to != None and type(pipe_to) != str:
            raise RelaxNoneStrError, ('pipe to', pipe_to)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError, "The pipe_from and pipe_to arguments cannot both be set to None."

        # Execute the functional code.
        align_tensor.copy(tensor_from=tensor_from, pipe_from=pipe_from, tensor_to=tensor_to, pipe_to=pipe_to)


    def delete(self, tensor=None):
        """Function for deleting alignment tensor data.


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.


        Description
        ~~~~~~~~~~~

        This function will delete the specified alignment tensor data from the current data pipe.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.delete("
            text = text + "tensor=" + `tensor` + ")"
            print text

        # Label argument.
        if type(tensor) != str:
            raise RelaxStrError, ('tensor', tensor)

        # Execute the functional code.
        align_tensor.delete(tensor=tensor)


    def display(self, tensor=None):
        """Function for displaying the alignment tensor information.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.display("
            text = text + "tensor=" + `tensor` + ")"
            print text

        # Label argument.
        if type(tensor) != str:
            raise RelaxStrError, ('tensor', tensor)

        # Execute the functional code.
        align_tensor.display(tensor=tensor)


    def init(self, tensor=None, params=None, scale=1.0, angle_units='deg', param_types=0, errors=0):
        """Function for initialising the alignment tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.

        params:  The alignment tensor data.

        scale:  The alignment tensor eigenvalue scaling value.

        angle_units:  The units for the angle parameters.

        param_types:  A flag to select different parameter combinations.

        errors:  A flag which determines if the alignment tensor data or its errors are being input.


        Description
        ~~~~~~~~~~~

        Using this function, the alignment tensor data can be set up.  The params argument should be
        a tuple of floating point numbers (a list surrounded by round brakets).  These correspond to
        the parameters of the tensor, which can be specified by the param_types argument, where the
        values correspond to

            0:  {Sxx, Syy, Sxy, Sxz, Syz}  (unitless),
            1:  {Szz, Sxx-yy, Sxy, Sxz, Syz}  (Pales default format),
            2:  {Axx, Ayy, Axy, Axz, Ayz}  (unitless),
            3:  {Azz, Axx-yy, Axy, Axz, Ayz}  (unitless),
            4:  {Axx, Ayy, Axy, Axz, Ayz}  (units of Hertz),
            5:  {Azz, Axx-yy, Axy, Axz, Ayz}  (units of Hertz),
            6:  {Pxx, Pyy, Pxy, Pxz, Pyz}  (unitless),
            7:  {Pzz, Pxx-yy, Pxy, Pxz, Pyz}  (unitless),
 
        Other formats may be added later.  The relationship between the Saupe order matrix S and the
        alignment tensor A is

            S = 3/2 A.

        The probability matrix P is related to the alignment tensor A by

            A = P - 1/3 I,

        where I is the identity matrix.  For the alignment tensor to be supplied in Hertz, the bond
        vectors must all be of equal length.


        Examples
        ~~~~~~~~

        To set a rhombic tensor to the run 'CaM', type one of:

        relax> align_tensor.init((-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05, 2.8599e-04),
                                 param_types=1)
        relax> align_tensor.init((-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05, 2.8599e-04),
                                 param_types=1)
        relax> align_tensor.init(params=(-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05,
                                 2.8599e-04), param_types=1)
        relax> align_tensor.init(params=(-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05,
                                 2.8599e-04), param_types=1)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.init("
            text = text + "tensor=" + `tensor`
            text = text + ", params=" + `params`
            text = text + ", scale=" + `scale`
            text = text + ", angle_units=" + `angle_units`
            text = text + ", param_types=" + `param_types`
            text = text + ", errors=" + `errors` + ")"
            print text

        # Label argument.
        if type(tensor) != str:
            raise RelaxStrError, ('tensor', tensor)

        # Parameter argument.
        if type(params) != tuple:
            raise RelaxNumTupleError, ('alignment tensor parameters', params)
        else:
            if len(params) != 5:
                raise RelaxError, "The alignment tensor parameters argument must be a tuple of numbers of length 5."
            for i in xrange(len(params)):
                if type(params[i]) != float and type(params[i]) != int:
                    raise RelaxNumTupleError, ('alignment tensor parameters', params)

        # Scale argument.
        if type(scale) != float:
            raise RelaxFloatError, ('scale', scale)

        # Angle units argument.
        if type(angle_units) != str:
            raise RelaxStrError, ('angle units', angle_units)

        # Parameter types argument.
        if type(param_types) != int:
            raise RelaxIntError, ('parameter types', param_types)

        # The errors flag.
        if type(errors) != int or (errors != 0 and errors != 1):
            raise RelaxBinError, ('errors flag', errors)

        # Execute the functional code.
        align_tensor.init(tensor=tensor, params=params, scale=scale, angle_units=angle_units, param_types=param_types, errors=errors)


    def matrix_angles(self):
        """Function for calculating the 5D angles between all alignment tensors.

        Description
        ~~~~~~~~~~~

        This function will calculate the angles between all loaded alignment tensors for the current
        data pipe.  The matrices are first converted to a 5D vector form and then then angles are
        calculated.  Unlike SVD, the basis set choice has no effect on the angles.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.matrix_angles()"
            print text

        # Execute the functional code.
        align_tensor.matrix_angles()


    def svd(self, basis_set=0):
        """Function for calculating the singular values for all tensors and the condition number.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        basis_set:  The basis set to operate with.


        Description
        ~~~~~~~~~~~

        This function will, using SVD, calculate the singular values of all tensors loaded for the
        current data pipe.  If the basis_set argument is set to the default of 0, the matrix on
        which SVD will be performed is composed of the unitary basis set {Sxx, Syy, Sxy, Sxz, Syz}
        layed out as:

            | Sxx1 Syy1 Sxy1 Sxz1 Syz1 |
            | Sxx2 Syy2 Sxy2 Sxz2 Syz2 |
            | Sxx3 Syy3 Sxy3 Sxz3 Syz3 |
            |  .    .    .    .    .   |
            |  .    .    .    .    .   |
            |  .    .    .    .    .   |
            | SxxN SyyN SxyN SxzN SyzN |

        If basis_set is set to 1, the geometric basis set consisting of the stretching and skewing
        parameters Szz and Sxx-yy respectively {Szz, Sxxyy, Sxy, Sxz, Syz} will be used instead.
        The matrix is:

        | Szz1 Sxxyy1 Sxy1 Sxz1 Syz1 |
        | Szz2 Sxxyy2 Sxy2 Sxz2 Syz2 |
        | Szz3 Sxxyy3 Sxy3 Sxz3 Syz3 |
        |  .     .     .    .    .   |
        |  .     .     .    .    .   |
        |  .     .     .    .    .   |
        | SzzN SxxyyN SxyN SxzN SyzN |

        The relationships between the geometric and unitary basis sets are:

            Szz = - Sxx - Syy,
            Sxxyy = Sxx - Syy,

        The SVD values and condition number are dependendent upon the basis set chosen.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "align_tensor.svd("
            text = text + "basis_set=" + `basis_set` + ")"
            print text

        # Basis set argument.
        if type(basis_set) != int:
            raise RelaxIntError, ('basis set', basis_set)

        # Execute the functional code.
        align_tensor.svd(basis_set)
