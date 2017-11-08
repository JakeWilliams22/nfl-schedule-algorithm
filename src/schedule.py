from datetime import *
import random
import json
from collections import namedtuple
import csv
import os.path
import numpy
import pandas as pd
# from schedule_optimizer.py import *

#from .schedule_score import travel_score

# This file contains code responsible for generating schedules

""" Static Data """

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
    num_weeks = 16
    game_days = []
    for i in range(num_weeks):
        game_days.append(start_date)
        start_date += timedelta(weeks=1)
    return game_days
        
game_days = generate_game_days(datetime(2018, 10, 6))

""" JSON Serializer """

# Converts certain objects to JSON for serialization
def json_default(o):
    if isinstance(o, Schedule):
        output = {}
        output["difficulty_score"] = o.difficulty_cost
        output["travel_score"] = o.travel_cost
        output["rule_score"] = o.rule_cost

        # Change sched array to have string keys for JSON compatibility
        str_sched = {}
        for key in o.sched.keys():
            str_sched[str(key)] = o.sched[key]
        output["sched"] = str_sched

        return output
    
    if isinstance(o, Game):
        return o.__dict__

        
""" Schedule """
class Schedule:

    # Constructor for loading from JSON
    def __init__(self, sched = None, difficulty_score = None, travel_score = None, rule_score = None):
        if sched is None:
            self.sched = {}
        else:
            self.sched = sched

        if difficulty_score is None:
            self.difficulty_score = 0
        else:
            self.difficulty_score = difficulty_score

        if travel_score is None:
            self.travel_score = 0
        else:
            self.travel_score = travel_score

        if rule_score is None:
            self.rule_score = 0
        
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

    global getOpponentListForTeam

    def getOpponentListForTeam(self,team):
        if self.opponentList == None:
            self.buildOpponentList()
        return self.opponentList[team] if team in self.opponentList else None

    global getDivisionForTeam

    def getDivisionForTeam(self,team):
        if team in afc_teams_east:
            return "AFC East"
        elif team in afc_teams_west:
            return "AFC West"
        elif team in afc_teams_north:
            return "AFC North"
        elif team in afc_teams_south:
            return "AFC South"
        elif team in nfc_teams_east:
            return "NFC East"
        elif team in nfc_teams_west:
            return "NFC West"
        elif team in nfc_teams_north:
            return "NFC North"
        elif team in nfc_teams_south:
            return "NFC South"

    global getConferenceForTeam

    def getConferenceForTeam(self, team):
        if team in nfc_teams:
            return "NFC"
        else:
            return "AFC"
    
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

    """ Cost functions for schedule """

    def calculate_cost(self):
        self.difficulty_cost = self.calc_difficulty_cost()
        self.travel_cost = self.calc_travel_cost()
        self.rule_cost = self.calc_rule_cost()

        # Weight the score to make rules most important
        return (self.difficulty_cost * 0.2 + self.travel_cost * 0.2 + self.rule_cost * 0.6)

    #####################################
    # Rule Cost

    def calc_rule_cost(self):
        if self == None:
            return 1

        counter = 0
        data = nfl_data
        for entry in data['Team Name']:
            x = localDivisionRule(self, entry)
            y = foreignDivisionRule(self, entry)
            z = interconferenceDivisionRule(self, entry)
            if x == 1 and y == 1 and z == 1:
                counter = counter + 1
        if counter == 32:
            return 1
        else:
            return 0

    #####################################
    # Travel Cost

    # Closer to 0 is better
    def calc_travel_cost(self):
        if self == None:
            return 0
        data = nfl_data
        travelTotals = {}
    
        for entry in data['Team Name']:
            travelTotals[entry] = 0
      
        for week in self.sched:
            for game in self.sched[week]:
                td = travelDistance(data, game.home_team, game.away_team)
                travelTotals[game.away_team] += td
    
        totalsList = travelTotals.values()
        totalsList = [x / (2830 * 16) for x in totalsList] #5423 is Max # of km between any two stadiums - Miami and Seattle

        return numpy.std(totalsList, axis = 0)

    #######################################
    # Difficulty Cost

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

""" Game """
class Game():
    possible_game_times = [13, 16, 20] # Possible hours of the day
    possible_broadcasters = ["NBC", "CBS", "FOX"]
    
    def __init__(self, home_team, away_team, game_time, broadcaster, approved):
        self.home_team = home_team
        self.away_team = away_team
        self.game_time = game_time
        self.broadcaster = broadcaster
        self.approved = approved # 0 - not set, 1 = approved, 2 = declined

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


