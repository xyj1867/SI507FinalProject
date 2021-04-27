import requests
import json
import http.client
from api_key_p3 import API_KEY
import http.client
from bs4 import BeautifulSoup
import sqlite3
from common_fig import generate_all_breed_bar, breeds_origin_distribution

CACHE_FILENAME = "cat_cache.json"
THE_CAT_API = "api.thecatapi.com"
CFA_URL = "https://cfa.org/"


def construct_cache_key(base_url, params_url):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    
    Parameters
    ----------
    base_url: string
        The URL for the API endpoint
    params_url: string
        The params string
    
    Returns
    -------
    string
        the unique key as a string
    '''

    combine_url = base_url + params_url
    return combine_url

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''

    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''

    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def get_data(base_url, request_url):
    '''Get the data from the base_url+request_url from theCatApi

    Parameters
    ----------
    base_url: string
        The URL for the API endpoint
    params_url: string
        The params string

    Returns
    -------
    string
        The result from api
    '''
    CACHE_DICT = open_cache()
    cache_key = construct_cache_key(base_url, request_url)
    use_cache = False
    if cache_key in CACHE_DICT.keys():
        data = CACHE_DICT[cache_key]
        use_cache = True
        print("using cache")
    else:
        print("fetching from api")
        headers = {'x-api-key': API_KEY }
        conn = http.client.HTTPSConnection(base_url)
        conn.request("GET", request_url, headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        CACHE_DICT[cache_key] = data
        save_cache(CACHE_DICT)
    return (use_cache, data)


def create_breed_table():
    ''' Get the cat breeds' details from theCatAPI and save it to the database

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''

    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_create_command = """
        CREATE TABLE IF NOT EXISTS cat_breeds ( 
        id TEXT PRIMARY KEY,
        breed_name TEXT,
        temperament TEXT,
        origin TEXT,
        origin_code TEXT,
        description TEXT,
        indoor INTEGER,
        adaptability INTEGER,
        affection_level INTEGER,
        child_friendly INTEGER,
        dog_friendly INTEGER,
        energy_level INTEGER,
        health_issues INTEGER,
        intelligence INTEGER,
        shedding_level INTEGER,
        social_needs INTEGER,
        stranger_friendly INTEGER,
        vocalisation INTEGER,
        wiki TEXT);
        """
    cursor.execute(sql_create_command)
    connection.commit()
    use_cache, data_dict = get_data(THE_CAT_API, "/v1/breeds")
    data_dict = json.loads(data_dict)
    for i in data_dict:
        try:
            sql_exist = f'SELECT id FROM cat_breeds'
            exist = cursor.execute(sql_exist).fetchall()
            i["description"] = i["description"].replace("'", "''")
            if "wikipedia_url" not in i.keys():
                i["wikipedia_url"] = ""
            i["wikipedia_url"] = i["wikipedia_url"].replace("'", "''")
            if (i["id"],) not in exist:
                sql_command = f'''
                INSERT INTO cat_breeds VALUES(
                "{i["id"]}", 
                "{i["name"]}", 
                "{i["temperament"]}", 
                "{i["origin"]}", 
                "{i["country_code"]}",
                '{i["description"]}',
                "{i["indoor"]}",
                "{i["adaptability"]}",
                "{i["affection_level"]}",
                "{i["child_friendly"]}",
                "{i["dog_friendly"]}",
                "{i["energy_level"]}",
                "{i["health_issues"]}",
                "{i["intelligence"]}",
                "{i["shedding_level"]}",
                "{i["social_needs"]}",
                "{i["stranger_friendly"]}",
                "{i["vocalisation"]}",
                "{i["wikipedia_url"]}"
                )
                '''
                cursor.execute(sql_command)
                connection.commit()
        except:
            continue
           


    connection.close()

def get_breed_img(breed):
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_create_command = """
        CREATE TABLE IF NOT EXISTS cat_images ( 
        id TEXT PRIMARY KEY, 
        breed_id TEXT, 
        url TEXT,
        width INTEGER,
        height INTEGER
        );
    """
    cursor.execute(sql_create_command)
    connection.commit()
    request_url = f"/v1/images/search?limit=100&breed_id={breed['id']}"
    use_cache, data_dict = get_data(THE_CAT_API, request_url)
    data_dict = json.loads(data_dict)
    for i in data_dict:
        sql_exist = f'SELECT id FROM cat_images'
        exist = cursor.execute(sql_exist).fetchall()
        if (i["id"],) not in exist:
            sql_command = f'''
                INSERT INTO cat_images VALUES(
                "{i["id"]}", 
                "{i["breeds"][0]["id"]}", 
                "{i["url"]}", 
                "{i["width"]}", 
                "{i["height"]}"
                )
            '''
            cursor.execute(sql_command)
            connection.commit()
    connection.close()


