
# Create your models here.
import re as re
import pandas as pd
import emoji
import collections
import plotly.express as px
import plotly   
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from datetime import datetime
import os


def extract_emojis(s):
    return ''.join(c for c in s if c in emoji.UNICODE_EMOJI)

def starts_with_date_and_time(s):
    # regex pattern for date.(Works only for android. IOS Whatsapp export format is different. Will update the code soon
    pattern = r'^([0-9]+)(\/)([0-9]+)(\/)([0-9]+)\ ([0-9]+)\:([0-9]+)\ -'
    result = re.match(pattern, s)
    if result:
        return True
    return False

# Finds username of any given format.
def find_author(s):
    patterns = [
        '([\w]+):',                        # First Name
        '([\w]+[\s]+[\w]+):',              # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',    # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',         # Mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',   # Mobile Number (US)
        '([+]\d{2} \d{2} \d{4}-?\d{4}):',   # Mobile Number (BR)
        '([\w]+)[\u263a-\U0001f999]+:',    # Name and Emoji              
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False

def get_data_point(line):  
    splitLine = line.split(' - ') 
    dateTime = splitLine[0]
    date, time = dateTime.split(' ') 
    message = ' '.join(splitLine[1:])
    if find_author(message): 
        splitMessage = message.split(': ') 
        author = splitMessage[0] 
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message

def list_of_days(i):
  l = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
  return l[i]
  
def dayofweek(messages_df, format):
    #plotly.io.orca.config.executable = 'C:/Users/joaov/anaconda3/orca_app/orca.exe'
    plotly.io.orca.config.save()
    day_df = pd.DataFrame(messages_df["Message"])
    day_df['day_of_date'] = messages_df['Date'].dt.weekday
    day_df['day_of_date'] = day_df["day_of_date"].apply(list_of_days)
    day_df["messagecount"] = 1
    day = day_df.groupby("day_of_date").sum()
    day.reset_index(inplace=True)

    if (format == 'json'):
        return day.to_json(orient = "records")

    fig = px.line_polar(day, r='messagecount', theta='day_of_date', line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True,
        range=[0,8000]
        )),
    showlegend=True
    )
    fig.show()
    fig.write_image("dayofweek.png")
    path = './dayofweek.png'
    return path

def emojiDist(emoji_df, format=None):
    if format == 'json':
        return emoji_df.to_json(orient = "records")

    fig = px.pie(emoji_df, values='count', names='emoji',
                title='Emoji Distribution')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.write_html("emojiDistribution.html")
    path = './emojiDistribution.html'
    htmlContent = ""
    with open(path, encoding="utf-8") as fp:
            while True:
                line = fp.readline()
                if not line: 
                    break
                line = line.strip() 
                htmlContent += line
    return htmlContent

