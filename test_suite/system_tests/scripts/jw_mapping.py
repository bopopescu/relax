"""Script for jw_mapping testing."""

# Python module imports.
from os import devnull, sep
import sys

# Create the run.
name = 'jw_mapping'
pipe.create(name, 'jw')

# Load the sequence.
sequence.read(sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat')

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R1.dat')
relax_data.read('R2', '600', 600.0 * 1e6, sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R2.dat')
relax_data.read('NOE', '600', 600.0 * 1e6, sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat')

# Set the nuclei types
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Set the bond length and CSA values.
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')

# Set the frequency.
jw_mapping.set_frq(frq=600.0 * 1e6)

# Jw mapping.
calc()

# Monte Carlo simulations.
monte_carlo.setup(number=500)
monte_carlo.create_data()
calc()
monte_carlo.error_analysis()

# Create grace files.
grace.write(y_data_type='j0', file='devnull', force=True)
grace.write(y_data_type='jwx', file='devnull', force=True)
grace.write(y_data_type='jwh', file='devnull', force=True)

# Finish.
results.write(file='devnull', force=True)
state.save('devnull', force=True)
