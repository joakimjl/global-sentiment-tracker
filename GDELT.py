from nltk.sentiment import SentimentIntensityAnalyzer
import requests
import json
import nltk
from datetime import datetime, timedelta, date
import psycopg
from settings import POSTGRES_PASSWORD, POSTGRES_USER
import pandas as pd
from deep_translator import GoogleTranslator as Translator
import re
from psycopg.types.composite import CompositeInfo, register_composite
from threading import Thread
import time


#Find KPI for display, decide how and when. If opinion changes on subject, should that be covered?

#Example
#"https://api.gdeltproject.org/api/v2/doc/doc?query=%22Trump%22%20sourcecountry:US%20sourcelang:English&format=json"

# Context might be ideal only issue is designating origin country.
# Resource: https://blog.gdeltproject.org/announcing-the-gdelt-context-2-0-api/
# TODO: Countries maybe needed, find optimal way to store data, most likely FK to country table and group by
# TODO: Add translation, check on ex, Swedish, Danish, Norweigan, Tagalog, German.
"""
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
def fetch_gdelt_headline(query_term="Morale", source_country=None, source_lang=None, mode="artlist", format="JSON", day=date.today()):
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    #Ensures only given values will be used, if null do not add.
    if source_country:
        if source_country[0] == "-":#Supporting to only get other countries as sources
            source_country_query = '-sourcecountry:'+str(source_country[1:])
        else:
            source_country_query = 'sourcecountry:'+str(source_country)
    else: source_country_query = ''

    if source_lang:
        source_lang_query = 'sourcelang:'+str(source_lang)
    else: source_lang_query = ''

    query = f'{query_term} {source_country_query} {source_lang_query}'

    start_day = day-timedelta(days=1)
    end_day = day
    
    params = {
        'query': query,
        'format': format,
        'maxrecords':250,
        'STARTDATETIME':str(start_day.strftime('%Y%m%d%H%M%S')),
        'ENDDATETIME':str(end_day.strftime('%Y%m%d%H%M%S')),
        'SORT':"HybridRel"
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
def get_titles(data):

    print("Translating")
    
    titles = []
    lang_batch = {}
    #Batch languages
    for ele in data['articles']:
        if ele['language'] not in lang_batch:
            lang_batch[ele['language']] = [ele['title']]
        else:
            lang_batch[ele['language']].append(ele['title'])
    
    #Translation in batches
    for lang in lang_batch:
        
        batch = lang_batch[lang]
        if lang != 'English':#Translation not needed (English (US) and (UK) default)
            time.sleep(1.01)
            try:
                if lang == "Chinese":
                    #New one requires only for chinese (simplified or traditional)
                    lang = "Chinese (simplified)"

                batch = Translator(source=lang.lower(), target='en').translate_batch(batch)
            except:
                print(f'BATCH FOR {lang} FAILED WITH {len(batch)} ARTICLES')

        for ele in batch:
            titles.append(ele)
    
    return titles


def get_gdelt_processed(query="economy", target_country="US", date=date.today()):
    data = fetch_gdelt_headline(query_term=query, source_country=target_country, day=date)
    if data == None:
        return None, None, None, None #Pretty ugly might find better fix.
    titles = get_titles(data)
    #tokens = tokenize(titles)
    sia = SentimentIntensityAnalyzer()
    sentiment_arr = []
    for title in titles:
        sentiment_arr.append(sia.polarity_scores(title))

    if target_country[0] == "-":
        target_country = target_country[1:]
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


def insert_data(sentiment, titles, sentiment_inter, titles_inter, tar_country, query, date) -> None:
    conn = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = "192.168.1.51",
                            port = "5432")
    
    date=date-timedelta(days=1)
                            
    #Gets type sentiment and makes the type in python, inserts into array
    all_sentiment = []
    info = CompositeInfo.fetch(conn, "sentiment")
    register_composite(info,conn)

    if sentiment:
        for ele in sentiment:
            sent = info.python_type(*ele.values())
            all_sentiment.append(sent)
    else:
        all_sentiment = None
            


    all_sentiment_inter = []
    if sentiment_inter:
        for ele in sentiment_inter:
            sent = info.python_type(*ele.values())
            all_sentiment_inter.append(sent)
    else:
        all_sentiment_inter = None 

    cur = conn.cursor()
    cur.execute("INSERT INTO global_info \
                (target_country,on_day,headline_national,headline_inter,on_subject,\
                sentiment_national,sentiment_inter,objectivity_national,objectivity_inter,latest_processed ) VALUES (%s, %s, %s, %s, %s, %s::sentiment[], %s::sentiment[], %s, %s, %s)",
    (tar_country,str(date.strftime('%Y%m%d')),titles,titles_inter,query,all_sentiment,all_sentiment_inter,0.5,0.5,str(datetime.today().strftime('%Y%m%d%H%M%S'))))

    conn.commit()
    cur.close()
    conn.close()


"""Completes all tasks for one row, separated for multithreading"""
def fetch_and_insert_one(target, subject, remain_rows, on_day=date.today()):
    print(f"Starting {target} about {subject}: remaining: {remain_rows}")
    sentiment_arr_nat, titles_nat, target_country, query = get_gdelt_processed(query=subject, target_country=target, date=on_day)
    print("Finished national")
    sentiment_arr_inter, titles_inter, target_country, query = get_gdelt_processed(query=subject, target_country=str("-"+target), date=on_day)
    print("Finished international")
    insert_data(sentiment_arr_nat, titles_nat, sentiment_arr_inter, titles_inter, target_country, query, on_day)

# TODO:Add popularity relevance (Already in from hybrid search, better if we can add weights)
# TODO:Fix large duping problem from GDELT data
if __name__ == "__main__":
    start_time = time.time()
    countries = ["US","UK","Germany","China","Japan","Australia","Ukraine","Russia"]
    countries_map = {
        "US":"America",
        "UK":"United Kingdom"}
    subjects = ["economy","housing","crime","inflation","immigration"]
    count = 0
    max_concurrent = 3
    threads = []

    on_days = []
    for i in range(2):
        on_days.append(date.today()-timedelta(days=i+1))

    #TODO: More function calls, less nesting
    """Need to make this abomination prettier"""
    for on_day in on_days:
        for target in countries:
            name = target
            if target in countries_map:
                name = countries_map[target]
            subjects = [f"({name} economy OR {name} market)",
                    f"{name} housing", f"{name} crime",
                    f"{name} inflation", f"{name} immigration"]
            for subject in subjects:
                time.sleep(1)#Not to spam too much on API's (ESP Google translate)
                #Due to once reaching google cap, either more than 5 per sec or 200k, should make 
                #Class that counts, also the GDELT now...
                while(len(threads) >= max_concurrent):
                    for t in threads:
                        if t.is_alive() == False:
                            threads.remove(t)
                    print("Waiting for threads")
                    for i in range(10):
                        #print(".",end="")
                        time.sleep(0.5)
                    
                remain_rows = len(countries)*len(subjects)*len(on_days)-count
                t = Thread(target=fetch_and_insert_one, args=[target, subject, remain_rows, on_day])
                t.start()
                threads.append(t)
                
                count += 1
    while len(threads) != 0:
        for t in threads:
            if t.is_alive() == False:
                threads.remove(t)
        time.sleep(2)
    print(f"Finished all, closing, total time: {time.time() - start_time}")