# A method based on model selection using bootstrap criteria.
#
# The Kullback-Leibeler discrepancy is used.
#
# The program is divided into the following stages:
#	Stage 1:  Creation of the files for the model-free calculations for models 1 to 5.  Monte Carlo
#		simulations are used, but the initial data rather than the backcalculated data is randomized.
#	Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors.  This stage has the option of optimizing the diffusion tensor along with the
#		model-free parameters.
#	Stage 3:  Extraction of the data.

from re import match

from common_ops import common_operations


class bootstrap(common_operations):
	def __init__(self, mf):
		"Model-free analysis based on bootstrap model selection."

		self.mf = mf

		print "Model-free analysis based on bootstrap model selection."
		self.mf.data.stage = self.ask_stage()

		title = "<<< Stage " + self.mf.data.stage + " of the bootstrap criteria based model-free analysis >>>\n\n\n"
		self.start_up(self.mf.data.stage, title)
		
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']

		if match('1', self.mf.data.stage):
			print "\n[ Stage 1 ]\n"
			self.initial_runs()
			print "\n[ End of stage 1 ]\n\n"

		if match('^2', self.mf.data.stage):
			print "\n[ Stage 2 ]\n"
			self.mf.file_ops.mkdir('final')
			self.stage2()
			if match('a$', self.mf.data.stage):
				self.final_run()
			if match('b$', self.mf.data.stage):
				self.final_run_optimized()
			print "\n[ End of stage 2 ]\n\n"

		if match('3', self.mf.data.stage):
			print "\n[ Stage 3 ]\n"
			self.stage3()
			print "\n[ End of stage 3 ]\n\n"


	def initial_runs(self):
		"Creation of the files for the Modelfree calculations for models 1 to 5."
		
		for run in self.mf.data.runs:
			print "Creating input files for model " + run
			self.mf.log.write("\n\n<<< Model " + run + " >>>\n\n")
			self.mf.file_ops.mkdir(dir=run)
			self.mf.file_ops.open_mf_files(dir=run)
			self.set_run_flags(run)
			self.log_params('M1', self.mf.data.usr_param.md1)
			self.log_params('M2', self.mf.data.usr_param.md2)
			self.create_mfin(sims='y', sim_type='expr')
			self.create_run(dir=run)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				self.create_mfmodel(res, self.mf.data.usr_param.md1, type='M1')
				# Mfpar.
				self.create_mfpar(res)
			self.mf.file_ops.close_mf_files(dir=run)
