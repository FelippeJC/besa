#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_restful import Api
from config import Config, DevelopmentConfig, TestingConfig
from .database import db

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
    return "Hello!"
