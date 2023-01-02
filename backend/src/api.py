import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
Implement endpoint
GET /drinks
    it should be a public endpoint
    it should contain only the drink.short() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def public_drinks():
    drinks = Drink.query.all()
    drinks_formated = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks_formated
    })

'''
Implement endpoint
GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks(payload):
    all_drinks = Drink.query.order_by(Drink.id).all()
    print(all_drinks)
    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in all_drinks]
    })


'''
Implement endpoint
POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    data = request.get_json()
    if not ('title' and 'recipe' in data):
        abort (422)

    title = data['title']
    recipe_json = json.dumps(data['recipe'])

    new_drinks = Drink(title=title, recipe=recipe_json)
    new_drinks.insert()

    return jsonify({
        "success": True,
        "drinks": [new_drinks.long()]
    })

'''
Implement endpoint
PATCH /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drinks(payload, id):
    
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    data = request.get_json()
    
    if not ('title' or 'recipe' in data):
        abort (422)

    
    if 'title' in data:
        drink.title = data['title']
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    drink.update()

   
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })
    

'''
Implement endpoint
DELETE /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row for <id>
    it should require the 'delete:drinks' permission
returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        "success": True,
        "deleted": drink.id
    })


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
Implement error handlers using the @app.errorhandler(error) decorator
each error handler should return (with approprate messages):
            jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
                }), 404

'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": True,
        "error": 404,
        "message": "Resource Not Found"
    }), 404
'''

Implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": True,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

'''

Implement error handler for AuthError
    error handler should conform to general task above
'''
# Error Handler (401) Unauthorized
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success":True,
        "erro": 401,
        "message": "Unauthorized Access"
    })