###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
"""Script for testing the Monte Carlo simulations of fitting an alignment tensor to RDCs and PCSs."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'monte_carlo_testing'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'sphere'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='MC test', pipe_type='N-state')

# Load the test structure.
self._execute_uf(uf_name='structure.read_pdb', file='sphere', dir=STRUCT_PATH)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins', spin_id='@N')
self._execute_uf(uf_name='structure.load_spins', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
self._execute_uf(uf_name='interatom.unit_vectors', ave=False)

# Set the nuclear isotope.
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# RDCs.
self._execute_uf(uf_name='rdc.read', align_id='synth', file='synth_rdc', dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

# PCSs.
self._execute_uf(uf_name='pcs.read', align_id='synth', file='synth_pcs', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Set the paramagnetic centre.
self._execute_uf(uf_name='paramag.centre', pos=[10.0, 0.0, 0.0])

# The temperature.
self._execute_uf(uf_name='spectrometer.temperature', id='synth', temp=303)

# The frequency.
self._execute_uf(uf_name='spectrometer.frequency', id='synth', frq=600.0 * 1e6)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='minimise.grid_search', inc=3)
self._execute_uf(uf_name='minimise.execute', min_algor='simplex', constraints=False, max_iter=500)

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=3)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='monte_carlo.initial_values')
self._execute_uf(uf_name='minimise.execute', min_algor='simplex', constraints=False, max_iter=500)
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Write out a results file.
self._execute_uf(uf_name='results.write', file='devnull', force=True)

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
print(cdp.align_tensors[0])
