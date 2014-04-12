#!/bin/bash

OUTPUT=../../games.json

if [ -f $OUTPUT ] 
then
  rm $OUTPUT
fi

scrapy crawl steam_games -o $OUTPUT -t json
