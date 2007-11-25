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
from re import search
from math import cos, pi, sin
from Numeric import Float64, dot, identity, transpose, zeros
from types import ListType

# relax module imports.
from data_classes import Element, SpecificData
from relax_errors import RelaxError



def calc_Diso(tm):
    """Function for calculating the Diso value.

    The equation for calculating the parameter is

        Diso  =  1 / (6tm).

    @keyword tm:    The global correlation time.
    @type tm:       float
    @return:        The isotropic diffusion rate (Diso).
    @rtype:         float
    """

    # Calculated and return the Diso value.
    return 1.0 / (6.0 * tm)


def calc_Dpar(Diso, Da):
    """Function for calculating the Dpar value.

    The equation for calculating the parameter is

        Dpar  =  Diso + 2/3 Da.

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @return:        The diffusion rate parallel to the unique axis of the spheroid.
    @rtype:         float
    """

    # Dpar value.
    return Diso + 2.0/3.0 * Da


def calc_Dpar_unit(theta, phi):
    """Function for calculating the Dpar unit vector.

    The unit vector parallel to the unique axis of the diffusion tensor is

                      | sin(theta) * cos(phi) |
        Dpar_unit  =  | sin(theta) * sin(phi) |.
                      |      cos(theta)       |

    @keyword theta: The azimuthal angle in radians.
    @type theta:    float
    @keyword phi:   The polar angle in radians.
    @type phi:      float
    @return:        The Dpar unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dpar_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dpar_unit[0] = sin(theta) * cos(phi)
    Dpar_unit[1] = sin(theta) * sin(phi)
    Dpar_unit[2] = cos(theta)

    # Return the unit vector.
    return Dpar_unit


def calc_Dper(Diso, Da):
    """Function for calculating the Dper value.

    The equation for calculating the parameter is

        Dper  =  Diso - 1/3 Da.

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @return:        The diffusion rate perpendicular to the unique axis of the spheroid.
    @rtype:         float
    """

    # Dper value.
    return Diso - 1.0/3.0 * Da


def calc_Dratio(Dpar, Dper):
    """Function for calculating the Dratio value.

    The equation for calculating the parameter is

        Dratio  =  Dpar / Dper.

    @keyword Dpar:  The diffusion rate parallel to the unique axis of the spheroid.
    @type Dpar:     float
    @keyword Dper:  The diffusion rate perpendicular to the unique axis of the spheroid.
    @type Dper:     float
    @return:        The ratio of the parallel and perpendicular diffusion rates.
    @rtype:         float
    """

    # Dratio value.
    return Dpar / Dper


def calc_Dx(Diso, Da, Dr):
    """Function for calculating the Dx value.

    The equation for calculating the parameter is

        Dx  =  Diso - 1/3 Da(1 + 3Dr).

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @keyword Dr:    The rhombic component of the diffusion tensor.
    @type Dr:       float
    @return:        The diffusion rate parallel to the x-axis of the ellipsoid.
    @rtype:         float
    """

    # Dx value.
    return Diso - 1.0/3.0 * Da * (1.0 + 3.0*Dr)


def calc_Dx_unit(alpha, beta, gamma):
    """Function for calculating the Dx unit vector.

    The unit Dx vector is

                    | -sin(alpha) * sin(gamma) + cos(alpha) * cos(beta) * cos(gamma) |
        Dx_unit  =  | -sin(alpha) * cos(gamma) - cos(alpha) * cos(beta) * sin(gamma) |.
                    |                    cos(alpha) * sin(beta)                      |

    @keyword alpha: The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @keyword beta:  The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @keyword gamma: The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Dx unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dx_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dx_unit[0] = -sin(alpha) * sin(gamma)  +  cos(alpha) * cos(beta) * cos(gamma)
    Dx_unit[1] = -sin(alpha) * cos(gamma)  -  cos(alpha) * cos(beta) * sin(gamma)
    Dx_unit[2] = cos(alpha) * sin(beta)

    # Return the unit vector.
    return Dx_unit


