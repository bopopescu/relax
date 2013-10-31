###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2013 Troels E. Linnet                                         #
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

# Module docstring.
"""Module for handling relaxation dispersion data within the relax data store.

The dispersion data model is based on the following concepts, in order of importance:

    - 'frq', the spectrometer frequency (if multiple field data is present),
    - 'point', the dispersion point (nu_CPMG value or spin-lock nu1 field strength),
    - 'time', the relaxation time point (if exponential curve data has been collected).

"""

# Python module imports.
from math import atan, pi, sqrt
from numpy import array, float64, int32, ones, zeros
from random import gauss
import sys
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoSpectraError, RelaxNoSpinError, RelaxSpinTypeError
from lib.io import extract_data, get_file_path, open_write_file, read_spin_data, write_data, write_spin_data
from lib.physical_constants import g1H, return_gyromagnetic_ratio
from lib.software.grace import write_xy_data, write_xy_header, script_grace2images
from lib.warnings import RelaxNoSpinWarning
from pipe_control import pipes
from pipe_control.mol_res_spin import check_mol_res_spin_data, exists_mol_res_spin_data, generate_spin_id_unique, return_spin, spin_loop
from pipe_control.result_files import add_result_file
from pipe_control.selection import desel_spin
from pipe_control.spectrum import add_spectrum_id, get_ids
from pipe_control.spectrometer import check_frequency, get_frequency, set_frequency
from specific_analyses.relax_disp.checks import check_exp_type, check_mixed_curve_types
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG, EXP_TYPE_DESC_CPMG, EXP_TYPE_DESC_DQ_CPMG, EXP_TYPE_DESC_R1RHO, EXP_TYPE_DESC_MQ_CPMG, EXP_TYPE_DESC_MQ_R1RHO, EXP_TYPE_DESC_ZQ_CPMG, EXP_TYPE_DQ_CPMG, EXP_TYPE_LIST, EXP_TYPE_LIST_CPMG, EXP_TYPE_LIST_R1RHO, EXP_TYPE_MQ_CPMG, EXP_TYPE_MQ_R1RHO, EXP_TYPE_R1RHO, EXP_TYPE_ZQ_CPMG
from stat import S_IRWXU, S_IRGRP, S_IROTH
from os import chmod, sep



def average_intensity(spin=None, exp_type=None, frq=None, point=None, time=None, sim_index=None, error=False):
    """Return the average peak intensity for the spectrometer frequency, dispersion point, and relaxation time.

    This is for handling replicate peak intensity data.


    @keyword spin:      The spin container to average the peak intensities for.
    @type spin:         SpinContainer instance
    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @keyword time:      The relaxation time period.
    @type time:         float
    @keyword sim_index: The simulation index.  This should be None for the measured intensity values.
    @type sim_index:    None or int
    @keyword error:     A flag which if True will average and return the peak intensity errors.
    @type error:        bool
    @return:            The average peak intensity value.
    @rtype:             float
    """

    # The keys.
    int_keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=point, time=time)

    # Initialise.
    intensity = 0.0

    # Loop over the replicates.
    for i in range(len(int_keys)):
        # Simulation intensity data.
        if sim_index != None:
            # Error checking.
            if not int_keys[i] in spin.intensity_sim:
                raise RelaxError("The peak intensity simulation data is missing the key '%s'." % int_keys[i])

            # Sum.
            intensity += spin.intensity_sim[int_keys[i]][sim_index]

        # Error intensity data.
        if error:
            # Error checking.
            if not int_keys[i] in spin.intensity_err:
                raise RelaxError("The peak intensity errors are missing the key '%s'." % int_keys[i])

            # Sum.
            intensity += spin.intensity_err[int_keys[i]]**2

        # Normal intensity data.
        else:
            # Error checking.
            if not int_keys[i] in spin.intensities:
                raise RelaxError("The peak intensity data is missing the key '%s'." % int_keys[i])

            # Sum.
            intensity += spin.intensities[int_keys[i]]

    # Average.
    if error:
        intensity = sqrt(intensity / len(int_keys))
    else:
        intensity /= len(int_keys)

    # Return the value.
    return intensity


def count_frq():
    """Count the number of spectrometer frequencies present.

    @return:    The spectrometer frequency count
    @rtype:     int
    """

    # Handle missing frequency data.
    if not hasattr(cdp, 'spectrometer_frq'):
        return 1

    # The normal count variable.
    return cdp.spectrometer_frq_count


def count_relax_times(exp_type=None):
    """Count the number of relaxation times present.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:            The relaxation time count for the given experiment.
    @rtype:             int
    """

    # Loop.
    times = []
    for frq, point, time in loop_frq_point_time(exp_type=exp_type):
        if time not in times:
            times.append(time)

    # Return the count.
    return len(times)


def cpmg_frq(spectrum_id=None, cpmg_frq=None):
    """Set the CPMG frequency associated with a given spectrum.

    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str
    @keyword cpmg_frq:      The frequency, in Hz, of the CPMG pulse train.
    @type cpmg_frq:         float
    """

    # Test if the spectrum id exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global CPMG frequency data structures if needed.
    if not hasattr(cdp, 'cpmg_frqs'):
        cdp.cpmg_frqs = {}
    if not hasattr(cdp, 'cpmg_frqs_list'):
        cdp.cpmg_frqs_list = []

    # Add the frequency at the correct position, converting to a float if needed.
    if cpmg_frq == None:
        cdp.cpmg_frqs[spectrum_id] = cpmg_frq
    else:
        cdp.cpmg_frqs[spectrum_id] = float(cpmg_frq)

    # The unique curves for the R2eff fitting (CPMG).
    if cdp.cpmg_frqs[spectrum_id] not in cdp.cpmg_frqs_list:
        cdp.cpmg_frqs_list.append(cdp.cpmg_frqs[spectrum_id])

    # Sort the list (handling None for Python 3).
    flag = False
    if None in cdp.cpmg_frqs_list:
        cdp.cpmg_frqs_list.pop(cdp.cpmg_frqs_list.index(None))
        flag = True
    cdp.cpmg_frqs_list.sort()
    if flag:
        cdp.cpmg_frqs_list.insert(0, None)

    # Update the exponential curve count (skipping the reference if present).
    cdp.dispersion_points = len(cdp.cpmg_frqs_list)
    if None in cdp.cpmg_frqs_list:
        cdp.dispersion_points -= 1

    # Printout.
    print("The spectrum ID '%s' CPMG frequency is set to %s Hz." % (spectrum_id, cdp.cpmg_frqs[spectrum_id]))


