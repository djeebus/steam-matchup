#!/bin/bash

OUTPUT=games.json

if [ -f $OUTPUT ]
then
  rm $OUTPUT
fi

scrapy runspider scraper.py -o $OUTPUT -t json -L INFO
