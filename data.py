# Imports
import requests, json, time
from lxml import html
from algoliasearch import algoliasearch
from github import Github
from bs4 import BeautifulSoup


def get_devpost(query):
    start = time.time()
    # get first page of query results... max of 4 documents returned
    page = requests.get('https://devpost.com/software/search?query=' + query + '&page=0').json()["software"]
    
    
    products = [] # list of json objects
    devpost_data = {'devpost': products}

    if len(page) != 0:
        for project in page:

            product_data = {}

            product_data['title'] = project['name']
            product_data['url'] = project['url']
            product_data['tagline'] = project['tagline']
            product_data['image_url'] = project['photo']
            product_data['tags'] = project['tags']

            products.append(product_data)
        print ('DEVPOST ELAPSED TIME: ', time.time() - start)
        return json.dumps(devpost_data)

    else: # no data found
        return None


def get_producthunt(query):
    start = time.time()

    client = algoliasearch.Client("0H4SMABBSG", '9670d2d619b9d07859448d7628eea5f3')
    index = client.init_index('Post_production')

    posts = index.search( query, {"page": 0} )['hits']

    products = [] # list of json objects
    producthunt_data = {'producthunt': products}

    if len(posts) != 0:
        for project in posts:

            product_data = {}

            product_data['title'] = project['name']
            product_data['tagline'] = project['tagline']
            product_data['url'] = 'https://www.producthunt.com/' + project['url']
            product_data['image_url'] = project['thumbnail']['image_url']

            topics_array = []
            for topic in project['topics']:
                topics_array.append(topic['name'])
        
            product_data['tags'] = topics_array

            products.append(product_data)
        print('PRODUCT HUNT:', time.time() - start)
        return json.dumps(producthunt_data)

    else:
        return None


def get_github (search_query):

    start = time.time()
    g = Github ("testhacks", "random123")
    _ = {}
    list_of_JSON = []
    for repo in g.search_repositories(search_query, sort = "stars", order= "desc").get_page(0):
        _ ['title'] = repo.name
        _ ['tagline'] = repo.description
        _ ['url'] = repo.html_url
        _ ['tags'] = repo.language
        _ ['image_url'] = None
        list_of_JSON.append(_)
    print('GITHUB TIME: ', time.time() - start)
    return (json.dumps (list_of_JSON))


def get_googleplay(search_query):
    start = time.time()
    search_url = "https://play.google.com/store/search?q="+ search_query +"&c=apps&hl=en"
    page = requests.get(search_url)
    data = page.text
    results = {}
    list_of_JSON = []

    soup = BeautifulSoup (data, "lxml")
    for link in soup.find_all('div', attrs = {"class" : "details"}):
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
            list_of_JSON.append (results)
        except:
            pass
    print('GOOGLE PLAY: ', start - time.time())
    return (json.dumps (list_of_JSON))

a = get_devpost('blockchain')
b = get_producthunt('blockchain')
c = get_googleplay('blockchain')
d = get_github('blockchain')
#print(a)
#print(b)