def find_intensity_keys(exp_type=None, frq=None, point=None, time=None):
    """Return the key corresponding to the spectrometer frequency, dispersion point, and relaxation time.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          Float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        Float
    @keyword time:      The relaxation time period.
    @type time:         Float
    @return:            The keys corresponding to the spectrometer frequency, dispersion point, and relaxation time.
    @rtype:             List of str
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # The dispersion data.
    if exp_type in EXP_TYPE_LIST_CPMG:
        disp_data = cdp.cpmg_frqs
    else:
        disp_data = cdp.spin_lock_nu1

    # Loop over all spectrum IDs, returning the matching ID.
    ids = []
    for id in cdp.spectrum_ids:
        # The spectrometer frequency.
        frq2 = None
        if hasattr(cdp, 'spectrometer_frq'):
            frq2 = cdp.spectrometer_frq[id]

        # Matching frequency and dispersion point.
        if frq2 == frq and disp_data[id] == point:
            # The reference point, so checking the time is pointless (and can fail as specifying the time should not be necessary).
            if point == None:
                ids.append(id)

            # Matching time.
            elif cdp.relax_times[id] == time:
                ids.append(id)

    # Check for missing IDs.
    if len(ids) == 0:
        if point == None:
            raise RelaxError("No reference intensity data could be found corresponding to the spectrometer frequency of %s MHz and relaxation time of %s s." % (frq*1e-6, time))
        else:
            raise RelaxError("No intensity data could be found corresponding to the spectrometer frequency of %s MHz, dispersion point of %s and relaxation time of %s s." % (frq*1e-6, point, time))

    # Return the IDs.
    return ids


def get_curve_type(id=None):
    """Return the unique curve type.

    @keyword id:    The spectrum ID.  If not supplied, then all data will be assumed.
    @type id:       str
    @return:        The curve type - either 'fixed time' or 'exponential'.
    @rtype:         str
    """

    # Data check.
    check_exp_type(id=id)

    # All data.
    if id == None:
        # Data checks.
        check_mixed_curve_types()

        # Determine the curve type.
        curve_type = 'fixed time'
        if has_exponential_exp_type():
            curve_type = 'exponential'

    # A specific ID.
    else:
        # Determine the curve type.
        curve_type = 'exponential'
        if count_relax_times(cdp.exp_type[id]) == 1:
            curve_type = 'fixed time'

    # Return the type.
    return curve_type


def get_exp_type(id=None):
    """Return the experiment type for the given ID.

    @keyword id:    The spectrum ID.
    @type id:       str
    @return:        The experiment type corresponding to the ID.
    @rtype:         str
    """

    # Data check.
    check_exp_type(id=id)

    # Return the type.
    return cdp.exp_type[id]


def has_cpmg_exp_type():
    """Determine if the current data pipe contains CPMG experiment types.

    @return:    True if CPMG experiment types exist, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all experiment types.
    for exp_type in cdp.exp_type_list:
        if exp_type in EXP_TYPE_LIST_CPMG:
            return True

    # No CPMG experiment types.
    return False


def has_exponential_exp_type():
    """Determine if the current data pipe contains exponential curves.

    @return:    True if spectral data for exponential curves exist, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all spectra IDs.
    for id in cdp.spectrum_ids:
        if get_curve_type(id) == 'exponential':
            return True

    # No exponential data.
    return False


def has_fixed_time_exp_type():
    """Determine if the current data pipe contains fixed time data.

    @return:    True if spectral data for fixed time data exists, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all experiment types.
    for id in cdp.spectrum_ids:
        if get_curve_type(id) == 'fixed time':
            return True

    # No exponential data.
    return False


