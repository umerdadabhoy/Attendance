update_attendance = """INSERT or IGNORE INTO att_punches(employee_id, punch_time, workstate, verifycode, terminal_id)
VALUES
(?,?,?,?,?);"""

update_in_out="""INSERT or IGNORE INTO att_day_details(employee_id,
att_date,
timetable_id, checkin,
checkout,
workedMinutes,rworkedMinutes,
breakMinutes,breakRealMinutes,sortindex)
VALUES
(?,?,?,?,?,?,?,?,?,0)"""

modify_missing_in_out = """UPDATE att_day_details SET '{column}' = CASE WHEN att_day_details.{column} == '{null_value}' THEN '{data}' ELSE att_day_details.{column} END
where att_day_details.employee_id =
(SELECT hr_employee.id
from hr_employee
where hr_employee.emp_firstname||' '||hr_employee.emp_lastname = '{employee_name}')
AND
att_day_details.att_date = '{date}'"""

work_h_missing = """UPDATE att_day_details 
SET 
workedMinutes = strftime('%s',checkout) - strftime('%s',checkin)
where att_day_details.employee_id =
(SELECT hr_employee.id
from hr_employee
where hr_employee.emp_firstname||' '||hr_employee.emp_lastname = '{employee_name}')
AND
att_day_details.att_date = '{date}'"""

update_shift_end = """
UPDATE att_employee_shift SET '{column}' = '{data}'
WHERE att_employee_shift.employee_id = (
SELECT hr_employee.id
from hr_employee
where hr_employee.emp_firstname||' '||hr_employee.emp_lastname = '{employee_name}'
)
AND
att_employee_shift.id = (
SELECT att_employee_shift.id FROM att_employee_shift
WHERE att_employee_shift.employee_id = (
SELECT hr_employee.id
from hr_employee
WHERE hr_employee.emp_firstname||' '||hr_employee.emp_lastname = '{employee_name}')
ORDER BY att_employee_shift.id DESC LIMIT 1
)
"""

update_shift = """INSERT or IGNORE INTO att_employee_shift(startDate,
endDate,
NoEndDate,
employee_id,
shift_id,
modifyDate)
VALUES
(?,?,?,?,?,?)"""

