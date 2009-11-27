# Python module imports.
from os import sep
import sys


# Create the data pipe.
pipe.create(pipe_name='rigid', pipe_type='frame order')

# Load the tensors.
script(sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors_rigid_rand_rot.py')

# The tensor reductions.
for i in range(10):
    align_tensor.reduction(full_tensor='a '+repr(i), red_tensor='b '+repr(i))

# Select the model.
frame_order.select_model('rigid')

# Set the reference domain.
frame_order.ref_domain('a')

# Optimise.
grid_search(inc=6)
minimise('simplex', constraints=False)

# Write the results.
results.write('devnull', dir=None, force=True)
