from scrapy import log
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
from SteamSpider.items import SteamGame
from scrapy.spider import BaseSpider

__author__ = 'digitaljeebus'


class GameSpider(BaseSpider):

    name = 'steam'
    allowed_domains = ['store.steampowered.com']
    start_urls = [
        'http://store.steampowered.com/search/?category1=998'
    ]

    FAKE_FEATURES = {
        "Captions available",
        "Commentary available",
        "HDR available",
        "Includes Source SDK",
        "Includes level editor",
        "Valve Anti-Cheat enabled",
        "Mods",
        "Mods (require HL2)"}

    def __init__(self):
        self.parsed_page_numbers = {1}

    def _get_string(self, result):
        if not result:
            return ''

        extracted = result.extract()

        if not extracted or len(extracted) == 0:
            return ''

        return extracted[0]

    def parse(self, response):
        log.msg('Parsing "%s"' % response.url, log.INFO)

        hxs = HtmlXPathSelector(response)
        results = hxs.select('//a[@class="search_result_row even" or @class="search_result_row odd"]')

        for result in results:
            href = result.select('@href').extract()[0]
            name = self._get_string(result.select('//h4/text()'))
            metascore = self._get_string(result.select('div[@class="col search_metascore"]/text()'))
            price = self._get_string(result.select('div[@class="col search_price"]/text()'))
            release_date = self._get_string(result.select('div[@class="col search_released"]/text()'))

            yield Request(
                href,
                callback=self.parse_page,
                cookies={'birthtime': '157795201', 'lastagecheckage': '1-January-1975'},
                meta={'metascore': metascore, 'price': price, 'release_date': release_date, 'name': name})

        pages = hxs.select('//div[@class="search_pagination_right"]/a')
        for page in pages:
            number = self._get_string(page.select('text()'))
            if not number.isdigit():
                log.msg('skipping search page called "%s": not a digit' % number, log.INFO)
                continue

            if number in self.parsed_page_numbers:
                log.msg('Skipping page: %s' % number, log.INFO)
                continue

            self.parsed_page_numbers.add(number)

            log.msg('queueing result page %s' % number, log.DEBUG)
            yield Request(
                self._get_string(page.select('@href')),
                meta={'page_number:': number}
            )

    def parse_page(self, response):
        hxs = HtmlXPathSelector(response)
        name = response.meta['name']
        url = response.url[:response.url.rfind('?') - 1]
        if url[len(url) - 1:] == '/':
            url = url[0:len(url) - 2]

        specs = hxs.select(
            "//div[@class='details_block']//div[@class='game_area_details_specs']//div[@class='name']/text()")
        features = [self._get_feature(s) for s in specs]
        details_block = hxs.select("//div[@class='details_block']//*[local-name() = 'a' or local-name() = 'b']")
        found_genre = False
        genres = []
        for detail in details_block:
            if not found_genre:
                found_genre = 'Genre:' in detail.select('text()').extract()
                continue

            if detail._root.tag != 'a':
                break

            for text in detail.select('text()').extract():
                genres.append(text)

        return SteamGame(
            id=url[url.rfind('/') + 1:],
            name=name,
            url=url,
            features=[f for f in features if f],
            genres=[g for g in genres if g],

            metascore=response.meta['metascore'],
            price=response.meta['price'],
            release_date=response.meta['release_date']
        )

    def _get_feature(self, spec_node):
        text = spec_node.extract().strip()
        if text in self.FAKE_FEATURES:
            return None

        return text
