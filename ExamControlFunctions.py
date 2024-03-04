import random
import DBCon

# Connect to the database
DB = DBCon.DB

# Get all results  from a query
def get_all_data(query):
    DB.execute(query)
    return DB.fetchall()