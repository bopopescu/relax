class Model:
    def __init__(self, relax):
        """Class for holding the preset model macros."""

        self.relax = relax

        self.create_mf = self.relax.model_free.create
        self.select_mf = self.relax.model_free.select
