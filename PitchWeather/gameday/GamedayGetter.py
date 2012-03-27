from urllib2 import urlopen, URLError
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import re
from Queue import Queue
from threading import Thread
from GamedayLoader import GamedayObjectLoader

BASEURL = 'http://gdx.mlb.com/components/game/mlb'
DIR_PATTERNS = ['year_', 'day_', 'month_', 'gid_']

class GamedayWalker(object):

    MAX_THREADS = 10

    def __init__(self):
        self.url_queue = Queue(maxsize=10000)
        self.gid_queue = Queue(maxsize=100)
        self.gameday_queue = Queue(maxsize=50)

    def walker(self, url, Session):
        """
        starting at the given URL walk the URL tree to find and load all of
        the games
        """
        # these find the URLs to the games
        for i in xrange(0, self.MAX_THREADS):
            url_thread = GamedayURLGetter(self.url_queue, self.gid_queue)
            url_thread.setDaemon(True)
            url_thread.start()

        # seed the queue with the starting url
        self.url_queue.put(url)

        # these download the data from the game urls and parses it into gameobjects
        for i in xrange(0, self.MAX_THREADS):
            gid_thread = GamedayXMLParser(self.gid_queue, self.gameday_queue)
            gid_thread.setDaemon(True)
            gid_thread.start()

        # these load the gameobjects into the database
        for i in xrange(0, 1):
            gameday_thread = GamedayObjectLoader(self.gameday_queue, Session)
            gameday_thread.setDaemon(True)
            gameday_thread.start()

        # these block until the queue is empty
        self.url_queue.join()
        self.gid_queue.join()
        self.gameday_queue.join()
    
class GamedayObject(object):

    def __init__(self):
        self.boxscore = ""
        self.players = ""
        self.game = ""
        self.innings = ""
        self.teams = ""
        self.runners = ""

    def isComplete(self):
        if not self.boxscore:
            print "missing boxscore"
            return False
        if not self.players:
            print "missing players"
            return False
        if not self.game:
            print "missing game"
            return False
        if not self.innings:
            print "missing innings"
            return False
        if not self.teams:
            print "missing team"
            return False
        if not self.runners:
            print "missing runners"
            return False
        # everything is present
        return True

class GamedayURLGetter(Thread):
    """
    url getter adapted from:
    http://www.ibm.com/developerworks/aix/library/au-threadingpython/
    finds the urls to all gameday games and puts them in the gid_queue
    """
    def __init__(self, url_queue, gid_queue):
        Thread.__init__(self)
        self.url_queue = url_queue
        self.gid_queue = gid_queue

    def run(self):
        """
        get all links to directories that might contain a game directory
        save all game directories to the gid_queue
        """
        while True:
            url = self.url_queue.get()
            if self._url_has_gid(url):
                self.gid_queue.put(url, block=True)
            else:
                links = self._get_gameday_links_from_url(url)
                for link in links:
                    self.url_queue.put(link, block=True)

            self.url_queue.task_done()

    def _get_gameday_links_from_url(self, url):
        response = self._get_response_from_url(url)
        links = []
        if not response:
            return None

        html = response.read()
        for link in BeautifulSoup(html).findAll("a"):
            for pattern in DIR_PATTERNS:
                if re.match(pattern, link['href']):
                    newurl = url + str(link['href'])
                    links.append(newurl)
                
        return links

    def _get_response_from_url(self, url):
        try:
            response = urlopen(url)
        except URLError:
            return False
        return(response)
        
    def _url_has_gid(self, url):
        if re.search('gid_', url):
            return True
        else:
            return False

class GamedayXMLParser(Thread):
    """
    takes a gameday url out of the gameday queue, gets it, parses it
    and loads it into the database
    """

    def __init__(self, gid_queue, gameday_queue):
        Thread.__init__(self)
        self.gid_queue = gid_queue
        self.gameday_queue = gameday_queue

    def run(self):
        while True:
            url = self.gid_queue.get()
            game = self._get_game_from_url(url)
            if game.isComplete():
                self.gameday_queue.put(game, block=True)
            self.gid_queue.task_done()
            
    def _get_response_from_url(self, url):
        try:
            response = urlopen(url)
        except URLError:
            return False
        return(response)

        
    def _get_game_from_url(self, url):
        """
        downloads and populates a gameday object with dictionaries
        """
        print "Getting game from %s." %(url)
        game = GamedayObject()
        game.url = url
        boxscore_xml = self._download_from_url(url, "boxscore.xml")
        boxscore_dict = self._make_dict_from_xml(boxscore_xml, "boxscore")
        if boxscore_dict:
            game.boxscore = self._make_dict_from_xml(boxscore_xml, "boxscore")[0]
        game_xml = self._download_from_url(url, "game.xml")
        game_dict = self._make_dict_from_xml(game_xml, "game")
        if game_dict:
            game.game = self._make_dict_from_xml(game_xml, "game")[0]
        players_xml = self._download_from_url(url, "players.xml")
        game.players = self._make_dict_from_xml(players_xml, "player")
        game.teams = self._make_dict_from_xml(game_xml, "team")
        innings_xml = self._download_from_url(url, "inning/inning_all.xml")
        game.innings = BeautifulStoneSoup(innings_xml).findAll("inning")
        game.runners = self._make_dict_from_xml(innings_xml, "runner")
        return game

    def _download_from_url(self, gameurl, filename):
        url = "/".join([gameurl, filename])
        response = self._get_response_from_url(url)
        if response:
            return response.read()
        else:
            return ""

    def _make_dict_from_xml(self, xml, string):
        stone_soup = BeautifulStoneSoup(xml)
        soup_subset = stone_soup.findAll(string)
        if soup_subset:
            xml_dictlist = [dict(x.attrs) for x in soup_subset]
            return xml_dictlist
        else:
            return None

