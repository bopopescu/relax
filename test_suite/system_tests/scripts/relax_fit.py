# Script for relaxation curve fitting.

import sys


# Create the data pipe.
pipe.create('rx', 'relax_fit')

# The path to the data files.
data_path = sys.path[-1] + '/test_suite/shared_data/curve_fitting'

# Load the sequence.
sequence.read('Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/shared_data')

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Spectrum names.
names = [
    'T2_ncyc1_ave',
    'T2_ncyc1b_ave',
    'T2_ncyc2_ave',
    'T2_ncyc4_ave',
    'T2_ncyc4b_ave',
    'T2_ncyc6_ave',
    'T2_ncyc9_ave',
    'T2_ncyc9b_ave',
    'T2_ncyc11_ave',
    'T2_ncyc11b_ave'
]

# Relaxation times (in seconds).
times = [
    0.0176,
    0.0176,
    0.0352,
    0.0704,
    0.0704,
    0.1056,
    0.1584,
    0.1584,
    0.1936,
    0.1936
]

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method='heights')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path)

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=10)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='devnull', force=True)

# Save the results.
results.write(file='devnull', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='devnull', force=True)    # Minimised chi-squared value.
grace.write(y_data_type='i0', file='devnull', force=True)    # Initial peak intensity.
grace.write(y_data_type='rx', file='devnull', force=True)    # Relaxation rate.
grace.write(x_data_type='relax_times', y_data_type='ave_int', file='devnull', force=True)    # Average peak intensities.
grace.write(x_data_type='relax_times', y_data_type='ave_int', norm=True, file='devnull', force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save(file='devnull', force=True)
