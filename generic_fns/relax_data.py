###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module for the manipulation of relaxation data."""

# Python module imports.
from copy import deepcopy
import string
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import create_spin, exists_mol_res_spin_data, generate_spin_id, return_spin, spin_index_loop, spin_loop
from generic_fns import pipes
from generic_fns import value
from relax_errors import RelaxError, RelaxNoRiError, RelaxNoSequenceError, RelaxNoSpinError, RelaxRiError
from relax_io import extract_data, strip
import specific_fns


def add_data_to_spin(spin=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, values=None, errors=None, sim=False):
    """Add the relaxation data to the spin.

    @keyword spin:          The spin container.
    @type spin:             SpinContainer instance
    @keyword ri_labels:     The labels corresponding to the data type, eg ['NOE', 'R1', 'R2',
                            'NOE', 'R1', 'R2'].
    @type ri_labels:        list of str
    @keyword remap_table:   A translation table to map relaxation data points to their
                            frequencies, eg [0, 0, 0, 1, 1, 1].
    @type remap_table:      list of int
    @keyword frq_labels:    NMR frequency labels, eg ['600', '500'].
    @type frq_labels:       list of str
    @keyword frq:           NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6].
    @type frq:              list of float
    @keyword values:        The relaxation data.
    @type values:           list of float
    @keyword errors:        The relaxation errors.
    @type errors:           list of float
    @keyword sim:           A flag which if True means the data corresponds to Monte Carlo
                            simulation data.
    @type sim:              bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Get the current data pipe.
    cdp = pipes.get_pipe()


    # Global (non-spin specific) data.
    #####################################

    # Initialise the global data if necessary.
    data_init(cdp, global_flag=True)

    # Add the data structures.
    cdp.ri_labels = deepcopy(ri_labels)
    cdp.remap_table = deepcopy(remap_table)
    cdp.frq_labels = deepcopy(frq_labels)
    cdp.frq = deepcopy(frq)
    cdp.num_ri = len(ri_labels)
    cdp.num_frq = len(frq)

    # Update the NOE R1 translation table.
    update_noe_r1_table(cdp)


    # Spin specific data.
    #####################

    # Relaxation data.
    if not sim:
        # Initialise the relaxation data structures (if needed).
        data_init(spin, global_flag=False)

        # Relaxation data and errors.
        spin.relax_data = values
        spin.relax_error = errors

        # Associated data structures.
        spin.ri_labels = ri_labels
        spin.remap_table = remap_table

        # Remove any data with the value None.
        for index, Ri in enumerate(spin.relax_data):
            if Ri == None:
                spin.relax_data.pop(index)
                spin.relax_error.pop(index)
                spin.ri_labels.pop(index)
                spin.remap_table.pop(index)

        # Remove any data with error of None.
        for index,error in enumerate(spin.relax_error):
            if error == None:
                spin.relax_data.pop(index)
                spin.relax_error.pop(index)
                spin.ri_labels.pop(index)
                spin.remap_table.pop(index)

        # Associated data structures.
        spin.frq_labels = frq_labels
        spin.frq = frq
        spin.num_ri = len(ri_labels)
        spin.num_frq = len(frq)

        # Update the NOE R1 translation table.
        update_noe_r1_table(spin)

    # Simulation data.
    else:
        # Create the data structure if necessary.
        if not hasattr(spin, 'relax_sim_data') or type(spin.relax_sim_data) != list:
            spin.relax_sim_data = []

        # Append the simulation's relaxation data.
        spin.relax_sim_data.append(values)


def back_calc(ri_label=None, frq_label=None, frq=None):
    """Back calculate the relaxation data.

    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    @param frq:         The spectrometer proton frequency in Hz.
    @type frq:          float
    """

    # Test if the current pipe exists.
    pipes.test()

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists.
    if test_labels(ri_label, frq_label):
        raise RelaxRiError, (ri_label, frq_label)


    # Global (non-residue specific) data.
    #####################################

    # Global data flag.
    global_flag = 1

    # Initialise the global data if necessary.
    data_init(cdp)

    # Update the global data.
    update_data_structures_pipe(ri_label, frq_label, frq)


    # Residue specific data.
    ########################

    # Global data flag.
    global_flag = 0

    # Specific back-calculate function setup.
    back_calculate = specific_fns.setup.get_specific_fn('back_calc', pipes.get_type())

    # Loop over the spins.
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # Initialise all data structures.
        update_data_structures_spin(spin, ri_label, frq_label, frq)

        # Back-calculate the relaxation value.
        value = back_calculate(spin=spin, ri_label=ri_label, frq_label=frq_label, frq=frq)

        # Update all data structures.
        update_data_structures_spin(spin, ri_label, frq_label, frq, value)


def bmrb_read(star):
    """Read the relaxation data from the NMR-STAR dictionary object.

    @param star:    The NMR-STAR dictionary object.
    @type star:     NMR_STAR instance
    """

    # R1, R2, and NOE.
    labels = ['R1', 'R2', 'NOE']
    objects = [star.heteronucl_T1_relaxation, star.heteronucl_T2_relaxation, star.heteronucl_NOEs]

    # Loop over the data types.
    for i in range(3):
        # Get the relaxation data.
        for frq, res_nums, res_names, spin_names, val, err in objects[i].loop():
            # Create the labels.
            ri_label = labels[i]
            frq_label = str(int(frq*1e-6))

            # Test if relaxation data corresponding to 'ri_label' and 'frq_label' already exists.
            if test_labels(ri_label, frq_label):
                raise RelaxRiError, (ri_label, frq_label)

            # Pack the data.
            pack_data(ri_label, frq_label, frq, val, err, mol_names=None, res_nums=res_nums, res_names=res_names, spin_nums=None, spin_names=spin_names, gen_seq=True)



def bmrb_write(star):
    """Generate the relaxation data saveframes for the NMR-STAR dictionary object.

    @param star:    The NMR-STAR dictionary object.
    @type star:     NMR_STAR instance
    """

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Initialise the spin specific data lists.
    res_num_list = []
    res_name_list = []
    atom_name_list = []
    isotope_list = []
    relax_data_list = []
    relax_error_list = []
    for i in range(cdp.num_ri):
        relax_data_list.append([])
        relax_error_list.append([])

    # Store the spin specific data in lists for later use.
    for spin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins with no relaxation data.
        if not hasattr(spin, 'relax_data'):
            continue

        # Check the data for None (not allowed in BMRB!).
        if res_num == None:
            raise RelaxError, "For the BMRB, the residue of spin '%s' must be numbered." % spin_id
        if res_name == None:
            raise RelaxError, "For the BMRB, the residue of spin '%s' must be named." % spin_id
        if spin.name == None:
            raise RelaxError, "For the BMRB, the spin '%s' must be named." % spin_id
        if spin.heteronuc_type == None:
            raise RelaxError, "For the BMRB, the spin isotope type of '%s' must be specified." % spin_id

        # The molecule/residue/spin info.
        res_num_list.append(str(res_num))
        res_name_list.append(str(res_name))
        atom_name_list.append(str(spin.name))

        # The relaxation data.
        for i in range(cdp.num_ri):
            relax_data_list[i].append(str(spin.relax_data[i]))
            relax_error_list[i].append(str(spin.relax_error[i]))

        # Other info.
        isotope_list.append(int(string.strip(spin.heteronuc_type, string.ascii_letters)))

    # The operators of the relaxation superoperator.
    operator_pair = []
    for i in range(cdp.num_ri):
        if cdp.ri_labels[i] == 'R1':
            operator_pair.append(['Iz', 'Iz'])
        elif cdp.ri_labels[i] == 'R2':
            operator_pair.append(['I+', 'I+'])
        elif cdp.ri_labels[i] == 'NOE':
            operator_pair.append(['Iz', 'Sz'])

    # Add the relaxation data.
    for i in range(cdp.num_ri):
        star.relaxation.add(operator_pair=operator_pair[i], frq=cdp.frq[cdp.remap_table[i]], res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, isotope=isotope_list, data=relax_data_list[i], errors=relax_error_list[i])
        #if cdp.ri_labels[i] == 'R1':
        #    star.heteronucl_T1_relaxation.add(frq=cdp.frq[cdp.remap_table[i]], res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, isotope=isotope_list, data=relax_data_list[i], errors=relax_error_list[i])
        #elif cdp.ri_labels[i] == 'R2':
        #    star.heteronucl_T2_relaxation.add(frq=cdp.frq[cdp.remap_table[i]], res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, isotope=isotope_list, data=relax_data_list[i], errors=relax_error_list[i])
        #elif cdp.ri_labels[i] == 'NOE':
        #    star.heteronucl_NOEs.add(frq=cdp.frq[cdp.remap_table[i]], res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, isotope=isotope_list, data=relax_data_list[i], errors=relax_error_list[i])


def copy(pipe_from=None, pipe_to=None, ri_label=None, frq_label=None):
    """Copy the relaxation data from one data pipe to another.

    @keyword pipe_from: The data pipe to copy the relaxation data from.  This defaults to the
                        current data pipe.
    @type pipe_from:    str
    @keyword pipe_to:   The data pipe to copy the relaxation data to.  This defaults to the current
                        data pipe.
    @type pipe_to:      str
    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    """

    # Defaults.
    if pipe_from == None and pipe_to == None:
        raise RelaxError, "The pipe_from and pipe_to arguments cannot both be set to None."
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # Test if the pipe_from and pipe_to data pipes exist.
    pipes.test(pipe_from)
    pipes.test(pipe_to)

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # Test if pipe_from contains sequence data.
    if not exists_mol_res_spin_data(pipe_from):
        raise RelaxNoSequenceError

    # Test if pipe_to contains sequence data.
    if not exists_mol_res_spin_data(pipe_to):
        raise RelaxNoSequenceError

    # Copy all data.
    if ri_label == None and frq_label == None:
        # Get all data structure names.
        names = get_data_names()

        # Spin loop.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            spin_from = dp_from.mol[mol_index].res[res_index].spin[spin_index]
            spin_to = dp_to.mol[mol_index].res[res_index].spin[spin_index]

            # Loop through the data structure names.
            for name in names:
                # Skip the data structure if it does not exist.
                if not hasattr(spin_from, name):
                    continue

                # Copy the data structure.
                setattr(spin_to, name, deepcopy(getattr(spin_from, name)))

    # Copy a specific data set.
    else:
        # Test if relaxation data corresponding to 'ri_label' and 'frq_label' exists for pipe_from.
        if not test_labels(ri_label, frq_label, pipe=pipe_from):
            raise RelaxNoRiError, (ri_label, frq_label)

        # Test if relaxation data corresponding to 'ri_label' and 'frq_label' exists for pipe_to.
        if not test_labels(ri_label, frq_label, pipe=pipe_to):
            raise RelaxRiError, (ri_label, frq_label)

        # Spin loop.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            spin_from = dp_from.mol[mol_index].res[res_index].spin[spin_index]
            spin_to = dp_to.mol[mol_index].res[res_index].spin[spin_index]

            # Find the index corresponding to 'ri_label' and 'frq_label'.
            index = find_index(spin_from, ri_label, frq_label)

            # Catch any problems.
            if index == None:
                continue

            # Get the value and error from pipe_from.
            value = spin_from.relax_data[index]
            error = spin_from.relax_error[index]

            # Update all data structures for pipe_to.
            update_data_structures_spin(spin_to, ri_label, frq_label, frq, value, error)


def data_init(container, global_flag=False):
    """Initialise the data structures for a spin container.

    @param container:       The data pipe or spin data container (PipeContainer or SpinContainer).
    @type container:        class instance
    @keyword global_flag:   A flag which if True corresponds to the pipe specific data structures
                            and if False corresponds to the spin specific data structures.
    @type global_flag:      bool
    """

    # Get the data names.
    data_names = get_data_names(global_flag)

    # Init.
    list_data = [ 'relax_data',
                  'relax_error',
                  'ri_labels',
                  'remap_table',
                  'noe_r1_table',
                  'frq_labels',
                  'frq' ]
    zero_data = [ 'num_ri', 'num_frq' ]

    # Loop over the data structure names.
    for name in data_names:
        # If the name is not in the container, add it as an empty array.
        if name in list_data and not hasattr(container, name):
            setattr(container, name, [])

        # If the name is not in the container, add it as a variable set to zero.
        if name in zero_data and not hasattr(container, name):
            setattr(container, name, 0)


def get_data_names(global_flag=False, sim_names=False):
    """Return a list of names of data structures associated with relax_data.

    Description
    ===========

    The names are as follows:

    relax_data:  Relaxation data.

    relax_error:  Relaxation error.

    num_ri:  Number of data points, eg 6.

    num_frq:  Number of field strengths, eg 2.

    ri_labels:  Labels corresponding to the data type, eg ['NOE', 'R1', 'R2', 'NOE', 'R1',
    'R2'].

    remap_table:  A translation table to map relaxation data points to their frequencies, eg [0,
    0, 0, 1, 1, 1].

    noe_r1_table:  A translation table to direct the NOE data points to the R1 data points.
    This is used to speed up calculations by avoiding the recalculation of R1 values.  eg [None,
    None, 0, None, None, 3]

    frq_labels:  NMR frequency labels, eg ['600', '500']

    frq:  NMR frequencies in Hz, eg [600.0 * 1e6, 500.0 * 1e6]


    @keyword global_flag:   A flag which if True corresponds to the pipe specific data structures
                            and if False corresponds to the spin specific data structures.
    @type global_flag:      bool
    @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object names as
                            well.
    @type sim_names:        bool
    @return:                The list of object names.
    @rtype:                 list of str
    """

    # Initialise.
    names = []

    # Global data names.
    if not sim_names and global_flag:
        names.append('num_frq')
        names.append('frq')
        names.append('frq_labels')
        names.append('num_ri')
        names.append('ri_labels')
        names.append('remap_table')
        names.append('noe_r1_table')

    # Residue specific data names.
    if not sim_names and not global_flag:
        names.append('num_frq')
        names.append('frq')
        names.append('frq_labels')
        names.append('num_ri')
        names.append('ri_labels')
        names.append('remap_table')
        names.append('noe_r1_table')
        names.append('relax_data')
        names.append('relax_error')

    # Simulation object names.
    if sim_names and not global_flag:
        names.append('relax_sim_data')

    # Return the list of names.
    return names


def delete(ri_label=None, frq_label=None):
    """Delete relaxation data corresponding to the Ri and frequency labels.

    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data corresponding to 'ri_label' and 'frq_label' exists.
    if not test_labels(ri_label, frq_label):
        raise RelaxNoRiError, (ri_label, frq_label)

    # Loop over the spins.
    for spin in spin_loop():
        # Global data flag.
        global_flag = False

        # Find the index corresponding to 'ri_label' and 'frq_label'.
        index = find_index(spin, ri_label, frq_label)

        # Catch any problems.
        if index == None:
            continue

        # Relaxation data and errors.
        spin.relax_data.pop(index)
        spin.relax_error.pop(index)

        # Update the number of relaxation data points.
        spin.num_ri = spin.num_ri - 1

        # Delete ri_label from the data types.
        spin.ri_labels.pop(index)

        # Update the remap table.
        spin.remap_table.pop(index)

        # Find if there is other data corresponding to 'frq_label'
        frq_index = spin.frq_labels.index(frq_label)
        if not frq_index in spin.remap_table:
            # Update the number of frequencies.
            spin.num_frq = spin.num_frq - 1

            # Update the frequency labels.
            spin.frq_labels.pop(frq_index)

            # Update the frequency array.
            spin.frq.pop(frq_index)

        # Update the NOE R1 translation table.
        spin.noe_r1_table.pop(index)
        for j in xrange(spin.num_ri):
            if spin.noe_r1_table[j] > index:
                spin.noe_r1_table[j] = spin.noe_r1_table[j] - 1


