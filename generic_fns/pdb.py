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

from math import sqrt
from Numeric import Float64, dot, zeros
from os import F_OK, access
import Scientific.IO.PDB


class PDB:
    def __init__(self, relax):
        """Class containing the PDB related functions."""

        self.relax = relax

        # Print flag.
        self.print_flag = 1


    def load_structures(self):
        """Function for loading the structures from the PDB file."""

        # Use pointers (references) if the PDB data exists in another run.
        for run in self.relax.data.run_names:
            if self.relax.data.pdb.has_key(run) and hasattr(self.relax.data.pdb[run], 'structures') and self.relax.data.pdb[run].file_name == self.file and self.relax.data.pdb[run].model == self.model:
                # Make a pointer to the data.
                self.relax.data.pdb[self.run].structures = self.relax.data.pdb[run].structures

                # Print out.
                if self.print_flag:
                    print "Using the structures from the run " + `run` + "."
                    for i in xrange(len(self.relax.data.pdb[self.run].structures)):
                        print self.relax.data.pdb[self.run].structures[i]

                # Exit this function.
                return

        # Initialisation.
        self.relax.data.pdb[self.run].structures = []

        # Load the structure i from the PDB file.
        if type(self.model) == int:
            # Print out.
            if self.print_flag:
                print "Loading structure " + `self.model` + " from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(self.file_path, self.model)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, self.file_path

            # Print the PDB info.
            if self.print_flag:
                print str

            # Place the structure in 'self.relax.data.pdb[self.run]'.
            self.relax.data.pdb[self.run].structures.append(str)


        # Load all structures.
        else:
            # Print out.
            if self.print_flag:
                print "Loading all structures from the PDB file."

            # First model.
            i = 1

            # Loop over all the other structures.
            while 1:
                # Load the pdb files.
                str = Scientific.IO.PDB.Structure(self.file_path, i)

                # No model 1.
                if len(str) == 0 and i == 1:
                    str = Scientific.IO.PDB.Structure(self.file_path)
                    if len(str) == 0:
                        raise RelaxPdbLoadError, self.file_path

                # Test if the last structure has been reached.
                if len(str) == 0:
                    del str
                    break

                # Print the PDB info.
                if self.print_flag:
                    print str

                # Place the structure in 'self.relax.data.pdb[self.run]'.
                self.relax.data.pdb[self.run].structures.append(str)

                # Increment i.
                i = i + 1


    def read(self, run=None, file=None, dir=None, model=None, load_seq=1, fail=1, print_flag=1):
        """The pdb loading function."""

        # Arguments.
        self.run = run
        self.file = file
        self.dir = dir
        self.model = model
        self.load_seq = load_seq
        self.fail = fail
        self.print_flag = print_flag

        # Tests.
        ########

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if PDB data corresponding to the run already exists.
        if self.relax.data.pdb.has_key(self.run):
            raise RelaxPdbError, self.run

        # Test if sequence data is loaded.
        if not self.load_seq and not len(self.relax.data.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # The file path.
        self.file_path = self.relax.IO.file_path(self.file, self.dir)

        # Test if the file exists.
        if not access(self.file_path, F_OK):
            if fail:
                raise RelaxFileError, ('PDB', self.file_path)
            else:
                warn(RelaxNoPDBFileWarning(self.file_path))
                return

        # Test that the nuclei have been correctly set.
        if self.heteronuc == self.proton:
            raise RelaxError, "The proton and heteronucleus are set to the same atom."


        # Data creation.
        ################

        # Add the run to the PDB data structure.
        self.relax.data.pdb.add_item(self.run)

        # File name.
        self.relax.data.pdb[self.run].file_name = self.file_path

        # Model.
        self.relax.data.pdb[self.run].model = model

        # Nuclei.
        self.relax.data.pdb[self.run].proton = proton
        self.relax.data.pdb[self.run].heteronuc = heteronuc


        # Load the structures.
        ######################

        self.load_structures()


        # Finish.
        #########

        # Sequence loading.
        if self.load_seq and not self.relax.data.res.has_key(self.run):
            self.relax.generic.sequence.load_PDB_sequence(self.run)

        # Load into Molmol (if running).
        self.relax.generic.molmol.open_pdb(self.run)


    def set_vector(self, run=None, res=None, xh_vect=None):
        """Function for setting the XH unit vectors."""

        # Place the XH unit vector in 'self.relax.data.res'.
        self.relax.data.res[run][res].xh_vect = xh_vect


    def vectors(self, heteronuc=None, proton=None, res_num=None, res_name=None):
        """Function for calculating/extracting the XH unit vector from the loaded structure."""

        # Arguments.
        self.heteronuc = heteronuc
        self.proton = proton

        # Test if the PDB file has been loaded.
        if not self.relax.data.pdb.has_key(run):
            raise RelaxPdbError, run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the residue number is a valid regular expression.
        if type(num) == str:
            try:
                compile(num)
            except:
                raise RelaxRegExpError, ('residue number', num)

        # Test if the residue name is a valid regular expression.
        if name:
            try:
                compile(name)
            except:
                raise RelaxRegExpError, ('residue name', name)

        # Print out.
        if self.print_flag:
            print "\nCalculating unit XH vectors.\n"

        # Number of structures.
        num_str = len(self.relax.data.pdb[self.run].structures)

        # Create a temporary vector list for each residue.
        for i in xrange(len(self.relax.data.res[self.run])):
            self.relax.data.res[self.run][i].xh_vect = []

        # Loop over the structures.
        for i in xrange(num_str):
            # Print out.
            if self.print_flag:
                print "\nStructure " + `i + 1` + "\n"

            # Reassign the first peptide or nucleotide chain of the first structure.
            if self.relax.data.pdb[self.run].structures[i].peptide_chains:
                pdb_residues = self.relax.data.pdb[self.run].structures[i].peptide_chains[0].residues
            elif self.relax.data.pdb[self.run].structures[i].nucleotide_chains:
                pdb_residues = self.relax.data.pdb[self.run].structures[i].nucleotide_chains[0].residues
            else:
                raise RelaxNoPdbChainError

            # Loop over the sequence.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Remap the data structure 'self.relax.data.res[self.run][j]'.
                data = self.relax.data.res[self.run][j]

                # Skip unselected residues.
                if not data.select:
                    continue

                # Skip the residue if there is no match to 'num'.
                if type(num) == int:
                    if not data.num == num:
                        continue
                elif type(num) == str:
                    if not match(num, `data.num`):
                        continue

                # Skip the residue if there is no match to 'name'.
                if name != None:
                    if not match(name, data.name):
                        continue

                # Find the corresponding residue in the PDB.
                pdb_res = None
                for k in xrange(len(pdb_residues)):
                    if data.num == pdb_residues[k].number:
                        pdb_res = pdb_residues[k]
                        break
                if pdb_res == None:
                    raise RelaxNoResError, data.num

                # Test if the proton atom exists for residue i.
                if not pdb_res.atoms.has_key(self.proton):
                    warn(RelaxNoAtomWarning(self.proton, data.num))
                    data.xh_vect.append(None)

                # Test if the heteronucleus atom exists for residue i.
                elif not pdb_res.atoms.has_key(self.heteronuc):
                    warn(RelaxNoAtomWarning(self.heteronuc, data.num))
                    data.xh_vect.append(None)

                # Calculate the vector.
                else:
                    # Get the proton position.
                    posH = pdb_res.atoms[self.proton].position.array

                    # Get the heteronucleus position.
                    posX = pdb_res.atoms[self.heteronuc].position.array

                    # Calculate the XH bond vector.
                    vector = posH - posX

                    # Normalisation factor.
                    norm_factor = sqrt(dot(vector, vector))

                    # Test for zero length.
                    if norm_factor == 0.0:
                        if self.print_flag:
                            print "The XH bond vector for residue " + `data.num` + " is of zero length."
                        data.xh_vect.append(None)

                    # Calculate the normalised vector.
                    else:
                        data.xh_vect.append(vector / norm_factor)

        # Print out.
        if self.print_flag:
            if num_str > 1:
                print "\nCalculating and averaging the unit XH vectors from all structures."
            else:
                print "\nCalculating the unit XH vectors from the structure."

        # Average the vectors and convert xh_vect from an array of vectors to a vector.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][j]'.
            data = self.relax.data.res[self.run][j]

            # Skip unselected residues.
            if not data.select:
                continue

            # Skip the residue if there is no match to 'num'.
            if type(num) == int:
                if not data.num == num:
                    continue
            elif type(num) == str:
                if not match(num, `data.num`):
                    continue

            # Skip the residue if there is no match to 'name'.
            if name != None:
                if not match(name, data.name):
                    continue

            # No vectors.
            if data.xh_vect[0] == None:
                del data.xh_vect
                continue

            # Average vectors.
            ave_vector = zeros(3, Float64)

            # Sum the vectors.
            for j in xrange(num_str):
                # Sum.
                ave_vector = ave_vector + data.xh_vect[j]

            # Average the vector.
            ave_vector = ave_vector / num_str

            # Replace the temporary vector list with the normalised average vector.
            data.xh_vect = ave_vector / sqrt(dot(ave_vector, ave_vector))
