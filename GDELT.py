import boto3.session
from nltk.sentiment import SentimentIntensityAnalyzer
import requests
import json
import nltk
from datetime import datetime, timedelta, date
import psycopg
from settings import POSTGRES_PASSWORD, POSTGRES_USER, CONNECT_IP_REMOTE, CONNECT_PORT_REMOTE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from deep_translator import GoogleTranslator as Translator
from psycopg.types.composite import CompositeInfo, register_composite
from threading import Thread
import time
from roberta_model import GST_Roberta
import numpy as np
from country_codes import country_codes_map
from country_list import countries, countries_map, subjects_given
import math
import boto3
import random
import re



#Find KPI for display, decide how and when. If opinion changes on subject, should that be covered?

#Example
#"https://api.gdeltproject.org/api/v2/doc/doc?query=%22Trump%22%20sourcecountry:US%20sourcelang:English&format=json"

# Context might be ideal only issue is designating origin country.
# Resource: https://blog.gdeltproject.org/announcing-the-gdelt-context-2-0-api/
# TODO: Countries maybe needed, find optimal way to store data, most likely FK to country table and group by
# TODO: Add translation, check on ex, Swedish, Danish, Norweigan, Tagalog, German.

class TranslatorSyncer():
    def __init__(self, max_concurrent=15, max_chars=990000) -> None:
        self.total_active = 0
        self.started_time_map = {}
        self.chars = 0
        self.id = 0
        self.max_con = max_concurrent
        self.max_chars = max_chars
        self.total_time = 0
        self.total_requests = 0
        self.all_batch_done = False
        self.total_batches = {}
        self.last_added_time = None
        self.finished_batches = {}
        self._started_process = False
        self._big_batch_lock = False
        self._wait_queue = [99999999999]

    def finished(self, id):
        sleep_time = self.started_time_map[id]-time.time()+2
        self.total_time -= self.started_time_map[id]-time.time()
        self.total_requests += 1
        if sleep_time <= -100:
            print(f"It took LONG: {sleep_time}")
        sleep_time = min(sleep_time, 0)
        sleep_time = max(sleep_time, 1)
        time.sleep(sleep_time)
        del self.started_time_map[id]

    def started(self):
        while (len(self.started_time_map) > self.max_con or self.chars >= self.max_chars):
            print(f"Thread waiting due to: {len(self.started_time_map)} > {self.max_con} or {self.chars} >= {self.max_chars}")
            time.sleep(1)
        self.started_time_map[self.id] = time.time()
        given_id = self.id
        self.id += 1
        return given_id
    
    def fetch_from_lambda(self,batch,lang):
        session = boto3.session.Session(region_name='eu-west-1')
        aws_lambda = session.client('lambda')
        payload = {"batch":batch, "lang": lang}
        payload = json.dumps(payload).encode("utf-8")
        res = aws_lambda.invoke(
            FunctionName='gst-translate-function',
            InvocationType='RequestResponse',
            LogType='None',
            Payload=payload,
        )

        res = json.loads(json.loads(res['Payload'].read()))

        return res

    def batch_process(self,batch,lang,res_arr=None,res_arr_index=-1):
        error_count = 0
        id = self.started()
        num_chars = len("".join(batch))
        self.chars += num_chars
        try:
            if lang == "Chinese":
                #New one requires only for chinese (simplified or traditional)
                lang = "Chinese (simplified)"

            batch = Translator(source=lang.lower(), target='en').translate_batch(batch)
            #batch = self.fetch_from_lambda(batch,lang)
        except:
            print(f'BATCH FOR {lang} FAILED WITH {len(batch)} ARTICLES')
            error_count += 1
            if error_count > 3:
                return False

        self.chars -= num_chars

        self.finished(id)

        print(f"Total req: {self.total_requests}, total time: {self.total_time}, avg time: {self.total_time/(self.total_requests+0.001)}")

        if res_arr != None:
            res_arr[res_arr_index] = batch

        return(batch)

    def big_batch(self,batch,lang):
        time.sleep(random.random()*0.1)
        queue_position = -1
        while self._big_batch_lock == True or queue_position != min(self._wait_queue):
            if queue_position == -1:
                queue_position = len(self._wait_queue)
                self._wait_queue.append(queue_position)
            time_to_wait = 0.01+random.random()*0.4
            time.sleep(time_to_wait)
            
        #print("Free")
        self._big_batch_lock = True
        if lang in self.total_batches:
            start = len(self.total_batches[lang])
            for ele in batch:
                self.total_batches[lang].append(ele)
            end = len(self.total_batches[lang])
        else:
            start = 0
            self.total_batches[lang] = batch
            end = len(self.total_batches[lang])
        
        self.last_added_time = time.time()
        #print("Let go")
        if queue_position != -1:
            self._wait_queue[queue_position] = 9999999 #Might find better fix

        self._big_batch_lock = False

        return [start, end]
    
    def big_batch_process(self):
        if self._started_process == False:
            self._started_process = True
            print(f"Big Batching now total of {len(self.total_batches)} batches")
            count = 1 #For printing only
            for lang,batch in self.total_batches.items():
                print(f"Batch nr: {count}/{len(self.total_batches)} batches has {len(batch)} in language: {lang}")
                threads_processing = []
                res_arr = []
                num_batch = int(len(batch)/50)
                if num_batch == 0: #Minimum 1 batch
                    num_batch = 1
                for j in range(num_batch):
                    res_arr.append([])
                inc_size = len(batch)/num_batch #Increment size
                sleep_after_num = 4
                sleep_count = 0
                for i in range(num_batch):
                    t = Thread(target=self.batch_process, args=[batch[int(i*inc_size):int(inc_size*(i+1))], lang, res_arr, i])
                    print(f"Thread doing: {int(i*inc_size)} to {int(inc_size*(i+1))} for: {lang}")
                    t.start()
                    threads_processing.append(t)
                    time.sleep(0.1)
                    threads_finished = False
                    while not threads_finished:
                        all_finished = True
                        for thread in threads_processing:
                            if thread.is_alive() == True:
                                all_finished = False
                        threads_finished = all_finished
                        time.sleep(1)
                    if sleep_count % sleep_after_num == 0 and sleep_count > 0:
                        time.sleep(5)
                    sleep_count += 1
                #titles = self.batch_process(batch,lang)
                #self.finished_batches[lang] = titles
                time.sleep(5)
                count += 1
                flat_res_arr = []
                for arr in res_arr:
                    for ele in arr:
                        flat_res_arr.append(ele)

                self.finished_batches[lang] = flat_res_arr
                print("Inserted")

            print("All Done")
            self.all_batch_done = True
    
    def retrive_translation(self,start,end,lang):
        if not self.all_batch_done:
            return False
        res = []
        for i in range(start,end):
            res.append(self.finished_batches[lang][i])
        return res

