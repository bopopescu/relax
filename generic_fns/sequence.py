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

from os import F_OK, access, makedirs


class Sequence:
    def __init__(self, relax):
        """Class containing functions specific to amino-acid sequence."""

        self.relax = relax


    def add(self, run=None, res_num=None, res_name=None, select=1):
        """Function for adding a residue onto the sequence."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Initialise the sequence data if no sequence currently exists.
        if not self.relax.data.res.has_key(run):
            # Add the run to 'self.relax.data.res'.
            self.relax.data.res.add_list(run)

        # Test if the residue number already exists.
        for i in xrange(len(self.relax.data.res[run])):
            if self.relax.data.res[run][i].num == res_num:
                raise RelaxError, "The residue number '" + `res_num` + "' already exists in the sequence."

        # Residue index.
        index = len(self.relax.data.res[run])

        # Append a data container.
        self.relax.data.res[run].add_element()

        # Insert the data.
        self.relax.data.res[run][index].num = res_num
        self.relax.data.res[run][index].name = res_name
        self.relax.data.res[run][index].select = select


    def copy(self, run1=None, run2=None):
        """Function for copying the sequence from run1 to run2."""

        # Test if run1 exists.
        if not run1 in self.relax.data.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in self.relax.data.run_names:
            raise RelaxNoRunError, run2

        # Test if the sequence data for run1 is loaded.
        if not self.relax.data.res.has_key(run1):
            raise RelaxNoSequenceError

        # Test if the sequence data already exists.
        if self.relax.data.res.has_key(run2):
            raise RelaxSequenceError, run2

        # Add run2 to 'self.relax.data.res'.
        self.relax.data.res.add_list(run2)

        # Copy the data.
        for i in xrange(len(self.relax.data.res[run1])):
            # Append a data container to run2.
            self.relax.data.res[run2].add_element()

            # Insert the data.
            self.relax.data.res[run2][i].num = self.relax.data.res[run1][i].num
            self.relax.data.res[run2][i].name = self.relax.data.res[run1][i].name
            self.relax.data.res[run2][i].select = self.relax.data.res[run1][i].select


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        return [ 'res' ]


    def delete(self, run=None):
        """Function for deleting the sequence."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Delete the data.
        del(self.relax.data.res[run])

        # Clean run.
        self.relax.generic.delete.clean_runs()


    def display(self, run=None):
        """Function for displaying the sequence."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Print a header.
        print "%-8s%-8s%-10s" % ("Number", "Name", "Selected")
        
        # Print the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            print "%-8i%-8s%-10i" % (self.relax.data.res[run][i].num, self.relax.data.res[run][i].name, self.relax.data.res[run][i].select)


    def load_PDB_sequence(self, run=None):
        """Function for loading the sequence out of a PDB file.

        This needs to be modified to handle multiple peptide chains.
        """

        print "Loading the sequence from the PDB file.\n"

        # Reassign the sequence of the first structure.
        if type(self.relax.data.pdb[run]) == list:
            res = self.relax.data.pdb[run][0].peptide_chains[0].residues
        else:
            res = self.relax.data.pdb[run].peptide_chains[0].residues

        # Add the run to 'self.relax.data.res'.
        self.relax.data.res.add_list(run)

        # Loop over the sequence.
        for i in xrange(len(res)):
            # Append a data container.
            self.relax.data.res[run].add_element()

            # Insert the data.
            self.relax.data.res[run][i].num = res[i].number
            self.relax.data.res[run][i].name = res[i].name
            self.relax.data.res[run][i].select = 1


    def read(self, run=None, file=None, dir=None, num_col=0, name_col=1, sep=None, header_lines=None):
        """Function for reading sequence data."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data has already been read.
        if self.relax.data.res.has_key(run):
            raise RelaxSequenceError, run

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file)

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Test if the sequence data is valid.
        for i in xrange(len(file_data)):
            try:
                int(file_data[i][num_col])
            except ValueError:
                raise RelaxError, "Sequence data is invalid."

        # Add the run to 'self.relax.data.res'.
        self.relax.data.res.add_list(run)

        # Fill the array 'self.relax.data.res[run]' with data containers and place sequence data into the array.
        for i in xrange(len(file_data)):
            # Append a data container.
            self.relax.data.res[run].add_element()

            # Insert the data.
            self.relax.data.res[run][i].num = int(file_data[i][num_col])
            self.relax.data.res[run][i].name = file_data[i][name_col]
            self.relax.data.res[run][i].select = 1


    def sort(self, run=None):
        """Function for sorting the sequence by residue number."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Sort the sequence.
        self.relax.data.res[run].sort(self.sort_cmpfunc)


    def sort_cmpfunc(self, x, y):
        """Sequence comparison function given to the ListType function 'sort'."""

        if x.num > y.num:
            return 1
        elif x.num < y.num:
            return -1
        elif x.num == y.num:
            return 0


    def write(self, run=None, file=None, dir=None, force=0):
        """Function for writing sequence data."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Create the directories.
        if dir:
            try:
                makedirs(dir)
            except OSError:
                pass

        # The file.
        if dir:
            file_name = dir + '/' + file
        else:
            file_name = file

        if access(file_name, F_OK) and not force:
            raise RelaxFileOverwriteError, (file_name, 'force flag')
        seq_file = open(file_name, 'w')

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Residue number.
            seq_file.write("%-5i" % self.relax.data.res[run][i].num)

            # Residue name.
            seq_file.write("%-6s" % self.relax.data.res[run][i].name)

            # New line.
            seq_file.write("\n")

        # Close the results file.
        seq_file.close()
