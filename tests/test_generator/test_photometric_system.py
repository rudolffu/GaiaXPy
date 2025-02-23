import unittest
from os import path
from os.path import join

import numpy as np
import numpy.testing as npt
import pandas as pd
from numpy import ndarray

from gaiaxpy import generate
from gaiaxpy.core.generic_functions import _get_built_in_systems
from gaiaxpy.generator.photometric_system import PhotometricSystem, load_additional_systems, remove_additional_systems
from tests.files.paths import files_path, with_missing_bp_ecsv_file
from tests.test_generator.test_internal_photometric_system import phot_systems_specs


def get_system_by_name(lst, name):
    return [item[1] for item in lst if item[0] == name][0]

available_systems = list(phot_systems_specs['name'])

# TODO: Extend for new systems

class TestSystemIsStandard(unittest.TestCase):

    def test_system_is_standard(self):
        """
        Check class assigned to each photometric system. Will raise an error if a system is missing in the solution
        dictionary.
        """
        all_phot_systems = [PhotometricSystem[s] for s in PhotometricSystem.get_available_systems().split(', ')]
        regular_systems = ["DECam", "Els_Custom_W09_S2", "Euclid_VIS", "Gaia_2", "Gaia_DR3_Vega", "Halpha_Custom_AB",
                           "H_Custom", "Hipparcos_Tycho", "HST_ACSWFC", "HST_WFC3UVIS", "HST_WFPC2", "IPHAS", "JKC",
                           "JPAS", "JPLUS", "JWST_NIRCAM", "LSST", "PanSTARRS1", "Pristine", "SDSS", "Sky_Mapper",
                           "Stromgren", "WFIRST"]
        standardised_systems = ["HST_HUGS_Std", "JKC_Std", "PanSTARRS1_Std", "SDSS_Std", "Stromgren_Std"]
        regular_dict = {s: "RegularPhotometricSystem" for s in regular_systems}
        standardised_dict = {s: "StandardisedPhotometricSystem" for s in standardised_systems}
        solution_dict = {**regular_dict, **standardised_dict}
        for system in all_phot_systems:
            self.assertEqual(system.value.__class__.__name__, solution_dict[system.name],
                             f'Test has failed for system {system.name}.')


class TestPhotometricSystem(unittest.TestCase):

    def setUp(self):
        self.phot_system_names = [phot_system.name for phot_system in PhotometricSystem]
        self.phot_systems = [(name, PhotometricSystem[name]) for name in self.phot_system_names]

    def test_init(self):
        for name, phot_system in self.phot_systems:
            self.assertIsInstance(phot_system, PhotometricSystem)

    def test_get_system_label(self):
        for name in available_systems:
            # Photometric systems created by the package
            system = get_system_by_name(self.phot_systems, name)
            system_label = system.get_system_label()
            test_label = phot_systems_specs.loc[phot_systems_specs['name'] == name]['label'].iloc[0]
            self.assertIsInstance(system_label, str)
            self.assertEqual(system_label, test_label)

    def test_bands(self):
        for name in available_systems:
            # Photometric systems created by the package
            system = get_system_by_name(self.phot_systems, name)
            test_bands = phot_systems_specs.loc[phot_systems_specs['name'] == name]['bands'].iloc[0]
            system_bands = system.get_bands()
            self.assertIsInstance(system_bands, list)
            self.assertEqual(system_bands, test_bands)

    def test_get_set_zero_points(self):
        for name in available_systems:
            # Photometric systems created by the package
            system = get_system_by_name(self.phot_systems, name)
            test_zero_points = phot_systems_specs.loc[phot_systems_specs['name'] == name]['zero_points'].iloc[0]
            system_zero_points = system.get_zero_points()
            self.assertIsInstance(system_zero_points, ndarray)
            npt.assert_array_equal(system_zero_points, test_zero_points)

    def tearDown(self):
        del self.phot_system_names
        del self.phot_systems


class TestAdditionalSystems(unittest.TestCase):

    def test_user_interaction(self):
        phot_system_list = [s for s in PhotometricSystem.get_available_systems().split(', ')]
        built_in_systems = _get_built_in_systems()
        self.assertEqual(set(phot_system_list), set(built_in_systems))
        _PhotometricSystem = load_additional_systems(join(files_path, 'additional_filters'))
        new_phot_systems = [s for s in _PhotometricSystem.get_available_systems().split(', ')]
        self.assertEqual(len(phot_system_list) + 3, len(new_phot_systems))
        ps = [_PhotometricSystem[s] for s in ['Pristine', 'SDSS', 'PanSTARRS1_Std', 'USER_Panstarrs1Std', 'USER_Sdss',
                                              'USER_Pristine']]
        output = generate(with_missing_bp_ecsv_file, photometric_system=ps, save_file=False)
        built_in_columns = [c for c in output.columns if not c.startswith('USER')]
        built_in_columns.remove('source_id')
        for column in built_in_columns:
            npt.assert_array_equal(output[column].values, output[f'USER_{column}'].values)
        _PhotometricSystem = remove_additional_systems()
        phot_system_list = [s for s in _PhotometricSystem.get_available_systems().split(', ')]
        self.assertEqual(set(phot_system_list), set(built_in_systems))
