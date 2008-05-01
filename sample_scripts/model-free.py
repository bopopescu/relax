###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# This script performs a model-free analysis for the single model 'm4'.
#######################################################################

# Create the run.
name = 'm4'
pipe.create(name, 'mf')

# Nuclei type
nuclei('N')

# Load the sequence.
sequence.read('noe.500.out')

# Load a PDB file.
#structure.read_pdb('example.pdb')

# Load the relaxation data.
relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out')
relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out')
relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out')
relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out')

# Setup other values.
diffusion_tensor.init(10e-9, fixed=True)
#diffusion_tensor.init((2e-8, 1.3, 60, 290), param_types=0, spheroid_type='prolate', fixed=True)
#diffusion_tensor.init((9e-8, 0.5, 0.3, 60, 290, 100), fixed=False)
value.set(1.02 * 1e-10, 'bond_length')
value.set(-172 * 1e-6, 'csa')
#value.set(1.0, 's2f')
#value.set(0.970, 's2')
#value.set(2048e-12, 'te')
#value.set(2048e-12, 'ts')
#value.set(2048e-12, 'tf')
#value.set(0.149/(2*pi*600e6)**2, 'rex')
value.set('15N', 'heteronucleus')
value.set('1H', 'proton')

# Select the model-free model.
model_free.select_model(model=name)
#model_free.create_model(model=name, equation='mf_ext2', params=['S2f', 'S2s', 'ts'])

# Fixed value.
#fix('all_res')

# Grid search.
grid_search(inc=11)
#value.set()

# Minimise.
minimise('newton')

# Monte Carlo simulations.
#monte_carlo.setup(number=100)
#monte_carlo.create_data()
#monte_carlo.initial_values()
#minimise('newton')
#eliminate()
#monte_carlo.error_analysis()

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
