from astroquery.gaia import GaiaClass

from gaiaxpy.core.server import data_release, gaia_server
from .archive_reader import ArchiveReader
from .dataframe_reader import DataFrameReader

not_supported_functions = ['apply_colour_equation', 'apply_error_correction', 'simulate_continuous', 'simulate_sampled']


def extremes_are_enclosing(first_row, column):
    if first_row[column][0] == '[' and first_row[column][-1] == ']':
        return True
    elif first_row[column][0] == '(' and first_row[column][-1] == ')':
        return True
    else:
        return False


class ListReader(ArchiveReader):

    def __init__(self, content, function, user, password, disable_info=False):
        super(ListReader, self).__init__(function, user, password)
        if content:
            self.content = content
        else:
            raise ValueError('Input list cannot be empty.')
        self.disable_info = disable_info

    def read(self, _data_release=data_release):
        # TODO: list could contain elements that are not sourceIds
        sources = self.content
        function_name = self.function.__name__
        if function_name in not_supported_functions:
            raise ValueError(f'Function {function_name} does not support receiving a list as input.')
        # Connect to geapre
        gaia = GaiaClass(gaia_tap_server=gaia_server, gaia_data_server=gaia_server)
        self._login(gaia)
        # ADQL query
        if not self.disable_info:
            print('Running query...', end='\r')
        result = gaia.load_data(ids=sources, format='csv', data_release=_data_release, data_structure='raw',
                                retrieval_type='XP_CONTINUOUS', avoid_datatype_check=True)
        try:
            continuous_key = [key for key in result.keys() if 'continuous' in key.lower()][0]
            data = result[continuous_key][0].to_pandas()
        except (KeyError, IndexError):
            raise ValueError('No continuous raw data found for the given sources.')
        return DataFrameReader(data).read_df()