def display(ri_label=None, frq_label=None):
    """Display relaxation data corresponding to the Ri and frequency labels.

    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data corresponding to 'ri_label' and 'frq_label' exists.
    if not test_labels(ri_label, frq_label):
        raise RelaxNoRiError, (ri_label, frq_label)

    # Print the data.
    value.write_data(param=(ri_label, frq_label), file=sys.stdout, return_value=return_value)


def find_index(data, ri_label, frq_label):
    """Find the index corresponding to ri_label and frq_label.

    @param data:        The class instance containing the ri_label and frq_label variables.
    @type data:         PipeContainer or SpinContainer
    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    @return:            The index corresponding to the relaxation data.  If there is no
                        relaxation data corresponding to the labels, None is returned.
    @rtype:             None or int
    """

    # No data.num_ri data structure.
    if not hasattr(data, 'num_ri'):
        return None

    # Initialise.
    index = None

    # Find the index.
    for j in xrange(data.num_ri):
        if ri_label == data.ri_labels[j] and frq_label == data.frq_labels[data.remap_table[j]]:
            index = j

    # Return the index.
    return index


def pack_data(ri_label, frq_label, frq, values, errors, mol_names=None, res_nums=None, res_names=None, spin_nums=None, spin_names=None, gen_seq=False):
    """Pack the relaxation data into the data pipe and spin containers.

    The values, errors, mol_names, res_nums, res_names, spin_nums, and spin_names arguments must be
    lists of equal length or None.  Each element i corresponds to a unique spin.

    @param ri_label:        The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:         str
    @param frq_label:       The field strength label.
    @type frq_label:        str
    @param frq:             The spectrometer proton frequency in Hz.
    @type frq:              float
    @keyword mol_names:     The list of molecule names for each spin.
    @type mol_names:        None or list of str
    @keyword res_nums:      The list of residue numbers for each spin.
    @type res_nums:         None or list of str
    @keyword res_names:     The list of residue names for each spin.
    @type res_names:        None or list of str
    @keyword spin_nums:     The list of spin numbers.
    @type spin_nums:        None or list of str
    @keyword spin_names:    The list of spin names.
    @type spin_names:       None or list of str
    @keyword gen_seq:       A flag which if True will cause the molecule, residue, and spin sequence
                            data to be generated.
    @type gen_seq:          bool
    """

    # The number of spins.
    N = len(values)

    # Convert None args.
    if not mol_names:
        mol_names = [None]*N
    if not res_nums:
        res_nums = [None]*N
    if not res_names:
        res_names = [None]*N
    if not spin_nums:
        spin_nums = [None]*N
    if not spin_names:
        spin_names = [None]*N

    # Test the data.
    if len(errors) != N:
        raise RelaxError, "The length of the errors arg (%s) does not match that of the value arg (%s)." % (len(errors), N)
    if len(mol_names) != N:
        raise RelaxError, "The length of the mol_names arg (%s) does not match that of the value arg (%s)." % (len(mol_names), N)
    if len(res_nums) != N:
        raise RelaxError, "The length of the res_nums arg (%s) does not match that of the value arg (%s)." % (len(res_nums), N)
    if len(res_names) != N:
        raise RelaxError, "The length of the res_names arg (%s) does not match that of the value arg (%s)." % (len(res_names), N)
    if len(spin_nums) != N:
        raise RelaxError, "The length of the spin_nums arg (%s) does not match that of the value arg (%s)." % (len(spin_nums), N)
    if len(spin_names) != N:
        raise RelaxError, "The length of the spin_names arg (%s) does not match that of the value arg (%s)." % (len(spin_names), N)

    # Get the current data pipe.
    cdp = pipes.get_pipe()

    # Initialise the global data for the current pipe if necessary.
    data_init(cdp, global_flag=True)

    # Update the global data.
    update_data_structures_pipe(ri_label, frq_label, frq)

    # Loop over the spin data.
    for value, error, mol_name, res_num, res_name, spin_num, spin_name in zip(values, errors, mol_names, res_nums, res_names, spin_nums, spin_names):
        # Generate the spin identification string.
        id = generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)

        # Skip all rows where the value or error is None.
        if value == None or error == None:
            continue

        # Get the corresponding spin container.
        spin = return_spin(id)
        if spin == None:
            if not gen_seq:
                raise RelaxNoSpinError, id
            else:
                create_spin(spin_num=spin_num, spin_name=spin_name, res_num=res_num, res_name=res_name, mol_name=mol_name)
                spin = return_spin(id)

        # Update all data structures.
        update_data_structures_spin(spin, ri_label, frq_label, frq, value, error)


def read(ri_label=None, frq_label=None, frq=None, file=None, dir=None, file_data=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None):
    """Read R1, R2, or NOE relaxation data from a file.

    @param ri_label:        The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:         str
    @param frq_label:       The field strength label.
    @type frq_label:        str
    @param frq:             The spectrometer proton frequency in Hz.
    @type frq:              float
    @param file:            The name of the file to open.
    @type file:             str
    @param dir:             The directory containing the file (defaults to the current directory
                            if None).
    @type dir:              str or None
    @param file_data:       An alternative opening a file, if the data already exists in the
                            correct format.  The format is a list of lists where the first index
                            corresponds to the row and the second the column.
    @type file_data:        list of lists
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    @param sep:             The column seperator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Minimum number of columns.
    min_col_num = max(mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col)

    # Extract the data from the file.
    if not file_data:
        # Extract.
        file_data = extract_data(file, dir)

        # Count the number of header lines.
        header_lines = 0
        num_col = max(res_num_col, spin_num_col)
        for i in xrange(len(file_data)):
            try:
                int(file_data[i][num_col])
            except:
                header_lines = header_lines + 1
            else:
                break

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip the data.
        file_data = strip(file_data)

        # Test the validity of the relaxation data.
        for i in xrange(len(file_data)):
            # Skip missing data.
            if len(file_data[i]) <= min_col_num:
                continue
            elif file_data[i][data_col] == 'None' or file_data[i][error_col] == 'None':
                continue

            # Test that the data are numbers.
            try:
                if res_num_col != None:
                    int(file_data[i][res_num_col])
                if spin_num_col != None:
                    int(file_data[i][spin_num_col])
                float(file_data[i][data_col])
                float(file_data[i][error_col])
            except ValueError:
                raise RelaxError, "The relaxation data in the line " + `file_data[i]` + " is invalid."

    # Loop over the file data to create the data structures for packing.
    values = []
    errors = []
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []
    for i in xrange(len(file_data)):
        # Skip missing data.
        if len(file_data[i]) <= min_col_num:
            continue

        # Pack the spin ID info.
        if mol_name_col != None:
            mol_names.append(file_data[i][mol_name_col])
        else:
            mol_names.append(None)
        if res_num_col != None:
            res_nums.append(file_data[i][res_num_col])
        else:
            res_nums.append(None)
        if res_name_col != None:
            res_names.append(file_data[i][res_name_col])
        else:
            res_names.append(None)
        if spin_num_col != None:
            spin_nums.append(file_data[i][spin_num_col])
        else:
            spin_nums.append(None)
        if spin_name_col != None:
            spin_names.append(file_data[i][spin_name_col])
        else:
            spin_names.append(None)

        # Convert the data.
        values.append(eval(file_data[i][data_col]))
        errors.append(eval(file_data[i][error_col]))

    # Pack the data.
    pack_data(ri_label, frq_label, frq, values, errors, mol_names, res_nums, res_names, spin_nums, spin_names)


