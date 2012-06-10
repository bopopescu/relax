"""Script for testing the Monte Carlo simulations of fitting an alignment tensor to RDCs and PCSs."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'monte_carlo_testing'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'sphere'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='MC test', pipe_type='N-state')

# Load the test structure.
self._execute_uf(uf_name='structure.read_pdb', file='sphere', dir=STRUCT_PATH)

# Load the spins.
self._execute_uf(uf_name='structure.load_spins')

# Load the NH vectors.
self._execute_uf(uf_name='structure.vectors', spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
self._execute_uf(uf_name='value.set', val=1.041 * 1e-10, param='r', spin_id="@N")
self._execute_uf(uf_name='value.set', val='15N', param='heteronuc_type', spin_id="@N")
self._execute_uf(uf_name='value.set', val='1H', param='proton_type', spin_id="@N")

# RDCs.
self._execute_uf(uf_name='rdc.read', align_id='synth', file='synth_rdc', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# PCSs.
self._execute_uf(uf_name='pcs.read', align_id='synth', file='synth_pcs', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Set the paramagnetic centre.
self._execute_uf(uf_name='paramag.centre', pos=[10.0, 0.0, 0.0])

# The temperature.
self._execute_uf(uf_name='temperature', id='synth', temp=303)

# The frequency.
self._execute_uf(uf_name='frq.set', id='synth', frq=600.0 * 1e6)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='grid_search', inc=3)
self._execute_uf(uf_name='minimise', min_algor='simplex', constraints=False, max_iter=500)

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=3)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='monte_carlo.initial_values')
self._execute_uf(uf_name='minimise', min_algor='simplex', constraints=False, max_iter=500)
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Write out a results file.
self._execute_uf(uf_name='results.write', file='devnull', force=True)

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
print((cdp.align_tensors[0]))
