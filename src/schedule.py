from datetime import *
import random

# This file contains code responsible for generating schedules

# NFL Team Names
afc_teams_east =  ["Buffalo Bills",
                   "Miami Dolphins",
                   "New England Patriots",
                   "New York Jets"]

afc_teams_north = ["Baltimore Ravens",
                   "Cincinnati Bengals",
                   "Cleveland Browns",
                   "Pittsburgh Steelers"]

afc_teams_south = ["Houston Texans",
                   "Indianapolis Colts",
                   "Jacksonville Jaguars",
                   "Tennessee Titans"]

afc_teams_west =  ["Denver Broncos",
                   "Kansas City Chiefs",
                   "Oakland Raiders",
                   "Los Angeles Chargers"]

nfc_teams_east =  ["Dallas Cowboys",
                   "New York Giants",
                   "Philadelphia Eagles",
                   "Washington Redskins"]

nfc_teams_north = ["Chicago Bears",
                   "Detroit Lions",
                   "Green Bay Packers",
                   "Minnesota Vikings"]

nfc_teams_south = ["Atlanta Falcons",
                   "Carolina Panthers",
                   "New Orleans Saints",
                   "Tampa Bay Buccaneers"]

nfc_teams_west =  ["Arizona Cardinals",
                   "Los Angeles Rams",
                   "San Francisco 49ers",
                   "Seattle Seahawks"]

afc_teams = afc_teams_east + afc_teams_north + afc_teams_south + afc_teams_west
nfc_teams = nfc_teams_east + nfc_teams_north + nfc_teams_south + nfc_teams_west

nfl_teams = afc_teams + nfc_teams

def generate_game_days(start_date):
    game_days = []
    for i in range(16):
        game_days.append(start_date)
        start_date += timedelta(weeks=1)
    return game_days
        
game_days = generate_game_days(datetime(2018, 10, 6))

# Represents a game
class game:
    possible_game_times = [13, 16, 20] # Possible hours of the day
    possible_broadcasters = ["NBC", "CBS", "FOX"]
    
    def __init__(self, home_team, away_team, datetime, broadcaster):
        self.home_team = home_team
        self.away_team = away_team
        self.datetime = datetime
        self.broadcaster = broadcaster

    def __str__(self):
        return self.home_team + ", " + self.away_team \
            + ", " + str(self.datetime) + ", " + self.broadcaster

# Generates a random schedule adhering to the following rules:
def generate_random_schedule(game_days, teams):
    schedule = {}
    teams = list(nfl_teams) # List of teams to match
    
    for day in game_days:
        games = []
        random.shuffle(teams)
        for i in range(0, len(teams), 2):
            home_team = teams[i]
            away_team = teams[i + 1]
            broadcaster = random.choice(game.possible_broadcasters)

            game_time = random.choice(game.possible_game_times)
            game_datetime = day
            game_datetime += timedelta(hours=game_time)

            games.append(game(home_team, away_team, game_datetime, broadcaster))

        schedule[day] = games

    return schedule

# For debugging
def print_schedule(schedule):
    for day in schedule:
        print day
        for game in schedule[day]:
            print "\t" + str(game)

schedule = generate_random_schedule(game_days, nfl_teams)
print_schedule(schedule)
