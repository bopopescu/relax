###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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
from os import sep
from shutil import rmtree
from string import split
import sys
from tempfile import mkdtemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_index_loop, spin_loop
from generic_fns import pipes


class Relax_fit(SystemTestCase):
    """Class for testing various aspects specific to relaxation curve-fitting."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir


    def tearDown(self):
        """Reset the relax data storage object."""

        # Remove the temporary directory.
        rmtree(self.tmpdir)

        # Reset the relax data storage object.
        ds.__reset__()


    def test_bug_12670_12679(self):
        """Test the relaxation curve fitting, replicating bug #12670 and bug #12679."""

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'1UBQ_relax_fit.py')

        # Open the intensities.agr file.
        file = open(ds.tmpdir + sep + 'intensities.agr')
        lines = file.readlines()
        file.close()

        # Split up the lines.
        for i in xrange(len(lines)):
            lines[i] = split(lines[i])

        # Check some of the Grace data.
        self.assertEqual(len(lines[23]), 2)
        self.assertEqual(lines[23][0], '0.004')
        self.assertEqual(lines[23][1], '487178.0')


    def test_curve_fitting(self):
        """Test the relaxation curve fitting C modules."""

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'relax_fit.py')

        # Data.
        relax_times = [0.0176, 0.0176, 0.0352, 0.0704, 0.0704, 0.1056, 0.1584, 0.1584, 0.1936, 0.1936]
        chi2 = [None, None, None, 3.1727215308183405, 5.9732236976178248, 17.633333237460601, 4.7413502242106036, 10.759950979457724, None, None, None, 6.5520255580798752]
        rx = [None, None, None, 8.0814894819861891, 8.6478971007171523, 9.5710638143380482, 10.716551832690667, 11.143793929315777, None, None, None, 12.828753698718391]
        i0 = [None, None, None, 1996050.9679873895, 2068490.9458262245, 1611556.5193290685, 1362887.2329727132, 1877670.5629299041, None, None, None, 897044.17270784755]

        # Some checks.
        self.assertEqual(cdp.curve_type, 'exp')
        self.assertEqual(cdp.int_method, 'height')
        self.assertEqual(len(cdp.relax_times), 10)
        for i in range(10):
            self.assertEqual(cdp.relax_times[i], relax_times[i])

        # Spin data check.
        i = 0
        for spin in spin_loop():
            # No data present.
            if chi2[i] == None:
                self.assert_(not hasattr(spin, 'chi2'))

            # Data present.
            else:
                self.assertAlmostEqual(spin.chi2, chi2[i])
                self.assertAlmostEqual(spin.rx, rx[i])
                self.assertAlmostEqual(spin.i0/1e6, i0[i]/1e6)

            # Increment the spin index.
            i = i + 1
            if i >= 12:
                break


    def test_read_sparky(self):
        """The Sparky peak height loading test."""

        # Load the original state.
        self.relax.interpreter._State.load(state='basic_heights_T2_ncyc1', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'saved_states', force=True)

        # Create a new data pipe for the new data.
        self.relax.interpreter._Pipe.create('new', 'relax_fit')

        # Load the Lupin Ap4Aase sequence.
        self.relax.interpreter._Sequence.read(file="Ap4Aase.seq", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

        # Name the spins so they can be matched to the assignments.
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak heights.
        self.relax.interpreter._Spectrum.read_intensities(file="T2_ncyc1_ave.list", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting', spectrum_id='0.0176')


        # Test the integrity of the data.
        #################################

        # Get the data pipes.
        dp_new = pipes.get_pipe('new')
        dp_rx = pipes.get_pipe('rx')

        # Loop over the spins of the original data.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            new_spin = dp_new.mol[mol_index].res[res_index].spin[spin_index]
            orig_spin = dp_rx.mol[mol_index].res[res_index].spin[spin_index]

            # Check the sequence info.
            self.assertEqual(dp_new.mol[mol_index].name, dp_rx.mol[mol_index].name)
            self.assertEqual(dp_new.mol[mol_index].res[res_index].num, dp_rx.mol[mol_index].res[res_index].num)
            self.assertEqual(dp_new.mol[mol_index].res[res_index].name, dp_rx.mol[mol_index].res[res_index].name)
            self.assertEqual(new_spin.num, orig_spin.num)
            self.assertEqual(new_spin.name, orig_spin.name)

            # Skip deselected spins.
            if not orig_spin.select:
                continue

            # Check intensities (if they exist).
            if hasattr(orig_spin, 'intensities'):
                self.assertEqual(orig_spin.intensities[0], new_spin.intensities[0])
