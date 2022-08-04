import re
import pandas as pd
from datetime import datetime as dt

def Text_to_dataframe(data):
    pattern='\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}\s\w\w\s-'
    message=re.split(pattern,data)[1:]
    if len(message)==0:
      pattern='\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}\s-'
      message=re.split(pattern,data)[1:]
    dates=re.findall(pattern,data)
    df=pd.DataFrame({"Date":dates,"User_Message":message})
   
    try:
        df["Date"]=pd.to_datetime(df["Date"],format='%d/%m/%Y, %I:%M %p -')
    except ValueError:
        try:
            df["Date"]=pd.to_datetime(df["Date"],format='%m/%d/%y, %I:%M %p -')
        except ValueError:
            try:
                df["Date"]=pd.to_datetime(df["Date"],format='%d/%m/%Y, %H:%M -')
            except ValueError:
                df["Date"]=pd.to_datetime(df["Date"],format='%d/%m/%y, %I:%M %p -')
            

    users=[]
    messages=[]
    for message in df['User_Message']:
      entry=re.split('([\w\W]+?):\s',message)
      if entry[1:]:
        users.append(entry[1])
        messages.append(entry[2])
      else:
        users.append('Notification')
        messages.append(entry[0])
    
    df.insert(loc=0,column="User_Name",value=users)
    df.insert(loc=1,column="Messages",value=messages)
    df=df.drop('User_Message',axis=1)
    Year=df['Date'].dt.year
    Month=df['Date'].dt.month_name()
    Day=df['Date'].dt.day
    df.insert(loc=0,column='Day',value=Day)
    df.insert(loc=1,column='Month',value=Month)
    df.insert(loc=2,column='Year',value=Year)
    Hour=df['Date'].dt.hour
    Minute=df['Date'].dt.minute
    df.insert(loc=3,column='Hour',value=Hour)
    df.insert(loc=4,column='Minute',value=Minute)
    return df
