#database address
database = r"C:\Program Files (x86)\ZKTime.Net\ZKTimeNet.db"


#1-emp-id,att_date, timerable-id,checkin,checkout
query = """SELECT DISTINCT att_punches.employee_id,
    hr_employee.emp_firstname ||" "|| hr_employee.emp_lastname AS name , hr_department.dept_name,
    att_punches.punch_time, 
    substr(att_timetable.timetable_start,12) As start, substr(att_timetable.timetable_end,12) AS end 
    FROM att_punches 
    INNER JOIN att_employee_shift 
    ON att_employee_shift.employee_id = att_punches.employee_id AND (att_punches.punch_time >= att_employee_shift.startDate
	AND att_punches.punch_time <= att_employee_shift.endDate)
    INNER JOIN att_shift_details
    USING(shift_id)
    INNER JOIN att_timetable
    ON att_shift_details.timetable_id = att_timetable.id
    INNER JOIN hr_employee
    ON att_punches.employee_id = hr_employee.id
	INNER JOIN hr_department 
	ON hr_employee.department_id = hr_department.id
    WHERE att_punches.punch_time  >= '{date1}' AND att_punches.punch_time  <= '{date2}+1'
    ORDER BY att_punches.employee_id;"""

query_update_attendance="""SELECT DISTINCT att_punches.employee_id,
    att_punches.punch_time, att_timetable.id As timetable_id,
    substr(att_timetable.timetable_start,12) As start, substr(att_timetable.timetable_end,12) AS end 
    FROM att_punches
    LEFT JOIN att_employee_shift 
    ON att_employee_shift.employee_id = att_punches.employee_id AND (att_punches.punch_time >= att_employee_shift.startDate
	AND att_punches.punch_time <= att_employee_shift.endDate)
    LEFT JOIN att_shift_details
    USING(shift_id)
    LEFT JOIN att_timetable
    ON att_shift_details.timetable_id = att_timetable.id
    LEFT JOIN hr_employee
    ON att_punches.employee_id = hr_employee.id
	LEFT JOIN hr_department 
	ON hr_employee.department_id = hr_department.id
	WHERE timetable_id != ''
    ORDER BY att_punches.employee_id;"""

query_terminal = """SELECT DISTINCT att_terminal_zone.terminal_id FROM  
att_employee_zone
LEFT JOIN att_terminal_zone
USING(zone_id)
WHERE employee_id == {user_id}"""

query_time_table = """SELECT att_timetable.timetable_name , att_timetable.timetable_color, 
substr(att_timetable.timetable_start,12) as 'Start Time' , substr(att_timetable.timetable_end,12) as 'End Time' ,
att_timetable.timetable_latecome as 'IN RELAX' , att_timetable.timetable_earlyout as 'OUT RELAX' from att_timetable"""

query_names = """SELECT hr_employee.emp_firstname||' '||hr_employee.emp_lastname as 'name', hr_department.dept_name
from hr_employee
LEFT JOIN  hr_department
ON hr_employee.department_id = hr_department.id;"""

query_attendance = """SELECT DISTINCT att_day_details.att_date as 'date' , strftime('%w',att_day_details.att_date) as 'DAY' ,
hr_employee.emp_firstname||' '||hr_employee.emp_lastname as 'name', hr_department.dept_name as 'dept_name',
substr(att_timetable.timetable_start,12) as 'start' , substr(att_timetable.timetable_end,12) as 'end',
strftime('%H:%M:%S',att_day_details.checkin) as 'in', 
strftime('%H:%M:%S',att_day_details.checkout) as 'out',
att_day_details.workedMinutes as'worked_hours',
att_day_details.rworkedMinutes as'total_hours'
 from att_day_details
 LEFT JOIN hr_employee
 ON att_day_details.employee_id = hr_employee.id
 LEFT JOIN hr_department
 ON hr_employee.department_id = hr_department.id
 LEFT JOIN att_timetable
 ON att_day_details.timetable_id = att_timetable.id
 ORDER BY att_day_details.employee_id;"""

query_shift = """SELECT att_shift.shift_name from att_shift;"""

query_start_or_end_of_shifts="""SELECT DISTINCT '{date}'||' '||substr(att_timetable.timetable_{column},12) as data 
from att_employee_shift
INNER JOIN att_shift_details
ON att_employee_shift.shift_id = att_shift_details.shift_id
INNER JOIN att_timetable
ON att_shift_details.timetable_id = att_timetable.id
where att_employee_shift.employee_id = (SELECT hr_employee.id
from hr_employee
where hr_employee.emp_firstname||' '||hr_employee.emp_lastname = '{employee_name}')
ORDER BY att_employee_shift.id DESC
LIMIT 1"""

query_employee_id = """SELECT hr_employee.id
from hr_employee
where hr_employee.emp_firstname||' '||hr_employee.emp_lastname = '{employee_name}'"""

query_shift_id = """SELECT att_shift.id
from att_shift
where att_shift.shift_name = '{shift_name}'"""