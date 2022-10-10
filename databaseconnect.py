from msilib.schema import Error
import sqlite3
import pandas as pd

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def query_db(conn , query_text):
    cur = conn.cursor()
    cur.execute(query_text)
    rows = pd.DataFrame(cur.fetchall(),columns= [description[0] for description in cur.description])
    
    return rows

def query_nodf(conn , query_text, method= "one" or "all"):
    cur = conn.cursor()
    cur.execute(query_text)
    if method == "one":
        return cur.fetchone()
    else:
        return cur.fetchall()

def run_triggers(conn, command_text):
    cur = conn.cursor()
    cur.execute(command_text)
    conn.commit()
    cur.close()
    
def insert_data(conn , query_text, data):
    cur = conn.cursor()
    cur.executemany(query_text, data)
    conn.commit()
    status = f"Total, {cur.rowcount}, Records entered successfully"
    cur.close()
    return status
