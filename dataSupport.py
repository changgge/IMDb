import pandas as pd 
import sqlite3
import datetime
import re
import numpy as np
import time
import os

dbRoute ='mydb.db'
def dataClear(df):
    """
    clear raw data from database  
    paras :
        df: dataframe of movie data got from database
    return:
        df1:dataframe of base information of moives, columns of this dataframe is ['moive title',	'director',	'Popularity',	'country',	'language',	'releaseDate','star acting the leading role']
        df2:dataframe including moive information and its genre, columns of this dataframe is ['movie title',	'director',	'Popularity',	'country',	'language',	'releaseDate','one genre belongs to']
        df3:dataframe including moive information and its stars, columns of this dataframe is ['movie title',	'director',	'Popularity',	'country',	'language',	'releaseDate','star act in']
    """
    df.dropna(axis=0,subset = ["title"],inplace = True)   # 丢弃‘a’和‘e’这两列中有缺失值的行  
    df = df[df['title']!='']   # 丢弃‘a’和‘e’这两列中有缺失值的行  
    #title
    df['title'] = df['title'].apply(lambda x: x.replace('(2020) - IMDb',''))
    #popularity
    df['Popularity'] = df['Popularity'].apply(lambda x: 0 if x in ['',' '] else int(x))
    #releasedate

    def getDate(x):
        xxx = re.findall(r':.* \(',x)
        if len(xxx):
            return xxx[0][1:-2]
        else:
            return None
    df['releaseDate'] = df['releaseDate'].apply(lambda x: getDate(x))
    def dateFormal(x):
        if x in ['', ' ',None,np.nan]:
            return np.nan
        try:
            return datetime.datetime.strptime(x, r"%d %B %Y")
        except:
            try:
                return datetime.datetime.strptime(x, r"%B %Y")
            except:
                return datetime.datetime.strptime(x, r"%Y")
    df['releaseDate'] = df['releaseDate'].apply(lambda x: dateFormal(x))

    def onlylookfirstTen(x):
        xList = x.split(',')
        if len(xList) < 10:
            return ','.join(xList)
        else:
            return ','.join(xList[:10])
    def onlylookfirstOne(x):
        xList = x.split(',')
        return xList[0]
    df['stars'] = df['stars'].apply(lambda x: onlylookfirstTen(x))
    df1 = df[['title',	'director',	'Popularity',	'country',	'language',	'releaseDate','stars']]
    df1['stars'] = df1['stars'].apply(lambda x: onlylookfirstOne(x))
    df2 = df.drop('genres', axis=1).join(df['genres'].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('belongGenre'))
    df2 = df2[['title',	'director',	'Popularity',	'country',	'language',	'releaseDate','belongGenre']]
    df3 = df.drop('stars', axis=1).join(df['stars'].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('hasStar'))
    df3 = df3[['title',	'director',	'Popularity',	'country',	'language',	'releaseDate','hasStar']]
 
    return df1,df2,df3

def getFromSql():
    """
    get all data from database by sqlite3.
    paras :
    return:
        df:dataframe of all movie data,its columns is ['title' , 'director' , 'Popularity' ,'country' ,'language' ,'releaseDate' ,'genres' ,'stars']
    """

    cx = sqlite3.connect(dbRoute)   #连接数据库
    cu = cx.cursor()     
    sqlStr = "select * from movie2"
    df1 = pd.read_sql(sqlStr,cx)
    #df1.to_excel('222.xls')
    #print(len(df1))
    sqlStr = "select * from movieActor2"
    df2 = pd.read_sql(sqlStr,cx)
    #df2.to_excel('333.xls')
    #print(len(df2))
    df = pd.merge(df1,df2,how='inner',on=['title','director'])
    #print(df)
    return df
#getFromSql()
def everyGenryNum(df):
    """
    cooking data for index calling.
    group dataframe by genre to get the quantity of moives belongs to each genre. 
    paras :
        df:dataframe of genre of movies, columns of this dataframe is ['movie title',	'director',	'Popularity',	'country',	'language',	'releaseDate','one genre belongs to']
    return:
        df2:dataframe of all genre and  quantity of moives belongs to it,its columns is ['genres' ,'movieNum']
    """    
    df2 = df.groupby('belongGenre',as_index=False).count()[['belongGenre','title']]
    df2.columns = ['genre','movieNum']
    return df2
#getFromSql()
def everylanguageNum(df):
    """
    cooking data for index calling.
    group dataframe by language to get the quantity of moives belongs to each language. 
    paras :
        df:dataframe of base information of moives,, columns of this dataframe is ['movie title',	'director',	'Popularity',	'country',	'language',	'releaseDate']
    return:
        df2:dataframe of all genre and  quantity of moives belongs to it,its columns is ['language' ,'movieNum']
    """    
    df2 = df.groupby('language',as_index=False).count()[['language','title']]
    df2.columns = ['language','movieNum']
    df2.sort_values(by='movieNum',ascending=False,inplace=True)
    return df2.iloc[:15,:]
