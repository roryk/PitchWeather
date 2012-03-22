from urllib2 import urlopen, URLError
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import re

class GamedayGetter(object):

    baseurl = 'http://gdx.mlb.com/components/game/mlb'

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
        gameurl = self._format_url(self.baseurl, year, month, day, gid)
        game = GamedayObject()
        boxscore_xml = self._download_from_url(gameurl, "boxscore.xml")
        game.boxscore = self._make_dict_from_xml(boxscore_xml, "boxscore")[0]
        game_xml = self._download_from_url(gameurl, "game.xml")
        game.game = self._make_dict_from_xml(game_xml, "game")[0]
        players_xml = self._download_from_url(gameurl, "players.xml")
        game.players = self._make_dict_from_xml(players_xml, "player")
        game.teams = self._make_dict_from_xml(game_xml, "team")
        innings_xml = self._download_from_url(gameurl, "inning/inning_all.xml")
        game.innings = BeautifulStoneSoup(innings_xml).findAll("inning")
        game.runners = self._make_dict_from_xml(innings_xml, "runner")
        return game

    def _get_links_from_response(self, response, pattern):
        links = []
        if response:
            html = response.read()
        for link in BeautifulSoup(html).findAll("a"):
            if re.match(pattern, link['href']):
                links.append(str(link['href']))
        return links
                             
    def get_day_of_gids(self, year, month, day):
        dayurl = self._format_url(self.baseurl, year, month, day)
        response = self._get_response_from_url(dayurl)
        gids = self._get_links_from_response(response, "gid_")
        return gids

    def get_month_of_days(self, year, month):
        monthurl = self._format_url(self.baseurl, year, month)
        response = self._get_response_from_url(monthurl)
        days = self._get_links_from_response(response, "day_")
        return days

    def get_year_of_months(self, year):
        yearurl = self._format_url(self.baseurl, year)
        response = self._get_response_from_url(yearurl)
        months = self._get_links_from_response(response, "month_")
        return months

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
