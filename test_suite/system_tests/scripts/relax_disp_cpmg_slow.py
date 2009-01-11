# Script for CPMG relaxation dispersion curve fitting in the slow-exchange limit.

import sys


# Create the data pipe.
pipe.create('rex', 'relax_disp')

# The path to the data files.
data_path = sys.path[-1] + '/test_suite/shared_data/curve_fitting_disp/Hansen/500_MHz'

# Load the sequence.
sequence.read('fake_sequence.in', dir=sys.path[-1] + '/test_suite/shared_data/curve_fitting_disp/Hansen')

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Relaxation dispersion magnetic field (in Hz).
frq.set(id='500', frq=500.0 * 1e6)

# Spectrum names.
names = [
    'reference.in_sparky',
    '66.667.in_sparky',
    '1000.in_sparky',
    '133.33.in_sparky',
    '933.33.in_sparky',
    '200.in_sparky',
    '866.67.in_sparky',
    '266.67.in_sparky',
    '800.in_sparky',
    '333.33.in_sparky',
    '733.33.in_sparky',
    '400.in_sparky',
    '666.67.in_sparky',
    '466.67.in_sparky',
    '600.in_sparky',
    '533.33.in_sparky',
    '133.33.in.bis_sparky',
    '933.33.in.bis_sparky',
    '533.33.in.bis_sparky'
]

# Relaxation dispersion CPMG constant time delay T (in s).
relax_disp.cpmg_delayT(id='500', delayT=0.030)

# Relaxation dispersion CPMG frequencies (in Hz).
cpmg_frq = [
    None,
    66.667,
    1000,
    133.33,
    933.33,
    200,
    866.67,
    266.67,
    800,
    333.33,
    733.33,
    400,
    666.67,
    466.67,
    600,
    533.33,
    133.33,
    933.33,
    533.33
]

# Set the relaxation dispersion experiment type.
relax_disp.exp_type('cpmg')

# Set the relaxation dispersion curve type.
relax_disp.select_model('slow')

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i], dir=data_path, spectrum_id=names[i], int_method='height')

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.cpmg_frq(cpmg_frq=cpmg_frq[i], spectrum_id=names[i])

# Specify the duplicated spectra.
spectrum.replicated(spectrum_ids=['133.33.in_sparky', '133.33.in.bis_sparky'])
spectrum.replicated(spectrum_ids=['533.33.in_sparky', '533.33.in.bis_sparky'])
spectrum.replicated(spectrum_ids=['933.33.in_sparky', '933.33.in.bis_sparky'])

# Peak intensity error analysis.
spectrum.error_analysis()

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path)

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

# Save the relaxation dispersion parameters.
value.write(param='rex', file='devnull', force=True)

# Save the results.
results.write(file='devnull', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='devnull', force=True)    # Minimised chi-squared value.
grace.write(y_data_type='R2', file='devnull', force=True)    # R2 parameter without Rex contribution.
grace.write(y_data_type='Rex', file='devnull', force=True)    # Chemical exchange contribution to observed R2.
grace.write(y_data_type='kex', file='devnull', force=True)    # Exchange rate.
grace.write(x_data_type='frq', y_data_type='int', file='devnull', force=True)    # Average peak intensities.
grace.write(x_data_type='frq', y_data_type='int', norm=True, file='devnull', force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save('devnull', force=True)