def everyDayNum(df):
    """
    cooking data for index calling.
    group dataframe by date to get the quantity of moives belongs to each day. 
    paras :
        df:dataframe of base information of moives, columns of this dataframe is ['moive title',	'director',	'Popularity',	'country',	'language',	'releaseDate']
    return:
        df2:dataframe of date and quantity of moives released in this day,its columns is ['date','movieNum']
    """  
    df2 = df.groupby('releaseDate',as_index=False).count()[['releaseDate','title']]
    df2.columns = ['date','movieNum']
    df2 = df2[df2['date']>=datetime.datetime.strptime(r'2020-11-01', r"%Y-%m-%d")]
    df2.sort_values(by='date',inplace=True)
    return df2

def mostWantedMovie(df):
    """
    cooking data for index calling.
    sort data by poularity of movies from highest to lowest
    paras :
        df:dataframe of base information of moives, columns of this dataframe is ['moive title',	'director',	'Popularity',	'country',	'language',	'releaseDate']
    return:
        df2:dataframe of movie title and its popularity,its columns is ['movie','popularity']
    """  
    df2 = df[['title','Popularity']]
    df2.sort_values(by='Popularity',ascending=False,inplace=True)
    df2.columns = ['movie','popularity']
    return df2

def getActorPopular(df):
    """
    cooking data for index calling.
    group data by stars to get average popularity of movies in which each star acted. and  sort data by actor poularity from highest to lowest
    paras :
        df:dataframe of base information of moives, columns of this dataframe is ['moive title',	'director',	'Popularity',	'country',	'language',	'releaseDate','star acting the leading role']
    return:
        df2:dataframe of star names and average popularity ,its columns is ['star','popularity']
    """  
    df2 = df[['stars','Popularity']]
    df2 = df2.groupby('stars',as_index=False).mean()
    df2.sort_values(by='Popularity',ascending=False,inplace=True)
    df2.columns = ['star','popularity']
    return df2

def getActorMoviesNum(df):
    """
    cooking data for index calling.
    group data by stars to get quantity of movies every star acted in . and  sort data by quantity of movies from highest to lowest
    paras :
        df:dataframe including moive information and its stars, columns of this dataframe is ['movie title',	'director',	'Popularity',	'country',	'language',	'releaseDate','star act in']
    return:
        df2:dataframe of star names and quantity of movies ,its columns is ['star','movieNum']
    """  
    df2 = df[['hasStar','title']]
    df2 = df2.groupby('hasStar',as_index=False).count()
    df2.sort_values(by='title',ascending=False,inplace=True)
    df2.columns = ['star','movieNum']
    return df2

def moviesOfGenry(df):
    """
    cooking data for index calling.
    make a dictionary . key is genre and value is the movie titles belongs to this genre
    paras :
        df:dataframe including moive information and its genre, columns of this dataframe is ['movie title',	'director',	'Popularity',	'country',	'language',	'releaseDate','one genre belongs to']
    return:
        df2:a dictionary ,its format is {'genre':[list of movie],....}
    """  
    genres = df['belongGenre'].unique()
    df.sort_values(by='Popularity',ascending=False,inplace=True)
    resultDict = {}
    for genre in genres:
        df3 = df[df['belongGenre']==genre]
        resultDict[genre] = [df3['title'].to_list(),df3['Popularity'].to_list()]
    return resultDict

def moviesOflanguage(df):
    """
    cooking data for index calling.
    make a dictionary . key is language and value is the movie titles belongs to this language
    paras :
        df:dataframe of base information of moives, columns of this dataframe is ['movie title',	'director',	'Popularity',	'country',	'language',	'releaseDate','one genre belongs to']
    return:
        df2:a dictionary ,its format is {'language':[list of movie],....}
    """  
    languages = df['language'].unique()
    df.sort_values(by='Popularity',ascending=False,inplace=True)
    resultDict = {}
    for lan in languages:
        df3 = df[df['language']==lan]
        resultDict[lan] = [df3['title'].to_list(),df3['Popularity'].to_list()]
    return resultDict
"""
df = getFromSql()
df.to_excel('111.xls')

movieDf,movieGenreDf,movieStarDf = dataClear(df)
print(everylanguageNum(movieDf))

print(moviesOfGenry(movieGenreDf))
#print(everyGenryNum(movieGenreDf))
#print(everyDayNum(movieDf))
print(mostWantedMovie(movieDf))
print(getActorPopular(movieDf))
print(getActorMoviesNum(movieStarDf))
"""



#print(df2.head())
