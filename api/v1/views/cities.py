#!/usr/bin/python3
"""
API endpoints for City objects.
"""

from flask import Flask, jsonify, request, abort
from models import storage
from models.city import City
from models.state import State
from api.v1.views import app_views


@app_views.route('/states/<state_id>/cities', methods=['GET'],
                 strict_slashes=False)
def get_cities(state_id):
    """
    Retrieves the list of all City objects of a State
    """
    state = storage.get(State, state_id)
    if state is None:
        return abort(404)

    cities = [city.to_dict() for city in state.cities]
    return jsonify(cities)


@app_views.route('/cities/<city_id>', methods=['GET'],
                 strict_slashes=False)
def get_city(city_id):
    """
    Retrieves a City object by ID
    """
    city = storage.get(City, city_id)
    if city is None:
        return abort(404)
    return jsonify(city.to_dict())


@app_views.route('/cities/<city_id>', methods=['DELETE'], strict_slashes=False)
def delete_city(city_id):
    """Deletes a City object by ID"""
    city = storage.get(City, city_id)

    if city is None:
        abort(404)
    storage.delete(city)
    storage.save()
    return jsonify({}), 200


@app_views.route('/states/<state_id>/cities', methods=['POST'],
                 strict_slashes=False)
def create_city(state_id):
    """
    Create a new City within a State
    """
    state = storage.get(State, state_id)
    if state is None:
        abort(404)

    data = request.get_json()
    if type(data) != dict:
        abort(400, description="Not a JSON")
    if not data.get('name'):
        abort(400, description="Missing name")

    new_city = City(**data)
    new_city.state_id = state_id
    new_city.save()
    return jsonify(new_city.to_dict()), 201


@app_views.route('/cities/<city_id>', methods=['PUT'], strict_slashes=False)
def update_city(city_id):
    """
    Updates a City object.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    data = request.get_json()
    if type(data) != dict:
        abort(400, description="Not a JSON")

    for key, value in data.items():
        if key not in ["id", "state_id", "created_at", "updated_at"]:
            setattr(city, key, value)

    storage.save()
    return jsonify(city.to_dict()), 200
