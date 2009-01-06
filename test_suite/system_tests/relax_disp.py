###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin
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
from shutil import rmtree
import sys
from tempfile import mkdtemp
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


class Relax_disp(TestCase):
    """Class for testing various aspects specific to relaxation dispersion curve-fitting."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('relax_disp', 'relax_disp')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(self.tmpdir)

        # Reset the relax data storage object.
        ds.__reset__()


#    def test_curve_fitting(self):
#        """Test the relaxation dispersion curve fitting C modules."""
#
#        # Execute the script.
#        self.relax.interpreter.run(script_file=sys.path[-1] + '/test_suite/system_tests/scripts/relax_disp.py')
