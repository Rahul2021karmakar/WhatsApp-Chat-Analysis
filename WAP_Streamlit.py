# -*- coding: utf-8 -*-
"""
WhatsApp Chat Analysis Streamlit App
Refactored version with improved structure and readability
"""
import pandas as pd
import streamlit as st
from urlextract import URLExtract
from matplotlib import pyplot as plt
from wordcloud import WordCloud 
from collections import Counter
import emoji
import seaborn as sns
from WAP import WhatsAppParser  # Assuming this is your custom module for data processing

# Constants
STOPWORDS_PATH = r'P:\Codes\Python programme\Data Science and ML\WAP chat analysis\stop_hinglish.txt'

# Initialize sidebar
st.sidebar.title("WhatsApp Chat Analysis")
uploaded_file = st.sidebar.file_uploader("Choose a file", type={"txt"})

class WhatsAppAnalyzer:
    def __init__(self):
        self.extractor = URLExtract()
        self.chat_df = None
        
    def load_data(self):
        """Load and preprocess WhatsApp chat data"""
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            data = bytes_data.decode("utf-8")
            # Parse into DataFrame
            self.chat_df = WhatsAppParser.parse_chat_data(data)
            self._preprocess_data()
            return True
        return False
    
    def _preprocess_data(self):
        """Preprocess the loaded dataframe"""
        self.chat_df["Date"] = pd.to_datetime(self.chat_df["Date"])
        self.chat_df['Month_num'] = self.chat_df['Date'].dt.month
        self.chat_df['Year'] = self.chat_df['Date'].dt.year
        self.chat_df['Month'] = self.chat_df['Date'].dt.month_name()
        self.chat_df['Hour'] = self.chat_df['Date'].dt.hour
        self.chat_df['Day_name'] = self.chat_df['Date'].dt.day_name()
        
    def get_user_list(self):
        """Get sorted list of unique users"""
        user_list = self.chat_df['User_Name'].unique().tolist()
        if 'Notification' in user_list:
            user_list.remove('Notification')
        user_list.sort()
        user_list.insert(0, "Overall")
        return user_list
    
    def get_basic_stats(self, selected_user):
        """Calculate basic statistics for selected user"""
        if selected_user == 'Overall':
            df = self.chat_df
        else:
            df = self.chat_df[self.chat_df["User_Name"] == selected_user]
            
        # Calculate statistics
        total_messages = df.shape[0]
        
        words = []
        for msg in df['Messages'].astype(str).str.split(" "):
            words.extend(msg)
        total_words = len(words)
        
        media_count = df[df['Messages'] == "<Media omitted>\n"].shape[0]
        
        links = []
        for msg in df['Messages'].astype(str):
            links.extend(self.extractor.find_urls(msg))
        total_links = len(links)
        
        return total_messages, total_words, media_count, total_links
    
    def get_busy_users(self):
        """Get statistics about most active users"""
        user_counts = self.chat_df["User_Name"].value_counts().head()
        user_percent = round((self.chat_df['User_Name'].value_counts() / 
                             self.chat_df.shape[0]) * 100, 2)
        user_percent = user_percent.reset_index().rename(
            columns={'index': 'Name', 'User_Name': 'Percent'})
        return user_counts, user_percent
    
    def generate_wordcloud(self, selected_user):
        """Generate word cloud for selected user"""
        temp = self.chat_df[
            (self.chat_df['User_Name'] != 'Notification') & 
            (self.chat_df['Messages'] != '<Media omitted>\n')
        ]
        
        with open(STOPWORDS_PATH, 'r') as f:
            stop_words = f.read()
            
        if selected_user != 'Overall':
            temp = temp[temp['User_Name'] == selected_user]
            
        words = []
        for msg in temp['Messages'].astype(str):
            for word in msg.lower().split():
                if word not in stop_words:
                    words.append(word)
                    
        wordcloud = WordCloud(
            width=500, height=500, 
            min_font_size=10, 
            background_color='white'
        ).generate(' '.join(words))
        
        return wordcloud
    
    def get_common_words(self, selected_user, n=50):
        """Get most common words for selected user"""
        temp = self.chat_df[
            (self.chat_df['User_Name'] != 'Notification') & 
            (self.chat_df['Messages'] != '<Media omitted>\n')
        ]
        
        with open(STOPWORDS_PATH, 'r') as f:
            stop_words = f.read()
            
        if selected_user != 'Overall':
            temp = temp[temp['User_Name'] == selected_user]
            
        words = []
        for msg in temp['Messages'].astype(str):
            for word in msg.lower().split():
                if word not in stop_words:
                    words.append(word)
                    
        return pd.DataFrame(Counter(words).most_common(n))
    
    def get_emoji_stats(self, selected_user):
        """Get emoji statistics for selected user"""
        emojis = []
        emoji_meanings = []
        
        if selected_user != 'Overall':
            df = self.chat_df[self.chat_df['User_Name'] == selected_user]
        else:
            df = self.chat_df
            
        for message in df['Messages'].astype(str):
            em_list = emoji.distinct_emoji_list(message)
            emojis.extend(em_list)
            emoji_meanings.extend([emoji.demojize(e) for e in em_list])
            
        em_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
        meanings_df = pd.DataFrame(Counter(emoji_meanings).most_common(len(Counter(emoji_meanings))))
        
        em_df.insert(loc=1, column='Meanings', value=meanings_df[0])
        em_df = em_df.rename(columns={0: 'Emoji', 1: 'Frequency'})
        
        return em_df
    
    def get_timeline_data(self, selected_user, freq='monthly'):
        """Get timeline data (monthly or daily)"""
        if selected_user != 'Overall':
            df = self.chat_df[self.chat_df['User_Name'] == selected_user]
        else:
            df = self.chat_df
            
        if freq == 'monthly':
            timeline = df.groupby(['Year', 'Month_num', 'Month']).count()['Messages'].reset_index()
            timeline['Time'] = timeline['Month'] + '-' + timeline['Year'].astype(str)
            return timeline
        else:  # daily
            df['Only_date'] = df['Date'].dt.date
            return df.groupby(['Only_date']).count()['Messages'].reset_index()

    def get_activity_data(self, selected_user, by='day'):
        """Get activity data by day or month with consistent column names"""
        if selected_user != 'Overall':
            df = self.chat_df[self.chat_df['User_Name'] == selected_user]
        else:
            df = self.chat_df
            
        if by == 'day':
            result = df['Day_name'].value_counts().reset_index()
            result.columns = ['Day', 'Count']  # Explicit column naming
            return result
        else:  # month
            result = df['Month'].value_counts().reset_index()
            result.columns = ['Month', 'Count']  # Explicit column naming
            return result


    def generate_heatmap(self, selected_user):
        """Generate activity heatmap"""
        # Create time periods
        periods = []
        for hour in self.chat_df['Hour']:
            if hour == 23:
                periods.append(f"{hour}-00")
            elif hour == 0:
                periods.append(f"00-{hour+1}")
            else:
                periods.append(f"{hour}-{hour+1}")
                
        df = self.chat_df.copy()
        df['Period'] = periods
        
        if selected_user != 'Overall':
            df = df[df['User_Name'] == selected_user]
            
        pivot = df.pivot_table(
            index='Day_name', 
            columns='Period', 
            values='Messages', 
            aggfunc='count'
        ).fillna(0)
        
        plt.figure(figsize=(20, 8))
        sns.heatmap(pivot)
        return plt

