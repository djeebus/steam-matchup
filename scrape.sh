#!/bin/bash

OUTPUT=games.json

if [ -f $OUTPUT ]
then
  rm $OUTPUT
fi

time scrapy runspider scraper.py -o $OUTPUT -t json -L INFO
