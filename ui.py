from datetime import datetime, timedelta , time
import streamlit as st
import pandas as pd
import numpy as np
from databaseconnect import query_db , run_triggers , query_nodf
import to_excel
import to_pdf
import image_prep
import insert_data
from in_out_calc import calculate_in_out
import pyautogui as pg
from sql_queries import query_attendance , query_time_table , query_update_attendance
from sql_queries import query_names , query_shift, query_start_or_end_of_shifts, query_employee_id , query_shift_id
import adjustments
#screen dimensions -- pyautogui work only on desktop 
s_d = pg.size()
s_w = s_d[0]
s_h = s_d[1]
#logo of rak services
logo = image_prep.image_prep()


#stm.option_menu("Menu" , )
def main_page(conn):
    page_config()    
    st.write(logo, unsafe_allow_html=True)
    hide_menues()

    #all report , manual insertion of record , add/remove/edit personnel -actvate - deactivate , shift creation edit and assign , machine management
    #don't forget to add salary and payroll calculation later on
    summary_report , adjust_attendance , manage_persons , shift_schedule , device_settings   = st.tabs(['REPORT' , 'ADJUSTMENTS' , 'MANAGE PERSONNEL' , 'SHIFT & SCHEDULING' , 'SETTINGS'])
    
    with summary_report:
        try:
            page1(conn)
        except IndexError:
            insert_data.insert_attendance()
            process_data(conn)
            st.experimental_rerun()
    with adjust_attendance:
        adjustment_page(conn)
    with manage_persons:
        None#manage_persons_page(conn)
    with shift_schedule:
        shift_schedule_page(conn)
    return None

    