# Main app execution
def main():
    analyzer = WhatsAppAnalyzer()
    
    if analyzer.load_data():
        st.dataframe(analyzer.chat_df, width=3000, height=200)
        
        # User selection
        user_list = analyzer.get_user_list()
        selected_user = st.sidebar.selectbox(
            "Show User analysis with respect to", 
            user_list
        )
        
        if st.sidebar.button("Show Analysis"):
            # Basic stats
            st.title("Top Statistics")
            total_msgs, total_words, media_count, total_links = analyzer.get_basic_stats(selected_user)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.header("Total Messages")
                st.title(total_msgs)
            with col2:
                st.header("Total Words")
                st.title(total_words)
            with col3:
                st.header("Total Media")
                st.title(media_count)
            with col4:
                st.header("Total Links")
                st.title(total_links)
            
            # User contribution (for Overall only)
            if selected_user == 'Overall':
                st.title("User Contribution in a chat")
                col31, col32 = st.columns(2)
                user_counts, user_percent = analyzer.get_busy_users()
                
                with col31:
                    st.header('Graphical View')
                    fig, ax = plt.subplots()
                    ax.bar(user_counts.index, user_counts.values, color=[0.1350, 0.2780, 0.3840])
                    plt.xticks(rotation=20)
                    plt.ylabel('No. of messages')
                    plt.xlabel('User Name')
                    st.pyplot(fig)
                
                with col32:
                    st.header('Statistical View')
                    st.dataframe(user_percent)
            
            # Activity Map
            st.title('Activity Map')
            col41, col42 = st.columns(2)
            
            with col41:
                st.header('Most busy day')
                busy_day = analyzer.get_activity_data(selected_user, by='day')
                fig, ax = plt.subplots()
                ax.bar(busy_day['Day'], busy_day['Count'], color=[0.75, 0.75, 0])
                plt.xticks(rotation=20)
                st.pyplot(fig)

            with col42:
                st.header('Most busy month')
                busy_month = analyzer.get_activity_data(selected_user, by='month')
                fig, ax = plt.subplots()
                ax.bar(busy_month['Month'], busy_month['Count'], color=[0.6350, 0.0780, 0.1840])
                plt.xticks(rotation=25)
                st.pyplot(fig)
            
            # Timeline Analysis
            st.title("Timeline Analysis")
            col21, col22 = st.columns(2)
            
            with col21:
                st.header("Monthly Timeline")
                monthly_timeline = analyzer.get_timeline_data(selected_user, freq='monthly')
                fig = plt.figure(figsize=(8, 6))
                plt.plot(monthly_timeline['Time'], monthly_timeline['Messages'], 
                         color=[0.3150, 0.6180, 0.9140])
                plt.xticks(rotation=50)
                st.pyplot(fig)
            
            with col22:
                st.header('Daily Timeline')
                daily_timeline = analyzer.get_timeline_data(selected_user, freq='daily')
                fig = plt.figure(figsize=(8, 6))
                plt.plot(daily_timeline['Only_date'], daily_timeline['Messages'], 
                         color=[0.4660, 0.6740, 0.1880])
                plt.xticks(rotation=50)
                st.pyplot(fig)
            
            # Weekly Activity Heatmap
            st.title('Weekly Activity Map')
            heatmap_plot = analyzer.generate_heatmap(selected_user)
            st.pyplot(heatmap_plot)
            
            # Word Cloud
            st.title("Word Cloud")
            wordcloud = analyzer.generate_wordcloud(selected_user)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud)
            st.pyplot(fig)
            
            # Most Common Words
            st.title("Most Common Word")
            common_words = analyzer.get_common_words(selected_user)
            fig, ax = plt.subplots()
            ax.barh(common_words[0], common_words[1], color=[0.1350, 0.5780, 0.5840])
            plt.yticks(fontsize=5)
            plt.xlabel("Frequency")
            plt.ylabel("Most Common Word")
            st.pyplot(fig)
            
            # Most Common Emoji
            st.title("Most Common Emoji")
            emoji_stats = analyzer.get_emoji_stats(selected_user)
            st.dataframe(emoji_stats, width=2000)
    else:
        st.header('Upload your WhatsApp chat...')

if __name__ == "__main__":
    main()