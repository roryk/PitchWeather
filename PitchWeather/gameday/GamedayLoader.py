from PitchWeather.models import Game, Player, Team, AtBat, Pitch, Runner
from threading import Thread
from sqlalchemy.exc import IntegrityError

class GamedayObjectLoader(Thread):

    def __init__(self, gameday_queue, session):
        Thread.__init__(self)
        self.session = session
        self.gameday_queue = gameday_queue

    def run(self):
        while True:
            gameday_object = self.gameday_queue.get()
            self._load_gameday_object_into_db(gameday_object)
            self.gameday_queue.task_done()

    def _load_gameday_object_into_db(self, gameday_object):
        print "Loading %s into the DB." %(gameday_object.url)
        self._load_game(gameday_object)
        print "finished loading game. %s" %(gameday_object.url)
        self._load_players(gameday_object)
        print "finished loading players. %s" %(gameday_object.url)
        self._load_teams(gameday_object)
        print "finished loading teams. %s" %(gameday_object.url)
        self._load_atbats_and_pitches(gameday_object)
        print "Finished loading %s into the DB." %(gameday_object.url)

    def _load_game(self, gameday_object):
        game = Game()
        game.load_from_gameday_object(gameday_object)
        self._add_to_db(game)

    def _does_game_exist(self, game):
        query = self.session.query(Game).filter(Game.game_pk == game.game_pk).all()
        if query:
            return True
        else:
            return False

    def _load_players(self, gameday_object):
        for player_dict in gameday_object.players:
            player = Player()
            player.load_from_player_dict(player_dict)
            self._add_to_db(player)

    def _does_player_exist(self, player):
        query = self.session.query(Player).filter(Player.id == player.id).all()
        if query:
            return True
        else:
            return False

    def _load_teams(self, gameday_object):
        for team_dict in gameday_object.teams:
            team = Team()
            team.load_from_team_dict(team_dict)
            self._add_to_db(team)

    def _add_to_db(self, item):
        try:
            self.session.add(item)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def _add_all_to_db(self, items):
        try:
            self.session.add_all(items)
            self.session.commit()
        except IntegrityError:
            print "Didn't load a list of things due to one error."
            self.session.rollback()
        
    def _does_team_exist(self, team):
        query = self.session.query(Team).filter(Team.code == team.code).all()
        if query:
            return True
        else:
            return False

    def _load_runner(self, gameday_object, atbat, runner):
        runner_dict = dict(runner.attrs)
        runner_dict['game_pk'] = gameday_object.game['game_pk']
        runner_dict['atbatnum'] = atbat['num']
        runner = Runner()
        runner.load_from_dict(runner_dict)
        #if not self._does_runner_exist(runner):
         #   self.session.add(runner)
         #   self.session.commit()
        self._add_to_db(runner)

    def _does_runner_exist(self, runner):
        query = self.session.query(Runner).filter(Runner.runner_pk ==
                                                  runner.runner_pk).all()
        if query:
            return True
        else:
            return False
        
    def _load_atbat(self, gameday_object, inning, atbat):
        atbat_dict = dict(atbat.attrs)
        atbat_dict['inning'] = dict(inning.attrs)['num']
        atbat_dict['game_pk'] = gameday_object.game['game_pk']
        atbat = AtBat()
        atbat.load_from_atbat_dict(atbat_dict)
        #if not self._does_atbat_exist(atbat):
        #    self.session.add(atbat)
        #    self.session.commit()
        self._add_to_db(atbat)

    def _does_atbat_exist(self, atbat):
        query = self.session.query(AtBat).filter(AtBat.num == atbat.num and
                                                 AtBat.game_pk == atbat.game_pk).all()
        if query:
            return True
        else:
            return False

    def _load_pitch(self, gameday_object, atbat, pitch, count):
        pitch_dict = dict(pitch.attrs)
        atbat_dict = dict(atbat.attrs)
        pitch_dict['on_1b'] = None
        pitch_dict['on_2b'] = None
        pitch_dict['on_3b'] = None
        pitch_dict['balls'] = count['balls']
        pitch_dict['strikes'] = count['strikes']
        pitch_dict['game_pk'] = gameday_object.game['game_pk']
        pitch_dict['batter'] = atbat_dict['batter']
        pitch_dict['pitcher'] = atbat_dict['pitcher']
        pitch_dict['atbatnum'] = atbat_dict['num']
        runners = pitch.findAll('runner')
        if runners:
            for runner in runners:
                if runner['start'] == '1B':
                    pitch_dict['on_1b'] = runner['id']
                if runner['start'] == '2B':
                    pitch_dict['on_2b'] = runner['id']
                if runner['start'] == '3B':
                    pitch_dict['on_3b'] = runner['id']
        pitch = Pitch()

        if pitch.is_pitch_dict_complete(pitch_dict):
            pitch.load_from_dict(pitch_dict)
            #self._add_to_db(pitch)
            return(pitch)
        else:
            return None
    
    def _does_pitch_exist(self, pitch):
        query = self.session.query(Pitch).filter(Pitch.id == pitch.id and
                                                 Pitch.game_pk == pitch.game_pk).all()
        if query:
            return True
        else:
            return False

    def _load_atbats_and_pitches(self, gameday_object):
        # these denote which half of an inning we are in
        half_strings = ["top", "bottom"]
        for inning in gameday_object.innings:
            for half_string in half_strings:
                half = inning.findAll(half_string)
                if not half:
                    continue
                half = half[0]
                for atbat in half.findAll('atbat'):
                    pitches = []
                    self._load_atbat(gameday_object, inning, atbat)
                    for runner in atbat.findAll('runner'):
                        self._load_runner(gameday_object, atbat, runner)
                    count = {'balls': 0, 'strikes': 0}
                    for pitch in atbat.findAll('pitch'):
                        if pitch['type'] == 'S':
                            count['strikes'] = count['strikes'] + 1
                        if pitch['type'] == 'B':
                            count['balls'] = count['balls'] + 1
                        new_pitch = self._load_pitch(gameday_object,
                                                     atbat, pitch, count)
                        if new_pitch:
                            pitches.append(new_pitch)
                    self._add_all_to_db(pitches)
