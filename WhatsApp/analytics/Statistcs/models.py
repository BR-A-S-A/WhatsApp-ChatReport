
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


def get_total_media_messages(df):
    total = 0
    for index, row in df.iterrows():
        if row['Message'] == "<arquivo de mídia oculto>":
            total += 1
    return total


def list_of_days(i):
  l = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
  return l[i]
  
def dayofweek(messages_df, format):
    plotly.io.orca.config.executable = 'C:/Users/joaov/anaconda3/orca_app/orca.exe'
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
    stopwords.update(["da", "pra", "a", "de", "tem", "e", "o", "é", "ele", "https","q","em","um","aí","na", "como", "foi", "só", "por", "dele", "essa", "deve", "ser", "que", "tá", "eu", "se", "era", "meu", "ma", "mas", "não", "n", "uma", "um", "este", "esta", "estes", "estas", "isto", "esse", "essa", "esses", "essas", "isso", "aquele", "aquela", "aqueles", "aquelas", "aquilo", "V./VV", "Sr", "Sr.ª", "Srs.", "Srª.s", "V. Ex.ª/V. Ex.ªs", "V. Mag.ª", "V. Mag.ªs"," V. S.ª", "V. S.ªs", "VM", "VVMM", "V.V.A. A", "V.A", "V.S"," V. Ex.ª", "V. Em.ªs", "V. Rev.m.ª", "V. Rev.m.ªs", "algum", "alguma", "alguns", "algumas", "nenhum", "nenhuma", "nenhuns", "nenhumas", "muito", "muita", "muitos", "muitas", "pouco", "pouca", "poucos", "poucas", "todo", "toda", "todos", "todas", "outro", "outra", "outros", "outras", "certo", "certa", "certos", "certas", "vário", "vária", "vários", "várias", "tanto", "tanta", "tantos", "tantas", "quanto", "quanta", "quantos", "quantas", "qualquer", "quaisquer", "qual", "quais", "um", "uma", "uns", "umas", "quem", "alguém", "ninguém", "tudo", "nada", "outrem", "algo", "cada", "qual", "quais", "quanto", "quantos", "quanta", "quantas", "quem", "que", "qnt", "qnts", "qnto", "td", "tds", "nd", "q", "qlqr", "vc", "vcs", "tu", "ti", "você", "ocê", "cê", "c"])
    wordcloud = WordCloud(stopwords=stopwords, max_font_size=600, max_words=100, scale = 3, width = 1920, height = 1080,  background_color="white", mask = mask).generate(text)
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

