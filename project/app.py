#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_restful import Api
from config import Config, DevelopmentConfig, TestingConfig
from .database import db
import folium

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
    return render_template('index.html')


@app.route("/city-initiatives")
def city_initiatives():
    return render_template('city_initiatives.html')


@app.route("/city-amenities")
def city_amenities():
    m = folium.Map(location=[45.5236, -122.6750],
                   tiles='Stamen Toner',
                   zoom_start=13,
                   )

    folium.Circle(radius=100,
                  location=[45.5244, -122.6699],
                  popup='The Waterfront',
                  color='crimson',
                  fill=True,
                  ).add_to(m)

    folium.CircleMarker(location=[45.5215, -122.6261],
                        radius=50,
                        popup='Laurelhurst Park',
                        color='#3186cc',
                        fill=True,
                        fill_color='#3186cc'
                        ).add_to(m)
    legend_html = '''
                <div style="position: fixed; background-color: rgba(255,255,255,0.85);
                            bottom: 50px; left: 50px; width: 100px; height: 90px;
                            border:2px solid grey; z-index:9999; font-size:14px;">
                    &nbsp; Cool Legend <br>
                    &nbsp; <i class="fa fa-map-marker fa-2x" style="color:green"></i> &nbsp; East <br>
                    &nbsp; <i class="fa fa-map-marker fa-2x" style="color:red"></i> &nbsp; West
                </div>
                '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return render_template('city_amenities.html', folium_map=m._repr_html_())


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/blank")
def blank():
    return render_template('blank.html')


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
