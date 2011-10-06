###############################################################################
#                                                                             #
# Copyright (C) 2008-2011 Edward d'Auvergne                                   #
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
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import sys
try:
    from unittest import TextTestResult    # Python 2.7 and above.
except ImportError:
    from unittest import _TextTestResult as TextTestResult    # Python 2.6 and below.
from unittest import TextTestRunner
import wx

# relax module imports.
from status import Status; status = Status()


class RelaxTestResult(TextTestResult):
    """A replacement for the TextTestResult class.

    This class is designed to catch STDOUT and STDERR during the execution of each test and to
    prepend the output to the failure and error reports normally generated by TextTestRunner.
    """

    def startTest(self, test):
        """Override of the TextTestResult.startTest() method.

        The start of STDOUT and STDERR capture occurs here.
        """

        # Store the original STDOUT and STDERR for restoring later on.
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

        # Catch stdout and stderr.
        self.capt = StringIO()
        if not status.debug:
            sys.stdout = self.capt
            sys.stderr = self.capt

        # Place the test name in the status object.
        status.exec_lock.test_name = str(test)

        # Execute the normal startTest method.
        TextTestResult.startTest(self, test)


    def stopTest(self, test):
        """Override of the TextTestResult.stopTest() method.

        The end of STDOUT and STDERR capture occurs here.
        """

        # Restore the IO streams.
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr


    def addError(self, test, err):
        """Override of the TestResult.addError() method.

        The STDOUT and STDERR captured text is prepended to the error text here.
        """

        # Execute the normal addError method.
        TextTestResult.addError(self, test, err)

        # Prepend the STDOUT and STDERR messages to the second element of the tuple.
        self.errors[-1] = (self.errors[-1][0], self.capt.getvalue() + self.errors[-1][1])


    def addFailure(self, test, err):
        """Override of the TestResult.addFailure() method.

        The STDOUT and STDERR captured text is prepended to the failure text here.
        """

        # Execute the normal addFailure method.
        TextTestResult.addFailure(self, test, err)

        # Prepend the STDOUT and STDERR messages to the second element of the tuple.
        self.failures[-1] = (self.failures[-1][0], self.capt.getvalue() + self.failures[-1][1])



class GuiTestResult(RelaxTestResult):
    """A replacement for the TextTestResult class for the GUI."""

    def stopTest(self, test):
        """Override of the RelaxTestResult.stopTest() method.

        The end of STDOUT and STDERR capture occurs here.
        """

        # Execute the RelaxTestResult.stopTest() method.
        super(GuiTestResult, self).stopTest(test)

        # Yield to allow the GUI to be updated.
        wx.GetApp().Yield(True)



class RelaxTestRunner(TextTestRunner):
    """A replacement unittest runner.

    This runner is designed to catch STDOUT during the execution of each test and to prepend the
    output to the failure and error reports normally generated by TextTestRunner.
    """

    def _makeResult(self):
        """Override of the TextTestRunner._makeResult() method."""

        return RelaxTestResult(self.stream, self.descriptions, self.verbosity)



class GuiTestRunner(TextTestRunner):
    """A replacement unittest runner.

    This runner is designed to catch STDOUT during the execution of each test and to prepend the
    output to the failure and error reports normally generated by TextTestRunner.
    """

    def _makeResult(self):
        """Override of the TextTestRunner._makeResult() method."""

        return GuiTestResult(self.stream, self.descriptions, self.verbosity)
