###############################################################################
#                                                                             #
# Copyright (C) 2006 Chris MacRaild                                           #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from generic_fns.selection import residue_loop
from physical_constants import N15_CSA, NH_BOND_LENGTH


class Jw(TestCase):
    """Class for testing various aspects specific to reduced spectral density mapping."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('jw', 'jw')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_calc(self):
        """The spectral density calculation test."""

        # Data directory.
        dir = sys.path[-1] + '/test_suite/system_tests/data/jw_mapping/'

        # Data paths.
        dataPaths = [dir + 'noe.dat',
                     dir + 'R1.dat',
                     dir + 'R2.dat']

        # Data types.
        dataTypes = [('NOE', '600', 600.0e6),
                     ('R1', '600', 600.0e6),
                     ('R2', '600', 600.0e6)]

        # Correct jw values:
        j0 = [4.0703318681008998e-09, 3.7739393907014834e-09]
        jwx = [1.8456254300773903e-10, 1.6347516082378241e-10]
        jwh = [1.5598167512718012e-12, 2.9480536599037041e-12]

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='test_seq', dir=sys.path[-1] + '/test_suite/system_tests/data')

        # Read the data.
        for dataSet in xrange(len(dataPaths)):
            self.relax.interpreter._Relax_data.read(dataTypes[dataSet][0], dataTypes[dataSet][1], dataTypes[dataSet][2], dataPaths[dataSet])

        # Set r, csa, and the heteronucleus type.
        self.relax.interpreter._Value.set(NH_BOND_LENGTH, 'bond_length')
        self.relax.interpreter._Value.set(N15_CSA, 'csa')
        self.relax.interpreter._Value.set('15N', 'heteronucleus')

        # Select the frequency.
        self.relax.interpreter._Jw_mapping.set_frq(frq=600.0 * 1e6)

        # Try the reduced spectral density mapping.
        self.relax.interpreter._Minimisation.calc()

        # Loop over residues.
        for res in residue_loop():
            # Residues -2 and -1 have data.
            if res.num == -2 or res.num == -1:
                self.assert_(res.spin[0].select)
                self.assertAlmostEqual(res.spin[0].j0, j0[index])
                self.assertAlmostEqual(res.spin[0].jwh, jwh[index])
                self.assertAlmostEqual(res.spin[0].jwx, jwx[index])

            # Other residues have insufficient data.
            else:
                self.assert_(not res.spin[0].select)


    def test_set_value(self):
        """The user function value.set()."""

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='test_seq', dir=sys.path[-1] + '/test_suite/system_tests/data')

        # Try to set the values.
        bond_length = NH_BOND_LENGTH
        csa = N15_CSA
        self.relax.interpreter._Value.set(bond_length, 'bond_length')
        self.relax.interpreter._Value.set(csa, 'csa')

        # Loop over residues.
        for res in residue_loop():
            self.assertEqual(res.spin[0].r, NH_BOND_LENGTH)
            self.assertEqual(res.spin[0].csa, N15_CSA)
