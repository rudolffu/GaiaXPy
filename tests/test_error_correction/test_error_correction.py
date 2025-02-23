import unittest
from os.path import join

import pandas as pd
import pandas.testing as pdt

from gaiaxpy import generate, apply_error_correction, PhotometricSystem
from tests.files.paths import phot_with_nan_path, mean_spectrum_csv_file
from tests.test_error_correction.error_correction_paths import corrected_error_solution_path, \
    phot_with_nan_corrected_sol_path

_ertol, _eatol = 1e-24, 1e-24
_rtol, _atol = 1e-15, 1e-15


class TestErrorCorrection(unittest.TestCase):

    def test_single_phot_object(self):
        phot_system = PhotometricSystem.Gaia_DR3_Vega
        synthetic_photometry = generate(mean_spectrum_csv_file, photometric_system=phot_system, save_file=False)
        corrected_synth_phot = apply_error_correction(synthetic_photometry, save_file=False)
        corrected_errors_df = pd.read_csv(corrected_error_solution_path, usecols=corrected_synth_phot.columns)
        error_columns = [column for column in corrected_errors_df.columns if 'error' in column]
        other_columns = [column for column in corrected_errors_df.columns if 'error' not in column]
        pdt.assert_frame_equal(corrected_errors_df[error_columns], corrected_synth_phot[error_columns], rtol=_ertol,
                               atol=_eatol)
        pdt.assert_frame_equal(corrected_errors_df[other_columns], corrected_synth_phot[other_columns], rtol=_rtol,
                               atol=_atol)

    def test_error_correction_no_vega(self):
        phot_list = [PhotometricSystem.Euclid_VIS, PhotometricSystem.HST_HUGS_Std]
        multi_synthetic_photometry = generate(mean_spectrum_csv_file, photometric_system=phot_list, save_file=False)
        with self.assertRaises(ValueError):
            apply_error_correction(multi_synthetic_photometry, save_file=False)

    def test_error_correction(self):
        phot_list = [PhotometricSystem.Euclid_VIS, PhotometricSystem.Gaia_DR3_Vega, PhotometricSystem.HST_HUGS_Std]
        multi_synthetic_photometry = generate(mean_spectrum_csv_file, photometric_system=phot_list, save_file=False)
        corrected_multiphotometry = apply_error_correction(multi_synthetic_photometry, save_file=False)
        # Load solution
        error_columns = [column for column in corrected_multiphotometry.columns if 'error' in column]
        other_columns = [column for column in corrected_multiphotometry.columns if 'error' not in column]
        corrected_multiphotometry_solution = pd.read_csv(corrected_error_solution_path, float_precision='high')
        pdt.assert_frame_equal(corrected_multiphotometry[error_columns],
                               corrected_multiphotometry_solution[error_columns], rtol=_ertol, atol=_eatol)
        pdt.assert_frame_equal(corrected_multiphotometry[other_columns],
                               corrected_multiphotometry_solution[other_columns], rtol=_rtol, atol=_atol)

    def test_error_correction_system_with_no_table(self):
        # Here the Halpha system has got no correction table
        phot_list = [PhotometricSystem.Euclid_VIS, PhotometricSystem.Gaia_DR3_Vega, PhotometricSystem.Halpha_Custom_AB]
        multi_synthetic_photometry = generate(mean_spectrum_csv_file, photometric_system=phot_list, save_file=False)
        # Extract Halpha columns from the original photometry
        halpha_columns = [column for column in multi_synthetic_photometry.columns if
                          column.startswith('HalphaCustomAb_')]
        corrected_multiphotometry = apply_error_correction(multi_synthetic_photometry, save_file=False)
        halpha_photometry = multi_synthetic_photometry[halpha_columns]  # The results for this system should not change
        # Load solution
        corrected_multiphotometry_solution = pd.read_csv(corrected_error_solution_path, float_precision='high')
        hst_columns = [column for column in corrected_multiphotometry_solution.columns if
                       column.startswith('HstHugsStd_')]
        corrected_multiphotometry_solution_first_two = corrected_multiphotometry_solution.drop(columns=hst_columns)
        complete_solution = pd.concat([corrected_multiphotometry_solution_first_two, halpha_photometry], axis=1)
        error_columns = [column for column in corrected_multiphotometry.columns if 'error' in column]
        other_columns = [column for column in corrected_multiphotometry.columns if 'error' not in column]
        pdt.assert_frame_equal(corrected_multiphotometry[error_columns], complete_solution[error_columns], rtol=_ertol,
                               atol=_eatol)
        pdt.assert_frame_equal(corrected_multiphotometry[other_columns], complete_solution[other_columns], rtol=_rtol,
                               atol=_atol)

    def test_photometry_with_nan(self):
        phot_with_nan_df = pd.read_csv(phot_with_nan_path)
        output = apply_error_correction(phot_with_nan_df, save_file=False)
        solution = pd.read_csv(phot_with_nan_corrected_sol_path)
        pdt.assert_frame_equal(output, solution)