def page1(conn):
    
    cont = st.container()
    exp = cont.expander("Filters")
    col1 , col2 , col3 = exp.columns(3)
    
    range_1_default=datetime.today().replace(day=1).date()
    range_2_default=datetime.today().date()
    
    st.header("Attendance Reporting")
    
    with col2:
        range1 = col2.date_input("From",range_1_default)
        
    with col3:
        range2 =col3.date_input("To",range_2_default)+timedelta(days=1)
    st.write(range1,"-",range2)
    
    df=query_db(conn,query_attendance)
    df.replace("--",np.nan,inplace = True)
        
    df['early_or_overtime'] = df['worked_hours'].astype(float) - df['total_hours'].astype(float)
   
    in_early_grace,in_late_grace=10,10
    out_early_grace,out_late_grace=10,30
    grace = 30
    
    df['early_or_overtime'] = df['early_or_overtime'].apply(lambda x: "Proper Time" if grace*-1<x<grace else ("Overtime" if  x > grace  else ("Early" if x < 0 else "Missing Details")))
    
    df['DAY'] = df['date'].astype('datetime64[ns]').dt.strftime("%A")
    
    df=adjustments.find_late_early(df=df,col_name="LOG IN STATUS",
    early_margin=in_early_grace,
    late_margin=in_late_grace, 
    calculation_method='in')
    
    df=adjustments.find_late_early(df=df,col_name="LOG OUT STATUS",
    log_in_or_out_col_name="out",
    late_value_to_display="Over",
    shift_start_or_end_col_name='end',
    early_margin=out_early_grace,
    late_margin=out_late_grace,
    calculation_method="out")
    
    df['name'] = df['name'].str.title()
    df['dept_name'] = df['dept_name'].str.title()

    df['LOG IN STATUS'][df['in'].isna() == True] = '\u2718'
    df['LOG OUT STATUS'][df['out'].isna() == True] = '\u2718'

    df['in'] = df['in'].astype('datetime64[ns]').dt.strftime('%I:%M:%S %p')
    df['out'] = df['out'].astype('datetime64[ns]').dt.strftime('%I:%M:%S %p')

    df['worked_hours'] = df['worked_hours'].astype('datetime64[s]').dt.strftime("%H:%M:%S")
    df['total_hours'] = df['total_hours'].astype('datetime64[s]').dt.strftime("%H:%M:%S")
    df=df.sort_values(by=['dept_name','name','date'], ascending=True)

    #replacement of unwanted
    df.replace(np.nan,"--",inplace = True)
    df.replace({np.nan:None},"--",inplace = True)
    df.replace('NaT',"\u2718",inplace = True)
    



    #name filter, drop down values
    filter_name = df['name'].unique().tolist()
    all = "All"
    filter_name.append(all)
    
    #deparment filter, drop down values
    filter_departments = df['dept_name'].unique().tolist()
    filter_departments.append(all)    

    with col1:
        name = col1.selectbox("Name",filter_name,filter_name.index(all))
        department = col1.selectbox("Department",filter_departments,filter_departments.index(all))
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").dt.date
    
    if name == all:
        df = df.query("name != @name and date >= @range1 and date < @range2")
    else:
        df = df.query("name == @name and date >= @range1 and date < @range2")
        df = missing_days(df=df , date1= range1 , date2 = range2 , date_col='date')
        df = df.iloc[0:-1]
    if department != all:
        df = df[df['dept_name'] == department]
    
    df = data_formatting(df)

    new_col_names =('DATE','DAY','EMPLOYEE NAME','DEPARTMENT','START','END','LOG IN','IN STATS','LOG OUT','OUT STATS','ACTUAL HOURS','SHIFT HOURS','STATUS')
    
    
    df = format_header(df,new_col_names)
    
    #fresh index with correct number
    df.reset_index(drop=True , inplace=True)
    
    #df = duplicate_formatting(df,[1,2])
    
    #highlight overtime
    #pass background-color for background and "color" for text  
    df = df.style.hide_index().set_caption(f"{logo}").applymap(change_color, 
    subset=['STATUS'],
    color ='yellow',
    filter ="Early",
    color_or_background = 'color').applymap(change_color, 
    subset=['STATUS'],
    color ='grey',
    filter ="Early",
    color_or_background = 'background-color').applymap(change_color, 
    subset=['STATUS'],
    color ='red',
    filter ="Not Present",
    color_or_background = 'background-color').applymap(change_color, 
    subset=['STATUS'],
    color ='white',
    filter ="Missing Details",
    color_or_background = 'color').applymap(change_color, 
    subset=['STATUS'],
    color ='magenta',
    filter ="Missing Details",
    color_or_background = 'background-color').applymap(change_color, 
    subset=['IN STATS'],
    color ='white',
    filter ="LATE",
    color_or_background = 'color').applymap(change_color, 
    subset=['IN STATS'],
    color ='red',
    filter ="LATE",
    color_or_background = 'background-color').applymap(change_color, 
    subset=['IN STATS'],
    color ='white',
    filter ="LATE",
    color_or_background = 'color').applymap(change_color, 
    subset=['IN STATS'],
    color ='red',
    filter ="LATE",
    color_or_background = 'background-color').applymap(change_color, 
    subset=['IN STATS'],
    color ='yellow',
    filter ="EARLY",
    color_or_background = 'color').applymap(change_color, 
    subset=['IN STATS'],
    color ='green',
    filter ="EARLY",
    color_or_background = 'background-color').applymap(change_color, 
    subset=['OUT STATS'],
    color ='white',
    filter ="EARLY",
    color_or_background = 'color').applymap(change_color, 
    subset=['OUT STATS'],
    color ='red',
    filter ="EARLY",
    color_or_background = 'background-color').applymap(change_color, 
    subset=['OUT STATS'],
    color ='red',
    filter ="Over",
    color_or_background = 'color').applymap(change_color, 
    subset=['OUT STATS'],
    color ='yellow',
    filter ="Over",
    color_or_background = 'background-color').set_properties(
    **{'border': '1px black solid !important'}).set_table_attributes(
    'style="border-collapse:collapse"').set_table_styles([{
        'selector': '.col_heading',
        'props': '''background-color: #5BDBF4; 
        color: black; 
        border-collapse: collapse; 
        border: 1px black solid !important;'''
    }])
    #applymap calls function change_color and send all parameters in subsequent arguments
    
    #to create pdf
    a = df.to_html()
    
    
    #a = to_pdf.to_pdf("test",a)

    buttons = st.container()
    col4 , col5 ,col6 = buttons.columns([1,2,4])

    with col4:
        st.download_button(label='PDF',
            data=a,
            file_name= f'Attendance {range1} - {range2} of {name} & {department}.html')
        
    df_xlsx = to_excel.to_excel(df)


    with col5:
        st.download_button(label='Download Excel',
                                    data=df_xlsx ,
                                    file_name= f'Attendance {range1} - {range2} of {name} & {department}.xlsx')
    with col6:
        if st.button("NEW DATA"):
            try:
                st.info(insert_data.insert_attendance())
                st.info(process_data(conn))
                #
            except:
                st.warning("DATA NOT IMPORTED \u2718")
            #st.experimental_rerun()
    #open(f'Attendance {range1} - {range2} of {name} & {department}.xlsx', 'wb').write(r.content)
    w_s = 1000
    h_s = 1000
    
    #pd.set_option('display.max_colwidth', None)
    
    #stc.html(a)
    #st._transparent_write(df)
    st.dataframe(df,use_container_width=True)
    #st.table(df)
    #old style , good for spread sheet methods
    ###st._legacy_dataframe(df,width=s_w-300 , height=s_h)