def has_r1rho_exp_type():
    """Determine if the current data pipe contains R1rho experiment types.

    @return:    True if R1rho experiment types exist, False otherwise.
    @rtype:     bool
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type'):
        return False

    # Loop over all experiment types.
    for exp_type in cdp.exp_type_list:
        if exp_type in EXP_TYPE_LIST_R1RHO:
            return True

    # No CPMG experiment types.
    return False


def insignificance(level=0.0):
    """Deselect all spins with insignificant dispersion profiles.

    @keyword level: The R2eff/R1rho value in rad/s by which to judge insignificance.  If the maximum difference between two points on all dispersion curves for a spin is less than this value, that spin will be deselected.
    @type level:    float
    """

    # Number of spectrometer fields.
    fields = [None]
    field_count = 1
    if hasattr(cdp, 'spectrometer_frq_count'):
        fields = cdp.spectrometer_frq_list
        field_count = cdp.spectrometer_frq_count

    # Loop over all spins.
    for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
        # Nothing to do (the R2eff model has no dispersion curves).
        if spin.model == 'R2eff':
            continue

        # Get all the data.
        try:
            values, errors, missing, frqs, exp_types = return_r2eff_arrays(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)

        # No R2eff data, so skip the rest.
        except RelaxError:
            continue

        # The flag.
        desel = True

        # Loop over the experiments.
        max_diff = 0.0
        for exp_index in range(len(values)):
            # Loop over the magnetic fields.
            for frq_index in range(len(values[exp_index, 0])):
                # The difference.
                diff = values[exp_index, 0,frq_index].max() - values[exp_index, 0,frq_index].min()
                if diff > level:
                    desel = False
                if diff > max_diff:
                    max_diff = diff

        # Deselect the spin.
        if desel:
            # Printout.
            print("Deselecting spin '%s', the maximum dispersion curve difference for all curves is %s rad/s." % (spin_id, max_diff))

            # Deselection.
            desel_spin(spin_id)


def is_cpmg_exp_type(id=None):
    """Determine if the given spectrum ID corresponds to a CPMG experiment type.

    @keyword id:    The spectrum ID string.
    @type id:       str
    @return:        True if the spectrum ID corresponds to a CPMG experiment type, False otherwise.
    @rtype:         bool
    """

    # No experiment type set.
    if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
        return False

    # CPMG experiment type.
    if cdp.exp_type[id] in EXP_TYPE_LIST_CPMG:
        return True

    # Not a CPMG experiment type.
    return False


def is_r1rho_exp_type(id=None):
    """Determine if the given spectrum ID corresponds to a R1rho experiment type.

    @keyword id:    The spectrum ID string.
    @type id:       str
    @return:        True if the spectrum ID corresponds to a R1rho experiment type, False otherwise.
    @rtype:         bool
    """

    # No experiment type set.
    if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
        return False

    # R1rho experiment type.
    if cdp.exp_type[id] in EXP_TYPE_LIST_R1RHO:
        return True

    # Not a R1rho experiment type.
    return False


def loop_cluster():
    """Loop over the spin groupings for one model applied to multiple spins.

    @return:    The list of spin IDs per block will be yielded.
    @rtype:     list of str
    """

    # No clustering, so loop over the sequence.
    if not hasattr(cdp, 'clustering'):
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Return the spin ID as a list.
            yield [spin_id]

    # Loop over the clustering.
    else:
        # The clusters.
        for key in cdp.clustering.keys():
            # Skip the free spins.
            if key == 'free spins':
                continue

            # Create the spin ID lists.
            spin_id_list = []
            for spin_id in cdp.clustering[key]:
                # Skip deselected spins.
                spin = return_spin(spin_id)
                if not spin.select:
                    continue

                # Add the spin ID.
                spin_id_list.append(spin_id)

            # Yield the cluster.
            yield spin_id_list

        # The free spins.
        for spin_id in cdp.clustering['free spins']:
            # Skip deselected spins.
            spin = return_spin(spin_id)
            if not spin.select:
                continue

            # Yield each spin individually.
            yield [spin_id]


def loop_exp():
    """Generator method for looping over all experiment types.

    @return:    The experiment type.
    @rtype:     str
    """

    # Yield each unique experiment type.
    for exp_type in cdp.exp_type_list:
        yield exp_type


def loop_exp_frq():
    """Generator method for looping over the exp and frq data.
    
    These are the experiment types and spectrometer frequencies.


    @return:    The experiment type and spectrometer frequency in Hz.
    @rtype:     str, float
    """

    # First loop over the experiment types.
    for exp_type in loop_exp():
        # Then loop over the spectrometer frequencies.
        for frq in loop_frq():
            # Yield the data.
            yield exp_type, frq


def loop_exp_frq_point():
    """Generator method for looping over the exp, frq, and point data.
    
    These are the experiment types, spectrometer frequencies and dispersion points.


    @return:    The experiment type, spectrometer frequency in Hz and dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @rtype:     str, float, float
    """

    # First loop over the experiment types.
    for exp_type in loop_exp():
        # Then loop over the spectrometer frequencies.
        for frq in loop_frq():
            # And finally the dispersion points.
            for point in loop_point(exp_type=exp_type):
                # Yield the data.
                yield exp_type, frq, point


def loop_exp_frq_point_time():
    """Generator method for looping over the exp, frq, point, and time data.
    
    These are the experiment types, spectrometer frequencies, dispersion points, and relaxation times.


    @return:    The experiment type, spectrometer frequency in Hz, dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the relaxation time.
    @rtype:     str, float, float, float
    """

    # First loop over the experiment types.
    for exp_type in loop_exp():
        # Then the spectrometer frequencies.
        for frq in loop_frq():
            # Then the dispersion points.
            for point in loop_point(exp_type=exp_type):
                # Finally the relaxation times.
                for time in loop_time():
                    # Yield all data.
                    yield exp_type, frq, point, time


def loop_frq():
    """Generator method for looping over all spectrometer frequencies.

    @return:    The spectrometer frequency in Hz
    @rtype:     float
    """

    # Handle missing frequency data.
    frqs = [None]
    if hasattr(cdp, 'spectrometer_frq_list'):
        frqs = cdp.spectrometer_frq_list

    # Yield each unique spectrometer field strength.
    for field in frqs:
        yield field


def loop_frq_point(exp_type=None):
    """Generator method for looping over the spectrometer frequencies and dispersion points.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:    The spectrometer frequency in Hz and dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @rtype:     float, float
    """

    # First loop over the spectrometer frequencies.
    for frq in loop_frq():
        # Then the dispersion points.
        for point in loop_point(exp_type=exp_type):
            # Yield the data.
            yield frq, point


def loop_frq_point_key(exp_type=None):
    """Generator method for looping over the spectrometer frequencies and dispersion points (returning the key).

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:    The key corresponding to the spectrometer frequency and dispersion point.
    @rtype:     str
    """

    # First loop over the spectrometer frequencies.
    for frq in loop_frq():
        # Then the dispersion points.
        for point in loop_point(exp_type=exp_type):
            # Generate and yield the key.
            yield return_param_key_from_data(frq=frq, point=point)


def loop_frq_point_time(exp_type=None):
    """Generator method for looping over the spectrometer frequencies, dispersion points, and relaxation times.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:    The spectrometer frequency in Hz, dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz), and the relaxation time.
    @rtype:     float, float, float
    """

    # First loop over the spectrometer frequencies.
    for frq in loop_frq():
        # Then the dispersion points.
        for point in loop_point(exp_type=exp_type):
            # Finally the relaxation times.
            for time in loop_time():
                # Yield all data.
                yield frq, point, time


def loop_point(exp_type=None, skip_ref=True):
    """Generator method for looping over the dispersion points.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword skip_ref:  A flag which if True will cause the reference point to be skipped.
    @type skip_ref:     bool
    @return:            Dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @rtype:             float
    """

    # CPMG type data.
    if exp_type == None:
        raise RelaxError("The experiment type must be supplied.")
    elif exp_type in EXP_TYPE_LIST_CPMG:
        fields = cdp.cpmg_frqs_list
    elif exp_type in EXP_TYPE_LIST_R1RHO:
        fields = cdp.spin_lock_nu1_list
    else:
        raise RelaxError("The experiment type '%s' is unknown." % exp_type)

    # Loop over the field data.
    for field in fields:
        # Skip the reference.
        if skip_ref and field == None:
            continue

        # Yield each unique field strength or frequency.
        yield field


def loop_spectrum_ids(exp_type=None, frq=None, point=None, time=None):
    """Generator method for selectively looping over the spectrum IDs.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @keyword time:      The relaxation time period.
    @type time:         float
    @return:            The spectrum ID.
    @rtype:             str
    """

    # Loop over all spectrum IDs.
    for id in cdp.spectrum_ids:
        # Experiment type filter.
        if exp_type != None:
            # No experiment type set.
            if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
                continue

            # No match.
            if cdp.exp_type[id] != exp_type:
                continue

        # The frequency filter.
        if frq != None:
            # No frequency data set.
            if not hasattr(cdp, 'spectrometer_frq') or id not in cdp.spectrometer_frq:
                continue

            # No match.
            if cdp.spectrometer_frq[id] != spectrometer_frq:
                continue

        # The dispersion point filter.
        if point != None:
            # No experiment type set.
            if not hasattr(cdp, 'exp_type') or id not in cdp.exp_type:
                continue

            # The experiment type.
            exp_type = cdp.exp_type[id]

            # The CPMG dispersion data.
            if exp_type in EXP_TYPE_LIST_CPMG:
                # No dispersion point data set.
                if not hasattr(cdp, 'cpmg_frqs') or id not in cdp.cpmg_frqs:
                    continue

                # Alias the structure
                disp_data = cdp.cpmg_frqs

            # The R1rho dispersion data.
            else:
                # No dispersion point data set.
                if not hasattr(cdp, 'spin_lock_nu1') or id not in cdp.spin_lock_nu1:
                    continue

                # Alias the structure
                disp_data = cdp.spin_lock_nu1

            # No match.
            if disp_data[id] != point:
                continue

        # The time filter.
        if time != None:
            # No time data set.
            if not hasattr(cdp, 'relax_times') or id not in cdp.relax_times:
                continue

            # No match.
            if cdp.relax_times[id] != time:
                continue

        # Yield the Id.
        yield id


def loop_time():
    """Generator method for looping over the relaxation times.

    @return:    The relaxation time.
    @rtype:     float
    """

    # Loop over the time points.
    if hasattr(cdp, 'relax_time_list'):
        for time in cdp.relax_time_list:
            yield time

    # No times set.
    else:
        yield None


def num_exp_types():
    """Count the number of experiment types present.

    @return:    The number of experiment types.
    @rtype:     int
    """

    # Return the count.
    return len(cdp.exp_type_list)


def plot_disp_curves(dir=None, force=None):
    """Custom 2D Grace plotting function for the dispersion curves.

    One file will be created per spin system.

    A python "grace to PNG/EPS/SVG..." conversion script is created at the end

    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @param force:           Boolean argument which if True causes the files to be overwritten if it already exists.
    @type force:            bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Loop over each experiment type.
    for exp_type in loop_exp():
        # Loop over each spin.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # The unique file name.
            file_name = "disp%s.agr" % spin_id.replace('#', '_').replace(':', '_').replace('@', '_')
            if num_exp_types() > 1:
                file_name = exp_type.replace(' ', '_') + file_name

            # Open the file for writing.
            file_path = get_file_path(file_name, dir)
            file = open_write_file(file_name, dir, force)

            # Initialise some data structures.
            data = []
            set_labels = []
            x_err_flag = False
            y_err_flag = False

            # Loop over the spectrometer frequencies.
            graph_index = 0
            err = False
            for frq in loop_frq():
                # Add a new set for the data at each frequency.
                data.append([])

                # Add a new label.
                if exp_type in EXP_TYPE_LIST_CPMG:
                    label = "R\\s2eff\\N"
                else:
                    label = "R\\s1\\xr\\B\\N"
                if frq != None:
                    label += " (%.1f MHz)" % (frq / 1e6)
                set_labels.append(label)

                # Loop over the dispersion points.
                for disp_point in loop_point(exp_type=exp_type):
                    # The data key.
                    key = return_param_key_from_data(frq=frq, point=disp_point)

                    # No data present.
                    if key not in spin.r2eff:
                        continue

                    # Add the data.
                    data[-1].append([disp_point, spin.r2eff[key]])

                    # Add the error.
                    if hasattr(spin, 'r2eff_err') and key in spin.r2eff_err:
                        err = True
                        data[-1][-1].append(spin.r2eff_err[key])

            # Add the back-calculated data.
            for frq in loop_frq():
                # Add a new set for the data at each frequency.
                data.append([])

                # Add a new label.
                if exp_type in EXP_TYPE_LIST_CPMG:
                    label = "Back-calculated R\\s2eff\\N"
                else:
                    label = "Back-calculated R\\s1\\xr\\B\\N"
                if frq != None:
                    label += " (%.1f MHz)" % (frq / 1e6)
                set_labels.append(label)

                # Loop over the dispersion points.
                for disp_point in loop_point(exp_type=exp_type):
                    # The data key.
                    key = return_param_key_from_data(frq=frq, point=disp_point)

                    # No data present.
                    if not hasattr(spin, 'r2eff_bc') or key not in spin.r2eff_bc:
                        continue

                    # Add the data.
                    data[-1].append([disp_point, spin.r2eff_bc[key]])

                    # Handle the errors.
                    if err:
                        data[-1][-1].append(None)

            # Add the residuals for statistical comparison.
            for frq in loop_frq():
                # Add a new set for the data at each frequency.
                data.append([])

                # Add a new label.
                label = "Residuals"
                if frq != None:
                    label += " (%.1f MHz)" % (frq / 1e6)
                set_labels.append(label)

                # Loop over the dispersion points.
                for disp_point in loop_point(exp_type=exp_type):
                    # The data key.
                    key = return_param_key_from_data(frq=frq, point=disp_point)

                    # No data present.
                    if key not in spin.r2eff or not hasattr(spin, 'r2eff_bc') or key not in spin.r2eff_bc:
                        continue

                    # Add the data.
                    data[-1].append([disp_point, spin.r2eff[key] - spin.r2eff_bc[key]])

                    # Handle the errors.
                    if err:
                        err = True
                        data[-1][-1].append(spin.r2eff_err[key])

            # The axis labels.
            if exp_type in EXP_TYPE_LIST_CPMG:
                axis_labels = ['\\qCPMG pulse train frequency (Hz)\\Q', '\\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)']
            else:
                axis_labels = ['\\qSpin-lock field strength (Hz)\\Q', '\\qR\\s1\\xr\\B\\N\\Q (rad.s\\S-1\\N)']

            # Write the header.
            title = "Relaxation dispersion plot"
            write_xy_header(file=file, title=title, sets=len(data), set_names=set_labels, axis_labels=axis_labels, legend_box_fill_pattern=0, legend_char_size=0.8)

            # Write the data.
            graph_type = 'xy'
            if err:
                graph_type = 'xydy'
            write_xy_data([data], file=file, graph_type=graph_type)

            # Close the file.
            file.close()

            # Add the file to the results file list.
            add_result_file(type='grace', label='Grace', file=file_path)

    # Write a python "grace to PNG/EPS/SVG..." conversion script.
    # Open the file for writing.
    file_name = "grace2images.py"
    file = open_write_file(file_name, dir, force)

    # Write the file.
    script_grace2images(file=file)

    # Close the batch script, then make it executable.
    file.close()
    if dir:
        chmod(dir + sep + file_name, S_IRWXU|S_IRGRP|S_IROTH)
    else:
        chmod(file_name, S_IRWXU|S_IRGRP|S_IROTH)


