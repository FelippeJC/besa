#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_restful import Api
from config import Config, DevelopmentConfig, TestingConfig
from .database import db
from datetime import datetime
import random
import folium
from .opendata.objects import (get_barcelona_map, get_bicycle_map_layer,
                               get_mercats_i_fires_al_carrer_map_layer,
                               get_public_wifi_map_layer,
                               get_bus_stations_map_layer,
                               Data,
                               )

##########################################################################
# Configurations
##########################################################################

app = Flask(__name__)

# Sets the configurations
if os.environ.get('FLASK_ENV', None) == 'production':
    config = Config()
elif os.environ.get('FLASK_ENV', None) == 'test':
    config = TestingConfig()
else:
    config = DevelopmentConfig()

app.config.from_object(config)

# Defines the API
api = Api(app)

# Sets the database
db.init_app(app)

# Sets flask-migrate
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


# HTTP error handling

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


##########################################################################
# Views
##########################################################################


@app.route("/")
def index():
    return render_template('index.html', data=[20, 40, 40])


@app.route("/city-initiatives")
def city_initiatives():
    return render_template('city_initiatives.html')


@app.route("/city-amenities")
def city_amenities():
    bcn_map = get_barcelona_map()
    bcn_map.add_child(get_mercats_i_fires_al_carrer_map_layer())
    wifi_map_layer = get_public_wifi_map_layer()
    if wifi_map_layer is not None:
        bcn_map.add_child(wifi_map_layer)
    folium.LayerControl().add_to(bcn_map)
    return render_template('city_amenities.html', folium_map=bcn_map._repr_html_())


@app.route("/about")
def about():
    return render_template('about.html')


###  ENVIRONMENT  ###