def wordCloudText(df):
    text = ', '.join(df.Message)
    text = re.sub(r'<arquivo de mídia oculto>', '', text)

    x, y = np.ogrid[:300, :300]

    mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
    mask = 255 * mask.astype(int)

    stopwords = set(STOPWORDS)
    stopwords.update(['tua', 'você', 'aí', 'seja', 'esta', 'fazer', 'coisa', 'fossem', 'últimos', 'tanta', 'for', 'ma', 'delas', 'fosse', 'pro', 'eles', 'ti', 'estavam', 'tido', 'vós', 'ia', 'alguns', 'pra', 'mas', 'primeiros', 'próprias', 'certos', 'dever', 'que', 'vários', 'aquilo', 'porém', 'quaisquer', 'nenhumas', 'aquele', 'o', 'no', 'poucos', 'deles', 'aqueles', 'nessas', 'seus', 'pouca', 'mesma', 'la', 'essas', 'até', 'q', 'próprios', 'ampla', 'elas', 'aquelas', 'não', 'podia', 'aos', 'vez', 'podiam', 'todo', 'vc', 'pelo', 'muitos', 'amplas', 'pois', 'através', 'qnts', 'tendo', 'teus', 'sendo', 'este', 'uma', 'nada', 'desse', 'dela', 'amplo', 'nem', 'qual', 'várias', 'nd', 'do', 'tuas', 'vos', 'suas', 'são', 'dos', 'qualquer', 'nunca', 'pelos', 'mesmas', 'em', 'tu', 'nestas', 'td', 'é', 'as', 'esse', 'ser', 'ta', 'dumas', 'era', 'pequenos', 'V.A', 'cê', 'tenha', 'deverão', 'pouco', 'tô', 'alguém', 'daqueles', 'tem', 'Srª.s', 'depois', 'por', 'nenhuma', 'umas', 'nossa', 'foi', 'tão', 'lo', 'a', 'muitas', 'tantas', 'essa', 'sob', 'eu', 'deverá', 'quem', 'pode', 'sua', 'sido', 'meu', 'Srs.', 'sem', 'certa', 'porque', 'como', 'dizem', 'outro', 'estamos', 'isto', 'isso', 'nas', 'numa', 'e', 'muita', 'uns', 'vou', 'um', 'nos', 'sobre', 'tudo', 'dele', 'todavia', 'Sr.ª', 'para', 'dá', 'vão', 'nós', 'dum', 'mim', 'devem', 'feitos', 'ou', 'quando', 'VM', 'há', 'último', 'alguma', 'V. Em.ªs', 'de', 'vário', 'já', 'vai', 'feito', 'podendo', 'diz', 'lá', 'esses', 'qnto', 'https', 'nesta', 'tantos', 'estes', 'estávamos', 'poderiam', 'estou', 'deste', 'muito', 'todas', 'nessa', 'desta', 'V. Rev.m.ª', 'vcs', 'antes', 'certas', 'quanta', 'os', 'toda', 'também', 'feitas', 'devia', 'duma', 'minhas', 'enquanto', 'tinham', 'teu', 'ocê', 'me', 'V. S.ª', 'dessas', 'outros', 'dito', 'pela', 'pequenas', 'lhe', 'perante', 'deve', 'estão', 'quantos', 'dessa', 'feita', 'outrem', 'ao', 'ver', 'tinha', 'outras', 'algumas', 'meus', 'seu', 'última', 'vindo', 'própria', 'estava', 'deveria', 'vendo', 'da', 'será', 'nenhum', 'aquela', 'só', 'disso', 'serão', 'pelas', 'poderia', 'deveriam', 'ela', 'últimas', 'te', 'tanto', 'disse', 'amplos', 'ele', 'nenhuns', 'VVMM', 'per', 'destas', 'sempre', 'lhes', 'certo', 'talvez', 'fazendo', 'quais', 'vir', 'nossas', 'tampouco', 'na', 'pequeno', 'quanto', 'tds', 'às', 'está', 'ante', 'após', 'coisas', 'destes', 'posso', 'qnt', 'V.S', 'V. Mag.ª', 'V. S.ªs', 'ainda', 'vária', 'pude', 'Sr', 'poder', 'ter', 'nossos', 'minha', 'tá', 'entre', 'cada', 'ninguém', 'algo', 'qlqr', 'grandes', 'sejam', 'nosso', 'desses', 'foram', 'se', 'com', 'contudo', 'próprio', 'mesmos', 'quantas', 'outra', 'agora', 'pequena', 'num', 'todos', 'c', 'daquele', 'n', 'poucas', 'si', 'mesmo', 'estas', 'devendo', 'disto', 'primeiro', 'deviam', 'contra', 'algum', 'das', 'grande', 'pq', 'viu', 'vem', 'sou', 'vi'])
    wordcloud = WordCloud(stopwords=stopwords, collocations=False ,max_font_size=600, max_words=100, scale = 3, width = 1920, height = 1080,  background_color="white", mask = mask).generate(text)
    wordCloudfile_name = "wordcloud.png"
    wordcloud.to_file(wordCloudfile_name)
    return wordCloudfile_name

def get_emoji_by_user(name, messages_df, format = None):
    # Creates a list of unique Authors - ['Manikanta', 'Teja Kura', .........]
    l = messages_df.Author.unique()
    for i in range(len(l)):
        if (l[i] == name):
            dummy_df = messages_df[messages_df['Author'] == l[i]]
            total_emojis_list = list([a for b in dummy_df.emoji for a in b])
            emoji_dict = dict(collections.Counter(total_emojis_list))
            emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
            print('Emoji Distribution for', l[i])
            author_emoji_df = pd.DataFrame(emoji_dict, columns=['emoji', 'count'])

            if format == 'json':
                return author_emoji_df.to_json(orient = "records")

            fig = px.bar(author_emoji_df, x='emoji', y='count')
            fig.update_traces(textposition='inside')
            fig.write_image('./emoji_by_' + name + '.png')
            path = './emoji_by_' + name + '.png'
            return path