def plot_exp_curves(file=None, dir=None, force=None, norm=None):
    """Custom 2D Grace plotting function for the exponential curves.

    @keyword file:          The name of the Grace file to create.
    @type file:             str
    @keyword dir:           The optional directory to place the file into.
    @type dir:              str
    @param force:           Boolean argument which if True causes the file to be overwritten if it already exists.
    @type force:            bool
    @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to a starting value of 1.
    @type norm:             bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Open the file for writing.
    file_path = get_file_path(file, dir)
    file = open_write_file(file, dir, force)

    # Initialise some data structures.
    data = []
    set_labels = []
    x_err_flag = False
    y_err_flag = False

    # Loop over the spectrometer frequencies.
    graph_index = 0
    err = False
    for exp_type, frq in loop_exp_frq():
        # Loop over the dispersion points.
        for disp_point in loop_point(exp_type=exp_type):
            # Create a new graph.
            data.append([])

            # Loop over each spin.
            for spin, id in spin_loop(return_id=True, skip_desel=True):
                # No data present.
                if not hasattr(spin, 'intensities'):
                    continue

                # Append a new set structure and set the name to the spin ID.
                data[graph_index].append([])
                if graph_index == 0:
                    set_labels.append("Spin %s" % id)

                # Loop over the relaxation time periods.
                for time in cdp.relax_time_list:
                    # The key.
                    keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=disp_point, time=time)

                    # Loop over each key.
                    for key in keys:
                        # No key present.
                        if key not in spin.intensities:
                            continue

                        # Add the data.
                        if hasattr(spin, 'intensity_err'):
                            data[graph_index][-1].append([time, spin.intensities[key], spin.intensity_err[key]])
                            err = True
                        else:
                            data[graph_index][-1].append([time, spin.intensities[key]])

            # Increment the frq index.
            graph_index += 1

    # The axis labels.
    axis_labels = ['Relaxation time period (s)', 'Peak intensities']

    # Write the header.
    write_xy_header(sets=len(data[0]), file=file, set_names=set_labels, axis_labels=axis_labels, norm=norm)

    # Write the data.
    graph_type = 'xy'
    if err:
        graph_type = 'xydy'
    write_xy_data(data, file=file, graph_type=graph_type, norm=norm)

    # Close the file.
    file.close()

    # Add the file to the results file list.
    add_result_file(type='grace', label='Grace', file=file_path)


def r2eff_read(id=None, file=None, dir=None, disp_frq=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None):
    """Read R2eff/R1rho values directly from a file whereby each row corresponds to a different spin.

    @keyword id:            The experiment ID string to associate the data with.
    @type id:               str
    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @keyword disp_frq:      For CPMG-type data, the frequency of the CPMG pulse train.  For R1rho-type data, the spin-lock field strength (nu1).  The units must be Hertz.
    @type disp_frq:         float
    @keyword spin_id_col:   The column containing the spin ID strings.  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information.  If supplied, spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information.  If supplied, spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.  If supplied, spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information.  If supplied, spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information.  If supplied, spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword data_col:      The column containing the R2eff/R1rho data in Hz.
    @type data_col:         int or None
    @keyword error_col:     The column containing the R2eff/R1rho errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Data checks.
    pipes.test()
    check_mol_res_spin_data()
    check_frequency(id=id)
    check_exp_type(id=id)

    # Store the spectrum ID.
    add_spectrum_id(id)

    # Get the metadata.
    frq = get_frequency(id=id)
    exp_type = get_exp_type(id=id)

    # Loop over the data.
    data_flag = False
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []
    values = []
    errors = []
    for data in read_spin_data(file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep):
        # Unpack.
        if data_col and error_col:
            mol_name, res_num, res_name, spin_num, spin_name, value, error = data
        elif data_col:
            mol_name, res_num, res_name, spin_num, spin_name, value = data
            error = None
        else:
            mol_name, res_num, res_name, spin_num, spin_name, error = data
            value = None

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError("An invalid error value of zero has been encountered.")

        # Get the corresponding spin container.
        spin_id = generate_spin_id_unique(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)
        spin = return_spin(spin_id)
        if spin == None:
            warn(RelaxNoSpinWarning(spin_id))
            continue

        # The dispersion point key.
        point_key = return_param_key_from_data(frq=frq, point=disp_frq)

        # Store the R2eff data.
        if data_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff'):
                spin.r2eff = {}

            # Store.
            spin.r2eff[point_key] = value

        # Store the R2eff error.
        if error_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff_err'):
                spin.r2eff_err = {}

            # Store.
            spin.r2eff_err[point_key] = error

        # Data added.
        data_flag = True

        # Append the data for printout.
        mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(spin_num)
        spin_names.append(spin_name)
        values.append(value)
        errors.append(error)

    # Print out.
    write_spin_data(file=sys.stdout, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names, data=values, data_name='R2eff', error=errors, error_name='R2eff_error')

    # Update the global structures.
    if data_flag:
        # Set the dispersion point frequency.
        if exp_type in EXP_TYPE_LIST_CPMG:
            cpmg_frq(spectrum_id=id, cpmg_frq=disp_frq)
        else:
            spin_lock_field(spectrum_id=id, field=disp_frq)


