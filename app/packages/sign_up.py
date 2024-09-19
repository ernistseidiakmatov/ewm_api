import hashlib
import os
from .db_conn import db_conn
from flask import jsonify

def hash_password(password):
    salt = os.urandom(32)
    hash_obj = hashlib.sha256()
    hash_obj.update(salt + password.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    return f"{salt.hex()}:{hash_hex}"

def user_exists(username, email):
    query = "SELECT COUNT(*) FROM users WHERE username = %s OR email = %s"
    param = (username, email)
    result = db_conn(query, param)
    return result[0][0] > 0

def sign_up_(details):
    try:
        username = details.get("username")
        email = details.get("email")
        phone_number = details.get("phone_number")
        password = details.get("password")

        if not all([username, email, phone_number, password]):
            return jsonify({"error": "All fields are required"}), 400

        if user_exists(username, email):
            return jsonify({"error": "Username or email already exists"}), 409

        hashed_password = hash_password(password)

        query = "INSERT INTO users (username, email, phone_number, password) VALUES (%s, %s, %s, %s)"
        param = (username, email, phone_number, hashed_password)
        insert_result = db_conn(query, param, fetch=False)

        if insert_result > 0:
            return jsonify({"message": "User registered successfully"}), 201
        else:
            return jsonify({"error": "Failed to register user"}), 500

    except Exception as e:
        # Log the error here
        return jsonify({"error": "An unexpected error occurred"}), 500