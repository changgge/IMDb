# IMDb

Final Project.


## Usage

Use work.py and dataSupport.py to crawl, clean and store data to SQL.
This process has been done, and the results are in mydb.db

Use app.py to see flask charts displayed on a temporary website (link will be shown in the terminal when you execute the file).

### Pakages Needed

requests, BeautifulSoup, sqlite3, flask


## Data sources
### 1. Data origin
The website [IMDb] (https://www.imdb.com/) is used in this project, which displays the information about released movies. URLs including information we need have been visited ad crawled, such as: https://www.imdb.com/search/title/?title_type=feature&year=2020-11-01,2020-12-31&start=1

### 2. Get the data
First, crawl the general information of 2,200 movies from the last two months of 2020. 
Then, crawl the Movie Details page address of these movies we obtained
Finally, crawl the detailed information of these movies from the Movie Details page address we obtained. 

## Summary of data
### 1. Database
the data is stored in a SQLite database (mydb.db), and it can be read and retrieved. 
### 2. Description of records
I crawl information on about 2,200 films that were set to be released in the November and December of the year 2020. It included attributes such as the name of the film, the director, the release date, the mass expectations index, the movie genre, and the actors.



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
