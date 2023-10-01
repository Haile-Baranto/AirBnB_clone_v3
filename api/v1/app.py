#!/usr/bin/python3
"""
Main Flask application.
"""
import os
from flask import Flask
from flask import jsonify
from models import storage
from api.v1.views import app_views
from flask_cors import CORS  # Import the CORS class

app = Flask(__name__)

# Configure CORS to allow requests from any origin during development
CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


app.register_blueprint(app_views, url_prefix="/api/v1")


@app.teardown_appcontext
def close_storage(exception):
    """Closes the storage on teardown."""
    storage.close()


if __name__ == "__main__":
    host = os.getenv("HBNB_API_HOST", "0.0.0.0")
    port = int(os.getenv("HBNB_API_PORT", 5000))
    app.run(host=host, port=port, threaded=True)
