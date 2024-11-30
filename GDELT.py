from nltk.sentiment import SentimentIntensityAnalyzer
import requests
import json
import nltk
from datetime import datetime, timedelta, date
import psycopg
from settings import POSTGRES_PASSWORD, POSTGRES_USER, CONNECT_IP_REMOTE, CONNECT_PORT_REMOTE 
from deep_translator import GoogleTranslator as Translator
from psycopg.types.composite import CompositeInfo, register_composite
from threading import Thread
import time
from roberta_model import GST_Roberta
import numpy as np
from country_codes import country_codes_map
from country_list import countries, countries_map
import math

#Find KPI for display, decide how and when. If opinion changes on subject, should that be covered?

#Example
#"https://api.gdeltproject.org/api/v2/doc/doc?query=%22Trump%22%20sourcecountry:US%20sourcelang:English&format=json"

# Context might be ideal only issue is designating origin country.
# Resource: https://blog.gdeltproject.org/announcing-the-gdelt-context-2-0-api/
# TODO: Countries maybe needed, find optimal way to store data, most likely FK to country table and group by
# TODO: Add translation, check on ex, Swedish, Danish, Norweigan, Tagalog, German.

class TranslatorSyncer():
    def __init__(self, max_concurrent=5, max_chars=990000) -> None:
        self.total_active = 0
        self.started_time_map = {}
        self.chars = 0
        self.id = 0
        self.max_con = max_concurrent
        self.max_chars = max_chars

    def finished(self, id):
        sleep_time = self.started_time_map[id]-time.time()+2
        sleep_time = min(sleep_time, 0)
        sleep_time = max(sleep_time, 1)
        time.sleep(sleep_time)
        del self.started_time_map[id]

    def started(self):
        while (len(self.started_time_map) > self.max_con or self.chars >= self.max_chars):
            #print(f"Thread waiting due to: {len(self.started_time_map)} > {self.max_con} or {self.chars} >= {self.max_chars}")
            time.sleep(1)
        self.started_time_map[self.id] = time.time()
        given_id = self.id
        self.id += 1
        return given_id
    
    def batch_process(self,batch,lang):
        id = self.started()
        num_chars = len("".join(batch))
        self.chars += num_chars
        try:
            if lang == "Chinese":
                #New one requires only for chinese (simplified or traditional)
                lang = "Chinese (simplified)"

            batch = Translator(source=lang.lower(), target='en').translate_batch(batch)
        except:
            print(f'BATCH FOR {lang} FAILED WITH {len(batch)} ARTICLES')

        self.chars -= num_chars

        self.finished(id)

        return(batch)

def check_exists(country, subject, day):
    connection = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = CONNECT_IP_REMOTE,
                            port = CONNECT_PORT_REMOTE)
    
    cur = connection.cursor()

    cur.execute(
        "SELECT count(*) FROM global_info\
        WHERE on_subject = %s AND target_country = %s AND on_day = %s",
        (subject, country, day))
    
    res = cur.fetchall()
    print((res, subject, country, day))
    if res[0][0] == 0:
        return False
    return True

def fetch_gdelt_headline(query_term="Morale", source_country=None, source_lang=None, mode="artlist", format="JSON", day=date.today()):
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

    domainis = "domainis:" + "(yahoo.com OR nyntimes.com OR aftonbladet.se OR cgtn.com OR vnexpress.net OR sky.it OR haberturk.com)"

    query = f'{query_term} {source_country_query} {source_lang_query}'

    start_day = day-timedelta(days=1)
    end_day = day
    
    params = {
        'query': query,
        'format': format,
        'maxrecords':250,
        'STARTDATETIME':str(start_day.strftime('%Y%m%d%H%M%S')),
        'ENDDATETIME':str(end_day.strftime('%Y%m%d%H%M%S')),
        'SORT':"HybridRel",
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

def tokenize(titles):
    # Returns list of words
    token_arr = []
    for title in titles:
        res = nltk.tokenize.word_tokenize(title)
        res = nltk.pos_tag(res)
        res = nltk.chunk.ne_chunk(res)
        token_arr.append(res)
    return token_arr

def get_domains(country):
    connection = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = CONNECT_IP_REMOTE,
                            port = CONNECT_PORT_REMOTE)

    country_code = country
    if country in country_codes_map:
        country_code = country_codes_map[country]
    

    cur = connection.cursor()

    if country[0] == '-':
        cur.execute("SELECT di.*\
            FROM domain_info di,\
            UNNEST(di.country_mentions) AS cm(country_code, count)\
            WHERE (cm.count > 300000\
            AND cm.country_code != %s )\
            OR (di.domain_weight >= %s\
            AND cm.country_code != %s )\
            GROUP BY di.domain",
            (country_code,0.70,country_code))
    else:
        cur.execute("SELECT di.*\
            FROM domain_info di,\
            UNNEST(di.country_mentions) AS cm(country_code, count)\
            WHERE (cm.count > 300000\
            AND cm.country_code = %s )\
            OR (di.domain_weight >= %s\
            AND cm.country_code = %s )\
            GROUP BY di.domain",
            (country_code,0.70,country_code))

    res = cur.fetchall()
    cur.close()
    connection.close()

    return res

