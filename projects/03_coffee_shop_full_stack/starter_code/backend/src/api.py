import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*": {"origins": "*"}})


db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    ''' 
    Retrieves all available drinks from the database
    without the recipe.
    '''
    try:
        drink_query = Drink.query.all()
        drinks = []

        for drink in drink_query:
            drinks.append(drink.short())

        print(drinks)

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    ''' 
    Retrive all drinks with the recipe information.
    Requieres the [get:drinks-detail] permission.
    '''
    try:
        drink_query = Drink.query.all()
        drinks = []

        for drink in drink_query:
            drinks.append(drink.long())

        print(drinks)

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(jwt):
    ''' 
    Creates a new drink with the name and recipe provided.
    Requieres the [post:drinks] permission.
    '''
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)

    try:
        if title is None:
            abort(400)
        elif recipe is None:
            abort(400)

        new_drink = Drink(title=title, recipe=str(recipe).replace("'", "\""))
        new_drink.insert()

        drinks = []
        drinks.append(new_drink.long())

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink_by_id(jwt, id):
    ''' 
    Update an existing drink information.
    Requieres the [patch:drinks] permission.
    '''
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)

    if title is None and recipe is None:
        abort(400)

    try:

        drink = Drink.query.filter(Drink.id == int(id)).one_or_none()

        if drink is None:
            abort(404)

        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = str(recipe).replace("'", "\"")

        drink.update()

        drinks = []
        drinks.append(drink.long())

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(jwt, id):
    ''' 
    Delete the drink with the provided id, if it exists.
    Requieres the [delete:drinks] permission.
    '''
    try:

        drink = Drink.query.filter(Drink.id == int(id)).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        })
    except Exception as e:
        print(e)
        abort(422)


# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Error: A bad request was made"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Error: The requested resource was not found"
    }), 404


@app.errorhandler(405)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Error: Forbidden method used"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Error: Cannot proccess request"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Error: Internal Server Error ocurred"
    }), 500


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error['description']
    }), e.status_code