def calc_Dy(Diso, Da, Dr):
    """Function for calculating the Dy value.

    The equation for calculating the parameter is

        Dy  =  Diso - 1/3 Da(1 - 3Dr),

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @keyword Dr:    The rhombic component of the diffusion tensor.
    @type Dr:       float
    @return:        The Dy value.
    @rtype:         float
    """

    # Dy value.
    return Diso - 1.0/3.0 * Da * (1.0 - 3.0*Dr)


def calc_Dy_unit(alpha, beta, gamma):
    """Function for calculating the Dy unit vector.

    The unit Dy vector is

                    | cos(alpha) * sin(gamma) + sin(alpha) * cos(beta) * cos(gamma) |
        Dy_unit  =  | cos(alpha) * cos(gamma) - sin(alpha) * cos(beta) * sin(gamma) |.
                    |                   sin(alpha) * sin(beta)                      |

    @keyword alpha: The Euler angle alpha in radians using the z-y-z convention.
    @type alpha:    float
    @keyword beta:  The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @keyword gamma: The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Dy unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dy_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dy_unit[0] = cos(alpha) * sin(gamma)  +  sin(alpha) * cos(beta) * cos(gamma)
    Dy_unit[1] = cos(alpha) * cos(gamma)  -  sin(alpha) * cos(beta) * sin(gamma)
    Dy_unit[2] = sin(alpha) * sin(beta)

    # Return the unit vector.
    return Dy_unit


def calc_Dz(Diso, Da):
    """Function for calculating the Dz value.

    The equation for calculating the parameter is

        Dz  =  Diso + 2/3 Da.

    @keyword Diso:  The isotropic diffusion rate.
    @type Diso:     float
    @keyword Da:    The anisotropic diffusion rate.
    @type Da:       float
    @return:        The Dz value.
    @rtype:         float
    """

    # Dz value.
    return Diso + 2.0/3.0 * Da


def calc_Dz_unit(beta, gamma):
    """Function for calculating the Dz unit vector.

    The unit Dz vector is

                    | -sin(beta) * cos(gamma) |
        Dz_unit  =  |  sin(beta) * sin(gamma) |.
                    |        cos(beta)        |

    @keyword beta:  The Euler angle beta in radians using the z-y-z convention.
    @type beta:     float
    @keyword gamma: The Euler angle gamma in radians using the z-y-z convention.
    @type gamma:    float
    @return:        The Dz unit vector.
    @rtype:         Numeric array (Float64)
    """

    # Initilise the vector.
    Dz_unit = zeros(3, Float64)

    # Calculate the x, y, and z components.
    Dz_unit[0] = -sin(beta) * cos(gamma)
    Dz_unit[1] = sin(beta) * sin(gamma)
    Dz_unit[2] = cos(beta)

    # Return the unit vector.
    return Dz_unit


def calc_rotation(diff_type, *args):
    """Function for calculating the rotation matrix.

    Spherical diffusion
    ===================

    As the orientation of the diffusion tensor within the structural frame is undefined when the
    molecule diffuses as a sphere, the rotation matrix is simply the identity matrix

              | 1  0  0 |
        R  =  | 0  1  0 |.
              | 0  0  1 |


    Spheroidal diffusion
    ====================

    The rotation matrix required to shift from the diffusion tensor frame to the structural
    frame is equal to

              |  cos(theta) * cos(phi)  -sin(phi)   sin(theta) * cos(phi) |
        R  =  |  cos(theta) * sin(phi)   cos(phi)   sin(theta) * sin(phi) |.
              | -sin(theta)              0          cos(theta)            |


    Ellipsoidal diffusion
    =====================

    The rotation matrix required to shift from the diffusion tensor frame to the structural
    frame is equal to

        R  =  | Dx_unit  Dy_unit  Dz_unit |,

              | Dx_unit[0]  Dy_unit[0]  Dz_unit[0] |
           =  | Dx_unit[1]  Dy_unit[1]  Dz_unit[1] |.
              | Dx_unit[2]  Dy_unit[2]  Dz_unit[2] |

    @param *args:       All the function arguments.
    @type *args:        tuple
    @param theta:       The azimuthal angle in radians.
    @type theta:        float
    @param phi:         The polar angle in radians.
    @type phi:          float
    @param Dpar_unit:   The Dpar unit vector.
    @type Dpar_unit:    Numeric array (Float64)
    @param Dx_unit:     The Dx unit vector.
    @type Dx_unit:      Numeric array (Float64)
    @param Dy_unit:     The Dy unit vector.
    @type Dy_unit:      Numeric array (Float64)
    @param Dz_unit:     The Dz unit vector.
    @type Dz_unit:      Numeric array (Float64)
    @return:            The rotation matrix.
    @rtype:             Numeric array ((3, 3), Float64)
    """

    # The rotation matrix for the sphere.
    if diff_type == 'sphere':
        return identity(3, Float64)

    # The rotation matrix for the spheroid.
    elif diff_type == 'spheroid':
        # Unpack the arguments.
        theta, phi, Dpar_unit = args

        # Initialise the rotation matrix.
        rotation = identity(3, Float64)

        # First row of the rotation matrix.
        rotation[0, 0] = cos(theta) * cos(phi)
        rotation[1, 0] = cos(theta) * sin(phi)
        rotation[2, 0] = -sin(theta)

        # Second row of the rotation matrix.
        rotation[0, 1] = -sin(phi)
        rotation[1, 1] = cos(phi)

        # Replace the last row of the rotation matrix with the Dpar unit vector.
        rotation[:, 2] = Dpar_unit

        # Return the tensor.
        return rotation

    # The rotation matrix for the ellipsoid.
    elif diff_type == 'ellipsoid':
        # Unpack the arguments.
        Dx_unit, Dy_unit, Dz_unit = args

        # Initialise the rotation matrix.
        rotation = identity(3, Float64)

        # First column of the rotation matrix.
        rotation[:, 0] = Dx_unit

        # Second column of the rotation matrix.
        rotation[:, 1] = Dy_unit

        # Third column of the rotation matrix.
        rotation[:, 2] = Dz_unit

        # Return the tensor.
        return rotation

    # Raise an error.
    else:
        raise RelaxError, 'The diffusion tensor has not been specified'


def calc_tensor(rotation, tensor_diag):
    """Function for calculating the diffusion tensor (in the structural frame).

    The diffusion tensor is calculated using the diagonalised tensor and the rotation matrix
    through the equation

        R . tensor_diag . R^T.

    @keyword rotation:      The rotation matrix.
    @type rotation:         Numeric array ((3, 3), Float64)
    @keyword tensor_diag:   The diagonalised diffusion tensor.
    @type tensor_diag:      Numeric array ((3, 3), Float64)
    @return:                The diffusion tensor (within the structural frame).
    @rtype:                 Numeric array ((3, 3), Float64)
    """

    # Rotation (R . tensor_diag . R^T).
    return dot(rotation, dot(tensor_diag, transpose(rotation)))


def calc_tensor_diag(diff_type, *args):
    """Function for calculating the diagonalised diffusion tensor.

    The diagonalised spherical diffusion tensor is defined as

                   | Diso     0     0 |
        tensor  =  |    0  Diso     0 |.
                   |    0     0  Diso |

    The diagonalised spheroidal tensor is defined as

                   | Dper     0     0 |
        tensor  =  |    0  Dper     0 |.
                   |    0     0  Dpar |

    The diagonalised ellipsoidal diffusion tensor is defined as

                   | Dx   0   0 |
        tensor  =  |  0  Dy   0 |.
                   |  0   0  Dz |

    @param *args:   All the arguments.
    @type *args:    tuple
    @param Diso:    The Diso parameter of the sphere.
    @type Diso:     float
    @param Dpar:    The Dpar parameter of the spheroid.
    @type Dpar:     float
    @param Dper:    The Dper parameter of the spheroid.
    @type Dper:     float
    @param Dx:      The Dx parameter of the ellipsoid.
    @type Dx:       float
    @param Dy:      The Dy parameter of the ellipsoid.
    @type Dy:       float
    @param Dz:      The Dz parameter of the ellipsoid.
    @type Dz:       float
    @return:        The diagonalised diffusion tensor.
    @rtype:         Numeric array ((3, 3), Float64)
    """

    # Spherical diffusion tensor.
    if diff_type == 'sphere':
        # Unpack the arguments.
        Diso, = args

        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = Diso
        tensor[1, 1] = Diso
        tensor[2, 2] = Diso

        # Return the tensor.
        return tensor

    # Spheroidal diffusion tensor.
    elif diff_type == 'spheroid':
        # Unpack the arguments.
        Dpar, Dper = args

        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = Dper
        tensor[1, 1] = Dper
        tensor[2, 2] = Dpar

        # Return the tensor.
        return tensor

    # Ellipsoidal diffusion tensor.
    elif diff_type == 'ellipsoid':
        # Unpack the arguments.
        Dx, Dy, Dz = args

        # Initialise the tensor.
        tensor = zeros((3, 3), Float64)

        # Populate the diagonal elements.
        tensor[0, 0] = Dx
        tensor[1, 1] = Dy
        tensor[2, 2] = Dz

        # Return the tensor.
        return tensor


def dependency_generator(diff_type):
    """Generator for the automatic updating the diffusion tensor data structures.

    The order of the yield statements is important!

    @param diff_type:   The type of Brownian rotational diffusion.
    @type diff_type:    str
    @return:            This generator successively yields three objects, the target object to
                        update, the list of parameters which if modified cause the target to be
                        updated, and the list of parameters that the target depends upon.
    """

    # Spherical diffusion.
    if diff_type == 'sphere':
        yield ('Diso',          ['tm'], ['tm'])
        yield ('tensor_diag',   ['tm'], ['type', 'Diso'])
        yield ('rotation',      ['tm'], ['type'])
        yield ('tensor',        ['tm'], ['rotation', 'tensor_diag'])

    # Spheroidal diffusion.
    elif diff_type == 'spheroid':
        yield ('Diso',          ['tm'],                         ['tm'])
        yield ('Dpar',          ['tm', 'Da'],                   ['Diso', 'Da'])
        yield ('Dper',          ['tm', 'Da'],                   ['Diso', 'Da'])
        yield ('Dratio',        ['tm', 'Da'],                   ['Dpar', 'Dper'])
        yield ('Dpar_unit',     ['theta', 'phi'],               ['theta', 'phi'])
        yield ('tensor_diag',   ['tm', 'Da'],                   ['type', 'Dpar', 'Dper'])
        yield ('rotation',      ['theta', 'phi'],               ['type', 'theta', 'phi', 'Dpar_unit'])
        yield ('tensor',        ['tm', 'Da', 'theta', 'phi'],   ['rotation', 'tensor_diag'])

    # Ellipsoidal diffusion.
    elif diff_type == 'ellipsoid':
        yield ('Diso',          ['tm'],                                         ['tm'])
        yield ('Dx',            ['tm', 'Da', 'Dr'],                             ['Diso', 'Da', 'Dr'])
        yield ('Dy',            ['tm', 'Da', 'Dr'],                             ['Diso', 'Da', 'Dr'])
        yield ('Dz',            ['tm', 'Da'],                                   ['Diso', 'Da'])
        yield ('Dx_unit',       ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
        yield ('Dy_unit',       ['alpha', 'beta', 'gamma'],                     ['alpha', 'beta', 'gamma'])
        yield ('Dz_unit',       ['alpha', 'beta'],                              ['alpha', 'beta'])
        yield ('tensor_diag',   ['tm', 'Da', 'Dr'],                             ['type', 'Dx', 'Dy', 'Dz'])
        yield ('rotation',      ['alpha', 'beta', 'gamma'],                     ['type', 'Dx_unit', 'Dy_unit', 'Dz_unit'])
        yield ('tensor',        ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma'],   ['rotation', 'tensor_diag'])



# Diffusion tensor specific data.
#################################

class DiffTensorData(SpecificData):
    def __init__(self):
        """Dictionary type class for the diffusion tensor data.

        The non-default diffusion parameters are calculated on the fly.
        """


    def add_item(self, key):
        """Function for adding an empty container to the dictionary.

        This overwrites the function from the parent class SpecificData.
        """

        self[key] = DiffTensorElement()



class DiffTensorElement(Element):
    def __init__(self):
        """An empty data container for the diffusion tensor elements."""

        # Set the initial diffusion type to None.
        self.type = None


    def __setattr__(self, name, value):
        """Function for calculating the parameters, unit vectors, and tensors on the fly.

        The equations for the parameters Dper, Dpar, and Dratio are

            Dratio  =  Dpar / Dper.
        """

        # Get the base parameter name and determine the object category ('val', 'err', or 'sim').
        if search('_err$', name):
            category = 'err'
            param_name = name[:-4]
        elif search('_sim$', name):
            category = 'sim'
            param_name = name[:-4]
        else:
            category = 'val'
            param_name = name

        # List of modifiable attributes.
        mod_attr = ['type',
                    'fixed',
                    'spheroid_type',
                    'tm',
                    'Da',
                    'Dr',
                    'theta',
                    'phi',
                    'alpha',
                    'beta',
                    'gamma']

        # Test if the attribute that is trying to be set is modifiable.
        if not param_name in mod_attr:
            raise RelaxError, "The object " + `name` + " is not modifiable."

        # Set the attribute normally.
        self.__dict__[name] = value

        # Skip the updating process for certain objects.
        if name in ['type', 'fixed', 'spheroid_type']:
            return

        # Update the data structures.
        for target, update_if_set, depends in dependency_generator(self.type):
            self.__update_object(param_name, target, update_if_set, depends, category)


    def __update_sim_append(self, param_name, index):
        """Update the Monte Carlo simulation data lists when a simulation value is appended.

        @param param_name:  The MC sim parameter name which is being appended to.
        @type param_name:   str
        @param index:       The index of the Monte Carlo simulation which was set.
        @type index:        int
        """

        # Loop over the targets.
        for target, update_if_set, depends in dependency_generator(self.type):
            # Only update if the parameter name is within the 'update_if_set' list.
            if not param_name in update_if_set:
                continue

            # Get the function for calculating the value.
            fn = globals()['calc_'+target]

            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the MC dependency.
                dep_obj = getattr(self, dep_name)

                # The diffusion tensor type.
                if dep_name == 'type':
                    deps = deps+(dep_obj,)
                    continue

                # Test if the MC sim dependency is long enough.
                if len(dep_obj) <= index:
                    missing_dep = 1
                    break

                # Place the value corresponding to the index into the 'deps' array.
                deps = deps+(dep_obj[index],)

            # Only update the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Get the target object.
                target_obj = getattr(self, target+'_sim')

                # Calculate and set the value.
                target_obj.append_untouchable_item(fn(*deps))


    def __update_sim_set(self, param_name, index):
        """Update the Monte Carlo simulation data lists when a simulation value is set.

        @param param_name:  The MC sim parameter name which is being set.
        @type param_name:   str
        @param index:       The index of the Monte Carlo simulation which was set.
        @type index:        int
        """

        # Loop over the targets.
        for target, update_if_set, depends in dependency_generator(self.type):
            # Only update if the parameter name is within the 'update_if_set' list.
            if not param_name in update_if_set:
                continue

            # Get the function for calculating the value.
            fn = globals()['calc_'+target]

            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the MC dependency.
                dep_obj = getattr(self, dep_name)

                # The diffusion tensor type.
                if dep_name == 'type':
                    deps = deps+(dep_obj,)
                    continue

                # Test if the MC sim dependency is long enough.
                if len(dep_obj) <= index:
                    missing_dep = 1
                    break

                # Place the value corresponding to the index into the 'deps' array.
                deps = deps+(dep_obj[index],)

            # Only update the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Get the target object.
                target_obj = getattr(self, target+'_sim')

                # Calculate and set the value.
                target_obj.set_untouchable_item(index, fn(*deps))


    def __update_object(self, param_name, target, update_if_set, depends, category):
        """Function for updating the target object, its error, and the MC simulations.

        If the base name of the object is not within the 'update_if_set' list, this function returns
        without doing anything (to avoid wasting time).  Dependant upon the category the object
        (target), its error (target+'_err'), or all Monte Carlo simulations (target+'_sim') are
        updated.

        @param param_name:      The parameter name which is being set in the __setattr__() function.
        @type param_name:       str
        @param target:          The name of the object to update.
        @type target:           str
        @param update_if_set:   If the parameter being set by the __setattr__() function is not
            within this list of parameters, don't waste time updating the
            target.
        @param depends:         An array of names objects that the target is dependent upon.
        @type depends:          array of str
        @param category:        The category of the object to update (one of 'val', 'err', or
            'sim').
        @type category:         str
        @return:                None
        """

        # Only update if the parameter name is within the 'update_if_set' list.
        if not param_name in update_if_set:
            return

        # Get the function for calculating the value.
        fn = globals()['calc_'+target]


        # The value.
        ############

        if category == 'val':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name),)

            # Only update the object if its dependencies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target] = value


        # The error.
        ############

        if category == 'err':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = ()
            for dep_name in depends:
                # Test if the error object exists.
                if not hasattr(self, dep_name+'_err'):
                    missing_dep = 1
                    break

                # Get the object and place it into the 'deps' tuple.
                deps = deps+(getattr(self, dep_name+'_err'),)

            # Only update the error object if its dependencies exist.
            if not missing_dep:
                # Calculate the value.
                value = fn(*deps)

                # Set the attribute.
                self.__dict__[target+'_err'] = value


        # The Monte Carlo simulations.
        ##############################

        if category == 'sim':
            # Get all the dependencies if possible.
            missing_dep = 0
            deps = []
            for dep_name in depends:
                # Modify the dependency name.
                if dep_name != 'type':
                    dep_name = dep_name+'_sim'

                # Test if the MC sim object exists.
                if not hasattr(self, dep_name):
                    missing_dep = 1
                    break

            # Only create the MC simulation object if its dependencies exist.
            if not missing_dep:
                # Initialise an empty array to store the MC simulation object elements (if it doesn't already exist).
                if not target+'_sim' in self.__dict__:
                    self.__dict__[target+'_sim'] = DiffTensorSimList(target, self)



class DiffTensorSimList(ListType):
    """Empty data container for Monte Carlo simulation diffusion tensor data."""

    def __init__(self, param_name, diff_element):
        """Initialise the Monte Carlo simulation parameter list.

        This function makes the parameter name and parent object accessible to the functions of this
        list object.
        """

        self.param_name = param_name
        self.diff_element = diff_element


    def __setitem__(self, index, value):
        """Set the value."""

        # Set the value.
        ListType.__setitem__(self, index, value)

        # Then update the other lists.
        self.diff_element._DiffTensorElement__update_sim_set(self.param_name, index)


    def append(self, value):
        """Replacement function for the normal self.append() method."""

        # Append the value to the list.
        self[len(self):len(self)] = [value]

        # Update the other MC lists.
        self.diff_element._DiffTensorElement__update_sim_append(self.param_name, len(self)-1)


    def append_untouchable_item(self, value):
        """Append the value for an untouchable MC data structure."""

        # Append the value to the list.
        self[len(self):len(self)] = [value]


    def set_untouchable_item(self, index, value):
        """Set the value for an untouchable MC data structure."""

        # Set the value.
        ListType.__setitem__(self, index, value)
