###############################################################################
#                                                                             #
# Copyright (C) 2019 Edward d'Auvergne                                        #
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
from copy import deepcopy

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from data_store.mol_res_spin import SpinContainer
from lib.dispersion.variables import MODEL_LIST_FULL, \
    MODEL_PARAMS, \
    MODEL_R2EFF, \
    MODEL_NOREX, \
    MODEL_LM63, \
    MODEL_LM63_3SITE, \
    MODEL_CR72, \
    MODEL_CR72_FULL, \
    MODEL_IT99, \
    MODEL_TSMFK01, \
    MODEL_B14, \
    MODEL_B14_FULL, \
    MODEL_M61, \
    MODEL_M61B, \
    MODEL_DPL94, \
    MODEL_TP02, \
    MODEL_TAP03, \
    MODEL_MP05, \
    MODEL_NS_CPMG_2SITE_3D, \
    MODEL_NS_CPMG_2SITE_3D_FULL, \
    MODEL_NS_CPMG_2SITE_STAR, \
    MODEL_NS_CPMG_2SITE_STAR_FULL, \
    MODEL_NS_CPMG_2SITE_EXPANDED, \
    MODEL_NS_R1RHO_2SITE, \
    MODEL_NS_R1RHO_3SITE, \
    MODEL_NS_R1RHO_3SITE_LINEAR, \
    MODEL_MMQ_CR72, \
    MODEL_NS_MMQ_2SITE, \
    MODEL_NS_MMQ_3SITE, \
    MODEL_NS_MMQ_3SITE_LINEAR, \
    MODEL_EXP_TYPE_R2EFF, \
    MODEL_EXP_TYPE_NOREX, \
    MODEL_EXP_TYPE_LM63, \
    MODEL_EXP_TYPE_LM63_3SITE, \
    MODEL_EXP_TYPE_CR72, \
    MODEL_EXP_TYPE_CR72_FULL, \
    MODEL_EXP_TYPE_TSMFK01, \
    MODEL_EXP_TYPE_TSMFK01, \
    MODEL_EXP_TYPE_B14, \
    MODEL_EXP_TYPE_B14_FULL, \
    MODEL_EXP_TYPE_M61, \
    MODEL_EXP_TYPE_M61B, \
    MODEL_EXP_TYPE_DPL94, \
    MODEL_EXP_TYPE_TP02, \
    MODEL_EXP_TYPE_TAP03, \
    MODEL_EXP_TYPE_MP05, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_3D, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_3D_FULL, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR_FULL, \
    MODEL_EXP_TYPE_NS_CPMG_2SITE_EXPANDED, \
    MODEL_EXP_TYPE_NS_R1RHO_2SITE, \
    MODEL_EXP_TYPE_NS_R1RHO_3SITE, \
    MODEL_EXP_TYPE_NS_R1RHO_3SITE_LINEAR, \
    MODEL_EXP_TYPE_MMQ_CR72, \
    MODEL_EXP_TYPE_NS_MMQ_2SITE, \
    MODEL_EXP_TYPE_NS_MMQ_3SITE, \
    MODEL_EXP_TYPE_NS_MMQ_3SITE_LINEAR