def get_titles(data,syncer):
    #Language given from gedelt is "Chinese" and google needs "Chinese (PRC) or (Taiwan)"
    #Portuguese (Portugal) (Brazil)

    print("Translating")
    
    titles = []
    headline_dict = {}
    domain_dict = {}
    #Batch languages
    for ele in data:
        if ele['language'] not in headline_dict:
            headline_dict[ele['language']] = [ele['title']]
            domain_dict[ele['language']] = [ele['domain']]
        else:
            headline_dict[ele['language']].append(ele['title'])
            domain_dict[ele['language']].append(ele['domain'])
    
    #Translation in batches
    for lang in headline_dict:
        batch = headline_dict[lang]
        domain_batch = domain_dict[lang]
        if lang != 'English':#Translation not needed (English (US) and (UK) default)
            batch = syncer.batch_process(batch,lang)

        for i in range(len(batch)):
            ele = batch[i]
            domain = domain_batch[i]
            titles.append([ele,domain])
    
    return titles

def get_gdelt_processed(query="economy", target_country="US", date=date.today(), roberta=None, syncer=None):
    data = fetch_gdelt_headline(query_term=query, source_country=target_country, day=date)
    if data == None:
        return None, None, None, None #Pretty ugly might find better fix.
    valid_domains = [res[0] for res in get_domains(target_country)]
    idx = 0
    kept = 0
    kept_data = []
    for arr in data['articles']:
        if arr['domain'] in valid_domains:
            kept_data.append(arr)
            kept += 1
        idx += 1

    print(f'{target_country} kept: {kept} removed: {idx-kept} about {query}')
    titles = get_titles(kept_data,syncer)
    #tokens = tokenize(titles)
    sia = SentimentIntensityAnalyzer()
    sentiment_arr = []
    vader = []
    text_titles = [text[0] for text in titles]
    for title in text_titles:
        vader.append(sia.polarity_scores(title))
    sentiment_arr.append(vader)

    if roberta:
        sentiment_arr.append(roberta.roberta_process_batch(text_titles))

    sentiment_arr.append(None) #Later to be trained model

    if target_country[0] == "-":
        target_country = target_country[1:]
    return sentiment_arr, titles, target_country, query

