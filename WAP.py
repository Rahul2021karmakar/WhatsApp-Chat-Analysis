# import re
# import pandas as pd
# from datetime import datetime as dt

# def Text_to_dataframe(data):
#     pattern='\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}\s\w\w\s-'
#     message=re.split(pattern,data)[1:]
#     if len(message)==0:
#       pattern='\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}\s-'
#       message=re.split(pattern,data)[1:]
#     dates=re.findall(pattern,data)
#     df=pd.DataFrame({"Date":dates,"User_Message":message})
   
#     try:
#         df["Date"]=pd.to_datetime(df["Date"],format='%d/%m/%Y, %I:%M %p -')
#     except ValueError:
#         try:
#             df["Date"]=pd.to_datetime(df["Date"],format='%m/%d/%y, %I:%M %p -')
#         except ValueError:
#             try:
#                 df["Date"]=pd.to_datetime(df["Date"],format='%d/%m/%Y, %H:%M -')
#             except ValueError:
#                 # try:
#                 #     df["Date"]=pd.to_datetime(df["Date"],format='%d/%m/%y, %I:%M %p -')
#                 # except ValueError:
#                     # try:
#                     #     df["Date"]=pd.to_datetime(df["Date"],format='%m/%d/%y, %H:%M -')
#                     # except ValueError:
#                         try:
#                             df["Date"]=pd.to_datetime(df["Date"],format='%m/%d/%Y, %H:%M -')
#                         except ValueError:
#                             print("Date format not matched!!!")
#                             # try:
#                             #     df["Date"]=pd.to_datetime(df["Date"],format='%m/%d/%Y, %I:%M %p -')
#                             # except ValueError:
#                             #     df["Date"]=pd.to_datetime(df["Date"],format='%d/%m/%y, %H:%M -')
            

#     users=[]
#     messages=[]
#     for message in df['User_Message']:
#       entry=re.split('([\w\W]+?):\s',message)
#       if entry[1:]:
#         users.append(entry[1])
#         messages.append(entry[2])
#       else:
#         users.append('Notification')
#         messages.append(entry[0])
    
#     df.insert(loc=0,column="User_Name",value=users)
#     df.insert(loc=1,column="Messages",value=messages)
#     df=df.drop('User_Message',axis=1)
#     Year=df['Date'].dt.year
#     Month=df['Date'].dt.month_name()
#     Day=df['Date'].dt.day
#     df.insert(loc=0,column='Day',value=Day)
#     df.insert(loc=1,column='Month',value=Month)
#     df.insert(loc=2,column='Year',value=Year)
#     Hour=df['Date'].dt.hour
#     Minute=df['Date'].dt.minute
#     df.insert(loc=3,column='Hour',value=Hour)
#     df.insert(loc=4,column='Minute',value=Minute)
#     return df



import re
import pandas as pd
from datetime import datetime

class WhatsAppParser:
    # Define date patterns in order of likelihood
    DATE_PATTERNS = [
        '%d/%m/%Y, %I:%M %p -',  # Most common format: 25/10/2023, 10:30 AM -
        '%m/%d/%y, %I:%M %p -',   # 10/25/23, 10:30 AM -
        '%d/%m/%Y, %H:%M -',      # 25/10/2023, 10:30 -
        '%m/%d/%Y, %H:%M -',      # 10/25/2023, 10:30 -
        '%d/%m/%y, %I:%M %p -',   # 25/10/23, 10:30 AM -
        '%m/%d/%y, %H:%M -',      # 10/25/23, 10:30 -
    ]
    
    MESSAGE_PATTERN = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}\s[\w\s]*-)'
    USER_MESSAGE_PATTERN = r'([^:]+):\s(.+)'

    @staticmethod
    def parse_chat_data(data):
        """Parse WhatsApp chat data into a structured DataFrame"""
        # Split messages using the date pattern
        messages = re.split(WhatsAppParser.MESSAGE_PATTERN, data)[1:]
        
        # Pair dates with messages
        dates = messages[0::2]  # Even indices
        text_messages = messages[1::2]  # Odd indices
        
        if not dates:
            raise ValueError("No valid messages found in the input data")
        
        # Create DataFrame with raw data
        df = pd.DataFrame({"Date": dates, "Raw_Message": text_messages})
        
        # Parse dates with multiple format attempts
        df = WhatsAppParser._parse_dates(df)
        
        # Extract users and messages
        df = WhatsAppParser._extract_users_messages(df)
        
        # Add datetime components as columns
        df = WhatsAppParser._add_datetime_components(df)
        
        return df

    @staticmethod
    def _parse_dates(df):
        """Parse date strings using multiple possible formats"""
        for pattern in WhatsAppParser.DATE_PATTERNS:
            try:
                df["Date"] = pd.to_datetime(
                    df["Date"].str.strip(), 
                    format=pattern,
                    errors='raise'
                )
                return df  # Return if successful
            except (ValueError, TypeError):
                continue
        
        # If all patterns fail, try flexible parsing
        try:
            df["Date"] = pd.to_datetime(
                df["Date"].str.strip(), 
                errors='coerce'
            )
            return df
        except Exception as e:
            raise ValueError("Failed to parse dates with all formats") from e

    @staticmethod
    def _extract_users_messages(df):
        """Extract users and messages from raw text"""
        users = []
        messages = []
        
        for raw_msg in df["Raw_Message"]:
            match = re.match(WhatsAppParser.USER_MESSAGE_PATTERN, raw_msg)
            if match:
                users.append(match.group(1).strip())
                messages.append(match.group(2).strip())
            else:
                users.append('Notification')
                messages.append(raw_msg.strip())
        
        df.insert(0, "User_Name", users)
        df.insert(1, "Messages", messages)
        return df.drop("Raw_Message", axis=1)

    @staticmethod
    def _add_datetime_components(df):
        """Add datetime components as separate columns"""
        datetime_components = {
            "Day": df["Date"].dt.day,
            "Month": df["Date"].dt.month_name(),
            "Year": df["Date"].dt.year,
            "Hour": df["Date"].dt.hour,
            "Minute": df["Date"].dt.minute,
            "DayOfWeek": df["Date"].dt.day_name(),
        }
        
        # Insert components at the beginning of the DataFrame
        for i, (col_name, values) in enumerate(datetime_components.items()):
            df.insert(i, col_name, values)
            
        return df

# Alias for backward compatibility
Text_to_dataframe = WhatsAppParser.parse_chat_data