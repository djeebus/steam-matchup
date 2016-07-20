import scrapy


class GameSpider(scrapy.Spider):
    name = 'steam_games'
    custom_settings = {
        'COOKIES_ENABLED': True,
        # 'COOKIES_DEBUG': True,
    }
    allowed_domains = ['store.steampowered.com']
    start_urls = [
        'http://store.steampowered.com/search/?category1=998',
    ]

    parsed_page_numbers = {1}

    BAD_PAGE_NAMES = {'<', '>'}

    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True,
                              meta={'cookiejar': 0})

    def parse(self, response):
        self.logger.info('Parsing "%s"' % response.url)

        cookiejar = response.meta['cookiejar']

        hxs = scrapy.Selector(response)
        results = hxs.xpath('//a[contains(@class, "search_result_row")]')

        for result in results:
            href = result.xpath('@href').extract()[0]

            yield scrapy.Request(
                href,
                callback=self.parse_page,
                meta={'cookiejar': cookiejar},
                cookies={
                    'birthtime': '28801',
                    'lastagecheckage': '1-January-1975',
                    'mature_content': '1',
                },
            )

        pages = hxs.xpath('//div[@class="search_pagination_right"]/a')
        for page in pages:
            number = self._get_string(page.xpath('text()'))
            if not number.isdigit():
                if number not in self.BAD_PAGE_NAMES:
                    self.logger.info('skipping search page called "%s": not a digit' % number)
                continue

            if number in self.parsed_page_numbers:
                self.logger.debug('Skipping page: %s' % number)
                continue

            self.parsed_page_numbers.add(number)

            self.logger.debug('queueing result page %s' % number)
            yield scrapy.Request(
                self._get_string(page.xpath('@href')),
                meta={
                    'page_number:': number,
                    'cookiejar': cookiejar,
                },
            )

    def _get_string(self, result):
        if not result:
            return ''

        extracted = result.extract()

        if not extracted or len(extracted) == 0:
            return ''

        return extracted[0]

    def parse_page(self, response):
        if 'agecheck' in response.url:
            import pdb; pdb.set_trace()
            self.logger.warning('Failed to submit age check')
            return

        hxs = scrapy.Selector(response)
        url = response.url
        if '?' in response.url:
            url = response.url[:response.url.rfind('?') - 1]
        if url[len(url) - 1] == '/':
            url = url[:len(url) - 1]  # trim last character

        name = hxs.xpath('//div[@class="apphub_AppName"]/text()').extract()[0]
        specs = hxs.xpath(
            "//div[contains(@class, 'game_meta_data')]//div[contains(@class, 'game_area_details_specs')]//a/text()")
        features = {self._get_feature(s) for s in specs}
        tags = [
            t.xpath('text()').extract()[0].strip()
            for t in hxs.xpath("//a[@class='app_tag']")
        ]
        details_block = hxs.xpath("//div[@class='details_block']//*[local-name() = 'a' or local-name() = 'b']")
        metascore = self._get_string(hxs.xpath('//div[@id="game_area_metascore"]/span[not(@class)]/text()'))
        price = self._get_string(hxs.xpath('//div[@class="game_purchase_price price"]/text()'))
        release_date = self._get_string(hxs.xpath('//div[@class="release_date"]/span[@class="date"]/text()'))
        found_genre = False
        genres = []
        for detail in details_block:
            if not found_genre:
                found_genre = 'Genre:' in detail.xpath('text()').extract()
                continue

            if detail.root.tag != 'a':
                break

            for text in detail.xpath('text()').extract():
                genres.append(text)

        self.logger.info('finished parsing %s' % name)
        return dict(
            id=url[url.rfind('/') + 1:],
            name=name,
            url=url,
            features=[f for f in features if f],
            tags=tags,
            genres=[g for g in genres if g],

            metascore=metascore,
            price=price.strip(),
            release_date=release_date,
        )

    def _get_feature(self, spec_node):
        text = spec_node.extract().strip()
        return text
