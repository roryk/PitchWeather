from urllib2 import urlopen, URLError
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import re

class GamedayGetter(object):

    baseurl = 'http://gdx.mlb.com/components/game/mlb'
    dir_patterns = ['year_', 'day_', 'month_', 'gid_']
    gameday_objects = []

    def _format_url(self, baseurl, year=None, month=None, day=None, gid=None):
        url = baseurl
        if year:
            url = "/".join([url, "year_" + str(year)])
        if month:
            url = "/".join([url, "month_" + str(month).zfill(2)])
        if day:
            url = "/".join([url, "day_" + str(day).zfill(2)])
        if gid:
            url = "/".join([url, gid])
        return url

    def _make_dict_from_xml(self, xml, string):
        stone_soup = BeautifulStoneSoup(xml)
        soup_subset = stone_soup.findAll(string)
        if soup_subset:
            xml_dictlist = [dict(x.attrs) for x in soup_subset]
            return xml_dictlist
        else:
            return None

    def get_one_game(self, year, month, day, gid):
        """
        get a single gameday object from the specified year, month, day and
        gid
        """
        gameurl = self._format_url(self.baseurl, year, month, day, gid)
        game = self._get_game_from_url(gameurl)
        return game

    def walker(self, url):
        """
        get all gameday objects starting at url and recursing through the
        directory tree.
        stores the gameday objects in gameday_objects
        """
        if self._url_has_gid(url):
            game = self._get_game_from_url(url)
            self.gameday_objects.append(game)
        else:
            links = self._get_gameday_links_from_url(url)
            for link in links:
                self.walker(link)

    def _get_game_from_url(self, url):
        print "Getting game from %s." %(url)
        game = GamedayObject()
        boxscore_xml = self._download_from_url(url, "boxscore.xml")
        game.boxscore = self._make_dict_from_xml(boxscore_xml, "boxscore")[0]
        game_xml = self._download_from_url(url, "game.xml")
        game.game = self._make_dict_from_xml(game_xml, "game")[0]
        players_xml = self._download_from_url(url, "players.xml")
        game.players = self._make_dict_from_xml(players_xml, "player")
        game.teams = self._make_dict_from_xml(game_xml, "team")
        innings_xml = self._download_from_url(url, "inning/inning_all.xml")
        game.innings = BeautifulStoneSoup(innings_xml).findAll("inning")
        game.runners = self._make_dict_from_xml(innings_xml, "runner")
        return game

    def _get_gameday_links_from_url(self, url):
        response = self._get_response_from_url(url)
        links = []
        if not response:
            return None

        html = response.read()
        for link in BeautifulSoup(html).findAll("a"):
            for pattern in self.dir_patterns:
                if re.match(pattern, link['href']):
                    newurl = url + str(link['href'])
                    links.append(newurl)
                    break
                
        return links

    def _url_has_gid(self, url):
        if re.search('gid_', url):
            return True
        else:
            return False

    def _get_links_from_response(self, response, pattern):
        links = []
        if not response:
            return None
        
        html = response.read()
        for link in BeautifulSoup(html).findAll("a"):
            if re.match(pattern, link['href']):
                links.append(str(link['href']))
        return links

    def _download_from_url(self, gameurl, filename):
        url = "/".join([gameurl, filename])
        response = self._get_response_from_url(url)
        if response:
            return response.read()
        else:
            return False
        
    def _get_response_from_url(self, url):
        try:
            response = urlopen(url)
        except URLError:
            return False
        return(response)
    

class GamedayObject(object):

    def __init__(self):
        self.boxscore = ""
        self.players = ""
        self.game = ""
        self.innings = ""
        self.team = ""
        self.runners = ""

    def isComplete(self):
        if not self.boxscore:
            return False
        if not self.players:
            return False
        if not self.game:
            return False
        if not self.innings:
            return False
        if not self.team:
            return False
        if not self.runners:
            return False
        # everything is present
        return True