def insert_data(sentiment, titles, sentiment_inter, titles_inter, tar_country, query, date) -> None:
    conn = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = CONNECT_IP_REMOTE,
                            port = CONNECT_PORT_REMOTE) 
                            
    #Gets type sentiment and makes the type in python, inserts into array
    all_sentiment = []
    info = CompositeInfo.fetch(conn, "sentiment")
    register_composite(info,conn)

    arti = CompositeInfo.fetch(conn, "article")
    register_composite(arti,conn)

    title_process = [titles,titles_inter]
    all_articles = []
    for title_arr in title_process:
        articles = []
        for pair in title_arr:
            articles.append(arti.python_type(*pair))
        all_articles.append(articles)

    senti_count = CompositeInfo.fetch(conn, "count_sentiment")
    register_composite(senti_count,conn)

    senti_count_arr_nat = []

    #TODO: make these two functions into one as it should've been
    all_sentiment = []
    if sentiment:
        for model_data in sentiment:
            if model_data == None:
                continue
            temp_arr = []
            temp_arr_count = [0]*3
            for ele in model_data:
                if type(ele) == np.ndarray:
                    sent = info.python_type(*ele.tolist(), 
                                            (ele.tolist()[2]-ele.tolist()[0])/(ele.tolist()[1]+1) )
                    polarity = math.tanh(ele.tolist()[2] - ele.tolist()[0])
                    if polarity <= -0.05:
                        temp_arr_count[0] += 1
                    elif polarity >= 0.05:
                        temp_arr_count[2] += 1
                    else:
                        temp_arr_count[1] += 1
                else:
                    sent = info.python_type(*ele.values())
                    if [val for val in ele.values()][3] <= -0.05:
                        temp_arr_count[0] += 1
                    elif [val for val in ele.values()][3] >= 0.05:
                        temp_arr_count[2] += 1
                    else:
                        temp_arr_count[1] += 1
                temp_arr.append(sent)
            all_sentiment.append(temp_arr)
            senti_count_arr_nat.append(senti_count.python_type(*temp_arr_count))
    else:
        all_sentiment = None 

    senti_count_arr_int = []

    all_sentiment_inter = []
    if sentiment_inter:
        for model_data in sentiment_inter:
            if model_data == None:
                continue
            temp_arr = []
            temp_arr_count = [0]*3
            for ele in model_data:
                if type(ele) == np.ndarray:
                    sent = info.python_type(*ele.tolist(), 
                                            (ele.tolist()[2]-ele.tolist()[0])/(ele.tolist()[1]+1) )
                    polarity = math.tanh(ele.tolist()[2] - ele.tolist()[0])
                    if polarity <= -0.05:
                        temp_arr_count[0] += 1
                    elif polarity >= 0.05:
                        temp_arr_count[2] += 1
                    else:
                        temp_arr_count[1] += 1
                else:
                    sent = info.python_type(*ele.values())
                    if [val for val in ele.values()][3] <= -0.05:
                        temp_arr_count[0] += 1
                    elif [val for val in ele.values()][3] >= 0.05:
                        temp_arr_count[2] += 1
                    else:
                        temp_arr_count[1] += 1
                temp_arr.append(sent)
            all_sentiment_inter.append(temp_arr)
            senti_count_arr_int.append(senti_count.python_type(*temp_arr_count))
    else:
        all_sentiment_inter = None 

    cur = conn.cursor()
    res1 = cur.execute("INSERT INTO global_info \
                (target_country,on_day,headline_national,headline_inter,on_subject,\
                sentiment_national,sentiment_inter,senti_count_nat,senti_count_int,latest_processed ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    (tar_country,date,all_articles[0],all_articles[1],query,all_sentiment,all_sentiment_inter,senti_count_arr_nat,senti_count_arr_int,datetime.today()))

    res2 = conn.commit()
    cur.close()
    conn.close()

    print(f"Insert results: {res1} {res2}")
    return True

def fetch_and_insert_one(target, subject, remain_rows, roberta, syncer, on_day=date.today(), short_subject="Any Subject"):
    """Completes all tasks for one row, separated for multithreading"""
    already_in_db = check_exists(target, short_subject, on_day)
    if already_in_db: 
        print(f"{target} on {short_subject} on {on_day} already in database")
        return
    try:

        print(f"Starting {target} about {subject}: remaining: {remain_rows}")
        sentiment_arr_nat, titles_nat, target_country, query = get_gdelt_processed(
            query=subject, target_country=target, date=on_day, roberta=roberta, syncer=syncer)
        if query == None:
           return False 
        print(f"Finished national {target}")
        sentiment_arr_inter, titles_inter, target_country, query = get_gdelt_processed(
            query=subject, target_country=str("-"+target), date=on_day, roberta=roberta, syncer=syncer)
        if query == None:
           return False
        print(f"Finished international {target}")
        insert_data(sentiment_arr_nat, titles_nat, sentiment_arr_inter, titles_inter, target_country, short_subject, on_day)
        print()
    except Exception as error:
        print(f"{error} \n Continuing anyway but {target} on {subject} on {on_day} not inserted")
    return True


# TODO:Fix large duping problem from GDELT data
if __name__ == "__main__":
    syncer = TranslatorSyncer()
    roberta = GST_Roberta()
    start_time = time.time()
    countries = ["US","UK","Germany","China","Japan","Australia","Ukraine","Russia"] 
    countries_map = {
        "US":"America",
        "UK":"United Kingdom"}
    count = 0
    max_concurrent = 2
    threads = []

    on_days = []
    for i in range(80):
        on_days.append(date.today()-timedelta(days=80-i))

    #TODO: More function calls, less nesting
    """Need to make this abomination prettier"""
    for on_day in on_days:
        for target in countries:
            name = target
            first_string = f"({name} economy OR {name} market)"
            if target in countries_map:
                name_2 = name
                name = countries_map[target]
                first_string = f"({name} economy OR {name} market OR {name_2} economy OR {name_2} market)"
            subjects = [first_string,
                    f"{name} housing", f"{name} crime",
                    f"{name} inflation", f"{name} immigration"]
            short_subjects = ["economy","housing","crime","inflation","immigration"]
            for i in range(len(subjects)):
                subject = subjects[i]
                short_subject = short_subjects[i]
                time.sleep(1)#Not to spam too much on API's (ESP Google translate)
                #Due to once reaching google cap, either more than 5 per sec or 200k, should make 
                #Class that counts, also the GDELT now...
                while(len(threads) >= max_concurrent):
                    for t in threads:
                        if t.is_alive() == False:
                            threads.remove(t)
                    #print("Waiting for threads")
                    for i in range(10):
                        #print(".",end="")
                        time.sleep(0.5)
                    
                remain_rows = len(countries)*len(subjects)*len(on_days)-count
                t = Thread(target=fetch_and_insert_one, args=[target, subject, remain_rows, roberta, syncer, on_day, short_subject])
                t.start()
                threads.append(t)
                
                count += 1
    while len(threads) != 0:
        for t in threads:
            if t.is_alive() == False:
                threads.remove(t)
        time.sleep(2)
    print(f"Finished all, closing, total time: {time.time() - start_time}")

