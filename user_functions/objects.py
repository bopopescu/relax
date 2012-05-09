###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""The module of all the objects used to hold the user function details."""

# relax module imports.
from graphics import IMAGE_PATH
from relax_errors import RelaxError


class Class_container:
    """This class is used to process and store all of the user function class information.

    @ivar title:            The user function class description.
    @type title:            str
    @ivar menu_text:        The text to use for the GUI menu entry.
    @type menu_text:        str
    @ivar gui_icon:         The code for the icon to use in the GUI.
    @type gui_icon:         str or None
    """

    # The list of modifiable objects (anything else will be rejected to prevent coding errors).
    __mod_attr__ = [
            'title',
            'menu_text',
            'gui_icon'
    ]

    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user function classes.
        self.title = None
        self.menu_text = None
        self.gui_icon = None


    def __setattr__(self, name, value):
        """Override the class __setattr__ method.

        @param name:    The name of the attribute to modify.
        @type name:     str
        @param value:   The new value of the attribute.
        @type value:    anything
        """

        # Test if the attribute that is trying to be set is modifiable.
        if not name in self.__mod_attr__:
            raise RelaxError("The object '%s' is not a modifiable attribute." % name)

        # Set the attribute normally.
        self.__dict__[name] = value



class Container:
    """An empty container object."""



