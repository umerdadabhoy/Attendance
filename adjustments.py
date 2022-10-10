from datetime import timedelta
import string
import pandas as pd
import numpy as np

#in: in , out , start
#out: out, in , end
def adjustment(df, what_to_adjust :string , what_not_to :string):
    val = df[(df[what_to_adjust].astype(str) == "--") & (df[what_not_to].astype(str) != "--")]
    indexes = val.index
    df[what_to_adjust].loc[indexes] = df[what_to_adjust].loc[indexes] + 9

#Calculate worked hours
def worked_hours(df,end:str, start:str):
    worked_hours = pd.to_datetime(df[end]) -pd.to_datetime(df[start])
    return worked_hours

#calculate total hours , in a persons shift , for both evening and day
def total_hours(df , end:str , start:str):
    
    evening = df[end][df[end] < df[start]]

    total_hours =  pd.to_datetime(df[start]) - pd.to_datetime(evening) -timedelta(hours=6)
    
    day = df[end][df[end] > df[start]]
    total_hours.loc[day.index] = pd.to_datetime(day)- pd.to_datetime(df[start])       
    
    return total_hours

#def weekend(df,):    
    #return df

#calculate attendance statuses , late , early , ontime
def find_late_early(df,col_name=str,
    default_value= "Ontime",
    date_col_name= "date",
    shift_start_or_end_col_name="start",
    shift_col_for_compare = "start",
    log_in_or_out_col_name= "in",
    early_value_to_display="EARLY",
    late_value_to_display="LATE",
    early_margin=int,
    late_margin=int,
    calculation_method= "in" or "out"):
        #insert column after the column whose report is seeked
        df.insert(df.columns.get_loc(log_in_or_out_col_name)+1 , col_name , default_value)
        

        val_shift = df[shift_start_or_end_col_name].astype('datetime64[ns]')
        val_shift_hours = val_shift.dt.hour

        val_col = df[log_in_or_out_col_name].astype('datetime64[ns]')
        val_col_hours = val_col.dt.hour
        #val_diff = np.nan

        #where niether shift is zero nor time
        val_diff = (val_col-val_shift)/np.timedelta64(1,'m')
        #add one day to blance error if column val is midnight 
        val_diff[(00<= val_col_hours) & (val_col_hours <= 6) & (val_shift_hours > df[shift_col_for_compare].astype('datetime64[ns]').dt.hour)] = (val_col-val_shift)/np.timedelta64(1,'m') + 1440
        #remove whole day if shift is midnight
        val_diff[(val_shift_hours == 00)] = (val_col-val_shift)/np.timedelta64(1,'m') - 1440
        

        if calculation_method == 'in':
            early_margin = early_margin*-1
            df[col_name][val_diff < early_margin] = early_value_to_display
            df[col_name][val_diff > late_margin] = late_value_to_display
        elif calculation_method == 'out':
            early_margin = early_margin
            df[col_name][val_diff < early_margin] = early_value_to_display
            df[col_name][val_diff > late_margin] = late_value_to_display
        
        df[col_name][val_diff.isna() == True] = np.nan
        
        return df
        