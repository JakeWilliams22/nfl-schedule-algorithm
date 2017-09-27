from datetime import *
import random
import json
import csv
import os.path
import numpy

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

# Converts certain objects to JSON for serialization
def json_default(o):
    if isinstance(o, Schedule):
        output = {}
        output["difficulty_score"] = o.difficulty_cost
        output["travel_score"] = o.travel_cost
        str_sched = {}
        for key in o.sched.keys():
            str_sched[str(key)] = o.sched[key]
        output["sched"] = str_sched
        return output
    
    if isinstance(o, Game):
        return o.__dict__

#Represents a schedule
class Schedule:
    def __init__(self):
        self.sched = {}
        self.difficulty_score = 0
        self.travel_score = 0

    def add_game(self, date, game):
        if date in self.sched.keys():
            self.sched[date].append(game)
        else:
            self.sched[date] = [game]

    def get_game(self, date, team):
        for game in self.sched[date]:
            if game.home_team == team or game.away_team == team:
                return game
        return None

    def calculate_cost(self):
        self.difficulty_cost = self.calc_difficulty_cost()
        self.travel_cost = self.calc_travel_cost()

        return (self.difficulty_cost + self.travel_cost) / 2.0

    # Closer to 0 is better
    def calc_travel_cost(self):
        return 0

    # Closer to 0 is better
    # Returns the score of the difficulty of the schedule
    # Calculated by using the standard deviation of the average schedule difficulty for each team
    def calc_difficulty_cost(self):
        difficulty_scores = []
        for team in nfl_teams:
            difficulty_scores.append(self.get_team_schedule_difficulty(team))
    
        arr = numpy.array(difficulty_scores)
        return numpy.std(arr, axis=0) # Closer to 0 = better

    def get_team_schedule_difficulty(self, team):
        num_games = 0
        total_difficulty = 0

        for date in self.sched.keys():
            game = self.get_game(date, team)
            if game != None:
                opponent = game.get_opposing_team(team)
                if opponent != None:
                    num_games += 1
                    total_difficulty += 0.2 * TEAM_DIFFICULTY_DICT[opponent] # Normalize to [0, 1]

        if num_games == 0: # Team doesn't exist in schedule
            return None
        else:
            return float(total_difficulty) / float(num_games)

    def __str__(self):
        string = ""
        for day in self.sched:
            string += str(day) + "\n"
            for game in self.sched[day]:
                string += "\t" + str(game) + "\n"
        return string

# Represents a game
class Game():
    possible_game_times = [13, 16, 20] # Possible hours of the day
    possible_broadcasters = ["NBC", "CBS", "FOX"]
    
    def __init__(self, home_team, away_team, game_time, broadcaster):
        self.home_team = home_team
        self.away_team = away_team
        self.game_time = game_time
        self.broadcaster = broadcaster

    def get_opposing_team(self, team):
        if self.home_team == team:
            return self.away_team
        elif self.away_team == team:
            return self.home_team
        else:
            return None

    def __str__(self):
        return self.home_team + ", " + self.away_team \
            + ", " + str(self.game_time) + ", " + self.broadcaster

# Utilities

def generate_difficulty_dict():
    team_difficulty_dict = {}

    basepath = os.path.dirname(__file__)
    filepath = os.path.abspath(os.path.join(basepath, "..", "data", "NFL.csv"))
    with open(filepath) as nfl_data:
        csv_reader = csv.reader(nfl_data)
        for row in csv_reader:
            if row[0] != "Team Name": # Skip title row
                team_name = row[0]
                team_difficulty = float(row[6])

                team_difficulty_dict[team_name] = team_difficulty

    return team_difficulty_dict

TEAM_DIFFICULTY_DICT = generate_difficulty_dict()

# Sample on how to call methods
#nfl_schedule = generate_random_schedule(game_days, nfl_teams)
#print(json.dumps(nfl_schedule, default=json_default))
