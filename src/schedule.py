from datetime import *
import random
import json

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
        str_sched = {}
        for key in o.sched.keys():
            str_sched[str(key)] = o.sched[key]
        return str_sched
    
    if isinstance(o, Game):
        return o.__dict__

#Represents a schedule
class Schedule:
    def __init__(self):
        self.sched = {}
        self.opponentList = None

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

    def getOpponentListForTeam(self,team):
        if self.opponentList == None:
            self.buildOpponentList()
        return self.opponentList[team] if team in self.opponentList else None
    
    def buildOpponentList(self):
        self.opponentList = {}
        for week in self.sched:
            for game in self.sched[week]:
                home = game.home_team
                away = game.away_team
                if home not in self.opponentList:
                    self.opponentList[home] = set()
                if away not in self.opponentList:
                    self.opponentList[away] = set()
                self.opponentList[home].add(away)
                self.opponentList[away].add(home)
        
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

# Sample on how to call methods
#nfl_schedule = generate_random_schedule(game_days, nfl_teams)
#print(json.dumps(nfl_schedule, default=json_default))
