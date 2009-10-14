# Script for testing the reading and writing of BMRB files.

# Python module imports.
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Missing temp file (allow this script to run outside of the system test framework).
state_file = 'devnull'
if not hasattr(ds, 'tmpfile'):
    stand_alone = True
    ds.tmpfile = 'temp_bmrb'
    ds.version = '3.2'
    state_file = 'temp_bmrb_state'

# Create the data pipe.
pipe.create(pipe_name='results', pipe_type='mf')

# Read the results.
results.read(file='final_results_trunc_1.3', dir=sys.path[-1] + '/test_suite/shared_data/model_free/OMP')

# Play with the data.
deselect.all()
spin.copy(spin_from=':9', spin_to=':9@NE')
select.spin(':9')
select.spin(':10')
select.spin(':11')
spin.name(name='N')
molecule.name(name='OMP')

# Display the data (as a test).
relax_data.display(ri_label='R1', frq_label='800')

# Temperature control.
ri_labels = ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
frq_labels = ['600', '600', '600', '800', '800', '800']
for i in range(6):
    relax_data.temp_calibration(ri_label=ri_labels[i], frq_label=frq_labels[i], method='methanol')
    relax_data.temp_control(ri_label=ri_labels[i], frq_label=frq_labels[i], method='single fid interleaving')

# Set up some BMRB information.
bmrb.software_select('NMRPipe')
bmrb.software_select('Sparky', version='3.106')
bmrb.citation(cite_id='test', authors=[["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]], doi="10.1039/b702202f", pubmed_id="17579774", full_citation="d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494.", title="Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm.", status="published", type="journal", journal_abbrev="Mol. Biosyst.", journal_full="Molecular Biosystems", volume=3, issue=7, page_first=483, page_last=498, year=2007)
bmrb.software(name='X', url='http://nmr-relax.com', vendor_name='me', cite_ids=['test'], tasks=['procrastinating', 'nothing much', 'wasting time'])

# Write, then read the data to a new data pipe.
bmrb.write(file=ds.tmpfile, dir=None, version=ds.version, force=True)
pipe.create(pipe_name='new', pipe_type='mf')
bmrb.read(file=ds.tmpfile, version=ds.version)

# Display tests.
sequence.display()
relax_data.display(ri_label='R1', frq_label='800')

# Save the program state.
state.save(state_file, force=True)
