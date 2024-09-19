from packages.db_conn import db_conn

username = 'test_1'
query = "SELECT * FROM events WHERE host_id = %s"
param = (username,)
res = db_conn(query, param)

print(res)