#second page
def adjustment_page(conn):
    df = query_db(conn ,query_names)
    names = df['name']
    dept = df['dept_name']
    
    cont = st.form("ATTENDANCE ADJUSTMENT",True)
    name = cont.selectbox("Name",names)
    punch_date = cont.date_input("Date",on_change=None)
    record_date = cont.date_input("IN/OUT Date")
    punch_time = cont.time_input("Punch Time",time(0))
    punch_type =  cont.radio("Select", ["IN" , "OUT"])
    punch_submit = cont.form_submit_button("Submit")

    if punch_submit:
        from sql_insertions import modify_missing_in_out , work_h_missing
        col_names = {"IN":"checkin","OUT":"checkout"}
        punch_type = col_names[punch_type]
        run_triggers(conn ,modify_missing_in_out.format(column = punch_type ,
        employee_name = name ,
        null_value = "--", 
        data = f"{record_date} {punch_time}",
        date = f"{punch_date}"))

        run_triggers(conn , work_h_missing.format(employee_name = name,
        date = f"{punch_date}") )
        #from databaseconnect import insert_data
        #from sql_insertions import update_in_out
        #st.info(insert_data(conn,update_in_out,list(calculate_in_out(query_db(conn,query_update_attendance)).to_records(index=False))))
        st.experimental_rerun()
        #st.write(punch_date,punch_time,punch_type,punch_submit)


def manage_persons_page(conn):
    from databaseconnect import insert_data
    from sql_insertions import update_in_out
    
    st.info(
    insert_data(conn,update_in_out,list(calculate_in_out(query_db(conn,query_update_attendance)).to_records(index=False)))
    )
    

#fourth shift page
def shift_schedule_page(conn):
    
    df_timetable = query_db(conn,query_time_table)
    df_shift = query_db(conn,query_shift)
    df_name = query_db(conn, query_names)
    cont = st.container()
    one , two  = cont.columns([0.35,0.65])

    with one:
        one_e1 = one.expander("TIMETABLES \U0001F4C5")
        one_e1.table(df_timetable)
        #o_e._transparent_write(df)
    
        one_e2 = one.expander("\U0001F4C5 CREATE NEW  \U000026CF")
        form_one_e2 = one_e2.form("PLS ENTER ALL DETAIL",True)
        x,y =None,None
        #---*--Inside elements of form---*--#
        timetable_name = form_one_e2.text_input("TIMETABLE NAME")
        timetable_color= form_one_e2.color_picker("ASSIGN COLOR")
        timetable_start = form_one_e2.time_input("START TIME",    value = x)
        timetable_end = form_one_e2.time_input("END TIME",   value = y)
        timetable_grace_in = form_one_e2.number_input("START LATE/EARLY MARGIN",value = 20)
        timetable_grace_out = form_one_e2.number_input("END LATE/EARLY MARGIN",value = 20)
        form_one_e2.form_submit_button("CREATE")
        #---*--Form ENDS HERE---*--#

        one_e3 = one.expander("CREATE SHIFT")
        form_one_e3 = one_e3.form("PLS ASSIGN TIME TABLES TO SHIFT",True)
        shift_name = form_one_e3.text_input("SHIFT NAME")
        shift_applicable = form_one_e3.date_input("DATE TO START SHIFT")
        shift_timetable = form_one_e3.selectbox("SUITABLE TIME TABLE",df_timetable['timetable_name'],1)
        
        shift_timetable_days = [form_one_e3.checkbox("Mon",0) , form_one_e3.checkbox("Tue",0) , form_one_e3.checkbox("Wed",0),
        form_one_e3.checkbox("Thur",0),form_one_e3.checkbox("Fri",0),
        form_one_e3.checkbox("Sat",0) , form_one_e3.checkbox("Sun",0)]
        
        form_one_e3.form_submit_button("GENERATE")
        #one.write(shift_timetable_days)
    with two:
        two_e1 = two.expander("ASSIGN SHIFTS")

        form_two_e1 = two_e1.form("PLS SELECT",True) 

        #---*--Inside elements of form---*--#
        name = form_two_e1.selectbox("SELECT PERSON", df_name['name'])
        shift_to_assign = form_two_e1.selectbox("SELECT SHIFT TO ASSIGN",df_shift)
        date_to_assign = form_two_e1.date_input("From")
        form_two_e1_submit = form_two_e1.form_submit_button("ASSIGN")
        #---*--Form ENDS HERE---*--#
        if form_two_e1_submit:
            from sql_insertions import update_shift_end , update_shift
            from databaseconnect import insert_data
            
            endDate_data =  query_nodf(conn,
            query_start_or_end_of_shifts.format(date= date_to_assign - timedelta(days=1) , 
            column = 'end' , employee_name = name))[0]

            run_triggers(conn,update_shift_end.format(column='endDate',data=endDate_data,employee_name=name))
            
            employee_id = query_nodf(conn,query_employee_id.format(employee_name=name))[0]

            shift_id = query_nodf(conn,query_shift_id.format(shift_name=shift_to_assign))[0]

            startDate_data = query_nodf(conn,
            query_start_or_end_of_shifts.format(date= date_to_assign, 
            column = 'start' , employee_name = name))[0]
            
            startDate_data = datetime.strptime(startDate_data,"%Y-%m-%d %H:%M:%S")-timedelta(hours=3)
            
            endDate_data = startDate_data + timedelta(days=3650)
            data = []
            data.append((startDate_data, endDate_data,'0',employee_id,shift_id ,datetime.now()))
            
            action = insert_data(conn,update_shift,data)

            st.write(action)


