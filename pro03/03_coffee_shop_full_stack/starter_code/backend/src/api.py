import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

# create and configure the app
app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorization'
    )
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,POST,PUT,PATCH,DELETE,OPTIONS'
    )
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


# a get method that return the short list of drinks
@app.route('/drinks')
def get_drinks_short_list():
    try:
        # Get all the drinks
        drinks = Drink.query.all()
        # reformat the drinks using the short method
        drinks_formated = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_formated
            }), 200
    except Exception:
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


# a get method that return a long list for the drinks_formated
# The requester/user should has the permission get:drinks-detail
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_long_list(payload):
    try:
        # Get all the drinks
        drinks = Drink.query.all()
        # reformat the drinks using the short method
        drinks_formated = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_formated
            }), 200
    except Exception as e:
        print(e)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


# a post method that handels the addtion of new drinks
# it will return the created drink as confirmation
# The requester/user should has the permission post:drinks
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    # Parse data as JSON
    body = request.get_json()
    # add each data in a proper variable
    new_title = body.get('title')
    new_recipe = body.get('recipe')

    try:
        # create the drink
        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        # calls the insert method to confirm the addition
        drink.insert()

        drink = [drink.long()]

        return jsonify({
            "success": True,
            "drinks": drink
            }), 200
    except Exception:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


# a patch method that applies amendment on an existed drink
# it requires drink ID as an input as well data to be modified
# The requester/user should has the permission patch:drinks
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    # Parse data as JSON
    body = request.get_json()
    # add each data in a proper variable
    new_title = body.get('title')
    new_recipe = body.get('recipe')
    # drink ID
    DID = id
    try:
        # Get the proper drink
        drink = Drink.query.filter(Drink.id == DID).one_or_none()
        # Update the drink
        if drink is None:
            abort(404)
        if new_title is not None:
            drink.title = new_title
        if new_recipe is not None:
            drink.recipe = json.dumps(new_recipe)
        # calls the update method to confirm the changes
        drink.update()

        drink = [drink.long()]

        return jsonify({
            "success": True,
            "drinks": drink
            }), 200
    except Exception:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# a delete method that remove a specific drink
# it requires drink ID as an input
# The requester/user should has the permission delete:drinks
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # drink ID
    DID = id

    try:
        # Get the drink
        drink = Drink.query.filter(Drink.id == DID).one_or_none()
        # Delete the drink
        if drink is None:
            abort(404)
        # confrim the removal
        drink.delete()
        return jsonify({
            "success": True,
            "delete": DID
            }), 200
    except Exception:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error)
decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def no_resource(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def no_resource(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
                    "success": False,
                    "error": e.status_code,
                    "message": e.error
                    }), e.status_code
