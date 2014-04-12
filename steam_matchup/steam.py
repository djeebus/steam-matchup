__author__ = 'jlombrozo'

import json
import logging
import urllib


logger = logging.getLogger(__name__)


class ApiClient(object):
    def get_player_summaries(self, gamer_ids):
        """ Get player summaries from steam
        """

        if not isinstance(gamer_ids, (frozenset, list, set, tuple, )):
            gamer_ids = [gamer_ids]

        return self._make_api_call('ISteamUser', 'GetPlayerSummaries', '0002', {"steamids": ",".join(gamer_ids)})

    def get_friends(self, steam_id):
        try:
            return self._make_api_call(
                'ISteamUser',
                'GetFriendList',
                '0001',
                {'steamid': steam_id, 'relationship': 'all'}
            )
        except IOError as e:
            if e.args[1] == 401:  # profile is private
                return {
                    'friendslist': {
                        'friends': []
                    }
                }

            raise  # all others

    def get_owned_games(self, steam_id):
        return self._make_api_call('IPlayerService', 'GetOwnedGames', '0001', {'steamid': steam_id, 'include_appinfo': 'true'})

    def get_all_games(self):
        return self._make_api_call('ISteamApps', 'GetAppList', '0002')

    def _make_api_call(self, interface_method, method_name, version, qs=None):
        if qs is None:
            qs = {}

        qs['key'] = '3F43D315F79104DE98A177968EE11A51'
        qs['format'] = 'json'

        url = "http://api.steampowered.com/%(interface)s/%(method)s/v%(version)s/?%(query)s" % {
            "interface": interface_method,
            "method": method_name,
            "version": version,
            "query": urllib.urlencode(qs)
        }

        logger.debug("steam request => %s" % url)

        f = urllib.urlopen(url)
        content = f.read()

        return json.loads(content)