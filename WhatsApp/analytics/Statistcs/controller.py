from datetime import datetime
import Statistcs.models 
import re as re
import pandas as pd
import emoji
import collections
import plotly.express as px
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import json
import multiprocessing as mp

class StatistcsController():
    df = None
    messages_df = None
    media_messages_df = None
    file_name = None

    def __init__(self, file_name = None):            
        self.file_name = file_name
        self.df = self.__get_df()
        self.media_messages_df = self.__get_messages_df()[0]
        self.messages_df = self.__get_messages_df()[1]


    def __get_df(self):
        startTime = datetime.now()
        URLPATTERN = r"(http(s?)\:)"
        parsedData = [] # List to keep track of data so it can be used by a Pandas dataframe
        # Upload your file here
        if self.file_name != None:
         conversationPath = '..//analytics//'+self.file_name # chat file

        with open(conversationPath, encoding="utf-8") as fp:   
            messageBuffer = [] 
            messageArray = []
            date, time, author = None, None, None
            while True:
                line = fp.readline()
                messageArray.append(line)
                if not line: 
                    break
                line = line.strip() 
                if Statistcs.models.starts_with_date_and_time(line): 
                    date, time, author, message = Statistcs.models.get_data_point(line) 
                    messageBuffer.clear() 
                    messageBuffer.append(message)
                    if len(messageBuffer) > 0 and author != None:
                        parsedData.append([date, time, author, ' '.join(messageBuffer).lower(), Statistcs.models.extract_emojis(messageBuffer)])  
                else:
                    messageBuffer.append(line)

        
        df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message', 'emoji']) # Initialising a pandas Dataframe.
        df["Date"] = pd.to_datetime(df["Date"])
        df['urlcount'] = df.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
        print('Dataframe creation: ', datetime.now() - startTime)
        return df

    def __get_messages_df(self):
        media_messages_df = self.df[self.df['Message'] == '<arquivo de mídia oculto>']
        messages_df = self.df.drop(media_messages_df.index)
        messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
        messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))        
        return [media_messages_df, messages_df]

    def get_dataframe_json_format(self):
        return self.df.to_json(orient = "records")

    def get_all(self):    
        startTime = datetime.now()
        print(self.media_messages_df)
        result = {}
        result['totalMessages'] = int(self.df.shape[0])
        print('totalMessages: ', datetime.now() - startTime)
        result['mediaMessages'] = int(self.media_messages_df.shape[0])
        print('totalMedias: ', datetime.now() - startTime)
        result['emojis'] = int(sum(self.df['emoji'].str.len()))
        print('totalEmojis: ', datetime.now() - startTime)
        result['links'] = int(np.sum(self.df.urlcount))
        print('totalLinks: ', datetime.now() - startTime)
        return (result)
    
    def get_user(self):
        # Creates a list of unique Authors - ['Manikanta', 'Teja Kura', .........]
        l = self.messages_df.Author.unique()
        result = {}
        for i in range(len(l)):
            data = {}
            # Filtering out messages of particular user
            req_df= self.messages_df[self.messages_df["Author"] == l[i]]
            data['author'] = l[i]
            # req_df will contain messages of only one particular user
            data['totalMessages'] = req_df.shape[0]
            # shape will print number of rows which indirectly means the number of messages
            #Word_Count contains of total words in one message. Sum of all words/ Total Messages will yield words per message
            words_per_message = (np.sum(req_df['Word_Count']))/req_df.shape[0]
            data['wordsPerMessage'] = words_per_message
            #media conists of media messages
            media = self.media_messages_df[self.media_messages_df['Author'] == l[i]].shape[0]
            data['totalMedia'] = media
            # emojis conists of total emojis
            emojis = sum(req_df['emoji'].str.len())
            data['emojis'] = emojis
            #links consist of total links
            links = sum(req_df["urlcount"])   
            data['links'] = links
            result[i+1] = data  
        return result

    def emojiDistCall(self, format=None):
        total_emojis_list = list([a for b in self.messages_df.emoji for a in b])
        emoji_dict = dict(collections.Counter(total_emojis_list))
        emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
        emoji_df = pd.DataFrame(emoji_dict, columns=['emoji', 'count'])
        return Statistcs.models.emojiDist(emoji_df.head(10), format)
    
    def wordcloudTextCall(self):
        return Statistcs.models.wordCloudText(self.df)

    def get_day_of_week(self, format=None):
        return Statistcs.models.dayofweek(self.messages_df, format)
    
    def get_emoji_by_user(self, name, format = None):
        return Statistcs.models.get_emoji_by_user(name, self.messages_df, format)
