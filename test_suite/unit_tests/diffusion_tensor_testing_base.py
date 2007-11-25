###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoTensorError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError, RelaxTensorError



class Diffusion_tensor_base_class:
    """Base class for the tests of the diffusion tensor modules.
    
    This includes both the 'prompt.diffusion_tensor' and 'generic_fns.diffusion_tensor' modules.
    The base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the diffusion tensor unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        relax_data_store.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        relax_data_store.current_pipe = 'orig'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_copy_pull_ellipsoid(self):
        """Test the copying of an ellipsoid diffusion tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=1)

        # Change the current data pipe.
        relax_data_store.current_pipe = 'test'

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig')

        # Test the diffusion tensor.
        self.assertEqual(relax_data_store['test'].diff_tensor.type, 'ellipsoid')
        self.assertAlmostEqual(relax_data_store['test'].diff_tensor.tm * 1e9, 13.9, 14)
        self.assertEqual(relax_data_store['test'].diff_tensor.Da, 1.8e7)
        self.assertEqual(relax_data_store['test'].diff_tensor.Dr, 0.7)
        self.assertEqual(relax_data_store['test'].diff_tensor.alpha, 1.1752220392306203)
        self.assertEqual(relax_data_store['test'].diff_tensor.beta, 1.8327412287183442)
        self.assertEqual(relax_data_store['test'].diff_tensor.gamma, 0.34)
        self.assertEqual(relax_data_store['test'].diff_tensor.fixed, 1)


    def test_copy_pull_sphere(self):
        """Test the copying of a spherical diffusion tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Change the current data pipe.
        relax_data_store.current_pipe = 'test'

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig')

        # Test the diffusion tensor 
        self.assertEqual(relax_data_store['test'].diff_tensor.type, 'sphere')
        self.assertEqual(relax_data_store['test'].diff_tensor.tm, 1e-9)
        self.assertEqual(relax_data_store['test'].diff_tensor.fixed, 1)


    def test_copy_pull_spheroid(self):
        """Test the copying of a spheroidal diffusion tensor (pulling the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=0)

        # Change the current data pipe.
        relax_data_store.current_pipe = 'test'

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig', pipe_to='test')

        # Test the diffusion tensor.
        self.assertEqual(relax_data_store['test'].diff_tensor.type, 'spheroid')
        self.assertEqual(relax_data_store['test'].diff_tensor.spheroid_type, 'prolate')
        self.assertAlmostEqual(relax_data_store['test'].diff_tensor.tm * 1e9, 8.6, 14)
        self.assertEqual(relax_data_store['test'].diff_tensor.Da, 5.2854122621564493e6)
        self.assertEqual(relax_data_store['test'].diff_tensor.theta, 2.0943951023931948)
        self.assertEqual(relax_data_store['test'].diff_tensor.phi, 2.7925268031909276)
        self.assertEqual(relax_data_store['test'].diff_tensor.fixed, 0)


    def test_copy_push_ellipsoid(self):
        """Test the copying of an ellipsoid diffusion tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=1)

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_to='test')

        # Test the diffusion tensor.
        self.assertEqual(relax_data_store['test'].diff_tensor.type, 'ellipsoid')
        self.assertAlmostEqual(relax_data_store['test'].diff_tensor.tm * 1e9, 13.9, 14)
        self.assertEqual(relax_data_store['test'].diff_tensor.Da, 1.8e7)
        self.assertEqual(relax_data_store['test'].diff_tensor.Dr, 0.7)
        self.assertEqual(relax_data_store['test'].diff_tensor.alpha, 1.1752220392306203)
        self.assertEqual(relax_data_store['test'].diff_tensor.beta, 1.8327412287183442)
        self.assertEqual(relax_data_store['test'].diff_tensor.gamma, 0.34)
        self.assertEqual(relax_data_store['test'].diff_tensor.fixed, 1)


    def test_copy_push_sphere(self):
        """Test the copying of a spherical diffusion tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_to='test')

        # Test the diffusion tensor 
        self.assertEqual(relax_data_store['test'].diff_tensor.type, 'sphere')
        self.assertEqual(relax_data_store['test'].diff_tensor.tm, 1e-9)
        self.assertEqual(relax_data_store['test'].diff_tensor.fixed, 1)


    def test_copy_push_spheroid(self):
        """Test the copying of a spheroidal diffusion tensor (pushing the data from another pipe).

        The functions tested are both generic_fns.diffusion_tensor.copy() and
        prompt.diffusion_tensor.copy().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=0)

        # Copy the tensor to the test pipe.
        self.diffusion_tensor_fns.copy(pipe_from='orig', pipe_to='test')

        # Test the diffusion tensor.
        self.assertEqual(relax_data_store['test'].diff_tensor.type, 'spheroid')
        self.assertEqual(relax_data_store['test'].diff_tensor.spheroid_type, 'prolate')
        self.assertAlmostEqual(relax_data_store['test'].diff_tensor.tm * 1e9, 8.6, 14)
        self.assertEqual(relax_data_store['test'].diff_tensor.Da, 5.2854122621564493e6)
        self.assertEqual(relax_data_store['test'].diff_tensor.theta, 2.0943951023931948)
        self.assertEqual(relax_data_store['test'].diff_tensor.phi, 2.7925268031909276)
        self.assertEqual(relax_data_store['test'].diff_tensor.fixed, 0)


    def test_delete(self):
        """Test the deletion of the diffusion tensor data structure.

        The functions tested are both generic_fns.diffusion_tensor.delete() and
        prompt.diffusion_tensor.delete().
        """

        # Set the tm value.
        relax_data_store['orig'].diff_tensor.tm = 0.0

        # Delete the tensor data.
        self.diffusion_tensor_fns.delete()

        # Test that tm does not exist.
        self.failIf(hasattr(relax_data_store['orig'].diff_tensor, 'tm'))


    def test_delete_fail_no_data(self):
        """Failure of deletion of the diffusion tensor data structure when there is no data.

        The functions tested are both generic_fns.diffusion_tensor.delete() and
        prompt.diffusion_tensor.delete().
        """

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoTensorError, self.diffusion_tensor_fns.delete)


    def test_delete_fail_no_pipe(self):
        """Failure of deletion of the diffusion tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.diffusion_tensor.delete() and
        prompt.diffusion_tensor.delete().
        """

        # Reset the relax data store.
        relax_data_store.__reset__()

        # Try to delete the tensor data.
        self.assertRaises(RelaxNoPipeError, self.diffusion_tensor_fns.delete)


    def test_display_ellipsoid(self):
        """Display an ellipsoidal diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=1)

        # Display the diffusion tensor.
        self.diffusion_tensor_fns.display()


    def test_display_fail_no_data(self):
        """Failure of the display of the diffusion tensor data structure when there is no data.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Try to display the tensor data.
        self.assertRaises(RelaxNoTensorError, self.diffusion_tensor_fns.display)


    def test_display_fail_no_pipe(self):
        """Failure of the display of the diffusion tensor data structure when there is no data pipe.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Reset the relax data store.
        relax_data_store.__reset__()

        # Try to display the tensor data.
        self.assertRaises(RelaxNoPipeError, self.diffusion_tensor_fns.display)


    def test_display_sphere(self):
        """Display a spherical diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Display the diffusion tensor.
        self.diffusion_tensor_fns.display()


    def test_display_spheroid(self):
        """Display a spheroidal diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.display() and
        prompt.diffusion_tensor.display().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=0)

        # Display the diffusion tensor.
        self.diffusion_tensor_fns.display()



    def test_init_bad_angle_units(self):
        """Test the failure of setting up a diffusion tensor when angle_units is incorrect.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Initialise the tensor.
        self.assertRaises(RelaxError, self.diffusion_tensor_fns.init, params=1e-9, angle_units='aaa')


    def test_init_ellipsoid(self):
        """Test the setting up of a ellipsoid diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(13.9, 1.8, 0.7, 10.6, -23.3, 0.34), time_scale=1e-9, d_scale=1e7, angle_units='rad', param_types=0, fixed=1)

        # Test the diffusion tensor.
        self.assertEqual(relax_data_store['orig'].diff_tensor.type, 'ellipsoid')
        self.assertAlmostEqual(relax_data_store['orig'].diff_tensor.tm * 1e9, 13.9, 14)
        self.assertEqual(relax_data_store['orig'].diff_tensor.Da, 1.8e7)
        self.assertEqual(relax_data_store['orig'].diff_tensor.Dr, 0.7)
        self.assertEqual(relax_data_store['orig'].diff_tensor.alpha, 1.1752220392306203)
        self.assertEqual(relax_data_store['orig'].diff_tensor.beta, 1.8327412287183442)
        self.assertEqual(relax_data_store['orig'].diff_tensor.gamma, 0.34)
        self.assertEqual(relax_data_store['orig'].diff_tensor.fixed, 1)


    def test_init_sphere(self):
        """Test the setting up of a spherical diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=1e-9)

        # Test the diffusion tensor 
        self.assertEqual(relax_data_store['orig'].diff_tensor.type, 'sphere')
        self.assertEqual(relax_data_store['orig'].diff_tensor.tm, 1e-9)
        self.assertEqual(relax_data_store['orig'].diff_tensor.fixed, 1)


    def test_init_spheroid(self):
        """Test the setting up of a spheroidal diffusion tensor.

        The functions tested are both generic_fns.diffusion_tensor.init() and
        prompt.diffusion_tensor.init().
        """

        # Initialise the tensor.
        self.diffusion_tensor_fns.init(params=(8.6, 1.3, 600, -20), time_scale=1e-9, d_scale=1e7, angle_units='deg', param_types=2, spheroid_type='prolate', fixed=0)

        # Test the diffusion tensor.
        self.assertEqual(relax_data_store['orig'].diff_tensor.type, 'spheroid')
        self.assertEqual(relax_data_store['orig'].diff_tensor.spheroid_type, 'prolate')
        self.assertAlmostEqual(relax_data_store['orig'].diff_tensor.tm * 1e9, 8.6, 14)
        self.assertEqual(relax_data_store['orig'].diff_tensor.Da, 5.2854122621564493e6)
        self.assertEqual(relax_data_store['orig'].diff_tensor.theta, 2.0943951023931948)
        self.assertEqual(relax_data_store['orig'].diff_tensor.phi, 2.7925268031909276)
        self.assertEqual(relax_data_store['orig'].diff_tensor.fixed, 0)
