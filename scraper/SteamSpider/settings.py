# Scrapy settings for SteamSpider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'SteamSpider'

SPIDER_MODULES = ['SteamSpider.spiders']
NEWSPIDER_MODULE = 'SteamSpider.spiders'

CONCURRENT_REQUESTS = 64
CONCURRENT_REQUESTS_PER_DOMAIN = 64

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'SteamSpider (+http://www.yourdomain.com)'
