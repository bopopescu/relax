###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""Target functions for relaxation dispersion."""

# Python module imports.
from numpy import dot, float64, zeros

# relax module imports.
from lib.dispersion.cr72 import r2eff_CR72
from lib.dispersion.dpl94 import r1rho_DPL94
from lib.dispersion.it99 import r2eff_IT99
from lib.dispersion.lm63 import r2eff_LM63
from lib.dispersion.m61 import r1rho_M61
from lib.dispersion.m61b import r1rho_M61b
from lib.dispersion.ns_2site_star import r2eff_ns_2site_star
from lib.errors import RelaxError
from target_functions.chi2 import chi2
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_DPL94, MODEL_IT99, MODEL_LIST_FULL, MODEL_LM63, MODEL_M61, MODEL_M61B, MODEL_NOREX, MODEL_NS_2SITE_STAR, MODEL_R2EFF


class Dispersion:
    def __init__(self, model=None, num_params=None, num_spins=None, num_frq=None, num_disp_points=None, values=None, errors=None, missing=None, frqs=None, cpmg_frqs=None, spin_lock_nu1=None, scaling_matrix=None):
        """Relaxation dispersion target functions for optimisation.

        Models
        ======

        The following analytic models are currently supported:

            - 'No Rex':  The model for no chemical exchange relaxation.
            - 'LM63':  The Luz and Meiboom (1963) 2-site fast exchange model.
            - 'CR72':  The Carver and Richards (1972) 2-site model for all time scales.
            - 'IT99':  The Ishima and Torchia (1999) 2-site model for all time scales with skewed populations (pA >> pB).
            - 'M61':  The Meiboom (1961) 2-site fast exchange model for R1rho-type experiments.
            - 'DPL94':  The Davis, Perlman and London (1994) 2-site fast exchange model for R1rho-type experiments.
            - 'M61 skew':  The Meiboom (1961) on-resonance 2-site model with skewed populations (pA >> pB) for R1rho-type experiments.

        The following numerical models are currently supported:

            - 'NS 2-site star':  The numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices.


        @keyword model:             The relaxation dispersion model to fit.
        @type model:                str
        @keyword num_param:         The number of parameters in the model.
        @type num_param:            int
        @keyword num_spins:         The number of spins in the cluster.
        @type num_spins:            int
        @keyword num_frq:           The number of spectrometer field strengths.
        @type num_frq:              int
        @keyword num_disp_points:   The number of points on the dispersion curve.
        @type num_disp_points:      int
        @keyword values:            The R2eff/R1rho values.  The first dimension is that of the spin cluster (each element corresponds to a different spin in the block), the second dimension is the spectrometer field strength, and the third is the dispersion points.
        @type values:               numpy rank-3 float array
        @keyword errors:            The R2eff/R1rho errors.  The three dimensions must correspond to those of the values argument.
        @type errors:               numpy rank-3 float array
        @keyword missing:           The data structure indicating missing R2eff/R1rho data.  The three dimensions must correspond to those of the values argument.
        @type missing:              numpy rank-3 int array
        @keyword frqs:              The spin Larmor frequencies (in MHz*2pi to speed up the ppm to rad/s conversion).  The dimensions correspond to the first two of the value, error and missing structures.
        @type frqs:                 numpy rank-2 float array
        @keyword cpmg_frqs:         The CPMG frequencies in Hertz for each separate dispersion point.  This will be ignored for R1rho experiments.
        @type cpmg_frqs:            numpy rank-1 float array
        @keyword spin_lock_nu1:     The spin-lock field strengths in Hertz for each separate dispersion point.  This will be ignored for CPMG experiments.
        @type spin_lock_nu1:        numpy rank-1 float array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        """

        # Check the args.
        if model not in MODEL_LIST_FULL:
            raise RelaxError("The model '%s' is unknown." % model)
        if values == None:
            raise RelaxError("No values have been supplied to the target function.")
        if errors == None:
            raise RelaxError("No errors have been supplied to the target function.")
        if missing == None:
            raise RelaxError("No missing data information has been supplied to the target function.")

        # Store the arguments.
        self.num_params = num_params
        self.num_spins = num_spins
        self.num_frq = num_frq
        self.num_disp_points = num_disp_points
        self.values = values
        self.errors = errors
        self.missing = missing
        self.frqs = frqs
        self.cpmg_frqs = cpmg_frqs
        self.spin_lock_nu1 = spin_lock_nu1
        self.scaling_matrix = scaling_matrix

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = zeros((num_spins, num_frq, num_disp_points), float64)

        # The post spin parameter indices.
        self.end_index = []
        self.end_index.append(self.num_spins * self.num_frq)
        if model == MODEL_NS_2SITE_STAR:
            self.end_index.append(self.num_spins * self.num_frq)
        self.end_index.append(self.end_index[-1] + self.num_spins)
        if model == MODEL_IT99:
            self.end_index.append(self.end_index[-1] + self.num_spins)

        # Set up the model.
        if model == MODEL_NOREX:
            self.func = self.func_NOREX
        if model == MODEL_LM63:
            self.func = self.func_LM63
        if model == MODEL_CR72:
            self.func = self.func_CR72
        if model == MODEL_IT99:
            self.func = self.func_IT99
        if model == MODEL_M61:
            self.func = self.func_M61
        if model == MODEL_DPL94:
            self.func = self.func_DPL94
        if model == MODEL_M61B:
            self.func = self.func_M61b
        if model == MODEL_NS_2SITE_STAR:
            self.func = self.func_ns_2site_star


    def func_CR72(self, params):
        """Target function for the Carver and Richards (1972) 2-site exchange model on all time scales.

        This assumes that pA > pB, and hence this must be implemented as a constraint.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[spin_index] * self.frqs[spin_index, frq_index]

                # Back calculate the R2eff values.
                r2eff_CR72(r20=R20[r20_index], pA=pA, dw=dw_frq, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_DPL94(self, params):
        """Target function for the Davis, Perlman and London (1994) fast 2-site exchange model for R1rho-type experiments.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r1rho_DPL94(r1rho_prime=R20[r20_index], phi_ex=phi_ex_scaled, kex=kex, spin_lock_fields=self.spin_lock_nu1, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_IT99(self, params):
        """Target function for the Ishima and Torchia (1999) 2-site model for all timescales with pA >> pB.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        padw2 = params[self.end_index[1]:self.end_index[2]]
        tex = params[self.end_index[2]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex and pa.dw^2 from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2
                padw2_scaled = padw2[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r2eff_IT99(r20=R20[r20_index], phi_ex=phi_ex_scaled, padw2=padw2_scaled, tex=tex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_LM63(self, params):
        """Target function for the Luz and Meiboom (1963) fast 2-site exchange model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r2eff_LM63(r20=R20[r20_index], phi_ex=phi_ex_scaled, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_M61(self, params):
        """Target function for the Meiboom (1961) fast 2-site exchange model for R1rho-type experiments.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert phi_ex from ppm^2 to (rad/s)^2.
                phi_ex_scaled = phi_ex[spin_index] * self.frqs[spin_index, frq_index]**2

                # Back calculate the R2eff values.
                r1rho_M61(r1rho_prime=R20[r20_index], phi_ex=phi_ex_scaled, kex=kex, spin_lock_fields=self.spin_lock_nu1, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_M61b(self, params):
        """Target function for the Meiboom (1961) R1rho on-resonance 2-site model for skewed populations (pA >> pB).

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[spin_index] * self.frqs[spin_index, frq_index]

                # Back calculate the R1rho values.
                r1rho_M61b(r1rho_prime=R20[r20_index], pA=pA, dw=dw_frq, kex=kex, spin_lock_fields=self.spin_lock_nu1, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_NOREX(self, params):
        """Target function for no exchange.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # The R2eff values as R20 values.
                for i in range(self.num_disp_points):
                    self.back_calc[spin_index, frq_index, i] = R20[r20_index]

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum


    def func_ns_2site_star(self, params):
        """Target function for the numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20A = params[:self.end_index[0]]
        R20B = params[self.end_index[0]:self.end_index[1]]
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for spin_index in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for frq_index in range(self.num_frq):
                # The R20 index.
                r20_index = frq_index + spin_index*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[spin_index] * self.frqs[spin_index, frq_index]

                # Back calculate the R2eff values.
                r2eff_ns_2site_star(r20a=R20A[r20_index], r20b=R20B[r20_index], pA=pA, dw=dw_frq, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc[spin_index, frq_index], num_points=self.num_disp_points)

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for point_index in range(self.num_disp_points):
                    if self.missing[spin_index, frq_index, point_index]:
                        self.back_calc[spin_index, frq_index, point_index] = self.values[spin_index, frq_index, point_index]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[spin_index, frq_index], self.back_calc[spin_index, frq_index], self.errors[spin_index, frq_index])

        # Return the total chi-squared value.
        return chi2_sum
