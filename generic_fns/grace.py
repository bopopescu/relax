###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

from os import system
from re import match


class Grace:
    def __init__(self, relax):
        """Operations, functions, etc common to the different model-free analysis methods."""

        self.relax = relax


    def determine_graph_type(self):
        """Function for determining if the graph is of type xy, xydy, xydx, or xydxdy."""

        # Initial flags.
        x_errors = 0
        y_errors = 0

        # Loop over the data.
        for i in xrange(len(self.data)):
            # X-axis errors.
            if self.x_data_type != 'res' and self.data[i][1] != None:
                x_errors = 1

            # Y-axis errors.
            if self.data[i][3] != None:
                y_errors = 1

        # Plot of values.
        if self.plot_data == 'value':
            # xy plot with errors along both axes.
            if x_errors and y_errors:
                self.graph_type = 'xydxdy'

            # xy plot with errors along the Y-axis.
            elif y_errors:
                self.graph_type = 'xydy'

            # xy plot with errors along the X-axis.
            elif x_errors:
                self.graph_type = 'xydx'

            # xy plot with no errors.
            else:
                self.graph_type = 'xy'

        # Plot of errors.
        elif self.plot_data == 'error':
            # xy plot of residue number vs error.
            if self.x_data_type == 'res' and y_errors:
                self.graph_type = 'xy'

            # xy plot of error vs error.
            elif x_errors and y_errors:
                self.graph_type = 'xy'

            # Invalid argument combination.
            else:
                raise RelaxError, "When plotting errors, the errors must exist."

        # Plot of simulation values.
        else:
            # xy plot with no errors.
            self.graph_type = 'xy'


    def get_data(self):
        """Function for getting all the xy data."""

        # Initialise.
        self.data = []

        # Loop over the residues.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Skip the residue if there is no match to 'self.res_num' (unless it is None).
            if type(self.res_num) == int:
                if not data.num == self.res_num:
                    continue
            elif type(self.res_num) == str:
                if not match(self.res_num, `data.num`):
                    continue

            # Skip the residue if there is no match to 'self.res_name' (unless it is None).
            if self.res_name != None:
                if not match(self.res_name, data.name):
                    continue

            # Number of data points per residue.
            if self.plot_data == 'sim':
                points = self.relax.data.sim_number[self.run]
            else:
                points = 1

            # Loop over the data points.
            for j in xrange(points):
                # Initialise an empty array for the individual residue data.
                res_data = [None, None, None, None]

                # Residue number on the x-axis.
                if self.x_data_type == 'res':
                    res_data[0] = data.num

                # Parameter value for the x-axis.
                else:
                    # Get the x-axis values and errors.
                    if self.plot_data == 'sim':
                        res_data[0], res_data[1] = self.x_return_value(self.run, i, self.x_data_type, sim=j)
                    else:
                        res_data[0], res_data[1] = self.x_return_value(self.run, i, self.x_data_type)

                # Get the y-axis values and errors.
                if self.plot_data == 'sim':
                    res_data[2], res_data[3] = self.y_return_value(self.run, i, self.y_data_type, sim=j)
                else:
                    res_data[2], res_data[3] = self.y_return_value(self.run, i, self.y_data_type)

                # Go to the next residue if there is missing data.
                if res_data[0] == None or res_data[2] == None:
                    continue

                # X-axis conversion factors.
                if self.x_data_type != 'res':
                    res_data[0] = res_data[0] / self.x_return_conversion_factor(self.x_data_type)
                    if res_data[1]:
                        res_data[1] = res_data[1] / self.x_return_conversion_factor(self.x_data_type)

                # Y-axis conversion factors.
                res_data[2] = res_data[2] / self.y_return_conversion_factor(self.y_data_type)
                if res_data[3]:
                    res_data[3] = res_data[3] / self.y_return_conversion_factor(self.y_data_type)

                # Append the array to the full data structure.
                self.data.append(res_data)


    def view(self, file=None, dir=None, grace_exe='xmgrace'):
        """Function for running Grace."""

        # File path.
        self.file_path = self.relax.IO.file_path(file, dir)

        # Run Grace.
        system(grace_exe + " " + self.file_path + " &")


    def write(self, run=None, x_data_type='res', y_data_type=None, res_num=None, res_name=None, plot_data='value', file=None, dir=None, force=0):
        """Function for writing data to a file."""

        # Arguments.
        self.run = run
        self.x_data_type = x_data_type
        self.y_data_type = y_data_type
        self.res_num = res_num
        self.res_name = res_name
        self.plot_data = plot_data

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the residue number is a valid regular expression.
        if type(self.res_num) == str:
            try:
                compile(self.res_num)
            except:
                raise RelaxRegExpError, ('residue number', self.res_num)

        # Test if the residue name is a valid regular expression.
        if self.res_name:
            try:
                compile(self.res_name)
            except:
                raise RelaxRegExpError, ('residue name', self.res_name)

        # Test if the plot_data argument is one of 'value', 'error', or 'sim'.
        if self.plot_data not in ['value', 'error', 'sim']:
            raise RelaxError, "The plot data argument " + `self.plot_data` + " must be set to either 'value', 'error', 'sim'."

        # Test if the simulations exist.
        if self.plot_data == 'sim' and (not hasattr(self.relax.data, 'sim_number') or not self.relax.data.sim_number.has_key(self.run)):
            raise RelaxNoSimError, self.run

        # Open the file for writing.
        self.file = self.relax.IO.open_write_file(file, dir, force)

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific value and error, conversion factor, and units returning functions.
        self.x_return_value =             self.y_return_value =             self.relax.specific_setup.setup('return_value', function_type)
        self.x_return_conversion_factor = self.y_return_conversion_factor = self.relax.specific_setup.setup('return_conversion_factor', function_type)
        self.x_return_units =             self.y_return_units =             self.relax.specific_setup.setup('return_units', function_type)
        self.x_return_grace_string =      self.y_return_grace_string =      self.relax.specific_setup.setup('return_grace_string', function_type)

        # Test if the X-axis data type is a minimisation statistic.
        if self.x_data_type != 'res' and self.relax.generic.minimise.return_data_name(self.x_data_type):
            self.x_return_value = self.relax.generic.minimise.return_value
            self.x_return_conversion_factor = self.relax.generic.minimise.return_conversion_factor
            self.x_return_units = self.relax.generic.minimise.return_units
            self.x_return_grace_string = self.relax.generic.minimise.return_grace_string

        # Test if the Y-axis data type is a minimisation statistic.
        if self.relax.generic.minimise.return_data_name(self.y_data_type):
            self.y_return_value = self.relax.generic.minimise.return_value
            self.y_return_conversion_factor = self.relax.generic.minimise.return_conversion_factor
            self.y_return_units = self.relax.generic.minimise.return_units
            self.y_return_grace_string = self.relax.generic.minimise.return_grace_string

        # Get the data.
        self.get_data()

        # Determine the graph type (ie xy, xydy, xydx, or xydxdy).
        self.determine_graph_type()

        # Write the header.
        self.write_header()

        # Write the data.
        self.write_data()

        # Close the file.
        self.file.close()


    def write_data(self):
        """Write the data into the grace file."""

        # Loop over the data.
        for i in xrange(len(self.data)):
            # Graph type xy.
            if self.graph_type == 'xy':
                # Write the data.
                self.file.write("%-30s%-30s\n" % (self.data[i][0], self.data[i][2]))

            # Graph type xydy.
            elif self.graph_type == 'xydy':
                # Catch y-axis errors of None.
                y_error = self.data[i][3]
                if y_error == None:
                    y_error = 0.0

                # Write the data.
                self.file.write("%-30s%-30s%-30s\n" % (self.data[i][0], self.data[i][2], y_error))

            # Graph type xydxdy.
            elif self.graph_type == 'xydxdy':
                # Catch x-axis errors of None.
                x_error = self.data[i][1]
                if x_error == None:
                    x_error = 0.0

                # Catch y-axis errors of None.
                y_error = self.data[i][3]
                if y_error == None:
                    y_error = 0.0

                # Write the data.
                self.file.write("%-30s%-30s%-30s%-30s\n" % (self.data[i][0], self.data[i][2], x_error, y_error))

        # End of graph 0, set 0.
        self.file.write("&\n")


    def write_header(self):
        """Write the grace header."""

        # Graph G0.
        self.file.write("@with g0\n")

        # X axis start and end.
        if self.x_data_type == 'res':
            self.file.write("@    world xmin " + `self.relax.data.res[self.run][0].num - 1` + "\n")
            self.file.write("@    world xmax " + `self.relax.data.res[self.run][-1].num + 1` + "\n")

        # X-axis label.
        if self.x_data_type == 'res':
            self.file.write("@    xaxis  label \"Residue number\"")
        else:
            # Get the units.
            units = self.x_return_units(self.x_data_type)

            # Label.
            if units:
                self.file.write("@    xaxis  label \"" + self.x_return_grace_string(self.x_data_type) + "\\N (" + units + ")\"\n")
            else:
                self.file.write("@    xaxis  label \"" + self.x_return_grace_string(self.x_data_type) + "\"\n")

        # X-axis specific settings.
        self.file.write("@    xaxis  label char size 1.48\n")
        self.file.write("@    xaxis  tick major size 0.75\n")
        self.file.write("@    xaxis  tick major linewidth 0.5\n")
        self.file.write("@    xaxis  tick minor linewidth 0.5\n")
        self.file.write("@    xaxis  tick minor size 0.45\n")
        self.file.write("@    xaxis  ticklabel char size 1.00\n")

        # Y-axis label.
        units = self.y_return_units(self.y_data_type)
        if units:
            self.file.write("@    yaxis  label \"" + self.y_return_grace_string(self.y_data_type) + "\\N (" + units + ")\"\n")
        else:
            self.file.write("@    yaxis  label \"" + self.y_return_grace_string(self.y_data_type) + "\"\n")

        # Y-axis specific settings.
        self.file.write("@    yaxis  label char size 1.48\n")
        self.file.write("@    yaxis  tick major size 0.75\n")
        self.file.write("@    yaxis  tick major linewidth 0.5\n")
        self.file.write("@    yaxis  tick minor linewidth 0.5\n")
        self.file.write("@    yaxis  tick minor size 0.45\n")
        self.file.write("@    yaxis  ticklabel char size 1.00\n")

        # Frame.
        self.file.write("@    frame linewidth 0.5\n")

        # Symbols.
        self.file.write("@    s0 symbol 9\n")
        self.file.write("@    s0 symbol size 1.00\n")
        self.file.write("@    s0 symbol fill pattern 1\n")
        self.file.write("@    s0 symbol linewidth 0.5\n")
        self.file.write("@    s0 line linestyle 0\n")

        # Error bars.
        self.file.write("@    s0 errorbar size 0.5\n")
        self.file.write("@    s0 errorbar linewidth 0.5\n")
        self.file.write("@    s0 errorbar riser linewidth 0.5\n")

        # Graph 0, set 0.
        self.file.write("@target G0.S0\n")
        self.file.write("@type " + self.graph_type + "\n")
