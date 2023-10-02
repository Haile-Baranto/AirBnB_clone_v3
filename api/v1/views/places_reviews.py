#!/usr/bin/python3
"""
Reviews view module for the API.
"""
from api.v1.views import app_views
from flask import Flask, jsonify, request, abort
from models import storage
from models.review import Review
from models.place import Place
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
def get_reviews_by_place(place_id):
    """
    Retrieves the list of all Review objects of a Place.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    reviews = place.reviews
    review_list = [review.to_dict() for review in reviews]
    return jsonify(review_list)


@app_views.route('/reviews/<review_id>', methods=['GET'],
                 strict_slashes=False)
def get_review(review_id):
    """
    Retrieves a Review object by ID.
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """
    Deletes a Review object by ID.
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    storage.delete(review)
    storage.save()
    return jsonify({})


@app_views.route('/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
def create_review(place_id):
    """
    Creates a new Review object.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    data = request.get_json()
    if type(data) != dict:
        abort(400, "Not a JSON")
    if not data.get("user_id"):
        abort(400, description="Missing user_id")
    user = storage.get(User, data.get('user_id'))
    if user is None:
        abort(404)
    if not data.get("text"):
        abort(400, description="Missing text")
    new_review = Review(**data)
    new_review.place_id = place_id
    new_review.save()
    return jsonify(new_review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['PUT'],
                 strict_slashes=False)
def update_review(review_id):
    """
    Updates a Review object by ID.
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    data = request.get_json()
    if type(data) != dict:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'user_id', 'place_id', 'created_at',
                       'updated_at']:
            setattr(review, key, value)
    storage.save()
    return jsonify(review.to_dict()), 200
