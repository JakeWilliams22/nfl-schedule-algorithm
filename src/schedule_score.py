from functools import reduce
import csv
import os.path
import numpy
import math
import pandas as pd

from .schedule import *

# Utilities

#Calculates the distance between two teams' stadiums in km
#Consider saving the results in a dict to save computation time (500 possible pairings)
def travelDistance(data, team1, team2):
    team1Lat = math.radians(data[data['Team Name'] == team1]['Latt'])
    team2Lat = math.radians(data[data['Team Name'] == team2]['Latt'])
    team1Long = math.radians(data[data['Team Name'] == team1]['Long'])
    team2Long = math.radians(data[data['Team Name'] == team2]['Long'])
    dlon = team2Long - team1Long
    dlat = team2Lat - team1Lat
    a = ((math.sin(dlat/2)) * (math.sin(dlat/2))) + math.cos(team1Lat) * math.cos(team2Lat) * ((math.sin(dlon/2)) * (math.sin(dlon/2)))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist = 6373 * c #approximate radius of earth
    if (dist > 5423):
      print(data[data['Team Name'] == team1]['Latt'])
      print(data[data['Team Name'] == team2]['Latt'])
      print(data[data['Team Name'] == team1]['Long'])
      print(data[data['Team Name'] == team2]['Long'])
      print(team1)
      print(team2)
      print(dist)
      print("\n")
    return(dist)
    
    
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


# This function generates a score for the provided schedule in [0, 1]
def score_schedule(sched):
    if sched == None:
        return 0

    scores = [travel_score(sched), \
              difficulty_score(sched)]

    # Return average of scores
    return reduce(lambda x, y: x + y, scores) / len(scores)

def travel_score(sched):
    #TODO: Return a normalized score that is the standard deviation of the travel distances for each team
    if sched == None:
      return 0;
    data = pd.read_csv('data/NFL.csv')
    travelTotals = {}
    
    for entry in data['Team Name']:
      travelTotals[entry] = 0
      
    for week in sched.sched:
      for game in sched.sched[week]:
        td = travelDistance(data, game.home_team, game.away_team)
        travelTotals[game.away_team] += td
    
    totalsList = travelTotals.values()
    totalsList = [x / (2830 * 16) for x in totalsList] #5423 is Max # of km between any two stadiums - Miami and Seattle

    return numpy.std(totalsList, axis = 0)
    
# Returns the score of the difficulty of the schedule
# Calculated by using the standard deviation of the average schedule difficulty for each team
def difficulty_score(sched):
    difficulty_scores = []
    for team in nfl_teams:
        difficulty_scores.append(get_team_schedule_difficulty(sched, team))
    
    arr = numpy.array(difficulty_scores)
    return 1 - numpy.std(arr, axis=0) # Closer to 0 = better

def get_team_schedule_difficulty(sched, team):
    num_games = 0
    total_difficulty = 0

    for date in sched.sched.keys():
        game = sched.get_game(date, team)
        if game != None:
            opponent = game.get_opposing_team(team)
            if opponent != None:
                num_games += 1
                total_difficulty += 0.2 * TEAM_DIFFICULTY_DICT[opponent] # Normalize to [0, 1]

    if num_games == 0: # Team doesn't exist in schedule
        return None
    else:
        return float(total_difficulty) / float(num_games)