def return_data_desc(name):
    """Return a description of the spin specific object.

    @param name:    The name of the spin specific object.
    @type name:     str
    """

    if name == 'num_frq':
        return 'Number of spectrometer frequencies'
    if name == 'frq':
        return 'Frequencies'
    if name == 'frq_labels':
        return 'Frequency labels'
    if name == 'num_ri':
        return 'Number of relaxation data sets'
    if name == 'ri_labels':
        return 'Relaxation data set labels'
    if name == 'remap_table':
        return 'Table mapping frequencies to relaxation data'
    if name == 'noe_r1_table':
        return 'Table mapping the NOE to the corresponding R1'
    if name == 'relax_data':
        return 'The relaxation data'
    if name == 'relax_error':
        return 'The relaxation data errors'


def return_value(spin, data_type):
    """Return the value and error corresponding to 'data_type'.

    @param spin:        The spin container.
    @type spin:         SpinContainer instance
    @param data_type:   A tuple of the Ri label and the frequency label.
    @type data_type:    tuple of str of length 2
    """

    # Unpack the data_type tuple.
    ri_label, frq_label = data_type

    # Initialise.
    value = None
    error = None

    # Find the index corresponding to 'ri_label' and 'frq_label'.
    index = find_index(spin, ri_label, frq_label)

    # Get the data.
    if index != None:
        value = spin.relax_data[index]
        error = spin.relax_error[index]

    # Return the data.
    return value, error


