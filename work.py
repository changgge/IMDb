import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import time
import random
import traceback
from requests.exceptions import RequestException
import os
import json


CACHE_FNAME = 'cache.json'
dbRoute = 'mydb.db'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

#base setting of database
conn = sqlite3.connect(dbRoute)
conn.text_factory = str
c = conn.cursor()

def make_request_using_cache(url,cookie=None):
    """
    get response from a url
    paras:
        url: website u want srawl,
        cookie:if u have a cookie then fill it
    return:
        if successed then return the cotent of page 
        if failed then return None
    """
    ## first, look in the cache to see if we already have this data
    if url in CACHE_DICTION:
        print("Getting cached data...",url)
        return CACHE_DICTION[url]

    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
        }
    if cookie:
        header['Cookie'] = cookie
    for i in range(5):
        try:
            response = requests.get(url,headers=header)
            if response.status_code == 200:
                print("Making a request for new data and stored in cache")
                CACHE_DICTION[url] = response.text
                dumped_json_cache = json.dumps(CACHE_DICTION)
                fw = open(CACHE_FNAME,"w")
                fw.write(dumped_json_cache)
                fw.close() # Close the open file
                return CACHE_DICTION[url]
        except RequestException as e:
            print('err: %s' % e)
        else:
            traceback.print_exc()
        time.sleep(1)
    return None

def craw_movie_list(eurl):
    """
    get the website of movie detail page  from a page cotains list of theses movies
    paras:
        eurl:  page website cotains list of theses movies
    return:
        movieUrlList: websites list of movie detail pages
    """
    orightml = make_request_using_cache(eurl)
    if not orightml:
        print('Scraw Error')
        return 0
    movieUrlList = []
    soup = BeautifulSoup(orightml)
    moiviesList = soup.find_all(name='div',attrs={'class':"lister-item mode-advanced"})
    for moiveDiv in moiviesList:
        thisMovieUrl = moiveDiv.h3.a['href']
        #print(urlModify(thisMovieUrl))
        movieUrlList.append(urlModify(thisMovieUrl))
    return movieUrlList


def findNumInStr(rawStr,errorNum='error'):
    """
    get number from a string and invert it to int
    paras:
        eurl: a string contains a num
    return:
        if successed return  a int
        if failed    return 'error'
    """
    aa = rawStr.replace(' ','')
    aa = aa.replace(r'\n','')
    aa = re.findall('\d*,*\d+',aa)
    if len(aa):
        return int(aa[0].replace(',',''))
    else:
        if errorNum=='error':
            raise NameError('找不到数字',rawStr)
        else:
            return errorNum


#create a new table every time run this program
c.execute('''DROP TABLE IF EXISTS movie2''')  #如果存在就删除
c.execute('''CREATE TABLE movie2 (title text, director text, Popularity int,country text,language text,releaseDate text,genres text)''')

c.execute('''DROP TABLE IF EXISTS movieActor2''')  #如果存在就删除
c.execute('''CREATE TABLE movieActor2 (title text,stars text)''')