def check_exists(country, subject, day, is_hourly=False):
    connection = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = CONNECT_IP_REMOTE,
                            port = CONNECT_PORT_REMOTE)
    
    cur = connection.cursor()

    if is_hourly:
        day = day-timedelta(hours=1)
    else:
        day = day-timedelta(days=1) #Start day is what is inserted always

    if not is_hourly:
        cur.execute(
            "SELECT count(*) FROM global_info\
            WHERE on_subject = %s AND target_country = %s AND on_day = %s",
            (subject, country, day))

    if is_hourly:
        cur.execute(
            "SELECT count(*) FROM global_info_hourly\
            WHERE target_country = %s AND on_time = %s",
            (country, day))
    
    res = cur.fetchall()
    print((res, subject, country, day))
    if res[0][0] == 0:
        return False
    return True

def fetch_gdelt_headline(query_term="Morale", source_country=None, source_lang=None, mode="artlist", format="JSON", day=date.today(), is_hourly=False):
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

    #domainis = "domainis:" + "(yahoo.com OR nyntimes.com OR aftonbladet.se OR cgtn.com OR vnexpress.net OR sky.it OR haberturk.com)"

    #Length must be between 5 and 74 inclusive
    split_terms = query_term.split(" OR ")
    res = []
    prep_queries = ["("]
    for i in range(len(split_terms)):

        if (len(prep_queries[-1]) + len(split_terms[i]) + 4) <= 60:
            if len(prep_queries[-1]) >= 4:
                prep_queries[-1] += " OR " + split_terms[i]
            else:
                prep_queries[-1] += split_terms[i]
        else:
            prep_queries[-1] += ")"
            prep_queries.append("(" + split_terms[i])
    if split_terms[-1][-1] != ")" and "OR" in split_terms[-1]:
        split_terms[-1] += ")"
    for query_batch in prep_queries:
        query = f'{query_batch} {source_country_query} {source_lang_query}'

        start_day = day-timedelta(days=1)
        if is_hourly:
            start_day = day-timedelta(hours=1)
        end_day = day
        
        params = {
            'query': query,
            'format': format,
            'maxrecords':250,
            'STARTDATETIME':str(start_day.strftime('%Y%m%d%H%M%S')),
            'ENDDATETIME':str(end_day.strftime('%Y%m%d%H%M%S')),
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
                print(f"Data was empty at: {query_batch} with country {source_country}. Ignoring")
                #return None
            if data == {}:
                print(f"Data was empty at: {query_batch} with country {source_country}. Ignoring")
                #return None
            else:
                res.append(data)
        else:
            print(f"Request failed with status code {response.status_code}")
            #return None
        time.sleep(0.2)
    temp_res = []
    all_titles = []
    for arr in res:
        for i in range(len(arr['articles'])):
            article = arr['articles'][i]
            if article['title'] not in all_titles:
                temp_res.append(article)
                all_titles.append(article['title'])
    
    return temp_res

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
            WHERE (cm.count > 3300000\
            AND cm.country_code != %s )\
            OR (di.domain_weight >= %s\
            AND cm.country_code != %s )\
            GROUP BY di.domain",
            (country_code,0.76,country_code))
    else:
        cur.execute("SELECT di.*\
            FROM domain_info di,\
            UNNEST(di.country_mentions) AS cm(country_code, count)\
            WHERE (cm.count > 3300000\
            AND cm.country_code = %s )\
            OR (di.domain_weight >= %s\
            AND cm.country_code = %s )\
            GROUP BY di.domain",
            (country_code,0.76,country_code))

    res = cur.fetchall()
    cur.close()
    connection.close()

    return res