def r2eff_read_spin(id=None, spin_id=None, file=None, dir=None, disp_point_col=None, data_col=None, error_col=None, sep=None):
    """Read R2eff/R1rho values from file whereby each row is a different dispersion point.

    @keyword id:                The experiment ID string to associate the data with.  This will be modified to include the dispersion point data as "%s_%s" % (id, disp_point).
    @type id:                   str
    @keyword spin_id:           The spin ID string.
    @type spin_id:              str
    @keyword file:              The name of the file to open.
    @type file:                 str
    @keyword dir:               The directory containing the file (defaults to the current directory if None).
    @type dir:                  str or None
    @keyword disp_point_col:    The column containing the dispersion point information.  For CPMG-type data, this is the frequency of the CPMG pulse train.  For R1rho-type data, this is the spin-lock field strength (nu1).  The units must be Hertz.
    @type disp_point_col:       int
    @keyword data_col:          The column containing the R2eff/R1rho data in Hz.
    @type data_col:             int
    @keyword error_col:         The column containing the R2eff/R1rho errors.
    @type error_col:            int
    @keyword sep:               The column separator which, if None, defaults to whitespace.
    @type sep:                  str or None
    """

    # Data checks.
    pipes.test()
    check_mol_res_spin_data()

    # Get the spin.
    spin = return_spin(spin_id)
    if spin == None:
        raise RelaxNoSpinError(spin_id)

    # Extract the data from the file, removing comments and blank lines.
    file_data = extract_data(file, dir, sep=sep)

    # Loop over the data.
    data = []
    new_ids = []
    for line in file_data:
        # Invalid columns.
        if disp_point_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no dispersion point column can be found." % line))
            continue
        if data_col > len(line):
            warn(RelaxWarning("The R2eff/R1rho data %s is invalid, no data column can be found." % line))
            continue
        if error_col > len(line):
            warn(RelaxWarning("The R2eff/R1rho data %s is invalid, no error column can be found." % line))
            continue

        # Unpack.
        disp_point = line[disp_point_col-1]
        value = line[data_col-1]
        error = line[error_col-1]

        # Convert and check the dispersion point.
        try:
            disp_point = float(disp_point)
        except ValueError:
            warn(RelaxWarning("The dispersion point data of the line %s is invalid." % line))
            continue

        # Convert and check the value.
        if value == 'None':
            value = None
        if value != None:
            try:
                value = float(value)
            except ValueError:
                warn(RelaxWarning("The R2eff/R1rho value of the line %s is invalid." % line))
                continue

        # Convert and check the error.
        if error == 'None':
            error = None
        if error != None:
            try:
                error = float(error)
            except ValueError:
                warn(RelaxWarning("The R2eff/R1rho error of the line %s is invalid." % line))
                continue

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError("An invalid error value of zero has been encountered.")

        # Generate a new spectrum ID.
        new_id = "%s_%s" % (id, disp_point)
        new_ids.append(new_id)

        # Data checks.
        check_frequency(id=new_id)
        check_exp_type(id=new_id)

        # Store the spectrum ID.
        add_spectrum_id(new_id)

        # Get the metadata.
        frq = get_frequency(id=new_id)
        exp_type = get_exp_type(id=new_id)

        # The dispersion point key.
        point_key = return_param_key_from_data(frq=frq, point=disp_point)

        # Store the R2eff data.
        if data_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff'):
                spin.r2eff = {}

            # Store.
            spin.r2eff[point_key] = value

        # Store the R2eff error.
        if error_col:
            # Initialise if necessary.
            if not hasattr(spin, 'r2eff_err'):
                spin.r2eff_err = {}

            # Store.
            spin.r2eff_err[point_key] = error

        # Set the dispersion point frequency.
        if exp_type in EXP_TYPE_LIST_CPMG:
            cpmg_frq(spectrum_id=new_id, cpmg_frq=disp_point)
        else:
            spin_lock_field(spectrum_id=new_id, field=disp_point)

        # Append the data for printout.
        data.append(["%20.15f" % disp_point, "%20.15f" % value, "%20.15f" % error])

        # Data added.
        data_flag = True

    # No data, so fail hard!
    if not len(data):
        raise RelaxError("No R2eff/R1rho data could be extracted.")

    # Print out.
    print("Using the experiment IDs %s." % new_ids)
    print("The following R2eff/R1rho data has been loaded into the relax data store:\n")
    write_data(out=sys.stdout, headings=["Disp_point", "R2eff", "R2eff_error"], data=data)


def randomise_R1(spin=None, ri_id=None, N=None):
    """Randomise the R1 data for the given spin for use in the Monte Carlo simulations.

    @keyword spin:      The spin container to randomise the data for.
    @type spin:         SpinContainer instance
    @keyword ri_id:     The relaxation data ID string.
    @type ri_id:        str
    @keyword N:         The number of randomisations to perform.
    @type N:            int
    """

    # The data already exists.
    if hasattr(spin, 'ri_data_sim') and ri_id in spin.ri_data_sim:
        return

    # Initialise the structure.
    if not hasattr(spin, 'ri_data_sim'):
        spin.ri_data_sim = {}
    spin.ri_data_sim[ri_id] = []

    # Randomise.
    for i in range(N):
        spin.ri_data_sim[ri_id].append(gauss(spin.ri_data[ri_id], spin.ri_data_err[ri_id]))


def relax_time(time=0.0, spectrum_id=None):
    """Set the relaxation time period associated with a given spectrum.

    @keyword time:          The time, in seconds, of the relaxation period.
    @type time:             float
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str
    """

    # Test if the spectrum id exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global relaxation time data structures if needed.
    if not hasattr(cdp, 'relax_times'):
        cdp.relax_times = {}
    if not hasattr(cdp, 'relax_time_list'):
        cdp.relax_time_list = []

    # Add the time, converting to a float if needed.
    cdp.relax_times[spectrum_id] = float(time)

    # The unique time points.
    if cdp.relax_times[spectrum_id] not in cdp.relax_time_list:
        cdp.relax_time_list.append(cdp.relax_times[spectrum_id])
    cdp.relax_time_list.sort()

    # Update the exponential time point count.
    cdp.num_time_pts = len(cdp.relax_time_list)

    # Printout.
    print("Setting the '%s' spectrum relaxation time period to %s s." % (spectrum_id, cdp.relax_times[spectrum_id]))


