#--make table duplicate proof--
from threading import local
from os.path import basename
'''
class db_update():
    def __init__(self):
        self.flag : bool
        self.query : str
    def set_flag(self,flag):
        self.flag = flag
'''

modify_att_punches_flag = True
modify_att_punches="""CREATE UNIQUE INDEX att_punches_index 
ON att_punches(employee_id, punch_time, workstate, verifycode, terminal_id)"""
 
modify_att_day_details = True
modify_new_table ="""
CREATE UNIQUE INDEX att_day_details_index ON att_day_details(employee_id,att_date,checkin,checkout)
"""

useful_vars = dir()[dir().index('local')+1:]
current_file = basename(__file__)
#print(vars().get(useful_vars[0]))
#print(useful_vars[0])
#print(vars().get(useful_vars[0]+"_flag"))
#vars().update({useful_vars[0]+"_flag":True})
#print(vars().get(useful_vars[0]+"_flag"))
def update_flags():       
    with open(current_file,'r') as record:
        data = record.readlines()
        for line_no, line in enumerate(data):
            for item in useful_vars:
                #print(line_no)
                if item+"_flag" in line:
                    if not globals().get(item+"_flag") :
                        data[line_no] = f"{item}_flag = True\n"
                        
    with open(current_file, 'w', encoding='utf-8') as file:
        file.writelines(data)
        #print(globals())
#print(locals())
print(update_flags())
print(useful_vars)
