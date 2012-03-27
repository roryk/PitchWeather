from wunderground import StadiumWeatherGetter
from models import Stadium, Weather, meta, Game, Player, Team, AtBat, Runner, Pitch
import yaml
from dateutil import parser
from gameday.GamedayGetter import GamedayWalker

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
        
def link_pitches_to_weather(session):
    #### probably have to convert the dates back to datetime obejcts
    ## pseudocode for this routine
    # get iterator for pitches from db
    for pitch in session.query(Pitch):
        # for each pitch, get the stadium by getting
        # pitch -> game_pk -> stadium
        # get the date by getting
        # pitch -> game_pk -> date
        pitch_stadium_id = pitch.game.stadium_id
        pitch_date = pitch.game.date
        # get the hourly weather weather associated for this stadium and date
        # weather.stadium = pitch.stadium and weather.date = pitch.date

        daily_weather = session.query(Weather).\
                        filter(Weather.stadium_id == pitch_stadium_id and
                               Weather.date == pitch_date).all()
        # find the pitch time: pitch.tfs_zulu
        time_differences = []
        for weather in daily_weather:
            pitch_time = parser.parse(pitch.tfs_zulu)
            time_delta = abs(weather.time - pitch_time)
            time_differences.append(time_delta)
        # find the closest weather time: min(abs(pitch.tfs_zulu - weather.time))
        # add that weather object id to the pitch.weather column
        closest_weather = daily_weather[time_differences.index(min(time_differences))]
        pitch.weather_id = closest_weather.id
        session.commit()

def test_queries(session):
    for weather in session.query(Weather):
        print weather

def main():
    sqlite_filename = 'data/baseball.sqlite'
    stadium_filename = 'data/ballparks.yaml'
    year = 2011
    Session = meta.start(sqlite_filename)
    load_stadiums(Session, stadium_filename)
    x = GamedayWalker()
    #x.walker('http://gd2.mlb.com/components/game/mlb/year_2011/',
    #         Session)
#    x.walker('http://gd2.mlb.com/components/game/mlb/year_2011/month_07/day_08/gid_2011_07_08_balmlb_bosmlb_1/', Session)
#    x.walker('http://gd2.mlb.com/components/game/mlb/year_2011/month_07/day_08/', Session)
#    x.walker('http://gd2.mlb.com/components/game/mlb/year_2011/month_07/', Session)
    x.walker('http://gd2.mlb.com/components/game/mlb/year_2011/', Session)
    #load_weather(Session(), year)
    #test_load_weather(session, year)
    #link_pitches_to_weather(Session())
    #test_queries(session)

if __name__ == "__main__":
    main()
