"""Script for testing the loading of phthalic acid NOEs from a generically formatted file."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Path of the relaxation data.
DATA_PATH = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep

# Pseudo-atoms.
PSEUDO = [
['Q7', ['@H16', '@H17', '@H18']],
['Q9', ['@H20', '@H21', '@H22']],
['Q10', ['@H23', '@H24', '@H25']]
]

# Read the structure.
structure.read_pdb('gromacs_phthalic_acid.pdb', dir=DATA_PATH+sep+'structures')

# Load all protons as the sequence.
structure.load_spins('@*H*', ave_pos=False)

# Create the pseudo-atoms.
for i in range(len(PSEUDO)):
    spin.create_pseudo(spin_name=PSEUDO[i][0], res_id=None, members=PSEUDO[i][1], averaging='linear')

# Read the NOE restraints.
noe.read_restraints(file=ds.file_name, dir=DATA_PATH+'noe_restraints')

# Set the type of N-state model.
n_state_model.select_model(model='fixed')

# Calculate the average NOE potential.
calc()


