from in_out_calc import *
from databaseconnect import *
from ui import *
import sql_queries

def main():
    #get database location
    database = sql_queries.database
    # create a database connection
    conn = create_connection(database)
    with conn:
        
    #query data base
    #df = query_db(conn, query)
    #get report
       
        main_page(conn)

    #generate csv
    #df.to_csv("test_report2.csv")
    conn.close()
main()
