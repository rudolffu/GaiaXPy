"""
parse_external.py
====================================
Module to parse input files containing externally calibrated sampled spectra.
"""

from .parse_generic import GenericParser
from ..core.generic_functions import _warning

# Columns that contain arrays (as strings)
array_columns = ['wl', 'flux', 'flux_error']


class ExternalParser(GenericParser):
    """
    Parser for externally calibrated sampled spectra.
    """

    def _parse_csv(self, csv_file, _array_columns=None, _matrix_columns=None):
        """
        Parse the input CSV file and store the result in a pandas DataFrame if it contains externally calibrated sampled
            spectra.

        Args:
            csv_file (str): Path to a CSV file.
            _array_columns (list): List of columns in the file that contain arrays as strings.
            _matrix_columns (list): Parameter required in the parser hierarchy. Not used in this function.

        Returns:
            DataFrame: Pandas DataFrame representing the CSV file.
        """
        if _array_columns is None:
            _array_columns = array_columns
        return super()._parse_csv(csv_file, _array_columns)

    def _parse_fits(self, fits_file, _array_columns=None, _matrix_columns=None):
        """
        Parse the input FITS file and store the result in a pandas DataFrame if it contains externally calibrated
            sampled spectra.

        Args:
            fits_file (str): Path to an FITS file.
            _array_columns (list): List of columns in the file that contain arrays as strings.

        Returns:
            DataFrame: Pandas DataFrame representing the FITS file.
        """
        if _array_columns is None:
            _array_columns = array_columns
        return super()._parse_fits(fits_file, _array_columns=_array_columns)

    def _parse_xml(self, xml_file, _array_columns=None, _matrix_columns=None):
        """
        Parse the input XML file and store the result in a pandas DataFrame if it contains externally calibrated sampled
            spectra.

        Args:
            xml_file (str): Path to an XML file.
            _array_columns (list): List of columns in the file that contain arrays as strings.

        Returns:
            DataFrame: Pandas DataFrame representing the XML file.
        """
        if _array_columns is None:
            _array_columns = array_columns
        return super()._parse_xml(xml_file, _array_columns=_array_columns)
