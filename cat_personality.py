import requests
import json
import http.client
from api_key_p3 import API_KEY
# API key
conn = http.client.HTTPSConnection("api.thecatapi.com")
headers = {'x-api-key': API_KEY }

def get_breed_id():
    url = "https://api.thecatapi.com/v1/breeds"
    page = requests.get(url, headers=headers)
    page_dict = json.loads(page.text)
    breeds_dict = {}
    for i in page_dict:
        # print(i['name'])
        breeds_dict[i['name']] = i['id']
    return breeds_dict


def get_personality_of_breed(breed='Sphynx'):
    '''
    '''

    
    # print(i)
    breeds_dict = get_breed_id()
    id = breeds_dict[breed]
    # print(breeds_dict)
    breed_url = f"https://api.thecatapi.com/v1/breeds/search?q={id}"
    page = requests.get(breed_url, headers=headers)
    page_dict = json.loads(page.text)
    print(page_dict)
    # print(page_dict[0])
    # conn.request("GET", "/v1/images/search?limit=5&breed_id=sphy", headers=headers)
    # res = conn.getresponse()
    # data = res.read()
    # page_dict = json.loads(data)
    # print(page_dict[1])

get_personality_of_breed()
