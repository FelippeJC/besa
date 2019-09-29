import pandas as pd
from pandas.io.json import json_normalize
from .parse import get_data_from_datastore


class Data(object):
    """Open Data class

    Is used to operate with a pandas dataframe gotten from the result of
    a given expression request to Barcelona Open Data API.

    This is a generic object created to avoid too many code repetitions.

    """

    def __init__(self, expression):
        self.data = get_data_from_datastore(expression)
        self.df = json_normalize(self.data) if self.data else pd.DataFrame()
