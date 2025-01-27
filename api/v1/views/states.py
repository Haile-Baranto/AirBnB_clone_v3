#!/usr/bin/python3
"""
API endpoints for State objects.
"""

from flask import Flask, jsonify, request, abort
from models import storage
from models.state import State
from api.v1.views import app_views


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_states():
    """
    Returns the list of all State objects
    """
    states = [state.to_dict() for state in storage.all(State).values()]
    return jsonify(states)


@app_views.route('/states/<string:state_id>', methods=['GET'],
                 strict_slashes=False)
def get_state(state_id):
    """
    Retrieves a State object by ID
    """
    state = storage.get(State, state_id)
    if state is None:
        return abort(404)
    else:
        return jsonify(state.to_dict())


@app_views.route('/states/<string:state_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_state(state_id):
    """Deletes a State object by ID"""
    state = storage.get(State, state_id)

    if state is None:
        abort(404)
    storage.delete(state)
    storage.save()
    return jsonify({}), 200


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """
    Create a new State
    """
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description="Missing name")
    new_state = State(**data)
    new_state.save()
    return jsonify(new_state.to_dict()), 201


@app_views.route('/states/<string:state_id>', methods=['PUT'],
                 strict_slashes=False)
def update_state(state_id):
    """
    Updates a State object.
    """
    state = storage.get(State, state_id)
    if state is None:
        abort(404)

    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    # Remove keys 'id', 'created_at', and 'updated_at' from the data
    data.pop('id', None)
    data.pop('created_at', None)
    data.pop('updated_at', None)

    for key, value in data.items():
        setattr(state, key, value)

    storage.save()
    return jsonify(state.to_dict()), 200
