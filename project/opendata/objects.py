# -*- coding: utf-8 -*-
import folium
import pandas as pd
from pandas.io.json import json_normalize
from .parse import get_data_from_datastore
from .request import raw_data
from . import urls

PLAZA_CATALUNA = (41.3863900, 2.1687300)
SAGRADA_FAMILIA = (41.4036299, 2.1743558)


class Data(object):
    """Open Data class

    Is used to operate with a pandas dataframe gotten from the result of
    a given expression request to Barcelona Open Data API.

    This is a generic object created to avoid too many code repetitions.

    """

    def __init__(self, expression):
        self.data = get_data_from_datastore(expression)
        self.df = json_normalize(self.data) if self.data else pd.DataFrame()


def get_barcelona_map(center=SAGRADA_FAMILIA, zoom_start=12.5, include_neighborhoods=True):
    barcelona_map = folium.Map(location=center, zoom_start=zoom_start)
    return barcelona_map


def get_bicycle_map_layer():
    bicycle_map_layer = None
    try:
        bicis = raw_data(urls.GEOJSON_BICYCLE_LANE)
        bicycle_map_layer = folium.GeoJson(bicis, name='Bike Lanes',
                                           tooltip=folium.features.GeoJsonTooltip(fields=['TOOLTIP'], aliases=['']))
    except ValueError as e:
        print(e)
    return bicycle_map_layer


def get_mercats_i_fires_al_carrer_map_layer():
    map_layer = folium.FeatureGroup("Mercats i fires al carrer")
    try:
        data = Data("resource_id={resource_id}&limit=100000".format(resource_id=urls.RESOURCE_ID["mercats_i_fires_al_carrer"]))
        popup_str = ("<h4>{name}</h4>"
                     "<address>"
                     "  {street_name}<br>"
                     "  {neighborhood}<br>"
                     "  {district}<br>"
                     "  Tel: {tel}<br>"
                     "</address>")
        for __, row in data.df.iterrows():
            folium.Marker((row['LATITUD'], row['LONGITUD']),
                          icon=folium.Icon(color="lightgreen", icon='shopping-bag', prefix='fa'),
                          tooltip=row['EQUIPAMENT'],
                          popup=popup_str.format(name=row['EQUIPAMENT'] or "",
                                                 street_name=row['ADRECA'] or "",
                                                 neighborhood=row['NOM_BARRI'] or "",
                                                 district=row['NOM_DISTRICTE'] or "",
                                                 tel=row['TELEFON'] or ""
                                                 )).add_to(map_layer)
    except ValueError as e:
        print(e)
    return map_layer


def get_public_wifi_map_layer():
    map_layer = folium.FeatureGroup("Public WiFi")
    try:
        data = Data("resource_id={resource_id}&limit=100000".format(resource_id=urls.RESOURCE_ID["public_wifi"]))
        popup_str = ("<h4>{name}</h4>"
                     "<address>"
                     "  {street_name}<br>"
                     "  {neighborhood}<br>"
                     "  {district}<br>"
                     "</address>")
        for __, row in data.df.iterrows():
            folium.Circle((row['LATITUD'], row['LONGITUD']), 40,
                          tooltip=row['NOM_CAPA'],
                          popup=popup_str.format(name=row['EQUIPAMENT'] or "",
                                                 street_name=row['ADRECA'] or "",
                                                 neighborhood=row['NOM_BARRI'] or "",
                                                 district=row['NOM_DISTRICTE'] or "",
                                                 ),
                          color='#3186cc',
                          fill=True,
                          fill_color='#3186cc').add_to(map_layer)
    except ValueError as e:
        print(e)
    return map_layer


def get_bus_stations_map_layer():
    map_layer = folium.FeatureGroup("Bus Stations")
    try:
        data = Data("resource_id={resource_id}&limit=4000".format(resource_id=urls.RESOURCE_ID["bus_stations"]))
        popup_str = ("<h4>{name}</h4>"
                     "<address>"
                     "  {street_name}<br>"
                     "  {neighborhood}<br>"
                     "  {district}<br>"
                     "</address>")
        for __, row in data.df.iterrows():
            bus_type = row['NOM_CAPA']
            color = "green"
            if "nocturns" in bus_type:
                color = "gray"
            if "diürns" in bus_type:
                color = "blue"
            folium.Marker((row['LATITUD'], row['LONGITUD']),
                          icon=folium.Icon(color=color, icon='bus', prefix='fa'),
                          tooltip=bus_type,
                          popup=popup_str.format(name=row['EQUIPAMENT'] or "",
                                                 street_name=row['ADRECA'] or "",
                                                 neighborhood=row['NOM_BARRI'] or "",
                                                 district=row['NOM_DISTRICTE'] or "",
                                                 )).add_to(map_layer)
    except ValueError as e:
        print(e)
    return map_layer