def return_cpmg_frqs(ref_flag=True):
    """Return the list of nu_CPMG frequencies.

    @keyword ref_flag:  A flag which if False will cause the reference spectrum frequency of None to be removed from the list.
    @type ref_flag:     bool
    @return:            The list of nu_CPMG frequencies in Hz.
    @rtype:             numpy rank-1 float64 array
    """

    # No data.
    if not hasattr(cdp, 'cpmg_frqs_list'):
        return None

    # Initialise.
    cpmg_frqs = []

    # Loop over the frequencies.
    for frq in cdp.cpmg_frqs_list:
        if frq == None and not ref_flag:
            continue

        # Add the frequency.
        cpmg_frqs.append(frq)

    # Return the new list.
    return array(cpmg_frqs, float64)


def return_index_from_disp_point(value, exp_type=None):
    """Convert the dispersion point data into the corresponding index.

    @param value:       The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type value:        float
    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:            The corresponding index.
    @rtype:             int
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # Initialise.
    index = 0
    ref_correction = False

    # CPMG-type experiments.
    if exp_type in EXP_TYPE_LIST_CPMG:
        index = cdp.cpmg_frqs_list.index(value)
        if None in cdp.cpmg_frqs_list:
            ref_correction = True

    # R1rho-type experiments.
    elif exp_type in EXP_TYPE_LIST_R1RHO:
        index = cdp.spin_lock_nu1_list.index(value)
        if None in cdp.spin_lock_nu1_list:
            ref_correction = True

    # Remove the reference point (always at index 0).
    for id in loop_spectrum_ids(exp_type=exp_type):
        if ref_correction and get_curve_type(id) == 'fixed time':
            index -= 1
            break

    # Return the index.
    return index


def return_index_from_exp_type(exp_type=None):
    """Convert the experiment type into the corresponding index.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @return:            The corresponding index.
    @rtype:             int
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # Return the index.
    return cdp.exp_type_list.index(exp_type)


def return_index_from_frq(value):
    """Convert the dispersion point data into the corresponding index.

    @param value:   The spectrometer frequency in Hz.
    @type value:    float
    @return:        The corresponding index.
    @rtype:         int
    """

    # No frequency present.
    if value == None:
        return 0

    # Return the index.
    return cdp.spectrometer_frq_list.index(value)


def return_index_from_disp_point_key(key, exp_type=None):
    """Convert the dispersion point key into the corresponding index.

    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @param key:         The dispersion point or R2eff/R1rho key.
    @type key:          str
    @return:            The corresponding index.
    @rtype:             int
    """

    # Check.
    if exp_type == None:
        raise RelaxError("The experiment type has not been supplied.")

    # CPMG-type experiments.
    if exp_type in EXP_TYPE_LIST_CPMG:
        return return_index_from_disp_point(cdp.cpmg_frqs[key], exp_type=exp_type)

    # R1rho-type experiments.
    elif exp_type in EXP_TYPE_LIST_R1RHO:
        return return_index_from_disp_point(cdp.spin_lock_nu1[key], exp_type=exp_type)


def return_intensity(spin=None, exp_type=None, frq=None, point=None, time=None, ref=False):
    """Return the peak intensity corresponding to the given field strength and dispersion point.

    The corresponding reference intensity can be returned if the ref flag is set.  This assumes that the data is of the fixed relaxation time period type.


    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @keyword time:      The relaxation time period.
    @type time:         float
    @keyword ref:       A flag which if True will cause the corresponding reference intensity to be returned instead.
    @type ref:          bool
    """

    # Checks.
    if ref:
        for id in loop_spectrum_ids(exp_type=exp_type, frq=frq, point=point, time=time):
            if get_curve_type(id) == 'exponential':
                raise RelaxError("The reference peak intensity does not exist for the variable relaxation time period experiment types.")

    # The key.
    if ref:
        keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=None, time=time)
    else:
        keys = find_intensity_keys(exp_type=exp_type, frq=frq, point=point, time=time)

    # Return the intensity.
    return spin.intensities[key]


def return_key_from_disp_point_index(frq_index=None, disp_point_index=None):
    """Convert the dispersion point index into the corresponding key.

    @keyword frq_index:         The spectrometer frequency index.
    @type frq_index:            int
    @keyword disp_point_index:  The dispersion point or R2eff/R1rho index.
    @type disp_point_index:     int
    @return:                    The corresponding key.
    @rtype:                     str
    """

    # Insert the reference point (always at index 0).
    if has_fixed_time_exp_type():
        disp_point_index += 1

    # The frequency.
    frq = return_value_from_frq_index(frq_index)

    # CPMG data.
    if exp_type in EXP_TYPE_LIST_CPMG:
        point = cdp.cpmg_frqs_list[disp_point_index]
        points = cdp.cpmg_frqs

    # R1rho data.
    else:
        point = cdp.spin_lock_nu1_list[disp_point_index]
        points = cdp.spin_lock_nu1

    # Find the keys matching the dispersion point.
    key_list = []
    all_keys = points.keys()
    for key in all_keys:
        if points[key] == point:
            key_list.append(key)

    # Return the key.
    return key


def return_offset_data(spins=None, spin_ids=None, fields=None, field_count=None):
    """Return numpy arrays of the chemical shifts, offsets and tilt angles.

    @keyword spins:         The list of spin containers in the cluster.
    @type spins:            list of SpinContainer instances
    @keyword spin_ids:      The list of spin IDs for the cluster.
    @type spin_ids:         list of str
    @keyword fields:        The list of spectrometer field strengths.
    @type fields:           list of float
    @keyword field_count:   The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
    @type field_count:      int
    @return:                The numpy array structures of the chemical shifts in rad/s, spin-lock offsets in rad/s, and rotating frame tilt angles.  For each structure, the first dimension corresponds to the spins of a spin block, the second to the spectrometer field strength, and the third is the dispersion points.  For the chemical shift structure, the third dimension is omitted.
    @rtype:                 numpy rank-2 float array, numpy rank-3 float array, numpy rank-3 float array
    """

    # The spin count.
    spin_num = len(spins)

    # Initialise the data structures for the target function.
    shifts = zeros((spin_num, field_count), float64)
    offsets = zeros((spin_num, field_count, cdp.dispersion_points), float64)
    theta = zeros((spin_num, field_count, cdp.dispersion_points), float64)

    # Assemble the shift data.
    data_flag = False
    for spin_index in range(spin_num):
        # Alias the spin.
        spin = spins[spin_index]

        # No data.
        if not hasattr(spin, 'chemical_shift'):
            continue
        data_flag = True

        # Loop over the spectrometer frequencies.
        for frq in loop_frq():
            # The index.
            frq_index = return_index_from_frq(frq)

            # Convert the shift from ppm to rad/s and store it.
            shifts[spin_index, frq_index] = spin.chemical_shift * 2.0 * pi * frq / g1H * return_gyromagnetic_ratio(spin.isotope) * 1e-6

    # No shift data for the spin cluster.
    if not data_flag:
        return None, None, None

    # Make sure offset data exists.
    if not hasattr(cdp, 'spin_lock_offset'):
        raise RelaxError("The spin-lock offsets have not been set.")

    # Loop over all spectrum IDs.
    for id in cdp.spectrum_ids:
        # The data.
        exp_type = cdp.exp_type[id]
        frq = cdp.spectrometer_frq[id]
        point = cdp.spin_lock_nu1[id]

        # Skip reference spectra.
        if point == None:
            continue

        # The indices.
        frq_index = return_index_from_frq(frq)
        disp_pt_index = return_index_from_disp_point(point, exp_type=exp_type)

        # Loop over the spins.
        for spin_index in range(spin_num):
            # Alias the spin.
            spin = spins[spin_index]

            # Store the offset in rad/s.
            offsets[spin_index, frq_index, disp_pt_index] = cdp.spin_lock_offset[id] * 2.0 * pi * frq / g1H * return_gyromagnetic_ratio(spin.isotope) * 1e-6

            # Calculate the tilt angle.
            omega1 = point * 2.0 * pi
            Delta_omega = shifts[spin_index, frq_index] - offsets[spin_index, frq_index, disp_pt_index]
            if Delta_omega == 0.0:
                theta[spin_index, frq_index, disp_pt_index] = pi / 2.0
            else:
                theta[spin_index, frq_index, disp_pt_index] = atan(omega1 / Delta_omega)

    # Return the structures.
    return shifts, offsets, theta


