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

# Script for model-free model selection.
########################################


# Nuclei type
nuclei('N')

# Set the run names.
runs = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Loop over the run names.
for name in runs:
    print "\n\n# " + name + " #"

    # Create the run.
    pipe.create(name, 'mf')

    # Reload precalculated results from the file 'm1/results', etc.
    results.read(run=name, file='results', dir=name)

# Model elimination.
eliminate()

# Model selection.
pipe.create('aic', 'mf')
model_selection('AIC', 'aic')

# Write the results.
state.save('save', force=1)
results.write(run='aic', file='results', force=1)

