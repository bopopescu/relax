###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Python module imports.
from numpy import array, float64, ones, pi, zeros
from unittest import TestCase

# relax module imports.
from lib.dispersion.tsmfk01 import r2eff_TSMFK01


class Test_tsmfk01(TestCase):
    """Unit tests for the lib.dispersion.tsmfk01 relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # Default parameter values.
        self.r20a = 2.0
        self.pA = 0.95
        self.dw = 2.0
        self.kex = 1000.0

        # Required data structures.
        self.num_points = 7
        self.ncyc = array([2, 4, 8, 10, 20, 40, 500])
        relax_times = 0.04
        self.cpmg_frqs = self.ncyc / relax_times
        self.tau_cpmg = 0.25 / self.cpmg_frqs
        self.R2eff = zeros(self.num_points, float64)

        # The spin Larmor frequencies.
        self.sfrq = 200. * 1E6


    def calc_r2eff(self):
        """Calculate and check the R2eff values."""

        # Parameter conversions.
        k_AB, k_BA, pB, dw_frq = self.param_conversion(pA=self.pA, kex=self.kex, dw=self.dw, sfrq=self.sfrq)

        a = ones([self.num_points])

        # Calculate the R2eff values.
        r2eff_TSMFK01(r20a=self.r20a*a, dw=dw_frq*a, dw_orig=dw_frq, k_AB=k_AB, tcp=self.cpmg_frqs, back_calc=self.R2eff)

        # Check all R2eff values.
        for i in range(self.num_points):
            self.assertAlmostEqual(self.R2eff[i], self.r20a)


    def param_conversion(self, pA=None, kex=None, dw=None, sfrq=None):
        """Convert the parameters.

        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @keyword dw:    The chemical exchange difference between states A and B in ppm.
        @type dw:       float
        @keyword sfrq:  The spin Larmor frequencies in Hz.
        @type sfrq:     float
        @return:        The parameters {k_AB, k_BA, pB, dw_frq}.
        @rtype:         tuple of float
        """

        # Calculate pB.
        pB = 1.0 - pA

        # Exchange rates.
        k_BA = pA * kex
        k_AB = pB * kex

        # Calculate spin Larmor frequencies in 2pi.
        frqs = sfrq * 2 * pi

        # Convert dw from ppm to rad/s.
        dw_frq = dw * frqs / 1.e6

        # Return all values.
        return k_AB, k_BA, pB, dw_frq


    def test_tsmfk01_no_rex1(self):
        """Test the r2eff_tsmfk01() function for no exchange when dw = 0.0."""

        # Parameter reset.
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_tsmfk01_no_rex2(self):
        """Test the r2eff_tsmfk01() function for no exchange when pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_tsmfk01_no_rex3(self):
        """Test the r2eff_tsmfk01() function for no exchange when kex = 0.0."""

        # Parameter reset.
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_tsmfk01_no_rex4(self):
        """Test the r2eff_tsmfk01() function for no exchange when dw = 0.0 and pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_tsmfk01_no_rex5(self):
        """Test the r2eff_tsmfk01() function for no exchange when dw = 0.0 and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_tsmfk01_no_rex6(self):
        """Test the r2eff_tsmfk01() function for no exchange when pA = 1.0 and kex = 0.0."""

        # Parameter reset.
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_tsmfk01_no_rex7(self):
        """Test the r2eff_tsmfk01() function for no exchange when dw = 0.0, pA = 1.0, and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()