class Uf_container(object):
    """This class is used to process and store all of the user function specific information.

    @ivar title:                The long title of the user function.
    @type title:                str
    @ivar title_short:          The optional short title.
    @type title_short:          str or None
    @ivar kargs:                The list of keyword argument details.
    @type kargs:                list of dict
    @ivar backend:              The user function back end.  This should be a string version with full module path of the function which executes the back end.  For example 'generic_fns.pipes.create'.  Note, this should be importable as __import__(backend)!
    @type backend:              executable object
    @ivar display:              A flag specifying if the user function displays output to STDOUT.  This is used for certain UIs to display that output.
    @type display:              str
    @ivar desc:                 The full, multi-paragraph description.
    @type desc:                 str
    @ivar additional:           Additional documentation, usually appended to the end of the description.
    @type additional:           list of str
    @ivar prompt_examples:      The examples of how to use the prompt front end.
    @type prompt_examples:      str or None
    @ivar menu_text:            The text to use for the GUI menu entry.
    @type menu_text:            str
    @ivar gui_icon:             The code for the icon to use in the GUI.
    @type gui_icon:             str or None
    @ivar wizard_size:          The size for the GUI user function wizard.  This defaults to (600, 400) if not supplied.
    @type wizard_size:          tuple of int or None
    @ivar wizard_image:         The 200 pixel wide image to use for the user function wizard.  This should be the path to the bitmap image.  This defaults to the relax Ulysses butterfly image.
    @type wizard_image:         str
    @ivar wizard_height_desc:   The height in pixels of the description part of the wizard.
    @type wizard_height_desc:   int
    @ivar wizard_apply_button:  A flag specifying if the apply button should be shown or not.  This defaults to True.
    @type wizard_apply_button:  bool
    """

    # The list of modifiable objects (anything else will be rejected to prevent coding errors).
    __mod_attr__ = [
            'title',
            'title_short',
            'kargs',
            'backend',
            'display',
            'desc',
            'additional',
            'prompt_examples',
            'menu_text',
            'gui_icon',
            'wizard_size',
            'wizard_image',
            'wizard_height_desc',
            'wizard_apply_button'
    ]


    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user functions.
        self.title = None
        self.title_short = None
        self.kargs = []
        self.backend = None
        self.display = False
        self.desc = None
        self.additional = None
        self.prompt_examples = None
        self.menu_text = ''
        self.gui_icon = None
        self.wizard_size = (600, 400)
        self.wizard_image = IMAGE_PATH + "relax.gif"
        self.wizard_height_desc = 220
        self.wizard_apply_button = True


    def __setattr__(self, name, value):
        """Override the class __setattr__ method.

        @param name:    The name of the attribute to modify.
        @type name:     str
        @param value:   The new value of the attribute.
        @type value:    anything
        """

        # Test if the attribute that is trying to be set is modifiable.
        if not name in self.__mod_attr__:
            raise RelaxError("The object '%s' is not a modifiable attribute." % name)

        # Check for duplicative modifications (to catch typo coding errors).
        if name in ['title', 'title_short', 'backend', 'prompt_examples', 'gui_icon']:
            # No object set yet.
            if not hasattr(self, name):
                obj = None

            # Get the current object.
            else:
                obj = getattr(self, name)

            # Not None!
            if obj != None:
                raise RelaxError("The variable '%s' is already set to %s." % (name, repr(obj)))

        # Set the attribute normally.
        self.__dict__[name] = value


    def add_keyarg(self, name=None, default=None, py_type=None, arg_type=None, size=None, dim=None, desc_short=None, desc=None, list_titles=None, wiz_element_type='default', wiz_combo_choices=[], wiz_combo_data=None, wiz_combo_iter=None, wiz_combo_list_size=None, wiz_read_only=None, can_be_none=False, can_be_empty=False, none_elements=False):
        """Wrapper method for adding keyword argument information to the container.

        @keyword name:                  The name of the argument.
        @type name:                     str
        @keyword default:               The default value of the argument.
        @type default:                  anything
        @keyword py_type:               The Python object type that the argument must match (taking the can_be_none flag into account).
        @type py_type:                  str
        @keyword arg_type:              The type of argument.  This is reserved for special UI elements:
                                            - 'file sel' will indicate to certain UIs that a file selection dialog is required.
                                            - 'dir' will cause the argument to not be shown in certain UIs, as this indicates that the user function already has a 'file sel' type argument and hence a directory is not required.
                                            - 'dir sel' will indicate to certain UIs that a dir selection dialog is required.
        @type arg_type:                 str
        @keyword size:                  The length that a list or tuple must conform to.
        @type size:                     int or None
        @keyword dim:                   The dimension that a matrix or list of lists must conform to.
        @type dim:                      tuple of int or None
        @keyword desc_short:            The short human-readable description of the argument.  This is used in the RelaxError messages to refer to the argument, as well as in the GUI user function page elements.
        @type desc_short:               str
        @keyword desc:                  The long human-readable description of the argument.
        @type desc:                     str
        @keyword list_titles:           The titles of each of the elements of the fixed width second dimension.  This only applies to list of lists.
        @type list_titles:              list of str
        @keyword wiz_element_type:      The type of GUI element to create.  If left to 'default', then the currently set default element will be used.  If set to 'text', a wx.TextCtrl element will be used.  If set to 'combo', a wx.ComboBox element will be used.
        @type wiz_element_type:         str
        @keyword wiz_combo_choices:     The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type wiz_combo_choices:        list of str
        @keyword wiz_combo_data:        The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type wiz_combo_data:           list
        @keyword wiz_combo_iter:        An iterator method for regenerating the ComboBox choices.
        @type wiz_combo_iter:           iterator or None
        @keyword wiz_combo_list_size:   An iterator method for regenerating the ComboBox choices.
        @type wiz_combo_list_size:      iterator or None
        @keyword wiz_read_only:         A flag which if True means that the text of the GUI wizard page element cannot be edited.  If the default of None is given, then each UI element will decide for itself what to do.
        @type wiz_read_only:            bool or None
        @keyword can_be_none:           A flag which specifies if the argument is allowed to have the None value.
        @type can_be_none:              bool
        @keyword can_be_empty:          A flag which if True allows the sequence type object to be empty.
        @type can_be_empty:             bool
        @keyword none_elements:         A flag which if True allows the sequence type object to contain None elements.
        @type none_elements:            bool
        """

        # Check that the args have been properly supplied.
        if name == None:
            raise RelaxError("The 'name' argument must be supplied.")
        if py_type == None:
            raise RelaxError("The 'py_type' argument must be supplied.")
        if desc_short == None:
            raise RelaxError("The 'desc_short' argument must be supplied.")
        if desc == None:
            raise RelaxError("The 'desc' argument must be supplied.")

        # Append a new argument dictionary to the list, and alias it.
        self.kargs.append({})
        arg = self.kargs[-1]

        # Add the data.
        arg['name'] = name
        arg['default'] = default
        arg['py_type'] = py_type
        arg['arg_type'] = arg_type
        arg['size'] = size
        arg['dim'] = dim
        arg['desc_short'] = desc_short
        arg['desc'] = desc
        arg['list_titles'] = list_titles
        arg['wiz_element_type'] = wiz_element_type
        arg['wiz_combo_choices'] = wiz_combo_choices
        arg['wiz_combo_data'] = wiz_combo_data
        arg['wiz_combo_iter'] = wiz_combo_iter
        arg['wiz_combo_list_size'] = wiz_combo_list_size
        arg['wiz_read_only'] = wiz_read_only
        arg['can_be_none'] = can_be_none
        arg['can_be_empty'] = can_be_empty
        arg['none_elements'] = none_elements
