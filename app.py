import sqlite3
from flask import Flask, request, render_template, jsonify
import sys
import dataSupport as data
#reload(sys)
#sys.setdefaultencoding('utf-8')

app = Flask(__name__)

#get data from database
#movieDf：    dataframe of base information of moives
#movieGenreDf:dataframe of genre of movies
#movieStarDf :dataframe of stars of movies
movieDf,movieGenreDf,movieStarDf = data.dataClear(data.getFromSql())

@app.route("/", methods=["GET"])
def index():
    """
    link to internet page of this project
    paras : 
    return:
    """
    return render_template("index.html")

@app.route("/movieData", methods=["GET"])
def movieDataCreate():
    """
    create json data to record processed data for index reading
    paras : 
    return: a json file
    """
    if request.method == "GET":
        #quantity of diffrent genre moives
        movieGenre = data.everyGenryNum(movieGenreDf)
        #quantity of moives released in diffrent days
        movieDate  = data.everyDayNum(movieDf)
        #most wanted movies
        moviePopularity = data.mostWantedMovie(movieDf)
        #most wanted actor
        actorPopularity = data.getActorPopular(movieDf)
        #number of movies by actors
        moviesByactors  = data.getActorMoviesNum(movieStarDf)
        #genre movies
        genreMovies  = data.moviesOfGenry(movieGenreDf)

        #quantity of diffrent language moives
        MovieLanguage = data.everylanguageNum(movieDf)
        # movies  by each language:
        languageMovies = data.moviesOflanguage(movieDf)
    
    return jsonify(genreMNum=[movieGenre['genre'].to_list(),movieGenre['movieNum'].to_list()],
                    genreMNum2=[{'name':x,'value':float(y)}  for x,y in zip(movieGenre['genre'].to_list(),movieGenre['movieNum'].to_list())],
                    genreMovies = genreMovies,
                    dateMNum=[movieDate['date'].to_list(),movieDate['movieNum'].to_list()],
                    moviePopular=[moviePopularity['movie'].to_list(),moviePopularity['popularity'].to_list()],
                    actorPopular=[actorPopularity['star'].to_list(),actorPopularity['popularity'].to_list()],
                    numMovieByActor=[moviesByactors['star'].to_list(),moviesByactors['movieNum'].to_list()],
                    languageMNum2 = [{'name':x,'value':float(y)}  for x,y in zip(MovieLanguage['language'].to_list(),MovieLanguage['movieNum'].to_list())],
                    languageMovies = languageMovies
                    )

if __name__ == "__main__":
    app.run(debug=True)