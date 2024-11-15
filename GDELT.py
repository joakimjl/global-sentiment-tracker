import requests
import json


#Example
#"https://api.gdeltproject.org/api/v2/doc/doc?query=%22News%22%20sourcecountry:US%20sourcelang:English&format=json"

# Context might be ideal only issue is designating origin country.
# Resource: https://blog.gdeltproject.org/announcing-the-gdelt-context-2-0-api/
# TODO: Add all outlets to countries
def fetch_gdelt_data(query_term="Newsletter", source_country="US", source_lang="English", mode="artlist"):
    #base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    base_url = "https://api.gdeltproject.org/api/v2/context/context"
    
    #query = f'"{query_term}" sourcecountry:{source_country} sourcelang:{source_lang}'
    query = f'"{query_term}"'
    
    params = {
        'format': "json",
        'timespan': "72H",
        'query': query,
        'searchlang': "english",
        'maxrecords':200,
        'sort':"DateDesc",
    }

    headers = { # Was needed for 429 error, might look for other solution
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    
    # Send GET request
    response = requests.get(base_url, params=params, headers=headers)
    print(response.url)
    if response.status_code == 200:
        
        data = json.loads(response.text)
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        return None

# Test usage
# TODO:Need to decide on what generic search terms should be...
if __name__ == "__main__":
    data = fetch_gdelt_data(query_term="Trump", source_country="US", source_lang="English", mode="artlist")
    if data:
        print(json.dumps(data, indent=2))