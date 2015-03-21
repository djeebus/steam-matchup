import requests

from os import path

from scrapy.http.request import Request
from scrapy.http.response.text import TextResponse
from steam_matchup.scraper.SteamSpider.spiders.GameSpider import GameSpider


def _run_test(file_name, game_url):
    request = Request(game_url, meta={
        'name': 'testing',
        'metascore': 1,
        'price': '$2.00',
        'release_date': 'Jan 3rd, 2014',
    })

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

    response = TextResponse(url=game_url, body=body, request=request, encoding=encoding)

    spider = GameSpider()

    game = spider.parse_page(response)

    assert game['name'] == 'testing'
    assert game['url'] == game_url

    return game


def test_parse_left_4_dead_2():
    file_name = 'left4dead2.html'
    game_url = 'http://store.steampowered.com/app/550'

    game = _run_test(file_name, game_url)

    assert game['id'] == '550'
    assert set(game['features']) == {
        'Captions available',
        'Co-op',
        'Commentary available',
        'Includes Source SDK',
        'Multi-player',
        'Single-player',
        'Steam Achievements',
        'Steam Cloud',
        'Steam Trading Cards',
        'Steam Workshop',
        'Stats',
        'Valve Anti-Cheat enabled',
    }
    assert set(game['genres']) == {
        'Action',
    }
    assert set(game['tags']) == {
        'Action',
        'Adventure',
        'Co-op',
        'First-Person',
        'FPS',
        'Gore',
        'Horror',
        'Local Co-Op',
        'Moddable',
        'Multiplayer',
        'Online Co-Op',
        'Post-apocalyptic',
        'Replay Value',
        'Shooter',
        'Singleplayer',
        'Survival',
        'Survival Horror',
        'Tactical',
        'Team-Based',
        'Zombies',
    }


def test_parse_simcity_4():
    file_name = 'simcity4.html'
    game_url = 'http://store.steampowered.com/app/24780'

    game = _run_test(file_name, game_url)

    assert game['id'] == '24780'
    assert set(game['features']) == {
        'Single-player',
    }
    assert set(game['genres']) == {
        'Simulation',
        'Strategy',
    }
    assert set(game['tags']) == {
        'Building',
        'City Builder',
        'Classic',
        'Economy',
        'Great Soundtrack',
        'Management',
        'Moddable',
        'Multiplayer',
        'Real-Time with Pause',
        'Sandbox',
        'Simulation',
        'Strategy',
        'Singleplayer',
    }


def test_parse_divinity_dragon_commander():
    file_name = 'divinity-dragon-commander.html'
    game_url = 'http://store.steampowered.com/app/243950'

    game = _run_test(file_name, game_url)

    assert game['id'] == '243950'
    assert set(game['features']) == {
        'Multi-player',
        'Single-player',
        'Steam Achievements',
        'Steam Leaderboards',
        'Steam Cloud',
        'Steam Trading Cards',
    }
    assert set(game['genres']) == {
        'Action',
        'RPG',
        'Strategy',
    }
    assert set(game['tags']) == {
        'Strategy',
        'RPG',
        'Dragons',
        'Political',
        'Action',
        'Fantasy',
        'RTS',
        'Singleplayer',
        'Turn-Based',
        'Steampunk',
        'Real-Time with Pause',
        'Multiplayer',
        'Choices Matter',
        'Story Rich',
        'Comedy',
    }


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
