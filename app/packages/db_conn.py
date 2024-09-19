import psycopg2
from psycopg2 import sql

def db_conn(query, params=None, fetch=True):
    """
    Execute a SQL query on the PostgreSQL database.
    
    :param query: SQL query string
    :param params: Optional parameters for the query (default: None)
    :param fetch: Boolean to determine if results should be fetched (default: True)
    :return: Query results as a list of tuples for SELECT queries, 
             or number of affected rows for other query types
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="rocker69psql",
            port="5432"
        )

        with conn.cursor() as cur:
            if params:
                cur.execute(sql.SQL(query), params)
            else:
                cur.execute(query)
            
            if fetch and cur.description:  # SELECT query
                rows = cur.fetchall()
                return rows
            else:  # INSERT, UPDATE, DELETE query
                conn.commit()
                return cur.rowcount  # Return number of affected rows

    except (Exception, psycopg2.Error) as error:
        print("Error executing query:", error)
        return error

    finally:
        if conn:
            conn.close()

# Example usage:

# # SELECT query
# select_query = "SELECT * FROM users WHERE age > %s"
# select_params = (30,)
# select_results = db_conn(select_query, select_params)
# print("Select Results:", select_results)

# # INSERT query
# insert_query = "INSERT INTO users (name, age) VALUES (%s, %s)"
# insert_params = ("John Doe", 35)
# insert_result = db_conn(insert_query, insert_params, fetch=False)
# print("Insert Result: {} rows affected".format(insert_result))

# # UPDATE query
# update_query = "UPDATE users SET age = age + 1 WHERE name = %s"
# update_params = ("John Doe",)
# update_result = db_conn(update_query, update_params, fetch=False)
# print("Update Result: {} rows affected".format(update_result))

# # DELETE query
# delete_query = "DELETE FROM users WHERE age > %s"
# delete_params = (50,)
# delete_result = db_conn(delete_query, delete_params, fetch=False)
# print("Delete Result: {} rows affected".format(delete_result))