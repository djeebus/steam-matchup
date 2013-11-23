#!/bin/bash

OUTPUT=../Website/games.json

if [ -f $OUTPUT ] 
then
  rm $OUTPUT
fi

scrapy crawl steam -o $OUTPUT -t json
