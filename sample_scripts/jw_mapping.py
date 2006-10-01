# Script for reduced spectral density mapping.

# Create the run.
name = 'jw'
run.create(name, 'jw')

# Nuclei type
nuclei('N')

# Load the sequence.
sequence.read(name, 'noe.500.out')

# Load the relaxation data.
relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')

# Set the bond length and CSA values.
value.set(name, 1.02 * 1e-10, 'bond_length')
value.set(name, -172 * 1e-6, 'csa')

# Select the frequency.
jw_mapping.set_frq(name, frq=600.0 * 1e6)

# Reduced spectral density mapping.
calc(name)

# Monte Carlo simulations.
monte_carlo.setup(name, number=5000)
monte_carlo.create_data(name)
calc(name)
monte_carlo.error_analysis(name)

# Finish.
results.write(run=name, file='results', force=1)
state.save('save', force=1)
