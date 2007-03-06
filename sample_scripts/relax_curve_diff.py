# Script: relax_curve_diff.py
# Author: Edward d'Auvergne
#
# This script creates a Grace plot of Ix - Ix(theta), the difference between the measured peak
# intensity and the back calculated peak intensity for each spin system x.  Ix(theta) is back
# calculated using the parameter vector theta = [Rx, I0], where Rx is either the R1 or R2 relaxation
# rate and I0 is the initial peak intensity.  The plot consists of distributions of intensity
# differences for each residue at each measured relaxation period.  The average and standard
# deviations of these distributions are also plotted.
#
# The resultant plot is useful for finding bad points or bad spectra when fitting exponential curves
# to determine the R1 and R2 relaxation rates.  If the averages deviate systematically from zero,
# then bias in the spectra or fitting will be clearly revealed.
#
# To use this script, R1 or R2 exponential curve fitting must have previously have been carried out
# and the program state saved to the file 'rx.save' (either with or without the .gz or .bz2
# extensions).  The file name of the saved state can be changed at the bottom of this script.  It is
# important to note that the same version of relax should be used for creating the saved state as
# reading the program state, these files are neither backwards nor forwards compatible.  The name of
# the run using in the curve fitting is expected to be 'rx' but this can also be changed at the
# bottom of the script.  Only the two parameter exponential fit is currently supported.


# Python modules.
from Numeric import Float64, array, identity, sqrt, zeros

# relax modules.
from maths_fns.relax_fit import back_calc_I, func, setup


def back_calc(name):
    """Back calculate the peak intensities.

    The simple two parameter exponential curve (Rx, I0) is assumed.
    """

    # Loop over the spins.
    for spin in self.relax.data.res[name]:
        # Skip deselected spins.
        if not spin.select:
            continue

        # The parameter vector.
        param_vector = array([spin.rx, spin.i0], Float64)

        # Initialise the relaxation fit functions.
        setup(num_params=len(spin.params), num_times=len(self.relax.data.relax_times[name]), values=spin.ave_intensities, sd=self.relax.data.sd[name], relax_times=self.relax.data.relax_times[name], scaling_matrix=identity(2, Float64))

        # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
        func(param_vector)

        # Get the data and store it in the spin specific data structure.
        spin.fit_int = back_calc_I()


def calc_ave_sd():
    """Calculate the average difference and sd between the measured and fitted intensities.

    The standard deviation formula is:
                  ___________________________
                 /   1
        sd =    /  ----- * sum({Xi - Xav}^2)],
              \/   n - 1

    where n is the total number of selected spins, Xi is the peak intensity difference for spin i,
    and Xav is the peak intensity difference averaged across all spins.
    """

    # Diff array, std deviation array, and number of spins.
    diff_array = zeros(sum(self.relax.data.num_spectra[name]), Float64)
    sd_array = zeros(sum(self.relax.data.num_spectra[name]), Float64)
    num_spins = 0


    # Calculate the average difference.
    ###################################

    # Loop over the spins.
    for spin in self.relax.data.res[name]:
        # Skip deselected spins.
        if not spin.select:
            continue

        # Loop over the intensities.
        index = 0
        for i in xrange(len(spin.intensities)):
            for j in xrange(len(spin.intensities[i])):
                # Add the difference between the measured and fitted intensity to the diff array.
                diff_array[index] = diff_array[index] + (spin.intensities[i][j] - spin.fit_int[i])

                # Increment the index.
                index = index + 1

        # The number of selected spins.
        num_spins = num_spins + 1

    # Average difference.
    diff_array = diff_array / num_spins


    # Calculate the standard deviations.
    ####################################

    # Loop over the spins.
    for spin in self.relax.data.res[name]:
        # Skip deselected spins.
        if not spin.select:
            continue

        # Loop over the intensities.
        index = 0
        for i in xrange(len(spin.intensities)):
            for j in xrange(len(spin.intensities[i])):
                # Calculate the sum of squares.
                sd_array[index] = sd_array[index] + ((spin.intensities[i][j] - spin.fit_int[i]) - diff_array[index])**2

                # Increment the index.
                index = index + 1

    # The standard deviations.
    sd_array = sqrt(sd_array / (num_spins - 1))


    # Return the values.
    ####################

    return diff_array, sd_array