def craw_movie_info(aMovieUrl):
    """
    craw a page of movie details,get this movie's 'title' , 'director' , 'Popularity' ,'country' ,'language' ,'releaseDate' ,'genres' ,'stars'
    paras:
        aMovieUrl:  website of a  movie details page
    return:
        dicts    :  a dict contains information of this movie

    """
    orightml = make_request_using_cache(aMovieUrl)
    #print(orightml)
    if not orightml:
        print('Scraw Error')
        return 0
    dicts = {}
    soup = BeautifulSoup(orightml)

    #title
    titleEm = soup.find_all(name='div',attrs={'class':"originalTitle"})
    if len(titleEm):
        dicts['title'] = titleEm[0].string
    else:
        dicts['title'] = ''.join(soup.head.title.stripped_strings)
    
    #director
    dirctorEm = soup.find_all(name='h4',text=["Director:","Directors:"])
    #print(PopularityEm)
    if len(dirctorEm):
        dicts['director'] = ''.join(dirctorEm[0].parent.a.stripped_strings)

    def popularity(tag):
        return  tag.name=='div' and  tag.has_attr('class') and "titleReviewBarSubItem" in tag['class'] and "Popularity" in ''.join(tag.stripped_strings)

    PopularityEm = soup.find_all(popularity)
    if len(PopularityEm):   
        dicts['Popularity'] = findNumInStr(''.join((PopularityEm[0].find_all(name='span',attrs={'class':"subText"})[0].stripped_strings)))    

    detailEm = soup.find_all(name='div',attrs={'id':"titleDetails"})
    if len(detailEm):
        #country
        if len(detailEm[0].find_all(name='h4',text="Country:")):
            dicts['country'] = ''.join(detailEm[0].find_all(name='h4',text="Country:")[0].parent.a.stripped_strings)
        #language
        if len(detailEm[0].find_all(name='h4',text="Language:")):
            dicts['language'] = ''.join(detailEm[0].find_all(name='h4',text="Language:")[0].parent.a.stripped_strings)
        #country
        if len(detailEm[0].find_all(name='h4',text="Release Date:")):
            dicts['releaseDate'] = ''.join(detailEm[0].find_all(name='h4',text="Release Date:")[0].parent.stripped_strings)
    
    #movie Genres
    genresEm = soup.find_all(name='h4',text="Genres:")
    genresList = []
    for aa in genresEm[0].parent.find_all(name='a'):
        genresList.append(''.join(aa.stripped_strings))
    dicts['genres'] = ','.join(genresList)

    #movie stars,record first ten stars
    starsEm = soup.find_all(name='table',attrs={'class':"cast_list"})
    starsList = []
    for aa in starsEm[0].find_all(name='tr',attrs={'class':["odd",'even']}):
        starsList.append(''.join(aa.find_all(name='a')[1].stripped_strings))
    dicts['stars'] = ','.join(starsList[:10])

    return dicts


def urlModify(eurl):
    eurl = r'https://www.imdb.com'+eurl
    return eurl

kinds = ['title' , 'director' , 'Popularity' ,'country' ,'language' ,'releaseDate' ,'genres' ,'stars' ]
pagesEurlList = []
for i in range(3,68,1):
    pagesEurlList.append(r'https://www.imdb.com/search/title/?title_type=feature&year=2020-11-01,2020-12-31&start={0}'.format(i*50+1))
kk = 0
for eurl1 in pagesEurlList:
    print('第{0}页'.format(kk))
    kk+=1
    eurlList = craw_movie_list(eurl1)
    jj=0
    for eurl in eurlList:
        time.sleep(random.randint(4,10))
        print('第{0}个'.format(jj),eurl)
        jj+=1
        try:
            aMovieDict = craw_movie_info(eurl)
            if isinstance(aMovieDict,str) and 'Scraw Error' in aMovieDict:
                continue
        except:
            traceback.print_exc()
            time.sleep(random.randint(4,10))
            continue
        aMovieList  = []
        movieactors = []
        for xx in kinds:
            if xx in aMovieDict:
                if xx == 'stars':
                    movieactors.append(aMovieDict[xx])
                elif xx == 'title':
                    movieactors.append(aMovieDict[xx])
                    aMovieList.append(aMovieDict[xx])
                else:
                    aMovieList.append(aMovieDict[xx])
            else:
                if xx == 'stars':
                    movieactors.append('')
                elif xx == 'title':
                    movieactors.append('')
                    aMovieList.append('')
                else:
                    aMovieList.append('')
        aMovieCell = tuple(aMovieList)
        movieactorsCell = tuple(movieactors)
        print(aMovieCell)
        c.execute("INSERT INTO movie2 values(?,?,?,?,?,?,?)", aMovieCell)
        c.execute("INSERT INTO movieActor2 values(?,?)", movieactorsCell)
        conn.commit()
    time.sleep(10)

