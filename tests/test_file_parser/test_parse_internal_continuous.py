import unittest
from os import path

import numpy.testing as npt
import pandas as pd
from numpy import ndarray, dtype

from gaiaxpy.core.satellite import BANDS
from gaiaxpy.file_parser.parse_internal_continuous import InternalContinuousParser
from tests.files.paths import mean_spectrum_avro_file, mean_spectrum_csv_file, mean_spectrum_fits_file,\
    mean_spectrum_xml_file
from tests.utils.utils import get_spectrum_with_source_id

parser = InternalContinuousParser()
parsed_avro_file, _ = parser._parse(mean_spectrum_avro_file)
parsed_csv_file, _ = parser._parse(mean_spectrum_csv_file)
parsed_fits_file, _ = parser._parse(mean_spectrum_fits_file)
parsed_plain_xml_file, _ = parser._parse(mean_spectrum_xml_file)
parsed_xml_file, _ = parser._parse(mean_spectrum_xml_file)

type_map = {'source_id': dtype('int64'),
            'solution_id': dtype('int64'),
            f'{BANDS.rp}_n_parameters': dtype('int64'),
            f'{BANDS.bp}_n_parameters': dtype('int64'),
            f'{BANDS.rp}_n_rejected_measurements': dtype('int64'),
            f'{BANDS.bp}_n_rejected_measurements': dtype('int64'),
            f'{BANDS.rp}_n_measurements': dtype('int64'),
            f'{BANDS.bp}_n_measurements': dtype('int64'),
            f'{BANDS.rp}_standard_deviation': dtype('float64'),
            f'{BANDS.bp}_standard_deviation': dtype('float64'),
            f'{BANDS.rp}_num_of_transits': dtype('int64'),
            f'{BANDS.bp}_num_of_transits': dtype('int64'),
            f'{BANDS.rp}_num_of_blended_transits': dtype('int64'),
            f'{BANDS.bp}_num_of_blended_transits': dtype('int64'),
            f'{BANDS.rp}_num_of_contaminated_transits': dtype('int64'),
            f'{BANDS.bp}_num_of_contaminated_transits': dtype('int64'),
            f'{BANDS.rp}_coefficients': dtype('O'),
            f'{BANDS.bp}_coefficients': dtype('O'),
            f'{BANDS.rp}_coefficient_covariances': dtype('O'),
            f'{BANDS.bp}_coefficient_covariances': dtype('O'),
            f'{BANDS.rp}_degrees_of_freedom': dtype('int64'),
            f'{BANDS.bp}_degrees_of_freedom': dtype('int64'),
            f'{BANDS.rp}_n_relevant_bases': dtype('int64'),
            f'{BANDS.bp}_n_relevant_bases': dtype('int64'),
            f'{BANDS.rp}_basis_function_id': dtype('int64'),
            f'{BANDS.bp}_basis_function_id': dtype('int64'),
            f'{BANDS.rp}_chi_squared': dtype('float64'),
            f'{BANDS.bp}_chi_squared': dtype('float64'),
            f'{BANDS.rp}_coefficient_errors': dtype('O'),
            f'{BANDS.bp}_coefficient_errors': dtype('O'),
            f'{BANDS.rp}_coefficient_correlations': dtype('O'),
            f'{BANDS.bp}_coefficient_correlations': dtype('O'),
            f'{BANDS.rp}_relative_shrinking': dtype('float64'),
            f'{BANDS.bp}_relative_shrinking': dtype('float64'),
            f'{BANDS.bp}_covariance_matrix': dtype('O'),
            f'{BANDS.rp}_covariance_matrix': dtype('O')}