def return_param_key_from_data(frq=None, point=None):
    """Generate the unique key from the spectrometer frequency and dispersion point.

    @keyword frq:   The spectrometer frequency in Hz.
    @type frq:      float
    @keyword point: The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:    float
    @return:        The unique key.
    @rtype:         str
    """

    # No frequency info.
    if frq == None:
        return "%s" % point

    # Generate and return the unique key.
    return "%.8f_%.3f" % (frq/1e6, point)


def return_r1_data(spins=None, spin_ids=None, fields=None, field_count=None, sim_index=None):
    """Return the R1 data structures for off-resonance R1rho experiments.

    @keyword spins:         The list of spin containers in the cluster.
    @type spins:            list of SpinContainer instances
    @keyword spin_ids:      The list of spin IDs for the cluster.
    @type spin_ids:         list of str
    @keyword fields:        The list of spectrometer field strengths.
    @type fields:           list of float
    @keyword field_count:   The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
    @type field_count:      int
    @keyword sim_index:     The index of the simulation to return the R1 data of.  This should be None if the normal data is required.
    @type sim_index:        None or int
    @return:                The R1 relaxation data.
    @rtype:                 numpy rank-2 float array
    """

    # Check for the presence of data.
    if not hasattr(cdp, 'ri_ids'):
        raise RelaxError("No R1 relaxation data has been loaded.  This data is essential for certain off-resonance R1rho experiments.")

    # The spin count.
    spin_num = len(spins)

    # Initialise the data structure.
    r1 = -ones((spin_num, field_count), float64)

    # Loop over the Rx IDs.
    flags = [False]*field_count
    for ri_id in cdp.ri_ids:
        # Only use R1 data.
        if cdp.ri_type[ri_id] != 'R1':
            continue

        # The frequency.
        frq = cdp.spectrometer_frq[ri_id]
        frq_index = return_index_from_frq(frq)

        # Flip the flag.
        flags[frq_index] = True

        # Spin loop.
        for spin_index in range(spin_num):
            # FIXME:  This is a kludge - the data randomisation needs to be incorporated into the dispersion base_data_loop() method and the standard Monte Carlo simulation pathway used.
            # Randomise the R1 data, when required.
            if sim_index != None and (not hasattr(spins[spin_index], 'ri_data_sim') or ri_id not in spins[spin_index].ri_data_sim):
                randomise_R1(spin=spins[spin_index], ri_id=ri_id, N=cdp.sim_number)

            # Store the data.
            if sim_index != None:
                r1[spin_index, frq_index] = spins[spin_index].ri_data_sim[ri_id][sim_index]
            else:
                r1[spin_index, frq_index] = spins[spin_index].ri_data[ri_id]

    # Check the data to prevent user mistakes.
    for frq_index in range(field_count):
        # The frequency.
        frq = return_value_from_frq_index(frq_index=frq_index)

        # Check for R1 data for this frequency.
        if not flags[frq_index]:
            raise RelaxError("R1 data for the %.1f MHz field strength cannot be found." % (frq/1e6))

        # Check the spin data.
        for spin_index in range(spin_num):
            if r1[spin_index, frq_index] == -1.0:
                raise RelaxError("R1 data for the '%s' spin at %.1f MHz field strength cannot be found." % (spin_ids[spin_index], frq/1e6))

    # Return the data.
    return r1


def return_r2eff_arrays(spins=None, spin_ids=None, fields=None, field_count=None, sim_index=None):
    """Return numpy arrays of the R2eff/R1rho values and errors.

    @keyword spins:         The list of spin containers in the cluster.
    @type spins:            list of SpinContainer instances
    @keyword spin_ids:      The list of spin IDs for the cluster.
    @type spin_ids:         list of str
    @keyword fields:        The list of spectrometer field strengths.
    @type fields:           list of float
    @keyword field_count:   The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
    @type field_count:      int
    @keyword sim_index:     The index of the simulation to return the data of.  This should be None if the normal data is required.
    @type sim_index:        None or int
    @return:                The numpy array structures of the R2eff/R1rho values, errors, missing data, and corresponding Larmor frequencies.  For each structure, the first dimension corresponds to the spins of a spin block, the second to the spectrometer field strength, and the third is the dispersion points.  For the Larmor frequency structure, the third dimension is omitted.
    @rtype:                 numpy rank-3 float array, numpy rank-3 float array, numpy rank-3 int array, numpy rank-2 int array
    """

    # The counts.
    exp_num = num_exp_types()
    spin_num = len(spins)

    # Initialise the data structures for the target function (errors are set to one to avoid divide by zero for missing data in the chi-squared function).
    values = zeros((exp_num, spin_num, field_count, cdp.dispersion_points), float64)
    errors = ones((exp_num, spin_num, field_count, cdp.dispersion_points), float64)
    missing = ones((exp_num, spin_num, field_count, cdp.dispersion_points), int32)
    frqs = zeros((spin_num, field_count), float64)

    # Pack the R2eff/R1rho data.
    data_flag = False
    for spin_index in range(spin_num):
        # Alias the spin.
        spin = spins[spin_index]

        # No data.
        if not hasattr(spin, 'r2eff'):
            continue
        data_flag = True

        # No isotope information.
        if not hasattr(spin, 'isotope'):
            raise RelaxSpinTypeError(spin_id=spin_ids[spin_index])

        # Loop over the R2eff data.
        for exp_type, frq, point in loop_exp_frq_point():
            # The indices.
            exp_type_index = return_index_from_exp_type(exp_type=exp_type)
            disp_pt_index = return_index_from_disp_point(point, exp_type=exp_type)
            frq_index = return_index_from_frq(frq)

            # The key.
            key = return_param_key_from_data(frq=frq, point=point)

            # The Larmor frequency for this spin and field strength (in MHz*2pi to speed up the ppm to rad/s conversion).
            if frq != None:
                frqs[spin_index, frq_index] = 2.0 * pi * frq / g1H * return_gyromagnetic_ratio(spin.isotope) * 1e-6

            # Missing data.
            if key not in spin.r2eff.keys():
                continue

            # The values.
            if sim_index == None:
                values[exp_type_index, spin_index, frq_index, disp_pt_index] = spin.r2eff[key]
            else:
                values[exp_type_index, spin_index, frq_index, disp_pt_index] = spin.r2eff_sim[sim_index][key]

            # The errors.
            errors[exp_type_index, spin_index, frq_index, disp_pt_index] = spin.r2eff_err[key]

            # Flip the missing flag to off.
            missing[exp_type_index, spin_index, frq_index, disp_pt_index] = 0

    # No R2eff/R1rho data for the spin cluster.
    if not data_flag:
        raise RelaxError("No R2eff/R1rho data could be found for the spin cluster %s." % spin_ids)

    # The experiment types.
    exp_types = cdp.exp_type_list

    # Return the structures.
    return values, errors, missing, frqs, exp_types


