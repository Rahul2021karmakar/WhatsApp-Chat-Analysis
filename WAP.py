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