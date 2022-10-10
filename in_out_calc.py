from datetime import datetime, timedelta
import string
import numpy as np
import adjustments
from databaseconnect import create_connection , insert_data
import pandas as pd

def calculate_in_out(df, name_of_att_date_col="att_date" , suffix_x="" ,suffix_y ="y" ,
in_early_grace=float ,in_late_grace=float,out_early_grace=float,out_late_grace=float ):
    att_date_time = df['punch_time'].str.split(" ", expand=True)
    df['att_date'] = att_date_time[0]
    df['time'] = att_date_time[1]
    
    df['checkin']  , df['checkout']= np.nan , np.nan
    #print(df['start'].astype('datetime64[h]'))

    nine = 9
    four = 4
    five = 5
    zero = 0
    three = 3
    end_val = df['end'].astype('datetime64[ns]').dt.hour
    punch_val = df['punch_time'].astype('datetime64[ns]').dt.hour
    start_val = df['start'].astype('datetime64[ns]').dt.hour    
    punch_date = df['punch_time'].astype('datetime64[ns]').dt.date
    #blanket case
    df['end'] = df['att_date'].astype('datetime64[ns]').dt.strftime("%Y-%m-%d") +" "+ df['end'].astype('datetime64[ns]').dt.strftime("%H:%M:%S")
    #case1
    df['end'][end_val < nine] = df['att_date'][end_val < nine].astype('datetime64[ns]').dt.strftime("%Y-%m-%d")+" "+ df['end'][end_val < nine].astype('datetime64[ns]').dt.strftime("%H:%M:%S")
    #case2
    df['end'][(end_val > nine) & (punch_val < nine)] = df['att_date'][(end_val > nine) & (punch_val < nine)].astype('datetime64[ns]').dt.strftime("%Y-%m-%d")+" "+ df['end'][(end_val > nine) & (punch_val < nine)].astype('datetime64[ns]').dt.strftime("%H:%M:%S")
    
    
    #for case1
    df['att_date'][(end_val < nine) & (punch_val < nine)] = df['att_date'][(end_val < nine) & (punch_val < nine)].astype('datetime64[ns]') - timedelta(days=1)
    #for case2 # day shif going after midnight , but not to affect early comers three hours margin
    df['att_date'][(end_val > nine) & (punch_val >= zero) & ((start_val - punch_val) > three)] = df['att_date'][(end_val > nine) & (punch_val >= zero) & ((start_val - punch_val) > three)].astype('datetime64[ns]') - timedelta(days=1)

    df['att_date'] = df['att_date'].astype('datetime64[D]')

    #att_date = df['att_date']

    df['start'] = df['att_date'].astype('datetime64[ns]').dt.strftime("%Y-%m-%d") +" "+ df['start'].astype('datetime64[ns]').dt.strftime("%H:%M:%S")
    #print(punch_val - start_val)

    df['checkin'][(-four<punch_val - start_val) & (punch_val - start_val<= five)] = df['punch_time'][(-four<punch_val - start_val) & (punch_val - start_val<=five)]

    df['checkout'] = df['punch_time'][df['punch_time'] != df['checkin']]

    check_out_dates = df['att_date'][df['checkout'].isna() == False]
    check_in_dates = df['att_date'][df['checkin'].isna() == False]
    
    for date in df['att_date'].unique():
        for emp in df['employee_id'].unique():
            df[(df['att_date'] == date) & (df['employee_id'] == emp)] = df[(df['att_date'] == date) & (df['employee_id'] == emp)].ffill().bfill()
    
    df1 = df[end_val < nine]
    df1.drop_duplicates(subset = ['employee_id','checkin','checkout'], keep = 'last', inplace= True)
    df2 = df[end_val > nine]
    df2.drop_duplicates(subset = ['employee_id','checkin','checkout'], keep = 'first', inplace= True)
    df = pd.concat([df1,df2] , ignore_index = True)
    
    punch_time = df['punch_time'][df['att_date'].isna() == True]
    #print(punch_time.astype('datetime64[D]'))
    df['att_date'][df['att_date'].isna() == True] =  punch_time.astype('datetime64[D]')

    #df.to_csv('raw2.csv') 
    df.drop_duplicates(['employee_id','att_date'] , keep= 'last' , inplace=True)
    
    replace_val = "--"
    
    #df.to_csv('raw.csv')
    
    df['worked_hours'] = np.nan
    df['total_hours'] = np.nan 

    df['worked_hours'] = adjustments.worked_hours(df=df ,end= 'checkout' , start= 'checkin')
    df['worked_hours'] = df['worked_hours'].dt.total_seconds()

    df['total_hours'] = adjustments.total_hours(df=df ,end= 'end' , start= 'start')
    df['total_hours'] = df['total_hours'].dt.total_seconds()
    
    
    df.replace(np.nan,"--",inplace = True)
    df.replace({np.nan:None},"--",inplace = True)
    df.replace('NaT',"--",inplace = True)
   
    #interested columns
    df= df.iloc[:,[0,5,2,7,8,9,10]]
    df['breakMinutes'] = 30
    df['breakRealMinutes'] = 30
    
    df.iloc[:,[0,1,2,7,8]]=df.iloc[:,[0,1,2,7,8]].astype('str')
    
    #dont include today , as in & out needed to be included
    today = datetime.strftime(datetime.now().date(),'%Y-%m-%d')
    df = df[df['att_date'] != today]
    #df.to_csv('raw1.csv')
    return df