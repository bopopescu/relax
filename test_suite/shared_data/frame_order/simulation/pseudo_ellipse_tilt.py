###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from numpy import array, eye, float64, zeros


# The pivot and atomic coordinates.
pivot = array([1, 1, 1], float64)
atom_pos = 100*eye(3)
centre = zeros(3, float64)

# Create the data pipe.
pipe.create(pipe_name='frame order', pipe_type='frame order')

# Create a single atom structure.
structure.add_atom(mol_name='axes', atom_name='N', res_name='X', res_num=1, pos=atom_pos[0], element='N')
structure.add_atom(mol_name='axes', atom_name='N', res_name='Y', res_num=2, pos=atom_pos[1], element='N')
structure.add_atom(mol_name='axes', atom_name='N', res_name='Z', res_num=3, pos=atom_pos[2], element='N')
structure.add_atom(mol_name='axes', atom_name='N', res_name='nX', res_num=4, pos=-atom_pos[0], element='N')
structure.add_atom(mol_name='axes', atom_name='N', res_name='nY', res_num=5, pos=-atom_pos[1], element='N')
structure.add_atom(mol_name='axes', atom_name='N', res_name='nZ', res_num=6, pos=-atom_pos[2], element='N')
structure.add_atom(mol_name='axes', atom_name='N', res_name='C', res_num=7, pos=centre, element='N')
structure.add_atom(mol_name='axes', atom_name='Ti', res_name='O', res_num=8, pos=centre, element='Ti')

# Set up the domains.
domain(id='moving', spin_id=':1-7')
domain(id='origin', spin_id=':8')
frame_order.ref_domain('origin')

# Select the model.
frame_order.select_model('pseudo-ellipse')

# The eigenframe.
eigen_alpha = 0.0
eigen_beta = -pi/4.0
eigen_gamma = 0.0

# Set the average domain position translation parameters.
value.set(param='ave_pos_x', val=pivot[0])
value.set(param='ave_pos_y', val=pivot[1])
value.set(param='ave_pos_z', val=pivot[2])
value.set(param='ave_pos_alpha', val=0.0)
value.set(param='ave_pos_beta', val=eigen_beta)
value.set(param='ave_pos_gamma', val=0.0)
value.set(param='eigen_alpha', val=eigen_alpha)
value.set(param='eigen_beta', val=eigen_beta)
value.set(param='eigen_gamma', val=eigen_gamma)
value.set(param='cone_theta_x', val=2.0)
value.set(param='cone_theta_y', val=0.5)
value.set(param='cone_sigma_max', val=0.1)

# Set the pivot.
frame_order.pivot(pivot=pivot, fix=True)

# The PDB model, to show with the simulation.
label = 'pseudo_ellipse_tilt'
frame_order.pdb_model(ave_pos='ave_pos_%s'%label, rep='frame_order_%s'%label, size=45, force=True)

# Create the PDB.
frame_order.simulate(file='simulation_%s.pdb'%label, step_size=10.0, snapshot=10, total=5000, force=True)

# Display in PyMOL with the PDB model representation.
pymol.frame_order(ave_pos='ave_pos_%s'%label, rep='frame_order_%s'%label, sim='simulation_%s'%label)
pymol.command("set all_states, 1")
pymol.command("cmd.center('all', animate=-1)")
pymol.command("cmd.zoom('all', animate=-1)")
pymol.command("select resn X")
pymol.command("cmd.color(4, 'sele')")
pymol.command("select resn nX")
pymol.command("cmd.color(5268, 'sele')")
pymol.command("select resn Y")
pymol.command("cmd.color(3, 'sele')")
pymol.command("select resn nY")
pymol.command("cmd.color(22, 'sele')")
pymol.command("select resn Z")
pymol.command("cmd.color(5, 'sele')")
pymol.command("select resn nZ")
pymol.command("cmd.color(2, 'sele')")
pymol.command("cmd.hide('everything', 'ave_pos_%s')" % label)
pymol.command("cmd.show('spheres', 'ave_pos_%s')" % label)
pymol.command("cmd.label('ave_pos_%s', 'resn')" % label)
pymol.command("cmd.hide('everything', 'simulation_%s')" % label)
pymol.command("cmd.show('spheres', 'simulation_%s')" % label)
pymol.command("cmd.delete('sele')")