from specific_analyses.relax_disp.parameters import loop_parameters, param_num
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_parameters(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.parameters module."""

    def setUp(self):
        """Setup some structures for the unit tests."""

        # Create a dispersion data pipe.
        ds.add(pipe_name='testing', pipe_type='relax_disp')

        # The experiment types for all models.
        self.exp_type = {
            MODEL_R2EFF: MODEL_EXP_TYPE_R2EFF,
            MODEL_NOREX: MODEL_EXP_TYPE_NOREX,
            MODEL_LM63: MODEL_EXP_TYPE_LM63,
            MODEL_LM63_3SITE: MODEL_EXP_TYPE_LM63_3SITE,
            MODEL_CR72: MODEL_EXP_TYPE_CR72,
            MODEL_CR72_FULL: MODEL_EXP_TYPE_CR72_FULL,
            MODEL_IT99: MODEL_EXP_TYPE_TSMFK01,
            MODEL_TSMFK01: MODEL_EXP_TYPE_TSMFK01,
            MODEL_B14: MODEL_EXP_TYPE_B14,
            MODEL_B14_FULL: MODEL_EXP_TYPE_B14_FULL,
            MODEL_M61: MODEL_EXP_TYPE_M61,
            MODEL_M61B: MODEL_EXP_TYPE_M61B,
            MODEL_DPL94: MODEL_EXP_TYPE_DPL94,
            MODEL_TP02: MODEL_EXP_TYPE_TP02,
            MODEL_TAP03: MODEL_EXP_TYPE_TAP03,
            MODEL_MP05: MODEL_EXP_TYPE_MP05,
            MODEL_NS_CPMG_2SITE_3D: MODEL_EXP_TYPE_NS_CPMG_2SITE_3D,
            MODEL_NS_CPMG_2SITE_3D_FULL: MODEL_EXP_TYPE_NS_CPMG_2SITE_3D_FULL,
            MODEL_NS_CPMG_2SITE_STAR: MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR,
            MODEL_NS_CPMG_2SITE_STAR_FULL: MODEL_EXP_TYPE_NS_CPMG_2SITE_STAR_FULL,
            MODEL_NS_CPMG_2SITE_EXPANDED: MODEL_EXP_TYPE_NS_CPMG_2SITE_EXPANDED,
            MODEL_NS_R1RHO_2SITE: MODEL_EXP_TYPE_NS_R1RHO_2SITE,
            MODEL_NS_R1RHO_3SITE: MODEL_EXP_TYPE_NS_R1RHO_3SITE,
            MODEL_NS_R1RHO_3SITE_LINEAR: MODEL_EXP_TYPE_NS_R1RHO_3SITE_LINEAR,
            MODEL_MMQ_CR72: MODEL_EXP_TYPE_MMQ_CR72,
            MODEL_NS_MMQ_2SITE: MODEL_EXP_TYPE_NS_MMQ_2SITE,
            MODEL_NS_MMQ_3SITE: MODEL_EXP_TYPE_NS_MMQ_3SITE,
            MODEL_NS_MMQ_3SITE_LINEAR: MODEL_EXP_TYPE_NS_MMQ_3SITE_LINEAR
        }


    def test_loop_parameters_clustered_spins(self):
        """Test the specific_analyses.relax_disp.parameters.loop_parameters() function for a cluster of 2 spins."""

        # The expected parameter information.
        expected = {
            MODEL_R2EFF: [
                ['r2eff', 0, None],
                ['r2eff', 1, None],
            ],
            MODEL_NOREX: [
                ['r2', 0, 'No Rex - 1.00000000 MHz'],
                ['r2', 1, 'No Rex - 1.00000000 MHz'],
            ],
            MODEL_LM63: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['phi_ex', 1, None],
                ['kex', None, None],
            ],
            MODEL_LM63_3SITE: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex_B', 0, None],
                ['phi_ex_C', 0, None],
                ['phi_ex_B', 1, None],
                ['phi_ex_C', 1, None],
                ['kB', None, None],
                ['kC', None, None],
            ],
            MODEL_CR72: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_CR72_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_IT99: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['tex', None, None],
            ],
            MODEL_TSMFK01: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['k_AB', None, None],
            ],
            MODEL_B14: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_B14_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_M61: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['phi_ex', 1, None],
                ['kex', None, None],
            ],
            MODEL_M61B: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_DPL94: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['phi_ex', 1, None],
                ['kex', None, None],
            ],
            MODEL_TP02: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_TAP03: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_MP05: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2a', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_EXPANDED: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2', 1, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_2SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_3SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_R1RHO_3SITE_LINEAR: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['r2', 1, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
            MODEL_MMQ_CR72: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['dwH', 0, None],
                ['dwH', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_2SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dw', 1, None],
                ['dwH', 0, None],
                ['dwH', 1, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_3SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['dwH_AB', 1, None],
                ['dwH_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_MMQ_3SITE_LINEAR: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['r2', 1, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dw_AB', 1, None],
                ['dw_BC', 1, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['dwH_AB', 1, None],
                ['dwH_BC', 1, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
        }

        # Loop over all models.
        print("Checking the parameter looping for a cluster of 2 spins.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spins = [SpinContainer(), SpinContainer()]
            for spin in spins:
                spin.model = model
                spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter loop.
            i = 0
            for name, param_index, spin_index, R20_key in loop_parameters(spins):
                print("        Parameter '%s', %s, %s, %s." % (name, param_index, spin_index, repr(R20_key)))
                self.assertEqual(name, expected[model][i][0])
                self.assertEqual(spin_index, expected[model][i][1])
                self.assertEqual(R20_key, expected[model][i][2])
                i += 1

            # Parameter count check.
            self.assertEqual(i, len(expected[model]))


    def test_loop_parameters_single_spin(self):
        """Test the specific_analyses.relax_disp.parameters.loop_parameters() function for a single spin."""

        # The expected parameter information.
        expected = {
            MODEL_R2EFF: [
                ['r2eff', 0, None],
            ],
            MODEL_NOREX: [
                ['r2', 0, 'No Rex - 1.00000000 MHz'],
            ],
            MODEL_LM63: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['kex', None, None],
            ],
            MODEL_LM63_3SITE: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['phi_ex_B', 0, None],
                ['phi_ex_C', 0, None],
                ['kB', None, None],
                ['kC', None, None],
            ],
            MODEL_CR72: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_CR72_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_IT99: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['tex', None, None],
            ],
            MODEL_TSMFK01: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['k_AB', None, None],
            ],
            MODEL_B14: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_B14_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_M61: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['kex', None, None],
            ],
            MODEL_M61B: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_DPL94: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['phi_ex', 0, None],
                ['kex', None, None],
            ],
            MODEL_TP02: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_TAP03: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_MP05: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_3D_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_STAR_FULL: [
                ['r2a', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['r2b', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_CPMG_2SITE_EXPANDED: [
                ['r2', 0, 'SQ CPMG - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_2SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_R1RHO_3SITE: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_R1RHO_3SITE_LINEAR: [
                ['r2', 0, 'R1rho - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
            MODEL_MMQ_CR72: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dwH', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_2SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw', 0, None],
                ['dwH', 0, None],
                ['pA', None, None],
                ['kex', None, None],
            ],
            MODEL_NS_MMQ_3SITE: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
                ['kex_AC', None, None],
            ],
            MODEL_NS_MMQ_3SITE_LINEAR: [
                ['r2', 0, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ - 1.00000000 MHz'],
                ['dw_AB', 0, None],
                ['dw_BC', 0, None],
                ['dwH_AB', 0, None],
                ['dwH_BC', 0, None],
                ['pA', None, None],
                ['kex_AB', None, None],
                ['pB', None, None],
                ['kex_BC', None, None],
            ],
        }

        # Loop over all models.
        print("Checking the parameter looping for a single spin.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            cdp.spectrometer_frq_list = [1e6]
            spin = SpinContainer()
            spin.model = model
            spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter loop.
            i = 0
            for name, param_index, spin_index, R20_key in loop_parameters([spin]):
                print("        Parameter '%s', %s, %s, %s." % (name, param_index, spin_index, repr(R20_key)))
                self.assertEqual(name, expected[model][i][0])
                self.assertEqual(spin_index, expected[model][i][1])
                self.assertEqual(R20_key, expected[model][i][2])
                i += 1

            # Parameter count check.
            self.assertEqual(i, len(expected[model]))


    def test_param_num_clustered_spins(self):
        """Test the specific_analyses.relax_disp.parameters.param_num() function for a cluster of 2 spins."""

        # The expected number of parameters for the single spin.
        expected = {
            MODEL_R2EFF: 2,
            MODEL_NOREX: 2,
            MODEL_LM63: 5,
            MODEL_LM63_3SITE: 8,
            MODEL_CR72: 6,
            MODEL_CR72_FULL: 8,
            MODEL_IT99: 6,
            MODEL_TSMFK01: 5,
            MODEL_B14: 6,
            MODEL_B14_FULL: 8,
            MODEL_M61: 5,
            MODEL_M61B: 6,
            MODEL_DPL94: 5,
            MODEL_TP02: 6,
            MODEL_TAP03: 6,
            MODEL_MP05: 6,
            MODEL_NS_CPMG_2SITE_3D: 6,
            MODEL_NS_CPMG_2SITE_3D_FULL: 8,
            MODEL_NS_CPMG_2SITE_STAR: 6,
            MODEL_NS_CPMG_2SITE_STAR_FULL: 8,
            MODEL_NS_CPMG_2SITE_EXPANDED: 6,
            MODEL_NS_R1RHO_2SITE: 6,
            MODEL_NS_R1RHO_3SITE: 11,
            MODEL_NS_R1RHO_3SITE_LINEAR: 10,
            MODEL_MMQ_CR72: 8,
            MODEL_NS_MMQ_2SITE: 8,
            MODEL_NS_MMQ_3SITE: 15,
            MODEL_NS_MMQ_3SITE_LINEAR: 14
        }

        # Loop over all models.
        print("Checking the parameter number counts for a cluster of 2 spins.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            spins = [SpinContainer(), SpinContainer()]
            for spin in spins:
                spin.model = model
                spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter number.
            self.assertEqual(param_num(spins), expected[model])


    def test_param_num_single_spin(self):
        """Test the specific_analyses.relax_disp.parameters.param_num() function for a single spin."""

        # The expected number of parameters for the single spin.
        expected = {
            MODEL_R2EFF: 1,
            MODEL_NOREX: 1,
            MODEL_LM63: 3,
            MODEL_LM63_3SITE: 5,
            MODEL_CR72: 4,
            MODEL_CR72_FULL: 5,
            MODEL_IT99: 4,
            MODEL_TSMFK01: 3,
            MODEL_B14: 4,
            MODEL_B14_FULL: 5,
            MODEL_M61: 3,
            MODEL_M61B: 4,
            MODEL_DPL94: 3,
            MODEL_TP02: 4,
            MODEL_TAP03: 4,
            MODEL_MP05: 4,
            MODEL_NS_CPMG_2SITE_3D: 4,
            MODEL_NS_CPMG_2SITE_3D_FULL: 5,
            MODEL_NS_CPMG_2SITE_STAR: 4,
            MODEL_NS_CPMG_2SITE_STAR_FULL: 5,
            MODEL_NS_CPMG_2SITE_EXPANDED: 4,
            MODEL_NS_R1RHO_2SITE: 4,
            MODEL_NS_R1RHO_3SITE: 8,
            MODEL_NS_R1RHO_3SITE_LINEAR: 7,
            MODEL_MMQ_CR72: 5,
            MODEL_NS_MMQ_2SITE: 5,
            MODEL_NS_MMQ_3SITE: 10,
            MODEL_NS_MMQ_3SITE_LINEAR: 9
        }

        # Loop over all models.
        print("Checking the parameter number counts for a single spin.")
        for model in MODEL_LIST_FULL:
            # Sanity check.
            if model not in expected:
                raise RelaxError("The model '%s' is not being checked." % model)

            # Printout.
            print("    Model '%s'." % model)

            # Set up the data store.
            ds.add(pipe_name=model, pipe_type='relax_disp')
            if model == MODEL_R2EFF:
                cdp.model_type = 'R2eff'
            else:
                cdp.model_type = 'disp'
            cdp.exp_type_list = [self.exp_type[model]]
            spin = SpinContainer()
            spin.model = model
            spin.params = deepcopy(MODEL_PARAMS[model])

            # Check the parameter number.
            self.assertEqual(param_num([spin]), expected[model])
