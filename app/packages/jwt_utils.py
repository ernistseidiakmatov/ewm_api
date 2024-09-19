import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your_secret_key'  # Store this securely, preferably in environment variables

def generate_token(user_id):
    expiration = datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
    return jwt.encode(
        {'user_id': user_id, 'exp': expiration},
        SECRET_KEY,
        algorithm='HS256'
    )

def verify_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return data['user_id']
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token