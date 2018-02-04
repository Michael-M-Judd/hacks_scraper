# Imports
from functools import wraps
import requests, json, time
import threading
from lxml import html
from algoliasearch import algoliasearch
from github import Github
from bs4 import BeautifulSoup
import os

container = []

def create_query(keywords):
    result = ""
    for keyword in keywords:
        result = result + "+" + keyword
    return result[1:]

def get_devpost(query):
    global container
    # get first page of query results... max of 4 documents returned
    page = requests.get('https://devpost.com/software/search?query=' + query + '&page=0').json()["software"]
    counter = 0

    if len(page) != 0:
        for project in page:
            if counter == 5: break
            product_data = {}
            product_data['title'] = project['name']
            product_data['url'] = project['url']
            product_data['tagline'] = project['tagline']
            product_data['image_url'] = project['photo']
            product_data['tags'] = project['tags']
            print(product_data)
            container.append(product_data)
            counter += 1
        print ('DEVPOST ELAPSED TIME: ', time.time())
    else: # no data found
        return None

def get_producthunt(query):
    global container
    client = algoliasearch.Client("0H4SMABBSG", '9670d2d619b9d07859448d7628eea5f3')
    index = client.init_index('Post_production')
    posts = index.search(query, {"page": 0})['hits']
    counter = 0

    if len(posts) != 0:
        for project in posts:
            if counter == 5: break
            product_data = {}
            product_data['title'] = project['name']
            product_data['tagline'] = project['tagline']
            product_data['url'] = 'https://www.producthunt.com/' + project['url']
            product_data['image_url'] = project['thumbnail']['image_url']

            topics_array = []
            for topic in project['topics']:
                topics_array.append(topic['name'])
        
            product_data['tags'] = topics_array
            container.append(product_data)
        print('PRODUCT HUNT:', time.time())
    else:
        return None


def get_github (search_query):
    global container
    g = Github("testhacks", "random123")
    _ = {}
    counter = 0
    for repo in g.search_repositories(search_query, sort = "stars", order= "desc").get_page(0):
        if counter == 5: break
        _ ['title'] = repo.name
        _ ['tagline'] = repo.description
        _ ['url'] = repo.html_url
        _ ['tags'] = repo.language
        _ ['image_url'] = None
        container.append(_)
        counter += 1
    print('GITHUB TIME: ', time.time())


def get_googleplay(search_query):
    global container
    search_url = "https://play.google.com/store/search?q="+ search_query +"&c=apps&hl=en"
    page = requests.get(search_url)
    data = page.text
    results = {}

    soup = BeautifulSoup(data, "lxml")
    counter = 0
    for link in soup.find_all('div', attrs = {"class" : "details"}):
        if (counter == 5): break
        #for _ in link.find_all ('a'):
        href = link.find ("a").get("href")
        url = "https://play.google.com" + href
        try:
            title = link.find ("a", {"class" : "title"}).get_text(strip = True)
            description = link.find ("div", {"class" : "description"}).get_text(strip = True)
            results ['title'] = title
            results ['tagline'] = description
            results ['url'] = url
            results ['tags'] = None
            results ['image_url'] = None
            container.append(results)
            counter += 1
        except:
            pass
    print('GOOGLE PLAY: ', time.time())

def delay(delay=0.):
    def wrap(f):
        @wraps(f)
        def delayed(*args, **kwargs):
            timer = threading.Timer(delay, f, args=args, kwargs=kwargs)
            timer.start()
        return delayed
    return wrap

@delay(0.8)
def getScore(title, desc):
    #global response
    global container
    print(container)
    payload = { "title": title, "description": desc, "candidates": container }
    resp = requests.post('http://52.233.33.65:5000/score', data = json.dumps(payload))
    payload = json.dumps(resp.json())
    print(payload)
    #response.write(payload)
    print("DONE!")
    #return response.close()

#postdata = json.loads(open(os.environ['req']).read())
#response = open(os.environ['res'], 'w')
postdata = {
	"name": "orchestra conductor",
	"description": "app conduct orchestra with phone",
	"sites": {
		"devpost": "t",
    "github": "t"
	}
}
title = postdata['name']
description = postdata['description']
tokens = description.split(' ')
sites = postdata['sites']


t1 = threading.Thread(target=get_devpost, args=(create_query(tokens), ))
t2 = threading.Thread(target=get_github, args=(description, ))
t3 = threading.Thread(target=get_googleplay, args=(description, ))
t4 = threading.Thread(target=get_producthunt, args=(description, ))
threads = { "devpost": t1, "github": t2, "producthunt": t3, "googleplay": t4}

for key, val in sites.items():
    if val == 't': threads[key].start()

getScore(title, description)