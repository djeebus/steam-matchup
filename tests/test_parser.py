import requests
import pytest

from os import path

from scrapy.http.request import Request
from scrapy.http.response.text import TextResponse
from scraper import GameSpider


games_to_test = {
    'left 4 dead 2': {
        'id': '550',
        'url': 'http://store.steampowered.com/app/550',
        'name': 'Left 4 Dead 2',
        'metascore': '89',
        'price': '$19.99',
        'release_date': 'Nov 16, 2009',
        'features': {
            u'Captions available',
            u'Co-op',
            u'Commentary available',
            u'Full controller support',
            u'Includes Source SDK',
            u'Multi-player',
            u'Single-player',
            u'Steam Achievements',
            u'Steam Cloud',
            u'Steam Trading Cards',
            u'Steam Workshop',
            u'Stats',
            u'Valve Anti-Cheat enabled',
        },
        'genres': {
            'Action',
        },
        'tags': {
            u'Action',
            u'Adventure',
            u'Co-op',
            u'First-Person',
            u'FPS',
            u'Gore',
            u'Horror',
            u'Local Co-Op',
            u'Moddable',
            u'Multiplayer',
            u'Online Co-Op',
            u'Post-apocalyptic',
            u'Replay Value',
            u'Shooter',
            u'Singleplayer',
            u'Survival',
            u'Survival Horror',
            u'Tactical',
            u'Team-Based',
            u'Zombies',
        },
    },
    'simcity 4 deluxe': {
        'id': '24780',
        'url': 'http://store.steampowered.com/app/24780',
        'name': u'SimCity™ 4 Deluxe Edition',
        'metascore': '',
        'price': u'$19.99',
        'release_date': u'Sep 22, 2003',
        'features': {
            u'Single-player',
        },
        'genres': {
            u'Simulation',
            u'Strategy'
        },
        'tags': {
            u'Building',
            u'City Builder',
            u'Classic',
            u'Economy',
            u'Great Soundtrack',
            u'Management',
            u'Moddable',
            u'Multiplayer',
            u'Real-Time with Pause',
            u'Sandbox',
            u'Simulation',
            u'Strategy',
            u'Singleplayer',
        },
    },
    'divinity: dragon commander': {
        'id': '243950',
        'url': 'http://store.steampowered.com/app/243950',
        'name': 'Divinity: Dragon Commander',
        'metascore': '',
        'price': '$39.99',
        'release_date': 'Aug 6, 2013',
        'features': {
            'Multi-player',
            'Single-player',
            'Steam Achievements',
            'Steam Leaderboards',
            'Steam Cloud',
            'Steam Trading Cards',
        },
        'tags': {
            u'Strategy',
            u'RPG',
            u'Dragons',
            u'Political',
            u'Action',
            u'Fantasy',
            u'RTS',
            u'Singleplayer',
            u'Turn-Based',
            u'Steampunk',
            u'Real-Time with Pause',
            u'Multiplayer',
            u'Choices Matter',
            u'Story Rich',
            u'Comedy',
            u'Co-op',
            u'Great Soundtrack',
        },
        'genres': {
            'Action',
            'RPG',
            'Strategy',
        },
    },
    'bob came in pieces': {
        'id': '46000',
        'url': 'http://store.steampowered.com/app/46000',
        'name': 'Bob Came in Pieces',
        'metascore': '73',
        'price': '$6.99',
        'release_date': 'Jan 22, 2010',
        'features': {
            'Single-player',
            'Steam Achievements',
            'Partial Controller Support',
            'Steam Cloud',
            'Steam Leaderboards',
        },
        'tags': {
            'Indie',
            'Adventure',
            'Puzzle',
            'Physics',
        },
        'genres': {
            'Adventure',
            'Indie',
        },
    }
}


@pytest.mark.parametrize("game_name", games_to_test)
def test_parser(game_name):
    valid_data = games_to_test[game_name]

    file_name = '%s.html' % valid_data['id']
    game_url = valid_data['url']

    request = Request(game_url, meta={})

    import tests
    file_name = path.join(path.dirname(tests.__file__), file_name)
    if path.isfile(file_name):
        with open(file_name, 'br') as f:
            body = f.read()
    else:
        response = requests.get(game_url)
        body = response.content

        with open(file_name, 'bw') as f:
            f.write(body)

    response = TextResponse(url=game_url, body=body.decode('utf-8'),
                            request=request, encoding='utf-8')

    spider = GameSpider()

    game = spider.parse_page(response)
    for key in ['features', 'tags', 'genres']:
        game[key] = set(game[key])

    assert game == valid_data


def test_results_page_parser():

    results_url = 'http://store.steampowered.com/search/?sort_by=&sort_order=0&category1=998&page=1'

    request = Request(results_url, meta={'cookiejar': 0})

    response = requests.get(results_url)
    body = response.text
    encoding = response.encoding

    response = TextResponse(
        url=results_url, body=body,
        request=request, encoding=encoding,
    )

    spider = GameSpider()

    results = list(spider.parse(response))

    app_results = [r for r in results if r.url.startswith('http://store.steampowered.com/app/')]
    assert len(app_results) == 25

    search_results = [r for r in results if r.url.startswith('http://store.steampowered.com/search/')]
    assert len(search_results) == 3
