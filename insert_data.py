from sql_insertions import update_attendance
from prepare_data import prepare_attendance_data
from sql_queries import database
from databaseconnect import create_connection , insert_data

#query_to_execute = map(sql_insertions.__dict__.get, list(sql_insertions.__dict__.keys())[8:])
#print(query_to_execute)
def insert_attendance():

    conn = create_connection(database)
    
    data = prepare_attendance_data(conn)

    query = update_attendance

    status = insert_data(conn , query , data)

    return status