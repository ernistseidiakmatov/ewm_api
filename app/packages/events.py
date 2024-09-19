from .db_conn import *

def create_event(details):
    event_name = details["event_name"]
    event_description = details["event_description"]
    event_date_time = details["event_date_time"]
    max_capacity = details["max_capacity"]
    restaurant_id = details["restaurant_id"]
    host_id = details["host_id"]

    if restaurant_id == "":
        full_address = details["full_address"]
        latitude = details["latitude"]
        longitude = details["longitude"]

        locations_query = "INSERT INTO locations (latitude, logitude, full_address) VALUES (%s, %s, %s)"
        locations_params = (latitude, longitude, full_address)
        insert_result = db_conn(locations_query, locations_params, fetch=False)
        locations_id = insert_result["restaurant_id"]

        restaurant_query = "INSERT INTO restaurants (restaurant_name, restaruant_contact_info, restaurant_rating, location_id) VALUES (%s, %s, %s, %s)"
        restaurant_params = (
            details["restaurant_name"], details["restaurant_contact_info"],
            details["restaurant_rating", locations_id]
        )
        db_conn(restaurant_query, restaurant_params, fetch=False)
    else:
        restaurant_id = details["restaurant_id"]
        event_query = """
            INSERT INTO events (
                event_name, event_description,
                event_date_time, max_capacity, restaurant_id, host_id
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (event_name, event_description, event_date_time, max_capacity, restaurant_id, host_id)

        res = db_conn(event_query, params, fetch=False)
        return res

    

def get_events():
    query = """
        SELECT 
            e.event_id, 
            e.event_name, 
            e.event_description,
            e.event_date_time, 
            e.registered_participants,
            e.max_capacity, 
            e.event_status, 
            e.host_id, 
            r.restaurant_name, 
            r.restaurant_contact_info,
            r.restaurant_rating,
            l.latitude, 
            l.longitude, 
            l.full_address
        FROM 
            events e
        INNER JOIN 
            restaurants r ON e.restaurant_id = r.restaurant_id
        INNER JOIN 
            locations l ON r.location_id = l.location_id
    """
    result = db_conn(query)
    data = []
    for row in result:
        data.append({
            "event_id": row[0],
            "event_name": row[1],
            "event_description": row[2],
            "event_date_time": row[3],
            "registered_participants": row[4],
            "max_capacity": row[5],
            "event_status": row[6],
            "host_id": row[7],
            "restaurant": {
                "restaurant_name": row[8],
                "restaurant_contact_info": row[9],
                "restaurant_rating": row[10],
                "location": {
                    "latitude": row[11],
                    "longitude": row[12],
                    "full_address": row[13]
                }
            }
        })
    
    return data


def get_my_events(user_id):
    query = """
        SELECT 
            e.event_id, e.event_name, e.event_description,
            e.event_date_time, e.registered_participants,
            e.max_capacity, e.event_status, e.host_id, 
            r.restaurant_name, r.restaurant_contact_info,
            r.restaurant_rating,
            l.latitude, l.longitude, l.full_address
        FROM events e
        LEFT JOIN restaurants r ON e.restaurant_id = r.restaurant_id
        LEFT JOIN locations l ON r.location_id = l.location_id
        WHERE e.host_id = %s
    """
    param = (user_id,)  # Add a comma to make it a tuple
    result = db_conn(query, param)

    data = []
    for row in result:
        data.append({
            "event_id": row[0],
            "event_name": row[1],
            "event_description": row[2],
            "event_date_time": row[3],
            "registered_participants": row[4],
            "max_capacity": row[5],
            "event_status": row[6],
            "host_id": row[7],
            "restaurant": {
                "restaurant_name": row[8],
                "restaurant_contact_info": row[9],
                "restaurant_rating": row[10],
                "location": {
                    "latitude": row[11],
                    "longitude": row[12],
                    "full_address": row[13]
                }
            }
        })
    return data