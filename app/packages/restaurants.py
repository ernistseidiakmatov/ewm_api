from .db_conn import *
import json

def get_restaurant_by_address(full_address):
    query = """
        SELECT *
        FROM restaurants
        JOIN locations ON restaurants.location_id = locations.location_id
        WHERE locations.full_address = %s;
    """
    param = (full_address,)
    result = db_conn(query, param)

    result = convert_to_json(result)
    return result

def convert_to_json(data):
    rest = data[0]

    location = {
            "location_id": rest[4],
            "latitude": rest[8],
            "longitude": rest[9],
            "qfull_address": rest[10],
            "created_at": rest[11],
            "updated_at": rest[12]
        }

    res = {
        "restaurant_id": rest[0],
        "restaurant_name": rest[1],
        "restaurant_contact_info": rest[2],
        "restaurant_rating": rest[3],
        "created_at": rest[5],
        "updated_at": rest[6],
        "location": location
    }

    # result = json.dumps(res, indent=4, default=str)
    
    return res