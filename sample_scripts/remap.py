# Script for mapping the model-free space.

from Numeric import Float64, array

def remap(values):
    """Remapping function."""

    # S2f.
    s2f = values[0]

    # S2s.
    if values[0] == 0.0:
        s2s = 1e99
    else:
        s2s = values[1]*values[0]

    # ts.
    ts = values[2]

    return array([s2f, s2s, ts], Float64)


# Load the sequence.
read.sequence('noe.500.out')

# Set the run name (also the name of a preset model-free model).
name = 'm5'

# Load the relaxation data.
read.rx_data(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
read.rx_data(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
read.rx_data(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
read.rx_data(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
read.rx_data(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
read.rx_data(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

# Setup other values.
diffusion_tensor(name, 'iso', 1e-8)
value.set(name, 'bond_length', 1.02 * 1e-10)
value.set(name, 'csa', -160 * 1e-6)

# Select the model-free model.
model.select_mf(name, name)

# Map data.
inc = 10
lower = [0.5, 0.5, 0]
upper = [1.0, 1.0, 300e-12]
swap = [0, 2, 1]
point = [0.952, 0.582, 32.0e-12]
point = [point[0], point[0]*point[1], point[2]]

map(name, res_num=1, inc=inc, lower=lower, upper=upper, swap=swap, file='remap', point=point, remap=remap, labels=['S2f', 'S2s', 'ts'])
dx(file='remap')
