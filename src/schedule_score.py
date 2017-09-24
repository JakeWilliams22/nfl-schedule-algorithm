from functools import reduce
import csv
import os.path
import numpy

from .schedule import *

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


# This function generates a score for the provided schedule in [0, 1]
def score_schedule(sched):
    if sched == None:
        return 0

    scores = [travel_score(sched), \
              difficulty_score(sched)]

    # Return average of scores
    return reduce(lambda x, y: x + y, scores) / len(scores)

def travel_score(sched):
    return 0

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