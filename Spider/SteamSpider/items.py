# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class SteamGame(Item):
    id = Field()
    url = Field()
    name = Field()
    features = Field()
    genres = Field()

    price = Field()
    metascore = Field()
    release_date = Field()
