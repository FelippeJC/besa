#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_restful import Api
from config import Config, DevelopmentConfig, TestingConfig
from .database import db
import folium
from .opendata.objects import (get_barcelona_map, get_bicycle_map_layer,
                               get_mercats_i_fires_al_carrer_map_layer,
                               get_public_wifi_map_layer,
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
    return render_template('public_transportation.html')


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


@app.route("/demography")
def demography():
    return render_template('demography.html')


@app.route("/society-and-welfare")
def society_and_welfare():
    return render_template('society_and_welfare.html')


@app.route("/blank")
def blank():
    return render_template('blank.html')


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
