###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Michael Bieri                                       #
# Copyright (C) 2009-2011,2019 Edward d'Auvergne                              #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the main relax menu bar."""

# Python module imports.
import wx

# relax module imports.
import dep_check


def build_menu_item(menu, parent=None, id=-1, text='', tooltip='', icon=None, fn=None, append=True):
    """Construct and return the menu sub-item.

    @param menu:        The menu object to place this entry in.
    @type menu:         wx.Menu instance
    @keyword id:        The element identification number.
    @type id:           int
    @keyword text:      The text for the menu entry.
    @type text:         None or str
    @keyword tooltip:   A tool tip.
    @type tooltip:      str
    @keyword icon:      The bitmap icon path.
    @type icon:         None or str
    @keyword fn:        The function to bind to the menu entry.
    @type fn:           class method
    @keyword append:    A flag which if true will cause the element to be appended to the given menu.
    @type append:       bool
    @return:            The initialised wx.MenuItem() instance.
    @rtype:             wx.MenuItem() instance
    """

    # Initialise the GUI element.
    element = wx.MenuItem(menu, id, text, tooltip)

    # Set the icon.
    if icon:
        element.SetBitmap(wx.Bitmap(icon))

    # Bind the menu entry.
    if fn and parent:
        parent.Bind(wx.EVT_MENU, fn, id=id)

    # Append the item.
    if append:
        if dep_check.old_wx:
             menu.AppendItem(element)
        else:
             menu.Append(element)

    # Return the element.
    return element
