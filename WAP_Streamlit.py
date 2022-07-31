# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 22:46:19 2022

@author: DELL
"""
import pandas as pd
import streamlit as st
from urlextract import URLExtract
from matplotlib import pyplot as plt
from wordcloud import WordCloud 
from collections import Counter
import emoji
import seaborn as sns
st.sidebar.title("WhatsApp chat analysis..")
uploaded_file = st.sidebar.file_uploader("Choose a file",type={"csv","txt"})

#@st.cache(allow_output_mutation=True)
def UploadFile():
    if uploaded_file is not None:
         data=pd.read_csv(uploaded_file)
         return data

chat1=UploadFile()
chat=chat1
chat["Date"]=pd.to_datetime(chat["Date"])
chat['Month_num']=chat['Date'].dt.month
st.dataframe(chat,width=3000,height=200)     
#st.text(type(chat))

user_list=chat['User_Name'].unique().tolist()
user_list.remove('Notification')
user_list.sort()
user_list.insert(0,"Overall")
selected_user=st.sidebar.selectbox("Show User analysis with respect to",user_list)

extractor=URLExtract()
@st.cache(allow_output_mutation=True)
def fetch_chat(selected_user,chat):
    if selected_user=='Overall':
        #count number of chat
        line=chat.shape[0]
        #count number of word 
        word=[]
        msg=chat['Messages'].astype(str).str.split(" ")
        for i in msg:
            word.extend(i)
        #count number of shared media
        msg1=chat[chat['Messages']=="<Media omitted>\n"]
        media=msg1.shape[0]
        #count number of shared link
        link=[]
        msg=chat['Messages'].astype(str)
        for i in msg:
            link.extend(extractor.find_urls(i))
        return line,len(word),media,len(link)
        
    else:
        df=chat[chat["User_Name"]==selected_user]
        line=df.shape[0]
        word=[]
        #df1=chat["Messages"]==selected_user
        msg=df['Messages'].astype(str).str.split(" ")
        for i in msg:
            word.extend(i)
        msg1=df[df['Messages']=="<Media omitted>\n"]
        media=msg1.shape[0]
        #count number of shared link
        link=[]
        msg=df['Messages'].astype(str)
        for i in msg:
            link.extend(extractor.find_urls(i))
        return line,len(word),media,len(link)
    
@st.cache(allow_output_mutation=True)
def most_busy_user(chat):
    x=chat["User_Name"].value_counts().head()
    per=round(((chat['User_Name'].value_counts())/chat.shape[0])*100,2)
    per=per.reset_index().rename(columns={'index':'Name','User_Name':'Percent'})
    return x,per

@st.cache(allow_output_mutation=True)
def create_wordcloud(selected_user,chat):
    temp=chat[chat['User_Name']!='Notification']
    temp=chat[chat['Messages']!='<Media omitted>\n']
    f=open('Stop word-English_Hindi_Bengali.txt','r')
    stop_word=f.read()
    
    if selected_user!='Overall':
        df=temp[temp['User_Name']==selected_user]
        words=[]
        tem=df['Messages'].astype(str)
        for i in tem:
            for j in i.lower().split():
                if j not in stop_word:
                    words.append(j)
        new=pd.DataFrame(words)
        wc=WordCloud(width=500,height=500,min_font_size=10,background_color='white')
        df_wc=wc.generate(new[0].str.cat(sep=" "))
    else:
        words=[]
        tem=temp['Messages'].astype(str)
        for i in tem:
            for j in i.lower().split():
                if j not in stop_word:
                    words.append(j)
        new=pd.DataFrame(words)
        wc=WordCloud(width=500,height=500,min_font_size=10,background_color='white')
        df_wc=wc.generate(new[0].str.cat(sep=" "))
   
    return df_wc
@st.cache(allow_output_mutation=True)
def most_common_words(selected_user,chat):
    temp=chat[chat['User_Name']!='Notification']
    temp=chat[chat['Messages']!='<Media omitted>\n']
    f=open('Stop word-English_Hindi_Bengali.txt','r')
    stop_word=f.read()
    words=[]
    if selected_user=='Overall':
        tem=temp['Messages'].astype(str)
        for i in tem:
            for j in i.lower().split():
                if j not in stop_word:
                    words.append(j)
        mcw=pd.DataFrame(Counter(words).most_common(50))
        return mcw
    else:
        df=temp[temp["User_Name"]==selected_user]
        tem=df['Messages'].astype(str)
        for i in tem:
            for j in i.lower().split():
                if j not in stop_word:
                    words.append(j)
        mcw=pd.DataFrame(Counter(words).most_common(50))
        return mcw


def fetch_emojis(selected_user,chat):
    emojis=[]
    emoji_meanings=[]
    if selected_user!='Overall':
        df=chat[chat['User_Name']==selected_user]

        for message in df['Messages'].astype(str):
            em=emoji.distinct_emoji_list(message)
            emojis.extend(em)
            emoji_meanings.extend([emoji.demojize(is_emoji)for is_emoji in em])
        
        em=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
        emoji_meanings=pd.DataFrame(Counter(emoji_meanings).most_common(len(Counter(emoji_meanings))))
        return em,emoji_meanings
    else:
        for message in chat['Messages'].astype(str):
            em=emoji.distinct_emoji_list(message)
            emojis.extend(em)
            emoji_meanings.extend([emoji.demojize(is_emoji)for is_emoji in em])
        
        em=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
        emoji_meanings=pd.DataFrame(Counter(emoji_meanings).most_common(len(Counter(emoji_meanings))))
        return em,emoji_meanings

@st.cache(allow_output_mutation=True)
def monthly_timeline(selected_user,chat):
    if selected_user!='Overall':
        df=chat[chat['User_Name']==selected_user]
        timeline=df.groupby(['Year','Month_num','Month']).count()['Messages'].reset_index()
        time=[]
        for i in range(timeline.shape[0]):
            time.append(timeline['Month'][i]+'-'+str(timeline['Year'][i]))
        timeline['Time']=time
        return timeline
    else:
        timeline=chat.groupby(['Year','Month_num','Month']).count()['Messages'].reset_index()
        time=[]
        for i in range(timeline.shape[0]):
            time.append(timeline['Month'][i]+'-'+str(timeline['Year'][i]))
        timeline['Time']=time
        return timeline

#@st.cache(allow_output_mutation=True)
def set_params(chat):
            params=dict()
            params['Year']=st.sidebar.slider('Year',min_value=int(chat['Year'].min()),max_value=int(chat['Year'].max()))
            params['Month']=st.sidebar.slider('Month',min_value=chat['Month_num'].min(),max_value=chat['Month_num'].max())
            return params    

#@st.cache(allow_output_mutation=True)
def daily_timeline(selected_user,chat):
            if selected_user!='Overall':
                st.sidebar.title("Daily Timeline")
                params=set_params(chat)
                daily=chat[chat['Year']==params['Year']]
                daily=daily[daily['Month_num']==params['Month']]
                daily['Only_date']=daily['Date'].dt.date
                timeline=daily.groupby(['Only_date']).count()['Messages'].reset_index()
                
                fig=plt.figure(figsize=(8,6))
                plt.plot(timeline['Only_date'],timeline['Messages'],color=	[0.1350, 0.2780, 0.3840])
                plt.xticks(rotation=50)
                st.pyplot(fig)
            else:
                chat['Only_date']=chat['Date'].dt.date
                timeline=chat.groupby(['Only_date']).count()['Messages'].reset_index()
                #st.dataframe(timeline)
                
                fig=plt.figure(figsize=(8,6))
                plt.plot(timeline['Only_date'],timeline['Messages'],color=[0.4660, 0.6740, 0.1880])
                plt.xticks(rotation=50)
                st.pyplot(fig)


def week_activity_map(selected_user,chat):
    chat["Date"]=pd.to_datetime(chat["Date"])
    chat['Day_name']=chat['Date'].dt.day_name()
    if selected_user!='Overall':
        df=chat[chat['User_Name']==selected_user]
        return df['Day_name'].value_counts().reset_index()
    else:
        return chat['Day_name'].value_counts().reset_index()
    
def month_activity_map(selected_user,chat):
    if selected_user!='Overall':
        df=chat[chat['User_Name']==selected_user]
        return df['Month'].value_counts().reset_index()
    else:
        return chat['Month'].value_counts().reset_index()

def hit_map(selected_user,chat):
    period=[]
    for hour in chat[['Day_name','Hour']]['Hour']:
        if hour == 23:
            period.append(str(hour)+'-'+str('00'))
        elif hour==0:
            period.append(str('00')+'-'+str(hour+1))
        else:
            period.append(str(hour)+'-'+str(hour+1))
    chat['Period']=period
    if selected_user!='Overall':
        df=chat[chat['User_Name']==selected_user]
        fig=plt.figure(figsize=(20,8))
        sns.heatmap(df.pivot_table(index='Day_name',columns='Period',values='Messages',aggfunc='count').fillna(0))
        st.pyplot(fig)
    else:
        fig=plt.figure(figsize=(20,8))
        sns.heatmap(chat.pivot_table(index='Day_name',columns='Period',values='Messages',aggfunc='count').fillna(0))
        st.pyplot(fig)

    
st.title("Top Statistics")

if st.sidebar.button("Show Analysis"):
    line,word,media,link=fetch_chat(selected_user,chat)
    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.header("Total Messages")
        st.title(line)

    with col2:
        st.header("Total Words: ")
        st.title(word)
        
    with col3:
        st.header("Total Media:")
        st.title(media)
    
    with col4:
        st.header("Total Links")
        st.title(link)

        
    if selected_user == 'Overall':
        st.title("User Contribution in a chat")
        col31,col32=st.columns(2)
        x,per=most_busy_user(chat)
        fig,ax=plt.subplots()
        with col31:
            st.header('Graphical View')
            ax.bar(x.index,x.values,color=	[0.1350, 0.2780, 0.3840])
            plt.xticks(rotation=20)
            plt.ylabel('No. of messages')
            plt.xlabel('User Name')
            st.pyplot(fig)
        with col32:
            st.header('Statistical View')
            st.dataframe(per)


#Activity Map
st.title('Activity Map')
col41,col42 = st.columns(2)
with col41:
    st.header('Most busy day')
    busy_day=week_activity_map(selected_user, chat)
    #busy_day=pd.DataFrame(busy_day)
    fig,ax=plt.subplots()
    ax.bar(busy_day['index'],busy_day['Day_name'],color=[0.75, 0.75, 0])
    plt.xticks(rotation=20)
    st.pyplot(fig)
with col42:
    st.header('Most busy month')
    busy_month=month_activity_map(selected_user, chat)
    fig,ax=plt.subplots()
    ax.bar(busy_month['index'],busy_month['Month'],color=[0.6350, 0.0780, 0.1840])
    plt.xticks(rotation=25)
    st.pyplot(fig)

#Timeline
        
col21,col22=st.columns(2)
      
#Monthly Timeline
with col21:
    st.title("Monthly Timeline")
    timeline=monthly_timeline(selected_user, chat)
    #st.dataframe(timeline)
    fig=plt.figure(figsize=(8,6))
    plt.plot(timeline['Time'],timeline['Messages'],color=[0.3150, 0.6180, 0.9140])
    plt.xticks(rotation=50)
    st.pyplot(fig) 
   
#Daily Timeline
with col22:
    st.title('Daily Timeline')
    daily_timeline(selected_user, chat)       


#Weekly activity map-Hit Map

st.title('Weekly Activity Map')
hit_map(selected_user, chat)

#WordCloud

#if st.sidebar.button("Show Word Cloud"):

st.title("Word Cloud")
df_wc=create_wordcloud(selected_user, chat)     
fig,ax=plt.subplots()
ax.imshow(df_wc)
#st.imshow(df_wc)
st.pyplot(fig)


st.title("Most Common Word")
most_common_word=most_common_words(selected_user,chat)
fig,ax=plt.subplots()
ax.barh(most_common_word[0],most_common_word[1],color=[0.1350, 0.5780, 0.5840])
plt.yticks(fontsize=5)
plt.xlabel("Frequency")
plt.ylabel("Most Common Word")
st.pyplot(fig)

#Most Common Emoji

emojii,emojii_meanings=fetch_emojis(selected_user, chat)

emojii.insert(loc=1,column='Meanings',value=emojii_meanings[0])
emojii=emojii.rename(columns={0:'Emoji',1:'Frequency'})
st.title("Most Common Emoji")

st.dataframe(emojii,width=2000)



