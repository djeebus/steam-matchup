import steam
import json

from dogpile.cache import make_region

region = make_region().configure(
        'dogpile.cache.memory'
)


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """

    config.add_route('api: games', '/games')
    config.add_view(request_method='GET', route_name='api: games',
                    view=SteamGamesHandler, attr='get',
                    renderer='json')

    config.add_route('api: gamers', '/gamers')
    config.add_view(request_method='GET', route_name='api: gamers',
                    view=SteamGamersHandler, attr='get',
                    renderer='json')


class SteamGamersHandler(object):
    def __init__(self, request):
        self.request = request

    def get(self):
        steam_client = steam.ApiClient()

        gamer_ids_string = self.request.GET['gamerIds']
        gamer_ids = gamer_ids_string.split(',')

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

    @region.cache_on_arguments()
    def _get_all_games(self):
        print 'downloading all games'
        fp = open('games.json', 'r')
        games = json.load(fp)
        return games

    def get(self):
        game_ids = self.request.GET.getall('gameIds')

        return {
            'success': True,
            'results': [self._get_game(app_id) for app_id in game_ids]
        }

    def _get_game(self, app_id):
        games = self._get_all_games()
        matching_games = [g for g in games if g['id'] == app_id]
        if not matching_games:
            return {
                'id': app_id,
                'isValid': False
            }

        match = matching_games[0]
        return {
            'id': app_id,
            'isValid': True,
            'name': match['name'],
            'gameUrl': 'http://store.steampowered.com/app/%s' % app_id,
            'iconUrl': 'http://cdn.akamai.steamstatic.com/steam/apps/%s/header.jpg' % app_id,
            'features': match['features'],
            'genres': match['genres'],
            'price': match['price'],
            'release_date': match['release_date'],
            'metascore': match['metascore']
        }
