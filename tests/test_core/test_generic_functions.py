import unittest

import numpy as np
import numpy.testing as npt

from gaiaxpy import generate, PhotometricSystem
from gaiaxpy.core.generic_functions import _get_system_label, _extract_systems_from_data, validate_pwl_sampling, \
    array_to_symmetric_matrix, correlation_to_covariance, get_matrix_size_from_lower_triangle
from tests.files.paths import mean_spectrum_fits_file

array = np.array([1, 2, 3, 4, 5, 6])
size = 3


# TODO: Add new systems
class TestGenericFunctions(unittest.TestCase):

    def test_get_system_label(self):
        self.assertEqual(_get_system_label('Els_Custom_W09_S2'), 'ElsCustomW09S2')
        self.assertEqual(_get_system_label('DECam'), 'Decam')
        self.assertEqual(_get_system_label('Els_Custom_W09_S2'), 'ElsCustomW09S2')
        self.assertEqual(_get_system_label('Euclid_VIS'), 'EuclidVis')
        self.assertEqual(_get_system_label('Gaia_2'), 'Gaia2')
        self.assertEqual(_get_system_label('Gaia_DR3_Vega'), 'GaiaDr3Vega')
        self.assertEqual(_get_system_label('Halpha_Custom_AB'), 'HalphaCustomAb')
        self.assertEqual(_get_system_label('H_Custom'), 'HCustom')
        self.assertEqual(_get_system_label('Hipparcos_Tycho'), 'HipparcosTycho')
        self.assertEqual(_get_system_label('HST_ACSWFC'), 'HstAcswfc')
        self.assertEqual(_get_system_label('HST_WFC3UVIS'), 'HstWfc3uvis')
        self.assertEqual(_get_system_label('HST_WFPC2'), 'HstWfpc2')
        self.assertEqual(_get_system_label('IPHAS'), 'Iphas')
        self.assertEqual(_get_system_label('JKC'), 'Jkc')
        self.assertEqual(_get_system_label('JPAS'), 'Jpas')
        self.assertEqual(_get_system_label('JPLUS'), 'Jplus')
        self.assertEqual(_get_system_label('JWST_NIRCAM'), 'JwstNircam')
        self.assertEqual(_get_system_label('PanSTARRS1'), 'Panstarrs1')
        self.assertEqual(_get_system_label('Pristine'), 'Pristine')
        self.assertEqual(_get_system_label('SDSS'), 'Sdss')
        self.assertEqual(_get_system_label('Sky_Mapper'), 'SkyMapper')
        self.assertEqual(_get_system_label('Stromgren'), 'Stromgren')
        self.assertEqual(_get_system_label('WFIRST'), 'Wfirst')

    def test_extract_systems_from_data(self):
        expected_output = ['Wfirst', 'HstWfc3uvis', 'GaiaDr3Vega', 'ElsCustomW09S2']
        phot_list = [PhotometricSystem.WFIRST, PhotometricSystem.HST_WFC3UVIS, PhotometricSystem.Gaia_DR3_Vega,
                     PhotometricSystem.Els_Custom_W09_S2]
        photometry = generate(mean_spectrum_fits_file, photometric_system=phot_list, save_file=False)
        self.assertListEqual(_extract_systems_from_data(photometry), expected_output)
        self.assertListEqual(_extract_systems_from_data(photometry, photometric_system=phot_list), expected_output)

    def test_validate_pwl_sampling_upper_limit(self):
        sampling = np.linspace(0, 71, 300)
        with self.assertRaises(ValueError):
            validate_pwl_sampling(sampling)

    def test_validate_pwl_sampling_lower_limit(self):
        sampling = np.linspace(-11, 70, 300)
        with self.assertRaises(ValueError):
            validate_pwl_sampling(sampling)

    def test_validate_pwl_sampling_len_zero(self):
        sampling = np.linspace(0, 0, 0)
        with self.assertRaises(ValueError):
            validate_pwl_sampling(sampling)

    def test_validate_pwl_sampling_none(self):
        sampling = None
        with self.assertRaises(ValueError):
            validate_pwl_sampling(sampling)

    def test_validate_pwl_sampling(self):
        sampling = np.array([0.3, 0.2, 0.5])
        with self.assertRaises(ValueError):
            validate_pwl_sampling(sampling)

    def test_correlation_to_covariance(self):
        _array = np.random.random(21)
        error = np.random.random(7)
        cov = correlation_to_covariance(_array, error, 1.0)
        npt.assert_allclose(cov, cov.T, rtol=1e-8)  # Check that the matrix is symmetric

    def test_get_matrix_size(self):
        self.assertEqual(get_matrix_size_from_lower_triangle(np.ones(6)), 4)
        self.assertEqual(get_matrix_size_from_lower_triangle(np.ones(10)), 5)
        self.assertEqual(get_matrix_size_from_lower_triangle(np.ones(15)), 6)
        self.assertEqual(get_matrix_size_from_lower_triangle(np.ones(21)), 7)


class TestArrayToSymmetricMatrix(unittest.TestCase):

    def test_array_to_symmetric_matrix_type(self):
        self.assertIsInstance(array_to_symmetric_matrix(array, size), np.ndarray)

    def test_array_to_symmetric_matrix_values(self):
        _array = np.array([4, 5, 6])
        expected_symmetric = np.array([[1., 4., 5.], [4., 1., 6.], [5., 6., 1.]])
        self.assertTrue((array_to_symmetric_matrix(_array, size) == expected_symmetric).all())

    def test_array_to_symmetric_matrix_mismatching(self):
        with self.assertRaises(ValueError):
            array_to_symmetric_matrix(array, 2)

    def test_array_to_symmetric_matrix_negative_size(self):
        with self.assertRaises(ValueError):
            array_to_symmetric_matrix(array, -1)
