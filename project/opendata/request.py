"""Connects with the Open Data API

This module is intended to deal with the flask app access to Barcelona's Open Data API.
The functions added here are better explained at https://opendata-ajuntament.barcelona.cat/en/desenvolupadors

There are two types of functions, one that handles the Catalogue management APIs and another to Query APIs on CSV resources.
The latest returns the data needed for the presentations.

Variables:
    OPENDATA_URL {str} -- is the base url where the Open Data Barcelona is hosted
"""

__all__ = ["raw_data",
           "current_package_list_with_resources", "package_search", "resource_show",  # Catalogue management APIs
           "datastore_search",  # Query APIs on CSV resources
           ]

import requests
import json

OPENDATA_URL = "https://opendata-ajuntament.barcelona.cat/data/api/action/"


def raw_data(url):
    """return the raw response of an url request on OpenData API
    Usefull when trying to get geojson file
    """
    try:
        data = requests.get(url, timeout=5)
        return data.json()
    except (requests.exceptions.RequestException, ValueError, json.decoder.JSONDecodeError) as e:
        print(e)
    return


def _request_json(url):
    """return the json response of an url request on OpenData API"""
    try:
        data = requests.get(url, timeout=5).json()
        if data.get("success", False):
            return data
    except:
        print("Problems with the request")
    return dict()


def current_package_list_with_resources(expression):
    """returns the list of current datasets and their resources"""
    url = OPENDATA_URL + "current_package_list_with_resources?{expression}".format(expression=expression)
    return _request_json(url).get("result", dict())


def package_search(expression):
    """performs a search within the dataset catalogue
        E.G.
        package_search('fq=name:punts-critics-neteja-barcelona')
    """
    url = OPENDATA_URL + "package_search?{expression}".format(expression=expression)
    return _request_json(url).get("result", dict())


def resource_show(expression):
    """returns the metadata of a resource"""
    url = OPENDATA_URL + "resource_show?{expression}".format(expression=expression)
    return _request_json(url).get("result", dict())


def datastore_search(expression):
    """Query APIs on CSV resources

    URL: https://opendata-ajuntament.barcelona.cat/data/api/action/datastore_search

    resource_id (string - required) - id of the CSV resource we want to search

    keyword arguments:

    filters (dictionary) - conditions to be met. Example: {“direccio”: “%carrer%”}
    q (string or dictionary) - search in full text. You can specify a string to search for in all fields
                               or a dictionary to search for specific fields.
                               Example: {“key1”: “a”, “key2”: “b”}
    distinct (boolean) - returns only the different rows
    plain (boolean) - treat the query as if it were a plain text
    language (string) - query language in full text
    limit (int) - maximum number of results. By default it returns 100 results.
    offset (int) - number of results to be skipped. Useful for making a results page.
    fields (string) - list of fields to be included in the response. By default,
                      returns all fields in the same order as in the CSV
    sort (string) - name of the fields for which to sort separated by commas: “nom, codi desc”

    Sample call to datastore_search
    We want to look for the public drinking fountains that are located on Mallorca street.
    To do this, we first need to know the resource ID and then the name of the field we want to search for.
    This information can be obtained from the preview page of the resource on the portal.

    Input Parameters:

    resource_id: This is the last part of the resource URL (21f7a4df-2e73-45f8-8c6d-0b3db8c21527)
    q: We consult it in the fields of the resource preview {“INVENTARI_CARRER” : “Mallorca”}
    Calling URL:

    URL + '?resource_id=21f7a4df-2e73-45f8-8c6d-0b3db8c21527&limit=5&q={%22INVENTARI_CARRER%22:%22%Mallorca%%22}'

    So, this function would be called like this
    datastore_search('resource_id=21f7a4df-2e73-45f8-8c6d-0b3db8c21527&limit=5&q={%22INVENTARI_CARRER%22:%22%Mallorca%%22}')
    """
    url = OPENDATA_URL + "datastore_search?{expression}".format(expression=expression)
    return _request_json(url)
