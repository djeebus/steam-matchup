import requests

from os import path

from scrapy.http.request import Request
from scrapy.http.response.text import TextResponse
from steam_matchup.scraper.SteamSpider.spiders.GameSpider import GameSpider


def _run_test(file_name, game_url, valid_data):
    valid_data['url'] = game_url

    request = Request(game_url, meta={})

    import tests
    file_name = path.join(path.dirname(tests.__file__), file_name)
    if path.isfile(file_name):
        encoding = 'ascii'
        with open(file_name, 'r') as f:
            body = f.read()
    else:
        response = requests.get(game_url)
        body = response.text
        encoding = response.encoding

        with open(file_name, 'w') as f:
            f.write(body.encode(encoding))

    response = TextResponse(url=game_url, body=body, request=request, encoding=encoding)

    spider = GameSpider()

    game = spider.parse_page(response)
    for key in ['features', 'tags', 'genres']:
        game[key] = set(game[key])

    assert game == valid_data


def test_parse_left_4_dead_2():
    file_name = 'left4dead2.html'
    game_url = 'http://store.steampowered.com/app/550'

    _run_test(file_name, game_url, {
        'id': '550',
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
        }
    })


def test_parse_simcity_4():
    file_name = 'simcity4.html'
    game_url = 'http://store.steampowered.com/app/24780'

    _run_test(file_name, game_url, {
        'id': '24780',
        'name': u'SimCity\xe2\u201e\xa2 4 Deluxe Edition',
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
    })


def test_parse_divinity_dragon_commander():
    _run_test(
        'divinity-dragon-commander.html',
        'http://store.steampowered.com/app/243950',
        {
            'id': '243950',
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
    )


def test_results_page_parser():

    results_url = 'http://store.steampowered.com/search/?sort_by=&sort_order=0&category1=998&page=1'

    request = Request(results_url)

    response = requests.get(results_url)
    body = response.text
    encoding = response.encoding

    response = TextResponse(url=results_url, body=body, request=request, encoding=encoding)

    spider = GameSpider()

    results = list(spider.parse(response))

    app_results = [r for r in results if r.url.startswith('http://store.steampowered.com/app/')]
    assert len(app_results) == 25

    search_results = [r for r in results if r.url.startswith('http://store.steampowered.com/search/')]
    assert len(search_results) == 3
