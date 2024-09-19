import hashlib
from .db_conn import db_conn
from flask import jsonify
from .jwt_utils import generate_token

def verify_password(stored_password, provided_password):
    salt_hex, stored_hash = stored_password.split(':')
    salt = bytes.fromhex(salt_hex)
    hash_obj = hashlib.sha256()
    hash_obj.update(salt + provided_password.encode('utf-8'))
    calculated_hash = hash_obj.hexdigest()
    return calculated_hash == stored_hash

def sign_in_(details):
    username = details.get("username")
    password = details.get("password")
    
    if not username or not password:
        return {"error": "Username and password are required"}, 400
    
    query = "SELECT user_id, password FROM users WHERE username = %s"
    param = (username,)
    result = db_conn(query, param)
    
    if not result:
        return {"error": "Invalid credentials"}, 401
    
    user_id, stored_password = result[0]
    
    if verify_password(stored_password, password):
        token = generate_token(user_id)
        return {
            "message": "Sign in successful",
            "token": token
        }, 200
    else:
        return {"error": "Invalid credentials"}, 401