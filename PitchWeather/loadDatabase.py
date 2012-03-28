from wunderground import StadiumWeatherGetter
from models import Stadium, Weather, meta, Pitch, Game
import yaml
import datetime
from dateutil import parser
from gameday.GamedayGetter import GamedayWalker
from sqlalchemy.exc import IntegrityError
import sys
from argparse import ArgumentParser

def load_stadiums(session, stadium_filename):
    f = open(stadium_filename, 'r')
    data = yaml.load(f)
    for line in data:
        stadium = Stadium()
        stadium.loadFromYaml(line)
        try:
            session.add(stadium)
            session.commit()
        except IntegrityError:
            session.rollback()

def load_weather(session, year):
    swg = StadiumWeatherGetter()
    for stadium in swg.getStadiums():
        yearly_weather = swg.getWeatherForYearAtStadium(stadium, year)
        for daily_weather in yearly_weather:
            for hourly_weather in daily_weather:
                new_weather_object = Weather()
                new_weather_object.loadWeatherContainer(hourly_weather)
                try:
                    session.add(new_weather_object)
                    session.commit()
                except IntegrityError:
                    session.rollback()

def link_pitches_to_weather(session):
    """
    populate the pitch.weather field with weather data from
    the airport nearest to the stadium
    """
    sys.stdout.write("Linking weather to pitches")
    for game in meta.page_query(session.query(Game)):
        sys.stdout.write(".")
        sys.stdout.flush()

        game_pitches = session.query(Pitch).filter(
            Pitch.game_pk == game.game_pk).all()
        # load the weather for the day of the game and the days surrounding
        # it incase the game goes into the next day
        game_weather = session.query(Weather).filter(
            Weather.date == game.date).filter(
            Weather.stadium_id == game.stadium_id).all()
        game_weather = game_weather + session.query(Weather).filter(
            Weather.date == game.date + datetime.timedelta(days=1)).filter(
            Weather.stadium_id == game.stadium_id).all()
        game_weather = game_weather + session.query(Weather).filter(
            Weather.date == game.date - datetime.timedelta(days=1)).filter(
            Weather.stadium_id == game.stadium_id).all()

        for pitch in game_pitches:
            # for each pitch, get the stadium by getting
            # pitch -> game_pk -> stadium
            # get the date by getting
            # pitch -> game_pk -> date
            # get the hourly weather weather associated for this stadium and date
            # weather.stadium = pitch.stadium and weather.date = pitch.date

            time_differences = []
            pitch_time = parser.parse(pitch.tfs_zulu)
            for weather in game_weather:
                time_delta = abs(weather.time - pitch_time)
                time_differences.append(time_delta)

            # find the closest weather time: min(abs(pitch.tfs_zulu -
            # weather.time))
            # add that weather object id to the pitch.weather column
            # if for some reason we didint find any, skip this part
            if(time_differences):
                closest_weather = game_weather[
                    time_differences.index(min(time_differences))]
                pitch.weather_id = closest_weather.id
            #else:
                #print "Skipping %s due to no weather data." %(str(pitch))
    session.commit()

def main():
    parser = ArgumentParser()
    parser.add_argument('year', type=int,
                        help='year to download')
    args = parser.parse_args()
    sqlite_filename = 'data/baseball.sqlite'
    stadium_filename = 'data/ballparks.yaml'
    Session = meta.start(sqlite_filename)
    load_stadiums(Session, stadium_filename)
    x = GamedayWalker()
    x.walk_year(args.year, Session)
    load_weather(Session(), args.year)
    link_pitches_to_weather(Session())

if __name__ == "__main__":
    main()