def return_spin_lock_nu1(ref_flag=True):
    """Return the list of spin-lock field strengths.

    @keyword ref_flag:  A flag which if False will cause the reference spectrum frequency of None to be removed from the list.
    @type ref_flag:     bool
    @return:            The list of spin-lock field strengths in Hz.
    @rtype:             numpy rank-1 float64 array
    """

    # No data.
    if not hasattr(cdp, 'spin_lock_nu1_list'):
        return None

    # Initialise.
    nu1 = []

    # Loop over the frequencies.
    for frq in cdp.spin_lock_nu1_list:
        if frq == None and not ref_flag:
            continue

        # Add the frequency.
        nu1.append(frq)

    # Return the new list.
    return array(nu1, float64)


def return_value_from_frq_index(frq_index=None):
    """Return the spectrometer frequency corresponding to the frequency index.

    @keyword frq_index: The spectrometer frequency index.
    @type frq_index:    int
    @return:            The spectrometer frequency in Hertz or None if no information is present.
    @rtype:             float
    """

    # No data.
    if not hasattr(cdp, 'spectrometer_frq_list'):
        return None

    # Return the field.
    return cdp.spectrometer_frq_list[frq_index]


def set_exp_type(spectrum_id=None, exp_type=None):
    """Select the relaxation dispersion experiment type performed.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword exp:           The relaxation dispersion experiment type.  It can be one of 'CPMG' or 'R1rho'.
    @type exp:              str
    """

    # Data checks.
    pipes.test()

    # Add the spectrum ID to the data store if needed.
    add_spectrum_id(spectrum_id)

    # Check the experiment type.
    if exp_type not in EXP_TYPE_LIST:
        raise RelaxError("The relaxation dispersion experiment '%s' is invalid, it must be one of %s." % (exp_type, EXP_TYPE_LIST))

    # Initialise the experiment type data structures if needed.
    if not hasattr(cdp, 'exp_type'):
        cdp.exp_type = {}
    if not hasattr(cdp, 'exp_type_list'):
        cdp.exp_type_list = []

    # Store the value.
    cdp.exp_type[spectrum_id] = exp_type

    # Unique experiments.
    if cdp.exp_type[spectrum_id] not in cdp.exp_type_list:
        cdp.exp_type_list.append(cdp.exp_type[spectrum_id])

    # Printout.
    text = "The spectrum ID '%s' is now set to " % spectrum_id
    if exp_type == EXP_TYPE_CPMG:
        text += EXP_TYPE_DESC_CPMG + "."
    elif exp_type == EXP_TYPE_MQ_CPMG:
        text += EXP_TYPE_DESC_MQ_CPMG + "."
    elif exp_type == EXP_TYPE_DQ_CPMG:
        text += EXP_TYPE_DESC_DQ_CPMG + "."
    elif exp_type == EXP_TYPE_ZQ_CPMG:
        text += EXP_TYPE_DESC_ZQ_CPMG + "."
    elif exp_type == EXP_TYPE_MQ_R1RHO:
        text += EXP_TYPE_DESC_MQ_R1RHO + "."
    elif exp_type == EXP_TYPE_R1RHO:
        text += EXP_TYPE_DESC_R1RHO + "."
    print(text)


def spin_has_frq_data(spin=None, frq=None):
    """Determine if the spin has intensity data for the given spectrometer frequency.

    @keyword spin:      The specific spin data container.
    @type spin:         SpinContainer instance
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @return:            True if data for that spectrometer frequency is present, False otherwise.
    @rtype:             bool
    """

    # Loop over the intensity data.
    for key in spin.intensities.keys():
        if key in cdp.spectrometer_frq and cdp.spectrometer_frq[key] == frq:
            return True

    # No data.
    return False


def spin_ids_to_containers(spin_ids):
    """Take the list of spin IDs and return the corresponding spin containers.

    This is useful for handling the data from the model_loop() method.


    @param spin_ids:    The list of spin ID strings.
    @type spin_ids:     list of str
    @return:            The list of spin containers.
    @rtype:             list of SpinContainer instances
    """

    # Loop over the IDs and fetch the container.
    spins = []
    for id in spin_ids:
        spins.append(return_spin(id))

    # Return the containers.
    return spins


def spin_lock_field(spectrum_id=None, field=None):
    """Set the spin-lock field strength (nu1) for the given spectrum.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword field:         The spin-lock field strength (nu1) in Hz.
    @type field:            int or float
    """

    # Test if the spectrum ID exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global nu1 data structures if needed.
    if not hasattr(cdp, 'spin_lock_nu1'):
        cdp.spin_lock_nu1 = {}
    if not hasattr(cdp, 'spin_lock_nu1_list'):
        cdp.spin_lock_nu1_list = []

    # Add the frequency, converting to a float if needed.
    if field == None:
        cdp.spin_lock_nu1[spectrum_id] = field
    else:
        cdp.spin_lock_nu1[spectrum_id] = float(field)

    # The unique curves for the R2eff fitting (R1rho).
    if cdp.spin_lock_nu1[spectrum_id] not in cdp.spin_lock_nu1_list:
        cdp.spin_lock_nu1_list.append(cdp.spin_lock_nu1[spectrum_id])

    # Sort the list (handling None for Python 3).
    flag = False
    if None in cdp.spin_lock_nu1_list:
        cdp.spin_lock_nu1_list.pop(cdp.spin_lock_nu1_list.index(None))
        flag = True
    cdp.spin_lock_nu1_list.sort()
    if flag:
        cdp.spin_lock_nu1_list.insert(0, None)

    # Update the exponential curve count (skipping the reference if present).
    cdp.dispersion_points = len(cdp.spin_lock_nu1_list)
    if None in cdp.spin_lock_nu1_list:
        cdp.dispersion_points -= 1

    # Printout.
    if field == None:
        print("The spectrum ID '%s' is set to the reference." % spectrum_id)
    else:
        print("The spectrum ID '%s' spin-lock field strength is set to %s kHz." % (spectrum_id, cdp.spin_lock_nu1[spectrum_id]/1000.0))


def spin_lock_offset(spectrum_id=None, offset=None):
    """Set the spin-lock offset (omega_rf) for the given spectrum.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword offset:        The spin-lock offset (omega_rf) in ppm.
    @type offset:           int or float
    """

    # Test if the spectrum ID exists.
    if spectrum_id not in cdp.spectrum_ids:
        raise RelaxNoSpectraError(spectrum_id)

    # Initialise the global offset data structures if needed.
    if not hasattr(cdp, 'spin_lock_offset'):
        cdp.spin_lock_offset = {}
    if not hasattr(cdp, 'spin_lock_offset_list'):
        cdp.spin_lock_offset_list = []

    # Add the offset, converting to a float if needed.
    if offset == None:
        raise RelaxError("The offset value must be provided.")
    cdp.spin_lock_offset[spectrum_id] = float(offset)

    # The unique curves for the R2eff fitting (R1rho).
    if cdp.spin_lock_offset[spectrum_id] not in cdp.spin_lock_offset_list:
        cdp.spin_lock_offset_list.append(cdp.spin_lock_offset[spectrum_id])

    # Sort the list.
    cdp.spin_lock_offset_list.sort()

    # Printout.
    print("Setting the '%s' spectrum spin-lock offset to %s ppm." % (spectrum_id, cdp.spin_lock_offset[spectrum_id]))