def grace_header(file, xmin, xmax, ymin, ymax):
    """Write the formatted Grace header."""

    # Grace version!
    file.write("@version 50118\n")

    # Graph G0.
    file.write("@with g0\n")

    # The graph zoom level.
    file.write("@    world %.1f, %.1f, %.1f, %.1f\n" % (xmin, ymin, xmax, ymax))

    # X-axis label.
    file.write("@    xaxis  label \"\qRelaxation time period (s)\Q\"\n")

    # X-axis specific settings.
    file.write("@    xaxis  label char size 1.48\n")
    file.write("@    xaxis  tick major size 0.75\n")
    file.write("@    xaxis  tick major linewidth 0.5\n")
    file.write("@    xaxis  tick minor linewidth 0.5\n")
    file.write("@    xaxis  tick minor size 0.45\n")
    file.write("@    xaxis  ticklabel char size 1.00\n")

    # Y-axis label.
    file.write("@    yaxis  label \"\qPeak intensity differences (I\\sx\\N - I\\sx\\N(\\xq\\f{}))\Q\"\n")

    # Y-axis specific settings.
    file.write("@    yaxis  label char size 1.48\n")
    file.write("@    yaxis  tick major size 0.75\n")
    file.write("@    yaxis  tick major linewidth 0.5\n")
    file.write("@    yaxis  tick minor linewidth 0.5\n")
    file.write("@    yaxis  tick minor size 0.45\n")
    file.write("@    yaxis  ticklabel char size 1.00\n")

    # Frame.
    file.write("@    frame linewidth 0.5\n")

    # Symbols.
    file.write("@    s0 symbol 9\n")
    file.write("@    s0 symbol size 0.45\n")
    file.write("@    s0 symbol linewidth 0.5\n")
    file.write("@    s0 line linestyle 0\n")
    file.write("@    s1 symbol 8\n")
    file.write("@    s1 symbol size 0.45\n")
    file.write("@    s1 symbol linewidth 0.5\n")
    file.write("@    s1 line linestyle 0\n")
    file.write("@    s2 symbol 1\n")
    file.write("@    s2 symbol size 1.00\n")
    file.write("@    s2 symbol fill pattern 1\n")
    file.write("@    s2 symbol linewidth 0.5\n")
    file.write("@    s2 line linestyle 3\n")


def grace_plot(ave, sd, name):
    """Grace plot of the intensity differences."""

    # Open the file.
    file = open('differences.agr', 'w')

    # Y-axis min and max.
    ymin = 2.5*min(ave - sd)
    ymax = 2.5*max(ave + sd)

    # Grace header.
    grace_header(file, xmin=0, xmax=self.relax.data.relax_times[name][-1], ymin=ymin, ymax=ymax)


    # First time point difference distributions.
    ############################################

    # First graph, first data set.
    file.write("@target G0.S0\n")
    file.write("@type xy\n")

    # Loop over the individual time points.
    for i in xrange(len(self.relax.data.num_spectra[name])):
        # Loop over the spins.
        for spin in self.relax.data.res[name]:
            # Skip deselected spins.
            if not spin.select:
                continue

            # Grace data point.
            file.write("%-30s%-30s\n" % (`self.relax.data.relax_times[name][i]`, `spin.intensities[i][0] - spin.fit_int[i]`))

    # End the graph.
    file.write("&\n")


    # Second time point difference distributions.
    #############################################

    # First graph, second data set.
    file.write("@target G0.S1\n")
    file.write("@type xy\n")

    # Loop over the individual time points.
    for i in xrange(len(self.relax.data.num_spectra[name])):
        # Loop over the spins.
        for spin in self.relax.data.res[name]:
            # Skip deselected spins.
            if not spin.select:
                continue

            # Grace data point.
            if len(spin.intensities[i]) == 2:
                file.write("%-30s%-30s\n" % (`self.relax.data.relax_times[name][i]`, `spin.intensities[i][1] - spin.fit_int[i]`))

    # End the graph.
    file.write("&\n")


    # Average and sd.
    #################

    # First graph, third data set.
    file.write("@target G0.S2\n")
    file.write("@type xydy\n")

    # Loop over the data.
    index = 0
    for i in xrange(len(self.relax.data.num_spectra[name])):
        for j in xrange(self.relax.data.num_spectra[name][i]):
            # Grace data point.
            file.write("%-30s%-30s%-30s\n" % (`self.relax.data.relax_times[name][i]`, `ave[index]`, `sd[index]`))

            # Increment the index.
            index = index + 1

    # End the graph.
    file.write("&\n")

    # Close the file.
    file.close()


# Load the program state containing saved by the 'relax_fit.py' sample script.
state.load('rx.save')

# The name of the run from the 'relax_fit.py' sample script.
name = 'rx'

# Back calculate the peak intensities from the fitted parameters.
back_calc(name)

# Calculate the average difference and standard deviations for each time point.
ave, sd = calc_ave_sd()

# Create a Grace plot of the differences.
grace_plot(ave, sd, name)

# View the graph.
grace.view(file='differences.agr', dir=None)
