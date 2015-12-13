set OUTPUT=..\..\games.json

IF EXIST "%OUTPUT%" del "%OUTPUT%"

scrapy crawl steam_games -o "%OUTPUT%" -t json
