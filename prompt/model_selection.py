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

import sys


class Modsel:
    def __init__(self, relax):
        """Class containing the function for selecting which model selection method should be used."""

        self.relax = relax


    def model_selection(self, method=None, modsel_run=None, runs=None):
        """Function for model selection.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        method:  The model selection technique (see below).

        modsel_run:  The run name to assign to the results of model selection.

        runs:  An array containing the names of all runs to include in model selection.


        Description
        ~~~~~~~~~~~

        The following model selection methods are supported:

        AIC:  Akaike's Information Criteria.

        AICc:  Small sample size corrected AIC.

        BIC:  Bayesian or Schwarz Information Criteria.

        Bootstrap:  Bootstrap model selection.

        CV:  Single-item-out cross-validation.

        Expect:  The expected overall discrepancy (the true values of the parameters are required).

        Farrow:  Old model-free method by Farrow et al., 1994.

        Palmer:  Old model-free method by Mandel et al., 1995.

        Overall:  The realised overall discrepancy (the true values of the parameters are required).


        If the runs argument is not supplied then all runs currently set or loaded will be used for
        model selection, although this could cause problems.


        Example
        ~~~~~~~

        For model-free analysis, if the preset models 1 to 5 are minimised and loaded into the
        program, the following commands will carry out AIC model selection and assign the results
        to the run name 'mixed':

        relax> model_selection('AIC', 'mixed')
        relax> model_selection(method='AIC', modsel_run='mixed')
        relax> model_selection('AIC', 'mixed', ['m1', 'm2', 'm3', 'm4', 'm5'])
        relax> model_selection(method='AIC', modsel_run='mixed', runs=['m1', 'm2', 'm3', 'm4', 'm5'])
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "model_selection("
            text = text + "method=" + `method`
            text = text + ", modsel_run=" + `modsel_run`
            text = text + ", runs=" + `runs` + ")"
            print text

        # Method.
        if type(method) != str:
            raise RelaxStrError, ('model selection method', method)

        # New run modsel_run.
        if type(modsel_run) != str:
            raise RelaxStrError, ('modsel_run', modsel_run)

        # Runs.
        if runs == None:
            pass
        elif type(runs) != list:
            raise RelaxNoneListError, ('runs', runs)
        else:
            for name in runs:
                if type(name) == list:
                    for name2 in name:
                        if type(name2) != str:
                            raise RelaxError, "The elements of the second dimension of the runs argument must be strings."
                elif type(name) != str:
                    raise RelaxError, "The elements of the first dimension of the runs argument must be either strings or arrays."

        # Execute the functional code.
        self.relax.generic.model_selection.select(method=method, modsel_run=modsel_run, runs=runs)
