#!/usr/bin/python3
"""
Places view module for the API.
"""
from api.v1.views import app_views
from models.city import City
from flask import Flask, jsonify, request, abort
from models.place import Place
from models import storage
from models.user import User
from models.state import State
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_by_city(city_id):
    """
    Retrieves the list of all Place objects of a City.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    place_list = [place.to_dict() for place in city.places]
    return jsonify(place_list)


@app_views.route('/places/<place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    """
    Retrieves a Place object by ID.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """
    Deletes a Place object by ID.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """
    Creates a new Place object.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    data = request.get_json()
    if type(data) != dict:
        abort(400, description="Not a JSON")
    if not data.get("user_id"):
        abort(400, description="Missing user_id")
    user = storage.get(User, data.get("user_id"))
    if user is None:
        abort(404)
    if not data.get("name"):
        abort(400, description="Missing name")
    new_place = Place(**data)
    new_place.city_id = city_id
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """
    Updates a Place object by ID.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    data = request.get_json()
    if type(data) != dict:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route("/places_search", methods=["POST"],
                 strict_slashes=False)
def places_search():
    """
    Search for Place objects based on JSON criteria.
    """
    data = request.get_json()
    if type(data) != dict:
        abort(400, description="Not a JSON")
    id_states = data.get("states", [])
    id_cities = data.get("cities", [])
    id_amenities = data.get("amenities", [])
    places = []
    if id_states == id_cities == []:
        places = storage.all(Place).values()
    else:
        states = [
            storage.get(State, _id) for _id in id_states
            if storage.get(State, _id)
        ]
        cities = [city for state in states for city in state.cities]
        cities += [
            storage.get(City, _id) for _id in id_cities
            if storage.get(City, _id)
        ]
        cities = list(set(cities))
        places = [place for city in cities for place in city.places]

    amenities = [
        storage.get(Amenity, _id) for _id in id_amenities
        if storage.get(Amenity, _id)
    ]

    response = []
    for place in places:
        response.append(place.to_dict())
        for amenity in amenities:
            if amenity not in place.amenities:
                response.pop()
                break

    return jsonify(response)