def get_titles(res,data,syncer,index):
    #Language given from gedelt is "Chinese" and google needs "Chinese (PRC) or (Taiwan)"
    #Portuguese (Portugal) (Brazil)

    print("Translating")
    
    titles = []
    headline_dict = {}
    domain_dict = {}
    source_dict = {}
    index_dict = {}
    #Batch languages
    for ele in data:
        if ele['language'] not in headline_dict:
            headline_dict[ele['language']] = [ele['title']]
            domain_dict[ele['language']] = [ele['domain']]
            source_dict[ele['language']] = [ele['sourcecountry']]
        else:
            headline_dict[ele['language']].append(ele['title'])
            domain_dict[ele['language']].append(ele['domain'])
            source_dict[ele['language']].append(ele['sourcecountry'])
    
    #Translation in batches
    
    eng_location = -1
    count = 0
    eng_batch = None
    for lang in headline_dict:
        batch = headline_dict[lang]
        domain_batch = domain_dict[lang]
        source_batch = source_dict[lang]
        if lang != 'English':#Translation not needed (English (US) and (UK) default)
            index_dict[lang] = syncer.big_batch(batch,lang)
        else:
            eng_location = count
            eng_batch = headline_dict[lang]
        count += 1

    total_batch = []
    while syncer.all_batch_done == False:       
        time.sleep(50)
        #print(f"Time to wait: {40 + syncer.last_added_time - time.time()}")
        if syncer.last_added_time <= time.time()-90:
            syncer.big_batch_process()
    
    count = 0
    lang_arr = []
    for lang_key, index_range in index_dict.items():
        if count == eng_location:
            total_batch.append(eng_batch)
            lang_arr.append("English")
        total_batch.append(syncer.retrive_translation(index_range[0],index_range[1],lang_key))
        lang_arr.append(lang_key)
        count += 1
    if count == 0 and eng_location != -1:
        lang_arr.append("English")
        total_batch.append(eng_batch)

    j = 0
    for batch in total_batch:
        for i in range(len(batch)):
            ele = batch[i]
            domain = domain_dict[lang_arr[j]][i]
            source = source_dict[lang_arr[j]][i]
            titles.append([ele,domain,source])
        j += 1
    
    res[index] = titles
    return titles

