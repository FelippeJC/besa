from .request import datastore_search


def get_data_from_datastore(expression):
    """Returns a list of records found in a datastore search"""
    response = datastore_search(expression)
    result = response.get("result", dict())
    return result.get("records", dict())
