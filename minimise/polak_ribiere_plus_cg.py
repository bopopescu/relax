from Numeric import dot

from generic_conjugate_gradient import generic_conjugate_gradient
from generic_minimise import generic_minimise
from line_search_functions import line_search_functions


def polak_ribiere_plus(func, dfunc=None, args=(), x0=None, min_options=None, func_tol=1e-5, maxiter=1000, full_output=0, print_flag=0, a0=1.0, mu=0.0001, eta=0.1):
	"""Polak-Ribi�re + conjugate gradient algorithm.

	Page 122 from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999

	The algorithm is:

	Given x0
	Evaluate f0 = f(x0), g0 = g(x0)
	Set p0 = -g0, k = 0
	while g0 != 0:
		Compute ak and set xk+1 = xk + ak.pk
		Evaluate gk+1
		bk+1 = max(dot(gk+1, (gk+1 - gk)) / dot(gk, gk), 0)
		pk+1 = -gk+1 + bk+1.pk
		k = k + 1
	"""

	min = Polak_ribiere_plus(func, dfunc, args, x0, min_options, func_tol, maxiter, full_output, print_flag, a0, mu, eta)
	if min.init_failure:
		print "Initialisation of minimisation has failed."
		return None
	results = min.minimise()
	return results


class Polak_ribiere_plus(generic_conjugate_gradient, generic_minimise, line_search_functions):
	def __init__(self, func, dfunc, args, x0, min_options, func_tol, maxiter, full_output, print_flag, a0, mu, eta):
		"Class for Polak-Ribi�re + conjugate gradient minimisation specific functions."

		self.func = func
		self.dfunc = dfunc
		self.args = args
		self.xk = x0
		self.func_tol = func_tol
		self.maxiter = maxiter
		self.full_output = full_output
		self.print_flag = print_flag

		# Minimisation options.
		#######################

		# Initialise.
		self.init_failure = 0

		# Line search options.
		if not self.line_search_option(min_options):
			self.init_failure = 1
			return

		# Set a0.
		self.a0 = a0

		# Line search constants for the Wolfe conditions.
		self.mu = mu
		self.eta = eta

		# Initialise the function, gradient, and Hessian evaluation counters.
		self.f_count = 0
		self.g_count = 0
		self.h_count = 0

		# Initialise the warning string.
		self.warning = None

		# Line search function initialisation.
		self.init_line_functions()


	def calc_bk(self):
		"Function to calcaluate the Polak-Ribi�re + beta value"

		# Calculate beta at k+1.
		bk_new = dot(self.dfk_new, self.dfk_new - self.dfk) / self.dot_dfk
		return max(bk_new, 0.0)
