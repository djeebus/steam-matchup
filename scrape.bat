set OUTPUT=..\..\games.json

IF EXIST "%OUTPUT%" del "%OUTPUT%"

cd steam_matchup\scraper
scrapy crawl steam_games -o "%OUTPUT%" -t json
