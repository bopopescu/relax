###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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

# Python module imports.
from math import pi
import string

# relax module imports.
from bmrblib.nmr_star_dict import NMR_STAR
from bmrblib.nmr_star_dict_v3_1 import NMR_STAR_v3_1
from bmrblib.nmr_star_dict_v3_2 import NMR_STAR_v3_2
from generic_fns import exp_info, mol_res_spin, pipes, relax_data
from generic_fns.mol_res_spin import spin_loop


class Bmrb:
    """Class containing methods related to BMRB STAR file reading and writing."""

    def bmrb_read(self, file_path, version='3.1'):
        """Read the model-free results from a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the NMR-STAR data object.
        if version == '3.2':
            star = NMR_STAR_v3_2('relax_model_free_results', file_path)
        elif version == '3.1':
            star = NMR_STAR_v3_1('relax_model_free_results', file_path)
        else:
            star = NMR_STAR('relax_model_free_results', file_path)

        # Read the contents of the STAR formatted file.
        star.read()

        # Generate the molecule and residue containers from the entity records.
        mol_res_spin.bmrb_read(star)

        # Read the relaxation data saveframes.
        relax_data.bmrb_read(star)


    def bmrb_write(self, file_path, version=None):
        """Write the model-free results to a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        @keyword version:   The BMRB NMR-STAR dictionary format to output to.
        @type version:      str
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Initialise the NMR-STAR data object.
        if version == '3.2':
            star = NMR_STAR_v3_2('relax_model_free_results', file_path)
        elif version == '3.1':
            star = NMR_STAR_v3_1('relax_model_free_results', file_path)
        else:
            star = NMR_STAR('relax_model_free_results', file_path)

        # Rex frq.
        rex_frq = cdp.frq[0]

        # Initialise the spin specific data lists.
        res_num_list = []
        res_name_list = []
        atom_name_list = []

        csa_list = []
        r_list = []
        isotope_list = []
        element_list = []

        s2_list = []
        s2f_list = []
        s2s_list = []
        te_list = []
        tf_list = []
        ts_list = []
        rex_list = []

        s2_err_list = []
        s2f_err_list = []
        s2s_err_list = []
        te_err_list = []
        tf_err_list = []
        ts_err_list = []
        rex_err_list = []

        chi2_list = []

        # Store the spin specific data in lists for later use.
        for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check the data for None (not allowed in BMRB!).
            if res_num == None:
                raise RelaxError("For the BMRB, the residue of spin '%s' must be numbered." % spin_id)
            if res_name == None:
                raise RelaxError("For the BMRB, the residue of spin '%s' must be named." % spin_id)
            if spin.name == None:
                raise RelaxError("For the BMRB, the spin '%s' must be named." % spin_id)
            if spin.heteronuc_type == None:
                raise RelaxError("For the BMRB, the spin isotope type of '%s' must be specified." % spin_id)

            # The molecule/residue/spin info.
            res_num_list.append(res_num)
            res_name_list.append(res_name)
            atom_name_list.append(spin.name)

            # Values.
            csa_list.append(spin.csa * 1e6)    # In ppm.
            r_list.append(spin.r)
            isotope_list.append(int(string.strip(spin.heteronuc_type, string.ascii_letters)))
            if hasattr(spin, 'element'):
                element_list.append(spin.element)
            else:
                element_list.append(None)

            # Model-free data.
            s2_list.append(spin.s2)
            s2f_list.append(spin.s2f)
            s2s_list.append(spin.s2s)
            te_list.append(spin.te)
            tf_list.append(spin.tf)
            ts_list.append(spin.ts)
            if spin.rex == None:
                rex_list.append(None)
            else:
                rex_list.append(spin.rex / (2.0*pi*rex_frq**2))

            s2_err_list.append(spin.s2_err)
            s2f_err_list.append(spin.s2f_err)
            s2s_err_list.append(spin.s2s_err)
            te_err_list.append(spin.te_err)
            tf_err_list.append(spin.tf_err)
            ts_err_list.append(spin.ts_err)
            if spin.rex_err == None:
                rex_err_list.append(None)
            else:
                rex_err_list.append(spin.rex_err / (2.0*pi*rex_frq**2))

            # Opt stats.
            chi2_list.append(spin.chi2)


        # Create Supergroup 2 : The citations.
        ######################################

        # Generate the citations saveframe.
        exp_info.bmrb_write_citations(star)


        # Create Supergroup 3 : The molecular assembly saveframes.
        ##########################################################

        # Generate the entity saveframe.
        mol_res_spin.bmrb_write_entity(star)


        # Create Supergroup 4:  The experimental descriptions saveframes.
        #################################################################

        # Generate the software saveframe.
        exp_info.bmrb_write_software(star)


        # Create Supergroup 5 : The NMR parameters saveframes.
        ######################################################

        # Generate the CSA saveframe.
        star.chem_shift_anisotropy.add(res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, atom_types=element_list, isotope=isotope_list, csa=csa_list)


        # Create Supergroup 6 : The kinetic data saveframes.
        ####################################################

        # Generate the relaxation data saveframes.
        relax_data.bmrb_write(star)


        # Create Supergroup 7 : The thermodynamics saveframes.
        ######################################################

        # Generate the model-free data saveframe.
        star.model_free.add(res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, atom_types=element_list, s2=s2_list, s2f=s2f_list, s2s=s2s_list, te=te_list, tf=tf_list, ts=ts_list, rex=rex_list, s2_err=s2_err_list, s2f_err=s2f_err_list, s2s_err=s2s_err_list, te_err=te_err_list, tf_err=tf_err_list, ts_err=ts_err_list, rex_err=rex_err_list, rex_frq=rex_frq, chi2=chi2_list)


        # Write the contents to the STAR formatted file.
        star.write()
