###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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


# Import statements.
from os import getcwd, path, sep, system, walk
from re import search
from tarfile import TarFile
from zipfile import ZipFile



def gpg_sign(target, source, env):
    """Builder action for creating a GPG signature of the binary distribution file."""

    # Print out.
    print
    print "############################################"
    print "# GPG signing the binary distribution file #"
    print "############################################\n\n"

    # Run the 'gpg' command.
    system("gpg --detach-sign --default-key relax " + path.pardir + path.sep + env['DIST_FILE'])

    # Final print out.
    print "\n\n\n"


def package(target, source, env):
    """Builder action for packaging the distribution archives."""

    # Print out.
    print
    print "#######################"
    print "# Packaging the files #"
    print "#######################\n\n"
    print "Creating the package distribution " + `env['DIST_FILE']` + ".\n"

    # Open the Zip distribution file.
    if env['DIST_TYPE'] == 'zip':
        archive = ZipFile(path.pardir + path.sep + env['DIST_FILE'], 'w', compression=8)

    # Open the Tar distribution file.
    elif env['DIST_TYPE'] == 'tar':
        if search('.bz2$', env['DIST_FILE']):
            archive = TarFile.bz2open(path.pardir + path.sep + env['DIST_FILE'], 'w')
        elif search('.gz$', env['DIST_FILE']):
            archive = TarFile.gzopen(path.pardir + path.sep + env['DIST_FILE'], 'w')
        else:
            archive = TarFile.open(path.pardir + path.sep + env['DIST_FILE'], 'w')

    # Base directory.
    base = getcwd() + sep

    # Walk through the directories.
    for root, dirs, files in walk(getcwd()):
        # Skip the subversion directories.
        if search("\.svn", root):
            continue

        # Add the files in the current directory to the archive.
        for i in xrange(len(files)):
            # Skip any '.sconsign' files, hidden files, byte-compiled '*.pyc' files, or binary objects '.o', '.os', 'obj', 'lib', and 'exp'.
            if search("\.sconsign", files[i]) or search("^\.", files[i]) or search("\.pyc$", files[i]) or search("\.o$", files[i]) or search("\.os$", files[i]) or search("\.obj$", files[i]) or search("\.lib$", files[i]) or search("\.exp$", files[i]):
                continue

            # Create the file name (without the base directory).
            name = path.join(root, files[i])
            name = name[len(base):]
            print 'relax-' + env['RELAX_VERSION'] + path.sep + name

            # The archive file name.
            arcname = 'relax-' + env['RELAX_VERSION'] + path.sep + name

            # Zip archives.
            if env['DIST_TYPE'] == 'zip':
                archive.write(filename=name, arcname=arcname)

            # Tar archives.
            if env['DIST_TYPE'] == 'tar':
                archive.add(name=name, arcname=arcname)

    # Close the archive.
    archive.close()

    # Final print out.
    print "\n\n\n"
