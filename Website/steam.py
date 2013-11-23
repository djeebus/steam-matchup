__author__ = 'jlombrozo'

import json
import urllib
from bs4 import BeautifulSoup


class SteamPageParser(object):
    def parse_app_page(self, app_id):
        url = "http://store.steampowered.com/app/%s" % app_id
        content = self._get_content(url)
        return self._get_info_from_content(content)

    def _get_content(self, url):
        f = urllib.urlopen(url)
        encoding = f.headers['content-type'].split('charset=')[-1]
        unicode_content = unicode(f.read(), encoding)
        return unicode_content

    def _get_info_from_content(self, content):
        soup = BeautifulSoup(content)
        game_name_element = soup.select('.game_name')
        if not game_name_element:
            return None
        return {
            'name': game_name_element[0].text
        }


class ApiClient(object):
    def get_player_summaries(self, gamerIds):
        """ Get player summaries from steam
        """

        if not isinstance(gamerIds, (frozenset, list, set, tuple, )):
            gamerIds = [gamerIds]

        return self._make_api_call('ISteamUser', 'GetPlayerSummaries', '0002', {"steamids": ",".join(gamerIds)})

    def get_friends(self, steam_id):
        return self._make_api_call('ISteamUser', 'GetFriendList', '0001', {'steamid': steam_id, 'relationship': 'all'})

    def get_owned_games(self, steam_id):
        return self._make_api_call('IPlayerService', 'GetOwnedGames', '0001', {'steamid': steam_id, 'include_appinfo':'true'})

    def get_all_games(self):
        return self._make_api_call('ISteamApps', 'GetAppList', '0002')

    def _make_api_call(self, interface_method, method_name, version, qs=None):
        if qs is None:
            qs = {}

        qs['key'] = '3F43D315F79104DE98A177968EE11A51'
        qs['format'] = 'json'

        url = "http://api.steampowered.com/%(interface)s/%(method)s/v%(version)s/?%(query)s" % \
            {"interface": interface_method, "method": method_name, "version": version, "query": urllib.urlencode(qs)}

        f = urllib.urlopen(url)
        content = f.read()

        print "steam request => %s" % url
        return json.loads(content)