def test_labels(ri_label, frq_label):
    """Test if data corresponding to 'ri_label' and 'frq_label' currently exists.

    @param ri_label:    The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:     str
    @param frq_label:   The field strength label.
    @type frq_label:    str
    @return:            The answer to the question of whether relaxation data exists corresponding
                        to the given labels.
    @rtype:             bool
    """

    # Loop over the spins.
    for spin in spin_loop():
        # No ri data.
        if not hasattr(spin, 'num_ri'):
            continue

        # Loop over the relaxation data.
        for j in xrange(spin.num_ri):
            # Test if the relaxation data matches 'ri_label' and 'frq_label'.
            if ri_label == spin.ri_labels[j] and frq_label == spin.frq_labels[spin.remap_table[j]]:
                return True

    # No match.
    return False


def update_data_structures_pipe(ri_label=None, frq_label=None, frq=None):
    """Update all relaxation data structures in the current data pipe.

    @param ri_label:        The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:         str
    @param frq_label:       The field strength label.
    @type frq_label:        str
    @param frq:             The spectrometer proton frequency in Hz.
    @type frq:              float
    """

    # Alias the current data pipe.
    cdp = pipes.get_pipe()

    # Initialise the relaxation data structures (if needed).
    data_init(cdp, global_flag=True)

    # The index.
    i = len(cdp.ri_labels) - 1

    # Update the number of relaxation data points.
    cdp.num_ri = cdp.num_ri + 1

    # Add ri_label to the data types.
    cdp.ri_labels.append(ri_label)

    # Find if the frequency has already been loaded.
    remap = len(cdp.frq)
    flag = 0
    for j in xrange(len(cdp.frq)):
        if frq == cdp.frq[j]:
            remap = j
            flag = 1

    # Update the remap table.
    cdp.remap_table.append(remap)

    # Update the data structures which have a length equal to the number of field strengths.
    if not flag:
        # Update the number of frequencies.
        cdp.num_frq = cdp.num_frq + 1

        # Update the frequency labels.
        cdp.frq_labels.append(frq_label)

        # Update the frequency array.
        cdp.frq.append(frq)

    # Update the NOE R1 translation table.
    cdp.noe_r1_table.append(None)

    # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
    if ri_label == 'NOE':
        for j in xrange(cdp.num_ri):
            if cdp.ri_labels[j] == 'R1' and frq_label == cdp.frq_labels[cdp.remap_table[j]]:
                cdp.noe_r1_table[cdp.num_ri - 1] = j

    # Update the NOE R1 translation table.
    # If the data corresponds to 'R1', try to find if the corresponding NOE data.
    if ri_label == 'R1':
        for j in xrange(cdp.num_ri):
            if cdp.ri_labels[j] == 'NOE' and frq_label == cdp.frq_labels[cdp.remap_table[j]]:
                cdp.noe_r1_table[j] = cdp.num_ri - 1


