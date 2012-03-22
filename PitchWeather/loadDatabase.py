from wunderground import StadiumWeatherGetter
from gameday import GamedayGetter
from models import Stadium, Weather, meta, Game, Player, Team, AtBat, Runner, Pitch
import yaml
from BeautifulSoup import BeautifulStoneSoup

"""
connect the databse properly up
for each pitch
figure out the correct stadium from the game_pk field (i think)
connect to the id of the right stadium
find closest time to the time of the pitch (the tfs_zulu field)
look up the weather on that date in that stadium at that time
insert the weather into the db
"""

def load_stadiums(session, stadium_filename):
    f = open(stadium_filename, 'r')
    data = yaml.load(f)
    stadiums = []
    for line in data:
        stadium = Stadium()
        stadium.loadFromYaml(line)
        stadiums.append(stadium)
    session.add_all(stadiums)
    session.commit()

def load_weather(session, year):
    swg = StadiumWeatherGetter()
    for stadium in swg.getStadiums():
        yearly_weather = swg.getWeatherForYearAtStadium(stadium, year)
        for daily_weather in yearly_weather:
            weather_objects = []
            for hourly_weather in daily_weather:
                new_weather_object = Weather()
                new_weather_object.loadWeatherContainer(hourly_weather)
                weather_objects.append(new_weather_object)
            session.add_all(weather_objects)
            session.commit()            

def test_load_weather(session, year):
    swg = StadiumWeatherGetter()
    for stadium in swg.getStadiums():
        daily_weather = swg.getWeatherForDayAtStadium(stadium,
                                             2011, 7, 14)
        for hourly_weather in daily_weather:
            new_weather_object = Weather()
            new_weather_object.loadWeatherContainer(hourly_weather)
            session.add(new_weather_object)
        session.commit()
        
def test_load_gameday(session, year):
    gg = GamedayGetter()
    year = 2011
    month = 7
    day = 14
    gid = 'gid_2011_07_14_clemlb_balmlb_1/'
    z = gg.get_one_game(year, month, day, gid)
    load_game(session, z)
    load_players(session, z)
    load_teams(session, z)
    #load_runners(session, z)
    load_atbats_and_pitches(session, z)
    session.commit()

def load_game(session, gameday_object):
    game = Game()
    game.load_from_gameday_object(gameday_object)
    if not session.query(Game).filter(Game.game_pk == game.game_pk).all():
        session.add(game)

def load_players(session, gameday_object):
    new_players = []
    for player_dict in gameday_object.players:
        player = Player()
        player.load_from_player_dict(player_dict)
        if not session.query(Player).filter(Player.id == player.id).all():
            new_players.append(player)
    session.add_all(new_players)

def load_teams(session, gameday_object):
    for team_dict in gameday_object.teams:
        team = Team()
        team.load_from_team_dict(team_dict)
        if not _does_team_exist(session, team):
            session.add(team)

def load_runners(session, gameday_object):
    print gameday_object.innings
    print len(gameday_object.innings)
    #for inning in gameday_object.innings:
    #    print inning

def _does_team_exist(session, team):
    query = session.query(Team).filter(Team.code == team.code).all()
    if query:
        return True
    else:
        return False
    
def _does_atbat_exist(session, atbat):
    query = session.query(AtBat).filter(AtBat.num == atbat.num and
                                        AtBat.game_pk == atbat.game_pk).all()
    if query:
        return True
    else:
        return False

def _load_atbat(session, gameday_object, inning, atbat):
    atbat_dict = dict(atbat.attrs)
    atbat_dict['inning'] = dict(inning.attrs)['num']
    atbat_dict['game_pk'] = gameday_object.game['game_pk']
    new_atbat = AtBat()
    new_atbat.load_from_atbat_dict(atbat_dict)
    if not _does_atbat_exist(session, new_atbat):
        session.add(new_atbat)

def _load_runner(session, gameday_object, atbat, runner):
    runner_dict = dict(runner.attrs)
    runner_dict['game_pk'] = gameday_object.game['game_pk']
    runner_dict['atbatnum'] = atbat['num']
    new_runner = Runner()
    new_runner.load_from_dict(runner_dict)
    session.add(new_runner)

def _load_pitch(session, gameday_object, atbat, pitch, count):
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
    new_pitch = Pitch()
    new_pitch.load_from_dict(pitch_dict)
    session.add(new_pitch)

def load_atbats_and_pitches(session, gameday_object):
    half_strings = ["top", "bottom"]

    for inning in gameday_object.innings:
        for half_string in half_strings:
            half = inning.findAll(half_string)[0]
            for atbat in half.findAll('atbat'):
                _load_atbat(session, gameday_object, inning, atbat)
                for runner in atbat.findAll('runner'):
                    _load_runner(session, gameday_object, atbat, runner)
                count = {'balls': 0, 'strikes': 0}
                for pitch in atbat.findAll('pitch'):
                    if pitch['type'] == 'S':
                        count['strikes'] = count['strikes'] + 1
                    if pitch['type'] == 'B':
                        count['balls'] = count['balls'] + 1
                    _load_pitch(session, gameday_object, atbat, pitch, count)

    session.commit()

def link_pitches_to_weather(session):
    #### probably have to convert the dates back to datetime obejcts
    ## pseudocode for this routine
    # get iterator for pitches from db
    for pitch in session.query(Pitch):
        # for each pitch, get the stadium by getting
        # pitch -> game_pk -> stadium
        # get the date by getting
        # pitch -> game_pk -> date
        pitch_stadium = pitch.game_pk.stadium
        pitch_date = pitch.game_pk.date
        # get the hourly weather weather associated for this stadium and date
        # weather.stadium = pitch.stadium and weather.date = pitch.date

        daily_weather = session.query(Weather).\
                        filter(Weather.stadium == pitch_stadium and
                               Weather.date == pitch_date).all()
        # find the pitch time: pitch.tfs_zulu
        time_differences = []
        for weather in daily_weather:
            time_delta = abs(weather.time - pitch.tfs_zulu)
            time_differences.append(time_delta)
        # find the closest weather time: min(abs(pitch.tfs_zulu - weather.time))
        # add that weather object id to the pitch.weather column
        closest_weather = daily_weather[time_differences.index(min(time_differences))]
        pitch.weather = closest_weather.id
        session.commit()

def test_queries(session):
    pass
        

def main():
    sqlite_filename = 'data/baseball.sqlite'
    stadium_filename = 'data/ballparks.yaml'
    year = 2011
    session = meta.start(sqlite_filename)
    #load_stadiums(session, stadium_filename)
    #load_weather(session, year)
    #test_load_weather(session, year)
    #test_load_gameday(session, year)
    #link_pitches_to_weather()
    test_queries(session)

if __name__ == "__main__":
    main()
