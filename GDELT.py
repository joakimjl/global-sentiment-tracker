from nltk.sentiment import SentimentIntensityAnalyzer
import requests
import json
import nltk
from datetime import datetime, timedelta
import psycopg2
from settings import POSTGRES_PASSWORD, POSTGRES_USER
import pandas as pd
from googletrans import Translator



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
def fetch_gdelt_headline(query_term="Morale", source_country=None, source_lang=None, mode="artlist", format="JSON", day=datetime.today()):
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    #Ensures only given values will be used, if null do not add.
    if source_country:
        source_country_query = 'sourcecountry:'+str(source_country)
    else: source_country_query = ''

    if source_lang:
        source_lang_query = 'sourcelang:'+str(source_lang)
    else: source_lang_query = ''

    query = f'{query_term} {source_country_query} {source_lang_query}'

    start_day = day-timedelta(days=3)
    end_day = day-timedelta(days=2)
    
    params = {
        'query': query,
        'format': format,
        'maxrecords':250,
        'STARTDATETIME':str(start_day.strftime('%Y%m%d%H%M%S')),
        'ENDDATETIME':str(end_day.strftime('%Y%m%d%H%M%S'))
    }

    headers = { # Was needed for 429 error, might look for other solution
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    
    # Send GET request
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        try :
            data = json.loads(response.text)
        except:
            print(f"Data was empty at: {query_term} with country {source_country}. Ignoring")
            return None
        if data == {}:
            print(f"Data was empty at: {query_term} with country {source_country}. Ignoring")
            return None
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

#Language given from gedelt is "Chinese" and google needs "Chinese (PRC) or (Taiwan)"
#Portuguese (Portugal) (Brazil)
def get_titles(data): #TODO: Fix batch translation for languages.
    translator = Translator()
    titles = []
    for ele in data['articles']:
        if ele['language'] != 'English':
            try:
                if ele['language'] == "Chinese":
                    #Defaulting to PRC and Brazil due to population
                    ele['language'] = "Chinese (PRC)"
                elif ele['language'] == "Portugese":
                    ele['language'] = "Portuguese (Brazil)"
                ele = translator.translate(ele['title'], src=ele['language']).text
            except:
                try:
                    ele = translator.translate(ele['title'])
                    ele = ele.text
                except:
                    ele = None
        else:
            ele = ele['title']
        if ele:
            titles.append(ele)
    return titles

def sentiment_check(sentence, sia):
    return(sia.polarity_scores(sentence))

def get_gdelt_processed(query="economy", target_country="US", date=datetime.today()):
    data = fetch_gdelt_headline(query_term=query, source_country=target_country)
    if data == None:
        return None, None, None, None #Pretty ugly might find better fix.
    titles = get_titles(data)
    #tokens = tokenize(titles)
    sia = SentimentIntensityAnalyzer()
    #sentiment_arr = []
    #for token in tokens:
    #    sentiment_arr.append(sentiment_check(token, sia))
    
    sentiment = sentiment_check(''.join(titles),sia)
    return sentiment, titles, target_country, query

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
    
    sent_arr = [e for k,e in sentiment.items()]

    sent_arr = str(sent_arr).replace('[','(').replace(']',')')

    cur = conn.cursor()

    cur.execute("INSERT INTO global_info \
                (target_country,on_day,nation_headline,inter_headline,on_subject,\
                sentiment,objectivity,latest_processed ) VALUES (%s, %s, %s, %s, %s, %s::sentiment, %s, %s)",
    (tar_country,str(datetime.today().strftime('%Y%m%d')),titles,None,query,sent_arr,0.5,str(datetime.today().strftime('%Y%m%d%H%M%S'))))

    conn.commit()
    cur.close()
    conn.close()



# Test usage
# TODO:Need to decide on what generic search terms should be...
if __name__ == "__main__":

    countries = ["US","UK","Germany","China","Japan","Australia","Ukraine","Russia"]
    subjects = ["economy","housing","crime","inflation","immigration"]
    count = 0
    for subject in subjects:
        for target in countries:
            print(f"Starting {target} about {subject}: remaining: {len(countries)*len(subjects)-count}")
            sentiment_arr, titles, target_country, query = get_gdelt_processed(query=subject, target_country=target)
            if sentiment_arr == None:
                count += 1
                continue
            insert_data(sentiment_arr, titles, target_country, query)
            count += 1
