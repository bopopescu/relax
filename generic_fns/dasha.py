###############################################################################
#                                                                             #
# Copyright (C) 2005-2006 Edward d'Auvergne                                   #
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

from math import pi
from os import F_OK, access, chdir, getcwd, system
from re import match, search
from string import lower, split
import sys

from relax_errors import RelaxDirError, RelaxError, RelaxFileError, RelaxNoPdbError, RelaxNoRunError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNucleusError


class Dasha:
    def __init__(self, relax):
        """Class used to create and process input and output for the program Modelfree 4."""

        self.relax = relax


    def create(self, run=None, algor='LM', dir=None, force=0):
        """Function for creating the Dasha script file 'dir/dasha_script'."""

        # Arguments.
        self.run = run
        self.algor = algor
        self.dir = dir
        self.force = force

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Determine the parameter set.
        self.param_set = self.relax.specific.model_free.determine_param_set_type(self.run)

        # Test if diffusion tensor data for the run exists.
        if self.param_set != 'local_tm' and not self.relax.data.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # Test if the PDB file has been loaded (for the spheroid and ellipsoid).
        if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'sphere' and not self.relax.data.pdb.has_key(self.run):
            raise RelaxNoPdbError, self.run

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Test the optimisation algorithm.
        if algor not in ['LM', 'NR']:
            raise RelaxError, "The Dasha optimisation algorithm " + `algor` + " is unknown, it should either be 'LM' or 'NR'."

        # Directory creation.
        if self.dir == None:
            self.dir = self.run
        self.relax.IO.mkdir(self.dir, print_flag=0)

        # Number of field strengths and values.
        self.num_frq = 0
        self.frq = []
        for i in xrange(len(self.relax.data.res[self.run])):
            if hasattr(self.relax.data.res[self.run][i], 'num_frq'):
                if self.relax.data.res[self.run][i].num_frq > self.num_frq:
                    # Number of field strengths.
                    self.num_frq = self.relax.data.res[self.run][i].num_frq

                    # Field strength values.
                    for frq in self.relax.data.res[self.run][i].frq:
                        if frq not in self.frq:
                            self.frq.append(frq)

        # Calculate the angle alpha of the XH vector in the spheroid diffusion frame.
        if self.relax.data.diff[self.run].type == 'spheroid':
            self.relax.generic.angles.spheroid_frame(self.run)

        # Calculate the angles theta and phi of the XH vector in the ellipsoid diffusion frame.
        elif self.relax.data.diff[self.run].type == 'ellipsoid':
            self.relax.generic.angles.ellipsoid_frame(self.run)

        # The 'dasha_script' file.
        script = self.relax.IO.open_write_file(file_name='dasha_script', dir=self.dir, force=self.force)
        self.create_script(script)
        script.close()


    def create_script(self, file):
        """Create the Dasha script file."""

        # Delete all data.
        file.write('# Delete all data.\n')
        file.write('del 1 10000\n')

        # Nucleus type.
        file.write('\n# Nucleus type.\n')
        nucleus = self.relax.generic.nuclei.find_nucleus()
        if nucleus == 'N':
            nucleus = 'N15'
        elif nucleus == 'C':
            nucleus = 'C13'
        else:
            raise RelaxError, 'Cannot handle the nucleus type ' + `nucleus` + ' within Dasha.'
        file.write('set nucl ' + nucleus + '\n')

        # Number of frequencies.
        file.write('\n# Number of frequencies.\n')
        file.write('set n_freq ' + `self.relax.data.num_frq[self.run]` + '\n')

        # Frequency values.
        file.write('\n# Frequency values.\n')
        for i in xrange(self.relax.data.num_frq[self.run]):
            file.write('set H1_freq ' + `self.relax.data.frq[self.run][i] / 1e6` + ' ' + `i+1` + '\n')

        # Set the diffusion tensor.
        file.write('\n# Set the diffusion tensor.\n')
        if self.param_set != 'local_tm':
            # Sphere.
            if self.relax.data.diff[self.run].type == 'sphere':
                file.write('set tr ' + `self.relax.data.diff[self.run].tm / 1e-9` + '\n')

            # Spheroid.
            elif self.relax.data.diff[self.run].type == 'spheroid':
                file.write('set tr ' + `self.relax.data.diff[self.run].tm / 1e-9` + '\n')

            # Ellipsoid.
            elif self.relax.data.diff[self.run].type == 'ellipsoid':
                # Get the eigenvales.
                Dx, Dy, Dz = self.relax.generic.diffusion_tensor.return_eigenvalues(self.run)

                # Geometric parameters.
                file.write('set tr ' + `self.relax.data.diff[self.run].tm / 1e-9` + '\n')
                file.write('set D1/D3 ' + `Dx / Dz` + '\n')
                file.write('set D2/D3 ' + `Dy / Dz` + '\n')

                # Orientational parameters.
                file.write('set alfa ' + `self.relax.data.diff[self.run].alpha / (2.0 * pi) * 360.0` + '\n')
                file.write('set betta ' + `self.relax.data.diff[self.run].beta / (2.0 * pi) * 360.0` + '\n')
                file.write('set gamma ' + `self.relax.data.diff[self.run].gamma / (2.0 * pi) * 360.0` + '\n')

        # Reading the relaxation data.
        file.write('\n# Reading the relaxation data.\n')
        file.write('echo Reading the relaxation data.\n')
        noe_index = 1
        r1_index = 1
        r2_index = 1
        for i in xrange(self.relax.data.num_ri[self.run]):
            # NOE.
            if self.relax.data.ri_labels[self.run][i] == 'NOE':
                # Data set number.
                number = noe_index

                # Data type.
                data_type = 'noe'

                # Increment the data set index.
                noe_index = noe_index + 1

            # R1.
            elif self.relax.data.ri_labels[self.run][i] == 'R1':
                # Data set number.
                number = r1_index

                # Data type.
                data_type = '1/T1'

                # Increment the data set index.
                r1_index = r1_index + 1

            # R2.
            elif self.relax.data.ri_labels[self.run][i] == 'R2':
                # Data set number.
                number = r2_index

                # Data type.
                data_type = '1/T2'

                # Increment the data set index.
                r2_index = r2_index + 1

            # Set the data type.
            if number == 1:
                file.write('\nread < ' + data_type + '\n')
            else:
                file.write('\nread < ' + data_type + ' ' + `number` + '\n')

            # The relaxation data.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Reassign the data.
                data = self.relax.data.res[self.run][j]

                # Skip unselected residues.
                if not data.select:
                    continue

                # Data and errors.
                file.write(`data.num` + ' ' + `data.relax_data[i]` + ' ' + `data.relax_error[i]` + '\n')

            # Terminate the reading.
            file.write('exit\n')

        # Individual residue optimisation.
        if self.param_set == 'mf':
            # Loop over the residues.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Reassign the data.
                data = self.relax.data.res[self.run][i]

                # Skip unselected residues.
                if not data.select:
                    continue

                # Comment.
                file.write('\n\n\n# Residue ' + `data.num` + '\n\n')

                # Echo.
                file.write('echo Optimisation of residue ' + `data.num` + '\n')

                # Select the residue.
                file.write('\n# Select the residue.\n')
                file.write('set cres ' + `data.num` + '\n')

                # The angle alpha of the XH vector in the spheroid diffusion frame.
                if self.relax.data.diff[self.run].type == 'spheroid':
                    file.write('set teta ' + `data.alpha` + '\n')

                # The angles theta and phi of the XH vector in the ellipsoid diffusion frame.
                elif self.relax.data.diff[self.run].type == 'ellipsoid':
                    file.write('\n# Setting the spherical angles of the XH vector in the ellipsoid diffusion frame.\n')
                    file.write('set teta ' + `data.theta` + '\n')
                    file.write('set fi ' + `data.phi` + '\n')

                # The 'jmode'.
                if 'ts' in data.params:
                    jmode = 3
                elif 'te' in data.params:
                    jmode = 2
                elif 'S2' in data.params:
                    jmode = 1

                # Chemical exchange.
                if 'Rex' in data.params:
                    exch = 1
                else:
                    exch = 0

                # Anisotropic diffusion.
                if self.relax.data.diff[self.run].type == 'sphere':
                    anis = 0
                else:
                    anis = 1

                # Axial symmetry.
                if self.relax.data.diff[self.run].type == 'spheroid':
                    sym = 1
                else:
                    sym = 0

                # Set the jmode.
                file.write('\n# Set the jmode.\n')
                file.write('set def jmode ' + `jmode`)
                if exch:
                    file.write(' exch')
                if anis:
                    file.write(' anis')
                if sym:
                    file.write(' sym')
                file.write('\n')

                # Parameter default values.
                file.write('\n# Parameter default values.\n')
                file.write('reset jmode ' + `data.num` + '\n')

                # Bond length.
                file.write('\n# Bond length.\n')
                file.write('set r_hx ' + `data.r / 1e-10` + '\n')

                # CSA value.
                file.write('\n# CSA value.\n')
                file.write('set csa ' + `data.csa / 1e-6` + '\n')

                # Fix the tf parameter if it isn't in the model.
                if not 'tf' in data.params and jmode == 3:
                    file.write('\n# Fix the tf parameter.\n')
                    file.write('fix tf 0\n')

            # Optimisation of all residues.
            file.write('\n\n\n# Optimisation of all residues.\n')
            if self.algor == 'LM':
                file.write('lmin ' + `self.relax.data.res[self.run][0].num` + ' ' + `self.relax.data.res[self.run][-1].num`)
            elif self.algor == 'NR':
                file.write('min ' + `self.relax.data.res[self.run][0].num` + ' ' + `self.relax.data.res[self.run][-1].num`)

            # Show the results.
            file.write('\n# Show the results.\n')
            file.write('echo\n')
            file.write('show all\n')

            # Write the results.
            file.write('\n# Write the results.\n')
            file.write('write S2.out S\n')
            file.write('write S2f.out Sf\n')
            file.write('write S2s.out Ss\n')
            file.write('write te.out te\n')
            file.write('write tf.out tf\n')
            file.write('write ts.out ts\n')
            file.write('write Rex.out rex\n')
            file.write('write chi2.out F\n')

        else:
            raise RelaxError, 'Optimisation of the parameter set ' + `self.param_set` + ' currently not supported.'


    def execute(self, run, dir, force, binary):
        """Function for executing Dasha."""

        # Arguments.
        self.run = run
        self.dir = dir
        self.force = force
        self.binary = binary

        # Test the binary file string corresponds to a valid executable.
        self.relax.IO.test_binary(self.binary)

        # The current directory.
        orig_dir = getcwd()

        # The directory.
        if self.dir == None:
            self.dir = self.run
        if not access(self.dir, F_OK):
            raise RelaxDirError, ('Dasha', self.dir)

        # Change to this directory.
        chdir(self.dir)

        # Catch failures and return to the correct directory.
        try:
            # Test if the 'dasha_script' script file exists.
            if not access('dasha_script', F_OK):
                raise RelaxFileError, ('dasha script', 'dasha_script')

            # Execute Dasha.
            system(binary + ' < dasha_script | tee dasha_results')

        # Failure.
        except:
            # Change back to the original directory.
            chdir(orig_dir)

            # Reraise the error.
            raise

        # Change back to the original directory.
        chdir(orig_dir)

        # Print some blank lines (aesthetics)
        sys.stdout.write('\n\n')


    def extract(self, run, dir):
        """Function for extracting the Dasha results out of the 'dasha_results' file."""

        # Arguments.
        self.run = run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # The directory.
        if dir == None:
            dir = run
        if not access(dir, F_OK):
            raise RelaxDirError, ('Dasha', dir)

        # Loop over the parameters.
        for param in ['S2', 'S2f', 'S2s', 'te', 'tf', 'ts', 'Rex']:
            # The file name.
            file_name = dir + '/' + param + '.out'

            # Test if the file exists.
            if not access(file_name, F_OK):
                raise RelaxFileError, ('Dasha', file_name)

            # Scaling.
            if param in ['te', 'tf', 'ts']:
                scaling = 1e-9
            elif param == 'Rex':
                scaling = 1.0 / (2.0 * pi * self.relax.data.frq[self.run][0]) ** 2
            else:
                scaling = 1.0

            # Set the values.
            self.relax.generic.value.read(self.run, param=param, scaling=scaling, file=file_name, num_col=0, name_col=None, data_col=1, error_col=2)

            # Clean up of non-existant parameters (set the parameter to None!).
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Skip the residue (don't set the parameter to None) if the parameter exists in the model.
                if param in self.relax.data.res[self.run][i].params:
                    continue

                # Set the parameter to None.
                setattr(self.relax.data.res[self.run][i], lower(param), None)

        # Extract the chi-squared values.
        file_name = dir + '/chi2.out'

        # Test if the file exists.
        if not access(file_name, F_OK):
            raise RelaxFileError, ('Dasha', file_name)

        # Set the values.
        self.relax.generic.value.read(self.run, param='chi2', file=file_name, num_col=0, name_col=None, data_col=1, error_col=2)
