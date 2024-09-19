import psycopg2
import json


def get_():
    return "world"

def get_select():
    conn = psycopg2.connect(host="localhost", port='5432', dbname='test_erp', user='postgres', password='rocker69psql')

    cur = conn.cursor()

    cur.execute("SELECT * FROM clients")

    records = cur.fetchall()

    name = records[0][1]
    l_name = records[0][2]
    role = records[0][3]

    res = {
        "name": name,
        "last": l_name,
        "role": role
    }
    return res