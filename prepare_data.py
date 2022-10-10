from databaseconnect import query_nodf
from sql_queries import query_terminal
from machine_access import machine_access

def prepare_attendance_data(conn):
    with conn:
        data = []
        attendances = machine_access()
        for attendance in attendances:
            user_id = attendance.user_id
            punch_time = str(attendance.timestamp)
            workstate = attendance.punch
            punch = attendance.status
            terminal_id = query_nodf(conn, query_terminal.format(user_id=user_id) ,"all")[-1][0]#-1 & 0 to get last most value 
            data.append((user_id , punch_time, workstate , punch , terminal_id))
    return data
#print(access_machine())