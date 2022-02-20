import json
import os

from flask import Flask, make_response
from . import db

def create_app(test_config=None):
    # Create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )
    
    # Set default config is therre is no test config
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
        
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize database
    db.init_app(app)
    
    # Routes
    @app.route('/getFlights', methods=['GET'])
    def getFlights():
        res = make_response(json.dumps(db.getFlights()))
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res
    
    return app