def create_img_table():
    ''' Get cat images from theCatAPI and save it to the database

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    # Get all breed id from the cat breeds table
    sql_find_breed_id = "SELECT id FROM cat_breeds"
    breed_id_list = cursor.execute(sql_find_breed_id).fetchall()
    for (breed,) in breed_id_list:
        get_breed_img(breed)

def scrape_cfa(breed_name):
    '''Get the cfa data of the breed

    Parameters
    ----------
    breed_name: string
        The breed name

    Returns
    -------
    string:
        html text from the cfa
    '''
    request_url = breed_name + "-top-cats/"
    url = CFA_URL + breed_name + '/' + request_url
    CACHE_DICT = open_cache()
    cache_key = url
    html_text = None
    if cache_key in CACHE_DICT.keys():
        html_text = CACHE_DICT[cache_key]
        print("using cache")
    else:
        page = requests.get(url)
        html_text = page.text
        CACHE_DICT[url] = html_text
        save_cache(CACHE_DICT)
    return html_text

def get_award_breed(breed):
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_create_command = '''
        CREATE TABLE IF NOT EXISTS cat_awards (
        id INTEGER PRIMARY KEY,
        name TEXT,
        url TEXT,
        breed_id TEXT,
        season TEXT,
        award TEXT,
        info TEXT
        );
    '''
    cursor.execute(sql_create_command)
    connection.commit()
    name = breed['name'].lower().replace(' ', '-')
    html_text = scrape_cfa(name)
    soup = BeautifulSoup(html_text, 'html.parser')
    winner_photo_list = soup.find_all(class_="winner-photo")
    winner_name_list = soup.find_all(class_="cat-name")
    winner_name_list_clean = [i.contents[0] for i in winner_name_list]
    winner_info_list = soup.find_all(class_="season")
    winner_season_list = [i.contents[0] for i in winner_info_list]
    winner_award_list = [i.contents[2] for i in winner_info_list]
    winner_info_list_clean = [i.contents[-1].contents[0].strip() for i in winner_info_list]
    counter = 0
    sql_command = '''SELECT COUNT(1) FROM cat_awards'''
    (id_counter,) = cursor.execute(sql_command).fetchall()[0]
    for cat in winner_name_list_clean:
        sql_exist = f'SELECT name FROM cat_awards'
        exist = cursor.execute(sql_exist).fetchall()
        cat_name = cat.replace(',','').replace('"','')
        if (cat_name,) not in exist:
            sql_command = f"""
            INSERT INTO cat_awards VALUES(
            '{id_counter}',
            '{cat_name}', 
            '{winner_photo_list[counter]['src']}', 
            '{breed['id']}', 
            '{winner_season_list[counter]}', 
            '{winner_award_list[counter]}',
            '{winner_info_list_clean[counter]}'
            )
            """
            try:
                cursor.execute(sql_command)
                connection.commit()
            except:
                print(sql_command)
            counter += 1
        id_counter += 1
    connection.close()




def create_award_cats():
    '''Get the awards cat image and their details

    Parameters
    ----------
    string
        The 4 characters breed id

    Returns
    -------
    None
    '''
    connection = sqlite3.connect("cache.db")
    cursor = connection.cursor()
    sql_create_command = '''
        CREATE TABLE IF NOT EXISTS cat_awards (
        id INTEGER PRIMARY KEY,
        name TEXT,
        url TEXT,
        breed_id TEXT,
        season TEXT,
        award TEXT,
        info TEXT
        );
    '''
    cursor.execute(sql_create_command)
    connection.commit()
    sql_find_breed_name = "SELECT id, breed_name FROM cat_breeds"
    breed_list = cursor.execute(sql_find_breed_name).fetchall()
    breed_name_list_lower = [x[1].lower().replace(' ', '-') for x in breed_list]
    for name in breed_name_list_lower:
        html_text = scrape_cfa(name)
        soup = BeautifulSoup(html_text, 'html.parser')
        winner_photo_list = soup.find_all(class_="winner-photo")
        winner_name_list = soup.find_all(class_="cat-name")
        winner_name_list_clean = [i.contents[0] for i in winner_name_list]
        winner_info_list = soup.find_all(class_="season")
        winner_season_list = [i.contents[0] for i in winner_info_list]
        winner_award_list = [i.contents[2] for i in winner_info_list]
        winner_info_list_clean = [i.contents[-1].contents[0].strip() for i in winner_info_list]
        counter = 0
        for cat in winner_name_list_clean:
            sql_exist = f'SELECT name FROM cat_awards'
            exist = cursor.execute(sql_exist).fetchall()
            cat_name = cat.replace(',','').replace('"','')
            if (cat_name,) not in exist:
                sql_command = f"""
                INSERT INTO cat_awards VALUES(
                '{id_counter}',
                '{cat_name}', 
                '{winner_photo_list[counter]['src']}', 
                '{breed_list[breed_name_list_lower.index(name)][0]}', 
                '{winner_season_list[counter]}', 
                '{winner_award_list[counter]}',
                '{winner_info_list_clean[counter]}'
                )
                """
                try:
                    cursor.execute(sql_command)
                    connection.commit()
                    id_counter += 1
                except:
                    continue
                counter += 1
    connection.close()


if __name__ == "__main__":
    '''WHEN SUBMIT, UNCOMMENT THE TWO LINES OF CODE
    BELOW IF YOU COMPLETED EC1'''

    create_breed_table()




