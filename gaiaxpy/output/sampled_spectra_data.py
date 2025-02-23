"""
sampled_spectra_data.py
====================================
Module to represent a dataframe of sampled spectra.
"""

import warnings
from os.path import join
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.io.votable.tree import Field, Param, Resource, Table, VOTableFile
from astropy.units import UnitsWarning
from fastavro import parse_schema, writer
from fastavro.validation import validate_many
from numpy import ndarray

from .output_data import OutputData
from .utils import _add_ecsv_header, _array_to_standard, _build_ecsv_header, _generate_fits_header, \
    _get_sampling_dict, _load_header_dict

warnings.filterwarnings('ignore', category=UnitsWarning)


class SampledSpectraData(OutputData):

    def __init__(self, data, positions):
        super().__init__(data, positions)

    def _save_avro(self, output_path, output_file):
        """
        Save the output spectra in AVRO format.

        Args:
            output_path (str): Path where to save the file.
            output_file (str): Name of the output file.
        """

        def _save_avro_sampling(_positions, _output_path, _output_file):
            """
            Save the sampling in a separate avro file.

            Args:
                _positions (list): Sampling positions.
                _output_path (str): Path where to store the output file.
                _output_file (str): Name of the output file.
            """
            schema = {'doc': 'Output sampling.', 'name': 'Sampling', 'namespace': 'sampling', 'type': 'record',
                      'fields': [{'name': 'pos', 'type': 'string'}, ], }
            # Must be an iterable
            sampling = [_get_sampling_dict(_positions)]
            # Sampling field to string
            sampling[0]['pos'] = str(sampling[0]['pos'])
            # Validate that records match the schema
            validate_many(sampling, schema)
            _parsed_schema = parse_schema(schema)
            with open(join(_output_path, f'{_output_file}_sampling.avro'), 'wb') as _output:
                writer(_output, _parsed_schema, sampling)

        def _generate_avro_schema(_spectra_dicts):
            """
            Generate the AVRO schema required to store the output.

            Args:
                _spectra_dicts (list): A list of dictionaries containing spectra.

            Returns:
                dict: A dictionary containing the parsed schema that matches the input.
                list: A list of dictionaries with the modified input spectra according to the valid AVRO types.
            """
            field_to_type = {'source_id': 'long', 'xp': 'string', 'flux': 'string', 'flux_error': 'string',
                             'correlation': 'string', 'standard_deviation': 'float'}

            def build_field(keys):
                return [{'name': key, 'type': field_to_type[key]} for key in keys]

            schema = {'doc': 'Spectrum output.', 'name': 'Spectra', 'namespace': 'spectrum', 'type': 'record',
                      'fields': build_field(_spectra_dicts[0].keys()), }
            # Spectrum fields to string
            for spectrum in _spectra_dicts:
                for field, _type in field_to_type.items():
                    if _type == 'string' and not field == 'xp':
                        try:
                            spectrum[field] = str(tuple(spectrum[field]))
                        except KeyError:
                            continue  # Key may not exist (e.g.: 'xp')
            # Validate that records match the schema
            validate_many(_spectra_dicts, schema)
            return parse_schema(schema), _spectra_dicts

        data = self.data
        positions = self.positions
        Path(output_path).mkdir(parents=True, exist_ok=True)
        _save_avro_sampling(positions, output_path, output_file)
        # List with one dictionary per source
        spectra_dicts = data.to_dict('records')
        parsed_schema, spectra_dicts = _generate_avro_schema(spectra_dicts)
        output_path = join(output_path, f'{output_file}.avro')
        with open(output_path, 'wb') as output:
            writer(output, parsed_schema, spectra_dicts)

    def _save_csv(self, output_path, output_file):
        """
        Save the output spectra in CSV format.

        Args:
            output_path (str): Path where to save the file.
            output_file (str): Name of the output file.
        """
        data = self.data
        positions = self.positions
        modified_data = data.applymap(lambda x: _array_to_standard(x) if isinstance(x, ndarray) else x)
        Path(output_path).mkdir(parents=True, exist_ok=True)
        modified_data.to_csv(join(output_path, f'{output_file}.csv'), index=False)
        # Assume the sampling is the same for all spectra
        pos = [str(_array_to_standard(positions))]
        sampling_df = pd.DataFrame({'pos': pos})
        sampling_df.to_csv(join(output_path, f'{output_file}_sampling.csv'), index=False)

    def _save_ecsv(self, output_path, output_file):
        """
        Save the output spectra in ECSV format.

        Args:
            output_path (str): Path where to save the file.
            output_file (str): Name of the output file.
        """
        data = self.data
        positions = self.positions
        modified_data = data.applymap(lambda x: _array_to_standard(x, 'ecsv') if isinstance(x, ndarray) else x)
        header_lines = _build_ecsv_header(modified_data, positions)
        Path(output_path).mkdir(parents=True, exist_ok=True)
        modified_data.to_csv(join(output_path, f'{output_file}.ecsv'), index=False)
        _add_ecsv_header(header_lines, output_path, output_file)

    def _save_fits(self, output_path, output_file):
        """
        Save the output data in FITS format.

        Args:
            output_path (str): Path where to save the file.
            output_file (str): Name of the output file.
        """
        data = self.data
        positions = self.positions
        # Get length of flux (should be the same as length of error)
        flux_format = f'{len(positions)}D'  # D: double precision float
        flux_error_format = f'{len(positions)}E'  # E: single precision float
        correlation_format = ''  # Correlation if requested
        try:
            correlation_format = f"{len(data['correlation'].iloc[0])}D"
        except KeyError:
            pass
        # Define formats for each type according to FITS
        column_formats = {'source_id': 'K', 'xp': '2A', 'flux': flux_format, 'flux_error': flux_error_format,
                          'correlation': correlation_format, 'standard_deviation': 'E'}
        # create a list of HDUs
        hdu_list = list()
        # create a header to include the sampling
        hdr = fits.Header()
        primary_hdu = fits.PrimaryHDU(header=hdr)
        hdu_list.append(primary_hdu)
        # Create a dictionary to hold all the data
        output_by_column_dict = data.reset_index().to_dict(orient='list')
        # Remove index from output dict
        output_by_column_dict.pop('index', None)
        spectra_keys = output_by_column_dict.keys()
        data_type = data.attrs['data_type']
        units_dict = data_type.get_units()
        columns = [fits.Column(name=key, array=np.array(output_by_column_dict[key]), format=column_formats[key],
                               unit=units_dict.get(key, '')) for key in spectra_keys]
        header = _generate_fits_header(data, column_formats)
        header['Sampling'] = str(tuple(positions))
        hdu = fits.BinTableHDU.from_columns(columns, header=header)
        hdu_list.append(hdu)
        # Put all HDUs together
        hdul = fits.HDUList(hdu_list)
        # Write the file and replace it if it already exists
        Path(output_path).mkdir(parents=True, exist_ok=True)
        output_path = join(output_path, f'{output_file}.fits')
        hdul.writeto(output_path, overwrite=True)

    def _save_xml(self, output_path, output_file):
        """
        Save the output spectra in XML/VOTABLE format.

        Args:
            output_path (str): Path where to save the file.
            output_file (str): Name of the output file.
        """

        def _create_params(_votable, sampling, data_type):
            column = 'sampling'
            unit = data_type.get_units().get('pos', '')
            return [Param(_votable, name=column, ID=f'_{column}', ucd='em.wl', datatype='double', arraysize='*',
                          unit=unit, value=list(sampling))]

        def _create_fields(_votable, _spectra_df):
            len_flux = str(len(_spectra_df['flux'].iloc[0]))
            len_error = str(len(_spectra_df['flux_error'].iloc[0]))
            len_correlation = str(len(_spectra_df['correlation'].iloc[0])) \
                if 'correlation' in _spectra_df.columns else ''
            fields_datatypes = {'source_id': 'long', 'xp': 'char', 'flux': 'double', 'flux_error': 'float',
                                'correlation': 'double', 'standard_deviation': 'float'}
            fields_array_size = {'source_id': '', 'xp': '2', 'flux': len_flux, 'flux_error': len_error,
                                 'correlation': len_correlation, 'standard_deviation': ''}
            fields_id = {key: f'_{key}' for key in ['source_id', 'xp', 'flux', 'flux_error', 'correlation']}
            fields_id.update({'source_id': None})
            header_dict = _load_header_dict()
            data_type = _spectra_df.attrs['data_type']
            units_dict = data_type.get_units()
            _fields = [Field(_votable, name=column, ucd=header_dict.get(column, dict()).get('meta', ''),
                             ID=fields_id[column], datatype=fields_datatypes[column],
                             arraysize=fields_array_size[column], unit=units_dict.get(column, None)) if
                       fields_array_size[column] != '' else Field(_votable, name=column,
                                                                  datatype=fields_datatypes[column],
                                                                  ucd=header_dict.get(column, dict()).get('meta', ''),
                                                                  unit=units_dict.get(column, None))
                       for column in _spectra_df.columns]
            for _field in _fields:
                _field.description = header_dict.get(_field.name, dict()).get('description', '')
            return _fields

        spectra_df = self.data
        positions = list(self.positions)
        # Create a new VOTable file
        votable = VOTableFile()
        # Add a resource
        resource = Resource()
        votable.resources.append(resource)
        # Add a table for the spectra (and add the sampling as metadata)
        spectra_table = Table(votable)
        resource.tables.append(spectra_table)
        # Add sampling as param
        params = _create_params(votable, positions, spectra_df.attrs['data_type'])
        spectra_table.params.extend(params)
        # Add spectrum fields
        fields = _create_fields(votable, spectra_df)
        spectra_table.fields.extend(fields)
        # Create the record arrays, with the given number of rows
        spectra_table.create_arrays(len(spectra_df))
        for index, row in enumerate(spectra_df.to_dict('records')):
            spectra_table.array[index] = tuple([row[column] for column in spectra_df.columns])
        # Write to a file
        Path(output_path).mkdir(parents=True, exist_ok=True)
        output_path = join(output_path, f'{output_file}.xml')
        votable.to_xml(output_path)
