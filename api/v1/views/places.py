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
    request_data = request.get_json()

    if type(request_data) != dict:
        abort(400, description="Not a JSON")

    states = request_data.get('states', [])
    cities = request_data.get('cities', [])
    amenities = request_data.get('amenities', [])

    places = []

    if states:
        for state_id in states:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    places.extend(city.places)

    if cities:
        for city_id in cities:
            city = storage.get(City, city_id)
            if city:
                places.extend(city.places)

    if amenities:
        amenities_set = set(amenities)
        places = [place for place in places if
                  amenities_set.issubset(set(place.amenity_ids))]

    places_list = [place.to_dict() for place in places]

    return jsonify(places_list), 200