def process_data(conn):
    from databaseconnect import insert_data
    from sql_insertions import update_in_out
    processing = insert_data(conn,update_in_out,list(calculate_in_out(query_db(conn,query_update_attendance)).to_records(index=False)))
    return processing


#repeated cols to only appear once
def duplicate_formatting(df , cols=[]):
    size = len(df.iloc[:,cols[0]])
    #cols = [df.columns.get_loc(col) for col in cols]
    new_value = df.iloc[0,cols].to_list()
    for i in range(1,size):
        if new_value == df.iloc[i,cols].to_list():
            df.iloc[i,cols] = ['']*len(cols)
        else:
            new_value = df.iloc[i,cols].to_list()
    return df

#change color of a cell or background -- call with apply map
def change_color(value, color:str , filter:str , color_or_background:'background-color' or 'color'):
    if value == filter:
        return f"{color_or_background}: %s"  %color

#def change_line_color(value, color:str , filter:str , color_or_background:'background-color' or 'color'):
#    if value == filter:
#        line_color = f"{color_or_background}: {color}"*10
#        return line_color
#    else:
#        line_color = f"{color_or_background}: white"*10
#        return line_color

#change table headings
def format_header(df , replace_names:list):
    df.columns = replace_names
    return df

#add dates
def missing_days(df, date1:datetime, date2:datetime , date_col: str ):
    delta = date2 - date1
    
    df.set_index(date_col, inplace =True)

    idx = []
    holidays = []
    missing_days = []
    for i in range(0,delta.days+1):
        idx.append(date1 + timedelta(days=i))
        missing_days.append(idx[i].strftime("%A"))
        date = idx[i]
        if date.isoweekday() > 5 :
            holidays.append(date)
            #idx = pd.date_range(date1, date2)
    
    #fill values of newly added days 
    df.drop_duplicates(inplace=True)
    df = df.reindex(idx,fill_value = "--")
    #add name of newly added days
    df['DAY'].loc[idx] = missing_days
    #df.index.dt.dayofweek.apply(lambda x : "Holiday" if x > 5 else x)
    #df.index = df.index.strftime("%Y-%m-%d")
    df.reset_index(inplace = True)
    df['early_or_overtime'][df['date'].isin(holidays)] = "Holiday"

     #= "Holiday"
    return df

def data_formatting(df):
    df['early_or_overtime'][(df['in']=='--') & (df['out']=='--') & (df['DAY'] != "Saturday") & (df['DAY'] != "Sunday")] = "Not Present"
   
    #print(df['name'][df['name']!="--"].iloc[0])
    df['name'][df['name']=="--"] = df['name'][df['name']!="--"].iloc[0]
    df['dept_name'][df['dept_name']=="--"] = df['dept_name'][df['dept_name']!="--"].iloc[0]
    
    def remove_unwanted(col_name:str , val_to_replace:str):
    
        df[col_name][(df['in']=='--') & 
        (df['out']=='--') & 
        ((df['DAY'] == "Saturday") | (df['DAY'] == "Sunday"))] = val_to_replace

    remove_unwanted('start','--'),remove_unwanted('end','--')
    remove_unwanted('LOG IN STATUS','--'), remove_unwanted('LOG OUT STATUS','--'),
    remove_unwanted('worked_hours','--'),remove_unwanted('total_hours','--')
    remove_unwanted('early_or_overtime',"Holiday")
    

    return df

#set page configuration
def page_config():
    
    st.set_page_config("Attendace Reports",layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About":None})
#eliminate unwanted items
def hide_menues():
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            {width: 1200px;}
            {height: 0px;}
            footer {visibility: hidden;}
            footer:after{
                visibility: visible;
                }
            </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

#page unresponsive fun    
def page_unresponsive():
    st.write("WELCOME PAGE UNDERCONSTRUCTION")
    st.balloons()