@app.route("/temperature")
def temperature():
    temp = Data("resource_id=0e3b6840-7dff-4731-a556-44fac28a7873&limit=400")
    temp.df = temp.df.astype(float)
    temp.df.astype({'Any': 'int32'}).dtypes
    temp.df.drop('_id', axis=1, inplace=True)
    temp.df.set_index('Any', inplace=True)
    temp.df.rename(columns={'Temp_Mitjana_Gener': 'January',
                            'Temp_Mitjana_Febrer': 'February',
                            'Temp_Mitjana_Marc': 'March',
                            'Temp_Mitjana_Abril': 'April',
                            'Temp_Mitjana_Maig': 'May',
                            'Temp_Mitjana_Juny': 'June',
                            'Temp_Mitjana_Juliol': 'July',
                            'Temp_Mitjana_Agost': 'August',
                            'Temp_Mitjana_Setembre': 'September',
                            'Temp_Mitjana_Octubre': 'October',
                            'Temp_Mitjana_Novembre': 'November',
                            'Temp_Mitjana_Desembre': 'December'},
                   inplace=True)
    dataset = list()
    for (columnName, columnData) in temp.df.iteritems():
        color_r, color_g, color_b = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        dataset.append({"label": columnName,
                        "lineTension": 0.3,
                        "backgroundColor": "rgba({r}, {g}, {b}, 0.05)".format(r=color_r, g=color_g, b=color_b),
                        "borderColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "borderWidth": 1,
                        "pointRadius": 1,
                        "pointBackgroundColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointBorderColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointHoverRadius": 1,
                        "pointHoverBackgroundColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointHoverBorderColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointHitRadius": 2,
                        "pointBorderWidth": 1,
                        "data": list(columnData)
                        })
    average_temperatures = dict(temp.df.mean())
    itemMinValue = min(average_temperatures.items(), key=lambda x: x[1])
    itemMaxValue = max(average_temperatures.items(), key=lambda x: x[1])
    # radar graph
    average_temperatures = sorted(average_temperatures.items(), key=lambda kv: (datetime.strptime(kv[0], '%B'), kv[1]))
    average_temperatures_labels = list()
    average_temperatures_data = list()
    average_temperatures_data_colors = list()
    for label, value in average_temperatures:
        average_temperatures_data_colors.append("#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]))
        average_temperatures_labels.append(label)
        average_temperatures_data.append(value)
    radar_graph_data = {"labels": average_temperatures_labels,
                        "datasets": [{
                            "data": average_temperatures_data,
                            "backgroundColor": average_temperatures_data_colors,
                            "hoverBackgroundColor": average_temperatures_data_colors,
                            "hoverBorderColor": "rgba(234, 236, 244, 0.4)",
                        }],
                        }
    labels = list(temp.df.index)
    return render_template('temperature.html',
                           label=labels,
                           data=dataset,
                           radar_graph_data=radar_graph_data,
                           itemMinValue="{month} ({temp:.2f}  °C)".format(month=itemMinValue[0], temp=itemMinValue[1]),
                           itemMaxValue="{month} ({temp:.2f}  °C)".format(month=itemMaxValue[0], temp=itemMaxValue[1]),
                           amount_of_data=len(labels))


@app.route("/precipitation")
def precipitation():
    data = Data("resource_id=6f1fb778-0767-478b-b332-c64a833d26d2&limit=400")
    data.df = data.df.astype(float)
    data.df.astype({'Any': 'int32'}).dtypes
    data.df.drop('_id', axis=1, inplace=True)
    data.df.set_index('Any', inplace=True)
    data.df.rename(columns={'Precip_Acum_Gener': 'January',
                            'Precip_Acum_Febrer': 'February',
                            'Precip_Acum_Marc': 'March',
                            'Precip_Acum_Abril': 'April',
                            'Precip_Acum_Maig': 'May',
                            'Precip_Acum_Juny': 'June',
                            'Precip_Acum_Juliol': 'July',
                            'Precip_Acum_Agost': 'August',
                            'Precip_Acum_Setembre': 'September',
                            'Precip_Acum_Octubre': 'October',
                            'Precip_Acum_Novembre': 'November',
                            'Precip_Acum_Desembre': 'December'},
                   inplace=True)
    dataset = list()
    for (columnName, columnData) in data.df.iteritems():
        color_r, color_g, color_b = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        dataset.append({"label": columnName,
                        "lineTension": 0.3,
                        "backgroundColor": "rgba({r}, {g}, {b}, 0.05)".format(r=color_r, g=color_g, b=color_b),
                        "borderColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "borderWidth": 1,
                        "pointRadius": 1,
                        "pointBackgroundColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointBorderColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointHoverRadius": 1,
                        "pointHoverBackgroundColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointHoverBorderColor": "rgba({r}, {g}, {b}, 1)".format(r=color_r, g=color_g, b=color_b),
                        "pointHitRadius": 2,
                        "pointBorderWidth": 1,
                        "data": list(columnData)
                        })
    average_precipitations = dict(data.df.mean())
    itemMinValue = min(average_precipitations.items(), key=lambda x: x[1])
    itemMaxValue = max(average_precipitations.items(), key=lambda x: x[1])
    labels = list(data.df.index)
    return render_template('precipitation.html',
                           label=labels,
                           data=dataset,
                           itemMinValue="{month} ({temp:.2f}  mm)".format(month=itemMinValue[0], temp=itemMinValue[1]),
                           itemMaxValue="{month} ({temp:.2f}  mm)".format(month=itemMaxValue[0], temp=itemMaxValue[1]),
                           amount_of_data=len(labels))


@app.route("/city-trees")
def city_trees():
    return render_template('city_trees.html')


@app.route("/green-spaces")
def green_spaces():
    return render_template('green_spaces.html')


@app.route("/waste-management")
def waste_management():
    return render_template('waste_management.html')


###  MOBILITY  ###


@app.route("/city-flow")
def city_flow():
    return render_template('city_flow.html')


@app.route("/public-transportation")
def public_transportation():
    bcn_map = get_barcelona_map()
    bus_map_layer = get_bus_stations_map_layer()
    if bus_map_layer is not None:
        bcn_map.add_child(bus_map_layer)
    folium.LayerControl().add_to(bcn_map)
    return render_template('public_transportation.html', folium_map=bcn_map._repr_html_())


@app.route("/bicycle")
def bicycle():
    bcn_map = get_barcelona_map()
    bicycle_map_layer = get_bicycle_map_layer()
    if bicycle_map_layer is not None:
        bcn_map.add_child(bicycle_map_layer)
    folium.LayerControl().add_to(bcn_map)
    return render_template('bicycle.html', folium_map=bcn_map._repr_html_())


@app.route("/car")
def car():
    return render_template('car.html')


@app.route("/traffic-incidents")
def traffic_incidents():
    return render_template('traffic_incidents.html')


###  POPULATION  ###


# @app.route("/demography")
# def demography():
#     return render_template('demography.html')


# @app.route("/society-and-welfare")
# def society_and_welfare():
#     return render_template('society_and_welfare.html')


@app.route("/blank")
def blank():
    return render_template('blank.html')


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
