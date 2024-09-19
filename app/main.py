from flask import Flask, request, make_response, jsonify
from functools import wraps
from packages.db_conn import *
from packages.sign_up import sign_up_ 
from packages.sign_in import sign_in_
from packages.restaurants import get_restaurant_by_address
from packages.events import *
from packages.jwt_utils import verify_token


app = Flask(__name__)

@app.route("/sign-up", methods=["POST"])
def sign_up_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    return sign_up_(data)

@app.route("/sign-in", methods=["POST"])
def sign_in_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    result, status_code = sign_in_(data)
    if status_code == 200:
        response = make_response(result)
        response.set_cookie('access_token', result.get('token'), httponly=True, secure=True, max_age=7*24*60*60)  # 7 days
        return response
    return result, status_code

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid or expired!'}), 401
        return f(user_id, *args, **kwargs)
    return decorated

@app.route('/protected', methods=['GET'])
@token_required
def protected(user_id):
    return jsonify({'message': f'This is a protected route! User ID: {user_id}'})


@app.route("/events", methods=["GET", "POST"])
def events():
    if request.method == "POST":
        data = request.get_json()
        result = create_event(data)
        res = {
            "message": result
        }
        return res
    elif request.method == "GET":

        result = get_events()

        return result


@app.route("/my-events", methods=["GET"])
@token_required
def my_events(user_id):
    result = get_my_events(user_id)
    return jsonify(result), 200

@app.route("/restaurants", methods=["POST"])
def restaurants():
    data = request.get_json()
    full_address = data["full_address"]

    result = get_restaurant_by_address(full_address)
    
    if result:
        return result
    else: 
        return {"message": "Restaurant not listed!"}

if __name__ == "__main__":
    app.run(debug=True)