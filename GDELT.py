from nltk.sentiment import SentimentIntensityAnalyzer
import requests
import json
import nltk
from datetime import datetime
import psycopg2
from settings import POSTGRES_PASSWORD, POSTGRES_USER
import pandas as pd


#Find KPI for display, decide how and when. If opinion changes on subject, should that be covered?

#Example
#"https://api.gdeltproject.org/api/v2/doc/doc?query=%22Trump%22%20sourcecountry:US%20sourcelang:English&format=json"

# Context might be ideal only issue is designating origin country.
# Resource: https://blog.gdeltproject.org/announcing-the-gdelt-context-2-0-api/
# TODO: Countries maybe needed, find optimal way to store data, most likely FK to country table and group by
# TODO: Add translation, check on ex, Swedish, Danish, Norweigan, Tagalog, German.
"""
Cleaner code functioning old kept for now. Headline sentiment will be analysed,


Response data:
"url": 
"url_mobile": 
"title": 
"seendate": 
"socialimage": 
"domain": 
"language": 
"sourcecountry":
"""
def fetch_gdelt_headline(query_term="Morale", source_country=None, source_lang=None, mode="artlist", format="JSON"):
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    #Ensures only given values will be used, if null do not add.
    if source_country:
        source_country_query = 'sourcecountry:'+str(source_country)
    else: source_country_query = ''

    if source_lang:
        source_lang_query = 'sourcelang:'+str(source_lang)
    else: source_lang_query = ''

    query = f'{query_term} {source_country_query} {source_lang_query}'
    
    params = {
        'query': query,
        'format': format,
        'maxrecords':250
    }

    headers = { # Was needed for 429 error, might look for other solution
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    
    # Send GET request
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        
        data = json.loads(response.text)
        prev = data['articles'][0]
        for i in range(len(data)-1):
            if data['articles'][i+1].title == prev.title:
                print(data['articles'])
                print(prev['articles'])
            prev = data['articles'][i+1]
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


# Returns list of words
def tokenize(titles):
    token_arr = []
    for title in titles:
        res = nltk.tokenize.word_tokenize(title)
        res = nltk.pos_tag(res)
        res = nltk.chunk.ne_chunk(res)
        token_arr.append(res)
    return token_arr

def get_titles(data):
    titles = []
    for ele in data['articles']:
        titles.append(ele['title'])
    return titles

def sentiment_check(sentence, sia):
    return(sia.polarity_scores(sentence))

def get_gdelt_processed(query="economy", target_country="US", date=datetime.today()):
    data = fetch_gdelt_headline(query_term=query, source_country=target_country, source_lang='English')
    titles = get_titles(data)
    #tokens = tokenize(titles)
    sia = SentimentIntensityAnalyzer()
    sentiment_arr = []
    for token in titles:
        sentiment_arr.append(sentiment_check(token, sia))
    return sentiment_arr, titles, target_country, query

"""
target_country: string,
on_day: string,
nation_headline: array<string>,
inter_headline: array<string>,
on_subject: string,
sentiment: string,
objectivity: float,
latest_processed: string
"""


def insert_data(sentiment, titles, tar_country, query):
    conn = psycopg2.connect(database = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = "192.168.1.51",
                            port = "5432")
    
    sent_arr = [e for k,e in sentiment[0].items()]

    cur = conn.cursor()

    cur.execute("INSERT INTO global_info \
                (target_country,on_day,nation_headline,inter_headline,on_subject,\
                objectivity,latest_processed ) VALUES (%s, %s, %s, %s, %s, %s, %s)",
    (tar_country,'2024',titles,sent_arr,query,0.5,'2024'))

    cur.execute("SELECT * FROM global_info;")

    conn.commit()
    
    #print(cur.fetchall())
    cur.close()
    conn.close()

# Test usage
# TODO:Need to decide on what generic search terms should be...
if __name__ == "__main__":
    sentiment_arr, titles, target_country, query = get_gdelt_processed(query="house", target_country="UK")
    insert_data(sentiment_arr, titles, target_country, query)