class TestInternalContinuousParserCSV(unittest.TestCase):

    def test_parse_returns_dataframe(self):
        self.assertIsInstance(parsed_csv_file, pd.DataFrame)

    # 'O' stands for object
    def test_column_types(self):
        actual_dtypes = dict(zip(parsed_csv_file.columns, parsed_csv_file.dtypes))
        for key in actual_dtypes.keys():
            self.assertEqual(actual_dtypes[key], type_map[key])

    def test_bp_coefficients_types(self):
        self.assertIsInstance(parsed_csv_file[f'{BANDS.bp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_csv_file[f'{BANDS.bp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_csv_file[f'{BANDS.bp}_coefficient_correlations'][0], ndarray)

    def test_rp_coefficients_type(self):
        self.assertIsInstance(parsed_csv_file[f'{BANDS.rp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_csv_file[f'{BANDS.rp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_csv_file[f'{BANDS.rp}_coefficient_correlations'][0], ndarray)

    # The column 'bp_coefficient_correlations' should be a matrix of size
    # 'bp_num_of_parameters'^2
    def test_bp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_csv_file[f'{BANDS.bp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_csv_file[f'{BANDS.bp}_coefficient_correlations'][0][0]),
                         parsed_csv_file[f'{BANDS.bp}_n_parameters'][0])

    # The column 'rp_coefficient_correlations' should be a matrix of size
    # 'rp_num_of_parameters'^2
    def test_rp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_csv_file[f'{BANDS.rp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_csv_file[f'{BANDS.rp}_coefficient_correlations'][0][0]),
                         parsed_csv_file[f'{BANDS.rp}_n_parameters'][0])


class TestInternalContinuousParserFITS(unittest.TestCase):

    def test_parse_returns_dataframe(self):
        self.assertIsInstance(parsed_fits_file, pd.DataFrame)

    # 'O' stands for object
    def test_column_types(self):
        actual_dtypes = dict(zip(parsed_csv_file.columns, parsed_csv_file.dtypes))
        for key in actual_dtypes.keys():
            self.assertEqual(actual_dtypes[key], type_map[key])

    def test_bp_coefficients_types(self):
        self.assertIsInstance(parsed_fits_file[f'{BANDS.bp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_fits_file[f'{BANDS.bp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_fits_file[f'{BANDS.bp}_coefficient_correlations'][0], ndarray)

    def test_rp_coefficients_type(self):
        self.assertIsInstance(parsed_fits_file[f'{BANDS.rp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_fits_file[f'{BANDS.rp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_fits_file[f'{BANDS.rp}_coefficient_correlations'][0], ndarray)

    # The column 'bp_coefficient_correlations' should be a matrix of size 'bp_num_of_parameters'^2
    def test_bp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_fits_file[f'{BANDS.bp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_fits_file[f'{BANDS.bp}_coefficient_correlations'][0][0]),
                         parsed_fits_file[f'{BANDS.bp}_n_parameters'][0])

    # The column 'rp_coefficient_correlations' should be a matrix of size 'rp_num_of_parameters'^2
    def test_rp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_fits_file[f'{BANDS.rp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_fits_file[f'{BANDS.rp}_coefficient_correlations'][0][0]),
                         parsed_fits_file[f'{BANDS.rp}_n_parameters'][0])


class TestInternalContinuousParserXMLPlain(unittest.TestCase):

    def test_parse_returns_dataframe(self):
        self.assertIsInstance(parsed_plain_xml_file, pd.DataFrame)

    # 'O' stands for object
    def test_column_types(self):
        actual_dtypes = dict(zip(parsed_csv_file.columns, parsed_csv_file.dtypes))
        for key in actual_dtypes.keys():
            self.assertEqual(actual_dtypes[key], type_map[key])

    def test_bp_coefficients_types(self):
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.bp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.bp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.bp}_coefficient_correlations'][0], ndarray)

    def test_rp_coefficients_type(self):
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.rp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.rp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.rp}_coefficient_correlations'][0], ndarray)

    # The column 'bp_coefficient_correlations' should be a matrix of size 'bp_num_of_parameters'^2
    def test_bp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.bp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_plain_xml_file[f'{BANDS.bp}_coefficient_correlations'][0][0]),
                         parsed_plain_xml_file[f'{BANDS.bp}_n_parameters'][0])

    # The column 'rp_coefficient_correlations' should be a matrix of size 'rp_num_of_parameters'^2
    def test_rp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_plain_xml_file[f'{BANDS.rp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_plain_xml_file[f'{BANDS.rp}_coefficient_correlations'][0][0]),
                         parsed_plain_xml_file[f'{BANDS.rp}_n_parameters'][0])


class TestInternalContinuousParserXML(unittest.TestCase):

    def test_parse_returns_dataframe(self):
        self.assertIsInstance(parsed_xml_file, pd.DataFrame)

    # 'O' stands for object
    def test_column_types(self):
        actual_dtypes = dict(zip(parsed_csv_file.columns, parsed_csv_file.dtypes))
        for key in actual_dtypes.keys():
            self.assertEqual(actual_dtypes[key], type_map[key])

    def test_bp_coefficients_types(self):
        self.assertIsInstance(parsed_xml_file[f'{BANDS.bp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_xml_file[f'{BANDS.bp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_xml_file[f'{BANDS.bp}_coefficient_correlations'][0], ndarray)

    def test_rp_coefficients_type(self):
        self.assertIsInstance(parsed_xml_file[f'{BANDS.rp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_xml_file[f'{BANDS.rp}_coefficient_errors'][0], ndarray)
        self.assertIsInstance(parsed_xml_file[f'{BANDS.rp}_coefficient_correlations'][0], ndarray)

    # The column 'bp_coefficient_correlations' should be a matrix of size 'bp_num_of_parameters'^2
    def test_bp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_xml_file[f'{BANDS.bp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_xml_file[f'{BANDS.bp}_coefficient_correlations'][0][0]),
                         parsed_xml_file[f'{BANDS.bp}_n_parameters'][0])

    # The column 'rp_coefficient_correlations' should be a matrix of size 'rp_num_of_parameters'^2
    def test_rp_coefficient_correlations_is_matrix(self):
        self.assertIsInstance(parsed_xml_file[f'{BANDS.rp}_coefficient_correlations'][0][0], ndarray)
        self.assertEqual(len(parsed_xml_file[f'{BANDS.rp}_coefficient_correlations'][0][0]),
                         parsed_xml_file[f'{BANDS.rp}_n_parameters'][0])


class TestInternalContinuousParserAVRO(unittest.TestCase):

    def test_parse_returns_dataframe(self):
        self.assertIsInstance(parsed_avro_file, pd.DataFrame)

    def test_column_names(self):
        self.assertEqual(list(parsed_avro_file.columns),
                         ['source_id',
                          f'{BANDS.rp}_n_rejected_measurements',
                          f'{BANDS.rp}_chi_squared',
                          f'{BANDS.rp}_degrees_of_freedom',
                          f'{BANDS.rp}_n_parameters',
                          f'{BANDS.rp}_standard_deviation',
                          f'{BANDS.rp}_n_measurements',
                          f'{BANDS.rp}_n_relevant_bases',
                          f'{BANDS.rp}_basis_function_id',
                          f'{BANDS.rp}_num_of_transits',
                          f'{BANDS.bp}_n_rejected_measurements',
                          f'{BANDS.bp}_chi_squared',
                          f'{BANDS.bp}_degrees_of_freedom',
                          f'{BANDS.bp}_n_parameters',
                          f'{BANDS.bp}_standard_deviation',
                          f'{BANDS.bp}_n_measurements',
                          f'{BANDS.bp}_n_relevant_bases',
                          f'{BANDS.bp}_basis_function_id',
                          f'{BANDS.rp}_num_of_blended_transits',
                          f'{BANDS.bp}_num_of_transits',
                          f'{BANDS.bp}_num_of_contaminated_transits',
                          f'{BANDS.rp}_num_of_contaminated_transits',
                          f'{BANDS.bp}_num_of_blended_transits',
                          'solution_id',
                          f'{BANDS.rp}_coefficient_covariances',
                          f'{BANDS.rp}_coefficients',
                          f'{BANDS.bp}_coefficient_covariances',
                          f'{BANDS.bp}_coefficients',
                          f'{BANDS.bp}_covariance_matrix',
                          f'{BANDS.rp}_covariance_matrix'])

    # 'O' stands for object
    def test_column_types(self):
        actual_dtypes = dict(zip(parsed_csv_file.columns, parsed_csv_file.dtypes))
        for key in actual_dtypes.keys():
            self.assertEqual(actual_dtypes[key], type_map[key])

    def test_bp_coefficients_types(self):
        self.assertIsInstance(parsed_avro_file[f'{BANDS.bp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_avro_file[f'{BANDS.bp}_coefficient_covariances'][0], ndarray)

    def test_rp_coefficients_type(self):
        self.assertIsInstance(parsed_avro_file[f'{BANDS.rp}_coefficients'][0], ndarray)
        self.assertIsInstance(parsed_avro_file[f'{BANDS.rp}_coefficient_covariances'][0], ndarray)

    # The column 'bp_coefficient_covariances' should be a matrix of size 'bp_num_of_parameters'^2
    def test_bp_coefficient_covariances_is_matrix(self):
        self.assertIsInstance(parsed_avro_file[f'{BANDS.bp}_coefficient_covariances'][0][0], ndarray)
        self.assertEqual(len(parsed_avro_file[f'{BANDS.bp}_coefficient_covariances'][0][0]),
                         parsed_avro_file[f'{BANDS.bp}_n_parameters'][0])

    # The column 'rp_coefficient_covariances' should be a matrix of size 'rp_num_of_parameters'^2
    def test_rp_coefficient_covariances_is_matrix(self):
        self.assertIsInstance(parsed_avro_file[f'{BANDS.rp}_coefficient_covariances'][0][0], ndarray)
        self.assertEqual(len(parsed_avro_file[f'{BANDS.rp}_coefficient_covariances'][0][0]),
                         parsed_avro_file[f'{BANDS.rp}_n_parameters'][0])


class TestFormatEquality(unittest.TestCase):

    def test_parse_equality(self):
        source_ids = parsed_csv_file['source_id'].to_list()
        for source_id in source_ids:
            csv_data = get_spectrum_with_source_id(source_id, parsed_csv_file)
            fits_data = get_spectrum_with_source_id(source_id, parsed_fits_file)
            plain_xml_data = get_spectrum_with_source_id(source_id, parsed_plain_xml_file)
            xml_data = get_spectrum_with_source_id(source_id, parsed_xml_file)
            self.assertEqual(csv_data.keys(), fits_data.keys())
            self.assertEqual(fits_data.keys(), plain_xml_data.keys())
            self.assertEqual(plain_xml_data.keys(), xml_data.keys())
            for key in csv_data.keys():
                decimal = 2 if key in ['bp_covariance_matrix', 'rp_covariance_matrix'] else 4
                npt.assert_almost_equal(csv_data[key], fits_data[key],
                                        decimal=decimal)  # Precision varies across formats
                npt.assert_almost_equal(fits_data[key], plain_xml_data[key], decimal=decimal)
                npt.assert_almost_equal(plain_xml_data[key], xml_data[key], decimal=decimal)