def update_data_structures_spin(spin=None, ri_label=None, frq_label=None, frq=None, value=None, error=None):
    """Update all relaxation data structures of the given spin container.

    @param spin:            The SpinContainer object.
    @type spin:             class instance
    @param ri_label:        The relaxation data type, ie 'R1', 'R2', or 'NOE'.
    @type ri_label:         str
    @param frq_label:       The field strength label.
    @type frq_label:        str
    @param frq:             The spectrometer proton frequency in Hz.
    @type frq:              float
    @param value:           The relaxation data value.
    @type value:            float
    @param error:           The relaxation data error.
    @type error:            float
    """

    # Initialise the relaxation data structures (if needed).
    data_init(spin, global_flag=False)

    # Find the index corresponding to 'ri_label' and 'frq_label'.
    index = find_index(spin, ri_label, frq_label)

    # Append empty data.
    if index == None:
        spin.relax_data.append(None)
        spin.relax_error.append(None)
        spin.ri_labels.append(None)
        spin.remap_table.append(None)
        spin.noe_r1_table.append(None)

    # Set the index value.
    if index == None:
        i = len(spin.relax_data) - 1
    else:
        i = index

    # Relaxation data and errors.
    spin.relax_data[i] = value
    spin.relax_error[i] = error

    # Update the number of relaxation data points.
    if index == None:
        spin.num_ri = spin.num_ri + 1

    # Add ri_label to the data types.
    spin.ri_labels[i] = ri_label

    # Find if the frequency frq has already been loaded.
    remap = len(spin.frq)
    flag = 0
    for j in xrange(len(spin.frq)):
        if frq == spin.frq[j]:
            remap = j
            flag = 1

    # Update the remap table.
    spin.remap_table[i] = remap

    # Update the data structures which have a length equal to the number of field strengths.
    if not flag:
        # Update the number of frequencies.
        if index == None:
            spin.num_frq = spin.num_frq + 1

        # Update the frequency labels.
        spin.frq_labels.append(frq_label)

        # Update the frequency array.
        spin.frq.append(frq)

    # Update the NOE R1 translation table.
    # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
    if ri_label == 'NOE':
        for j in xrange(spin.num_ri):
            if spin.ri_labels[j] == 'R1' and frq_label == spin.frq_labels[spin.remap_table[j]]:
                spin.noe_r1_table[spin.num_ri - 1] = j

    # Update the NOE R1 translation table.
    # If the data corresponds to 'R1', try to find if the corresponding NOE data.
    if ri_label == 'R1':
        for j in xrange(spin.num_ri):
            if spin.ri_labels[j] == 'NOE' and frq_label == spin.frq_labels[spin.remap_table[j]]:
                spin.noe_r1_table[j] = spin.num_ri - 1