def get_gdelt_processed(query="economy", target_country="US", date=date.today(), roberta=None, syncer=None, is_hourly=False):
    data = fetch_gdelt_headline(query_term=query, source_country=target_country, day=date, is_hourly=is_hourly)
    if data == None:
        return None, None, None, None #Pretty ugly might find better fix.
    valid_domains = [res[0] for res in get_domains(target_country)]
    idx = 0
    kept = 0
    kept_data = []
    for article in data:
        if article['domain'] in valid_domains:
            kept_data.append(article)
            kept += 1
        idx += 1

    print(f'{target_country} kept: {kept} removed: {idx-kept} about {query}')
    
    return kept_data

def process_titles(query="economy", target_country="US", date=date.today(), roberta=None, syncer=None, titles=None) :
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

def insert_data(sentiment, titles, sentiment_inter, titles_inter, tar_country, query, date, is_hourly=False) -> None:
    conn = psycopg.Connection.connect(dbname = "postgres",
                            user = POSTGRES_USER,
                            password = POSTGRES_PASSWORD,
                            host = CONNECT_IP_REMOTE,
                            port = CONNECT_PORT_REMOTE) 
    
    date=date-timedelta(days=1) #Inserting on start day
        
                            
    #Gets type sentiment and makes the type in python, inserts into array
    all_sentiment = []
    info = CompositeInfo.fetch(conn, "sentiment")
    register_composite(info,conn)


    arti = CompositeInfo.fetch(conn, "article")
    register_composite(arti,conn)
    if is_hourly:
        arti = CompositeInfo.fetch(conn, "article_v2")
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

    if not is_hourly:
        cur = conn.cursor()
        cur.execute("INSERT INTO global_info \
                    (target_country,on_day,headline_national,headline_inter,on_subject,\
                    sentiment_national,sentiment_inter,senti_count_nat,senti_count_int,latest_processed ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (tar_country,date,all_articles[0],all_articles[1],query,all_sentiment,all_sentiment_inter,senti_count_arr_nat,senti_count_arr_int,datetime.today()))

    if is_hourly:
        cur = conn.cursor()
        cur.execute("INSERT INTO global_info_hourly \
                    (target_country,on_time,headline_national,headline_inter,\
                    sentiment_national,sentiment_inter,senti_count_nat,senti_count_int,latest_processed ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (tar_country,date,all_articles[0],all_articles[1],all_sentiment,all_sentiment_inter,senti_count_arr_nat,senti_count_arr_int,datetime.today()))
    conn.commit()
    cur.close()
    conn.close()

    return True

def fetch_and_insert_one(target, subject, remain_rows, roberta, syncer, on_day=date.today(), short_subject="Any Subject", is_hourly=False):
    """Completes all tasks for one row, separated for multithreading"""
    already_in_db = check_exists(target, short_subject, on_day, is_hourly=is_hourly)
    inside_threads = []
    if already_in_db: 
        print(f"{target} on {short_subject} on {on_day} already in database")
        return
    try:
        print(f"Starting {target} about {subject}: remaining: {remain_rows}")
        data_nat = get_gdelt_processed(
            query=subject, target_country=target, date=on_day, roberta=roberta, syncer=syncer, is_hourly=is_hourly)
        data_inter = get_gdelt_processed(
            query=subject, target_country=str("-"+target), date=on_day, roberta=roberta, syncer=syncer, is_hourly=is_hourly)
        title_arr = [None] * 2
        if len(data_nat) == 0 or len(data_inter) == 0:
            print(f"Length of one headline array was 0 for: {target}")
        if data_nat[0] == None:
            return False
        t = Thread(target=get_titles, args=[title_arr, data_nat, syncer, 0])
        t.start()
        inside_threads.append(t)
        if data_inter[0] == None:
            return False
        t = Thread(target=get_titles, args=[title_arr, data_inter, syncer, 1])
        t.start()
        inside_threads.append(t)
        #titles_inter =  asyncio.run(get_titles(data_inter,syncer))
        while inside_threads[0].is_alive() or inside_threads[1].is_alive():
            #print(f"international: {title_arr[1]},{inside_threads[1]} national: {title_arr[0]},{inside_threads[0]}")
            time.sleep(5)

        titles_nat = title_arr[0]
        titles_inter = title_arr[1]
        if titles_nat == None:
           return False 
        if titles_nat == False:
            return False
        
        if titles_inter == None:
           return False
        if titles_inter == False:
            return False
        
        print(f"Working on insdert for {target}")
        
        sentiment_arr_nat, titles_nat, target_country, query = process_titles(
                target_country=target, date=on_day, roberta=roberta, syncer=syncer, titles=titles_nat) 
        sentiment_arr_inter, titles_inter, target_country, query = process_titles(
                query=subject, target_country=str("-"+target), date=on_day, roberta=roberta, syncer=syncer, titles=titles_inter) 
        insert_data(sentiment_arr_nat, titles_nat, sentiment_arr_inter, titles_inter, target_country, short_subject, on_day, is_hourly=is_hourly)
        print(f"Inserted sucessfully: {target} on {subject} on {on_day}")
    except Exception as error:
        print(f"{error} \n Continuing anyway but {target} on {on_day} not inserted")
    return True


# TODO:Fix large duping problem from GDELT data
if __name__ == "__main__":
    syncer = TranslatorSyncer()
    roberta = GST_Roberta()
    start_time = time.time()
    count = 0
    max_concurrent = 160
    threads = []

    on_days = []
    is_hourly = True
    if is_hourly:
        for i in range(1):
            cur_hour = datetime.today()-timedelta(hours=i+10)
            cur_hour = cur_hour.replace(minute=0,second=0,microsecond=0)
            on_days.append(cur_hour)
    else:
        for i in range(1):
            on_days.append(date.today()-timedelta(days=i+7))

    subjects = ""

    #TODO: More function calls, less nesting 
    """Need to make this abomination prettier"""
    for on_day in on_days:
        for target in countries:
            name = target
            name_2 = None
            first_string = f"({name} economy OR {name} market)"

            """if target in countries_map:
                name_2 = name
                name = countries_map[target]
                first_string = f"({name} economy OR {name} market OR {name_2} economy OR {name_2} market)"""
            
            target = re.sub(r'\s+', '', target) #Need to remove spaces for sourcecountry

            short_subjects = ["economy","housing","crime","inflation","immigration"]
            if is_hourly:
                hourly_subjects =  name + ' ' + subjects_given[0]
                for i in range(1,len(subjects_given)):
                    hourly_subjects += ' OR ' + name + ' ' + subjects_given[i]
                subjects = [hourly_subjects]
            for i in range(len(subjects)):
                subject = subjects[i]
                short_subject = short_subjects[i]
                time.sleep(5)#Not to spam too much on API's (ESP Google translate)
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
                #asyncio.run(fetch_and_insert_one(target, subject, remain_rows, roberta, syncer, on_day, short_subject))
                t = Thread(target=fetch_and_insert_one, args=[target, subject, remain_rows, roberta, syncer, on_day, short_subject, True])
                t.start()
                threads.append(t)
                
                count += 1
    while len(threads) != 0:
        for t in threads:
            if t.is_alive() == False:
                threads.remove(t)
        time.sleep(2)
    for i in range(2):
        time.sleep(5)
    print(f"Finished all, closing, total time: {time.time() - start_time}")

