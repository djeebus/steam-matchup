import json

from steam_matchup.steam import ApiClient


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """

    all_games = _load_games()
    config.add_request_method(lambda r: all_games, 'games', reify=True)

    config.add_route('api: games', '/games')
    config.add_view(request_method='GET', route_name='api: games',
                    view=SteamGamesHandler, attr='get',
                    renderer='json')

    config.add_route('api: gamers', '/gamers')
    config.add_view(request_method='GET', route_name='api: gamers',
                    view=SteamGamersHandler, attr='get',
                    renderer='json')


def _load_games():
    fp = open('games.json', 'r')
    games = json.load(fp)
    games = {int(game['id']): game for game in games}
    print("found %s games" % len(games))
    return games


class SteamGamersHandler(object):
    def __init__(self, request):
        self.request = request

    def get(self):
        steam_client = ApiClient()

        gamer_ids = self.request.GET.getall('gamerId')

        summaries_response = steam_client.get_player_summaries(gamer_ids)
        json_players = summaries_response['response']['players']
        return {
            'success': True,
            'results': [self._get_player(p, steam_client) for p in json_players]
        }

    def _get_player(self, json_player, steam_client):
        return {
            'id': json_player['steamid'],
            'name': json_player['personaname'],
            'gameIds': self._get_games(json_player['steamid'], steam_client),
            'friends': self._get_friends(json_player['steamid'], steam_client)
        }

    def _get_games(self, steam_id, steam_client):
        json_games = steam_client.get_owned_games(steam_id)
        return [g['appid'] for g in json_games['response']['games']]

    def _get_friends(self, steam_id, steam_client):
        json_result = steam_client.get_friends(steam_id)
        friend_steam_ids = [f['steamid'] for f in json_result['friendslist']['friends']]
        json_friends = steam_client.get_player_summaries(friend_steam_ids)
        return [self._get_friend(f) for f in json_friends['response']['players']]

    def _get_friend(self, json_player_summary):
        return {
            'id': json_player_summary['steamid'],
            'name': json_player_summary['personaname']
        }


class SteamGamesHandler(object):
    def __init__(self, request):
        self.request = request

    def get(self):
        game_ids = self.request.GET.getall('gameId')

        return {
            'success': True,
            'results': [self._get_game(app_id) for app_id in game_ids]
        }

    def _get_game(self, app_id):
        match = self.request.games.get(int(app_id))
        if not match:
            return {
                'id': app_id,
                'isValid': False
            }

        return {
            'id': app_id,
            'isValid': True,
            'name': match['name'],
            'gameUrl': 'http://store.steampowered.com/app/%s' % app_id,
            'iconUrl': 'http://cdn.akamai.steamstatic.com/steam/apps/%s/header.jpg' % app_id,
            'features': match['features'],
            'genres': match['genres'],
            'tags': match['tags'],
            'price': match['price'],
            'release_date': match['release_date'],
            'metascore': match['metascore']
        }