#Checks if team plays each of the other 3 teams in its division twice, 1 home and 1 away
def localDivisionRule(self, team):
    teamSchedule = getOpponentListForTeam(self,team)
    teamDivision = getDivisionForTeam(self, team)
    counter = 0
    testing = list(teamSchedule)[0]
    for i in range(0,len(list(teamSchedule))):
        oppDivision = getDivisionForTeam(self,list(teamSchedule)[i])
        if teamDivision == oppDivision:
            counter = counter + 1
    if counter == 3:
        return 1
    else:
        return 0

""" Helper functions for calculating rule cost of schedule """

#Checks if team plays all 4 teams in a different division within the same conference, 2 home and 2 away
def foreignDivisionRule(self, team):
    teamSchedule = getOpponentListForTeam(self,team)
    teamDivision = getDivisionForTeam(self, team)
    testing = list(teamSchedule)[0]
    if teamDivision == "AFC East":
        foreignDivision = random.choice([afc_teams_south, afc_teams_north, afc_teams_west])
    elif teamDivision == "AFC South":
        foreignDivision = random.choice([afc_teams_east, afc_teams_north, afc_teams_west])
    elif teamDivision == "AFC North":
        foreignDivision = random.choice([afc_teams_east, afc_teams_south, afc_teams_west])
    elif teamDivision == "AFC West":
        foreignDivision = random.choice([afc_teams_east, afc_teams_south, afc_teams_north])
    elif teamDivision == "NFC East":
        foreignDivision = random.choice([nfc_teams_south, nfc_teams_north, nfc_teams_west])
    elif teamDivision == "NFC South":
        foreignDivision = random.choice([nfc_teams_east, nfc_teams_north, nfc_teams_west])
    elif teamDivision == "NFC North":
        foreignDivision = random.choice([nfc_teams_east, nfc_teams_south, nfc_teams_west])
    elif teamDivision == "NFC West":
        foreignDivision = random.choice([nfc_teams_east, nfc_teams_south, nfc_teams_north])
    counter = 0
    for team in foreignDivision:
        if team in teamSchedule:
            counter = counter + 1
    if counter == 4:
        return 1
    else:
        return 0

#Checks if team plays all 4 teams in a division from the other conference, 2 home and 2 away
def interconferenceDivisionRule(self, team):
    teamSchedule = getOpponentListForTeam(self,team)
    teamConference = getConferenceForTeam(self, team)
    if teamConference == "AFC":
        interconferenceDivision = random.choice([nfc_teams_south, nfc_teams_north, nfc_teams_west, nfc_teams_east])
    else:
        interconferenceDivision = random.choice([afc_teams_south, afc_teams_north, afc_teams_west, afc_teams_east])
    counter = 0
    for team in interconferenceDivision:
        if team in teamSchedule:
            counter = counter + 1
    if counter == 4:
        return 1 
    else:
        return 0


""" Utilities """

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

nfl_data = pd.read_csv('data/NFL.csv')

#Calculates the distance between two teams' stadiums in km
#Consider saving the results in a dict to save computation time (500 possible pairings)
def readStadiumDistances(fileName):
    stadiumDistances = pd.read_csv(fileName)
    stadiumDistanceDict = {}
    for i, row in stadiumDistances.iterrows():
        teamTuple = (row['Team1'], row['Team2'])
        stadiumDistanceDict[teamTuple] = row['Dist']
    return stadiumDistanceDict
 
stadiumDistances = readStadiumDistances('data/stadiumDistances.csv') 
 
def travelDistance(data, team1, team2):
    teamTuple = (team1, team2)
    return stadiumDistances[teamTuple]

""" Functions to serialize and load schedule """

def serialize_schedule(sched):
    with open('data/json', 'w') as sched_file:
        sched_file.write(json.dumps(sched, default=json_default))

def load_schedule():
    with open('data/json', 'r') as sched_file:
        data = sched_file.read()
    return data

def json_to_sched(json_sched):
    x = json.loads(json_sched)
    sched = Schedule(**x)

    # Need to convert the string key schedule into a datetime key schedule
    sched_map = {}
    for date_str, games in sched.sched.items():
        date_key = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        sched_map[date_key] = []
        for game_map in games:
            game = Game(**game_map)
            sched_map[date_key].append(game)

    sched.sched = sched_map # Replace with the properly formatted sched
    return sched

# Sample on how to call methods
#nfl_schedule = generate_random_schedule(game_days, nfl_teams)
#print(json.dumps(nfl_schedule, default=json_default))