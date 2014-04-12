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
    with open(file_name, 'r') as f:
        body = f.read()

    response = TextResponse(url=game_url, body=body, request=request)

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
    assert game['features'] == [
        'Single-player',
        'Multi-player',
        'Co-op',
        'Steam Achievements',
        'Steam Cloud',
        'Commentary available',
        'Captions available',
        'Stats',
        'Valve Anti-Cheat enabled',
        'Full controller support',
        'Includes Source SDK',
        'Steam Trading Cards',
        'Steam Workshop',
    ]
    assert game['genres'] == [
        'Action',
    ]
    assert game['tags'] == [
        'Zombies',
        'FPS',
        'Co-op',
        'Multiplayer',
        'Online Co-Op',
        'Action',
        'Valve',
        'Steam Workshop',
        'Shooter',
        'Moddable',
        'First-Person',
        'Steam Trading Cards',
        'Versus',
        'Intense',
        'Addictive',
        'Local Co-Op',
        'Tactical',
        'Survival',
        'Pills',
    ]


def test_parse_simcity_4():
    file_name = 'simcity4.html'
    game_url = 'http://store.steampowered.com/app/24780'

    game = _run_test(file_name, game_url)

    assert game['id'] == '24780'
    assert game['features'] == [
        'Single-player',
    ]
    assert game['genres'] == [
        'Simulation',
        'Strategy',
    ]
    assert game['tags'] == [
        'Simulation',
        'City Builder',
        'Strategy',
        'Sandbox',
        'Management',
        'Classic',
        'Moddable',
        'Timesink',
        'Mod Support',
        'Singleplayer',
        'Real-Time with Pause',
        'Creative',
        'Addictive',
        'Mod-friendly',
    ]


def test_parse_divinity_dragon_commander():
    file_name = 'divinity-dragon-commander.html'
    game_url = 'http://store.steampowered.com/app/243950'

    game = _run_test(file_name, game_url)

    assert game['id'] == '243950'
    assert game['features'] == [
        'Single-player',
        'Multi-player',
        'Steam Achievements',
        'Steam Leaderboards',
        'Steam Cloud',
        'Steam Trading Cards',
    ]
    assert game['genres'] == [
        'Action',
        'RPG',
        'Strategy',
    ]
    assert game['tags'] == [
        'Strategy',
        'RPG',
        'Political',
        'Dragons',
        'Fantasy',
        'Action',
        'Singleplayer',
        'Turn-based',
        'RTS',
        'Real-Time with Pause',
        'Steam Trading Cards',
        'Steampunk',
    ]