def update_noe_r1_table(cont):
    """Update the NOE-R1 translation table.

    @param cont:    Either the pipe container or spin container to update the structure of.
    @type cont:     PipeContainer or SpinContainer instance
    """

    # Create an array of None for the NOE R1 translation table, if the table is empty.
    if cont.noe_r1_table == []:
        for i in xrange(cont.num_ri):
            cont.noe_r1_table.append(None)

    # Loop over the relaxation data.
    for i in xrange(cont.num_ri):
        # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
        if cont.ri_labels[i] == 'NOE':
            for j in xrange(cont.num_ri):
                if cont.ri_labels[j] == 'R1' and cont.frq_labels[cont.remap_table[i]] == cont.frq_labels[cont.remap_table[j]]:
                    cont.noe_r1_table[i] = j

        # If the data corresponds to 'R1', try to find if the corresponding NOE data.
        if cont.ri_labels[i] == 'R1':
            for j in xrange(cont.num_ri):
                if cont.ri_labels[j] == 'NOE' and cont.frq_labels[cont.remap_table[i]] == cont.frq_labels[cont.remap_table[j]]:
                    cont.noe_r1_table[j] = i


def write(ri_label=None, frq_label=None, file=None, dir=None, force=False):
    """Write relaxation data to a file."""

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data corresponding to 'ri_label' and 'frq_label' exists.
    if not test_labels(ri_label, frq_label):
        raise RelaxNoRiError, (ri_label, frq_label)

    # Create the file name if none is given.
    if file == None:
        file = ri_label + "." + frq_label + ".out"

    # Write the data.
    value.write(param=(ri_label, frq_label), file=file, dir=dir, force=force, return_value=return_value)
