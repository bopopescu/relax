###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module containing the class for threaded and non-threaded analysis execution."""


# Python module imports.
from threading import Thread



class Execute(Thread):
    """The analysis execution object."""

    def __init__(self, gui, data, data_index, thread=True):
        """Set up the NOE analysis execution object.

        @param gui:         The GUI object.
        @type gui:          wx object
        @param data:        The data container with all data for the analysis.
        @type data:         class instance
        @param data_index:  The index of the analysis in the relax data store.
        @type data_index:   int
        @keyword thread:    The flag for turning threading on and off.
        @type thread:       bool
        """

        # Store the args.
        self.gui = gui
        self.data = data
        self.data_index = data_index

        # Threaded execution.
        if thread:
            # Set up the thread object.
            Thread.__init__(self)

        # No treaded execution.
        else:
            # Alias the start method.
            self.start = self._start


    def _start(self):
        """Replacement start() method for when execution is not threaded."""

        # Execute the run() method.
        self.run()
