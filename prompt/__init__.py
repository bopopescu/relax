###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


__all__ = ['command',
           'create_run',
           'diffusion_tensor',
           'echo_data',
           'fixed',
           'format',
           'generic_functions',
           'gpl',
           'grid',
           'init_data'
           'interpreter',
           'load',
           'map',
           'minimise',
           'model',
           'model_selection',
           'pdb',
           'print_all_data',
           'select_res',
           'set_value',
           'state',
           'tab_completion',
           'write']

__doc__ = \
"""Package for the prompt based interface.

The functions should only contain code for checking the validity of arguments.  If any other code is
required, this should be placed elsewhere.
"""
