from scipy import optimize
from .schedule import *
import random
import math

# Generates a random schedule adhering to the following rules:
def generate_random_schedule(game_days, teams):
    nfl_sched = Schedule()
    teams = list(nfl_teams) # List of teams to match
    
    for day in game_days:
        games = []
        random.shuffle(teams)
        for i in range(0, len(teams), 2):
            home_team = teams[i]
            away_team = teams[i + 1]
            broadcaster = random.choice(Game.possible_broadcasters)
            game_time = random.choice(Game.possible_game_times)

            games.append(Game(home_team, away_team, game_time, broadcaster, 0))
            nfl_sched.add_game(day, Game(home_team, away_team, game_time, broadcaster, 0))

    return nfl_sched

class ScheduleTakeStep(object):
    # Optional constructor
    #def __init__(self):
    
    # TODO: This function should generate a different schedule given a schedule
    def __call__(self, sched):
        sched = sched.item()
        dates = list(sched.sched.keys())
        teams = list(nfl_teams)
        
        #Randomly decide how many weeks to alter
        numWeeksToChange = math.ceil(random.random() * len(sched.sched))

        dateIndexesToChange = set()
        while len(dateIndexesToChange) < numWeeksToChange:
            dateIndexesToChange.add(math.floor(random.random() * len(sched.sched[dates[0]])))
            
        for dateIndex in dateIndexesToChange:
            date = dates[dateIndex]
            #Randomly pick two teams to swap
            team1 = teams[math.floor(random.random() * len(teams))]
            team2 = team1
            while team2 == team1: #Continue picking random numbers if we pick the same team twice
                team2 = teams[math.floor(random.random() * len(teams))]
            
            #Perform the actual swap - team 1 will now play team 2's opponent and vice versa
            swapTeams(team1, team2, date, sched)

        return sched

#Currently ignores bye weeks and any other NFL rules//TODO        
def swapTeams(team1, team2, week, sched):
    game1 = sched.get_game(week, team1)
    team1Home = game1.home_team == team1 if game1 != None else False
    game2 = sched.get_game(week, team2)
    team2Home = game2.home_team == team2 if game2 != None else False
    if game1 == game2: #If the teams are playing eachother, swap who is home/away
        temp = game1.away_team
        game1.away_team = game2.home_team
        game1.home_team = temp
    elif game1 != None and game2 != None: 
        #If team 1 is not already playing team 2's opponent at some point in the season AND
        #Team 2 is not playing team 1's opponent at some point in the season
        if swapWontViolateOpponentConstraint(game1, game2, team1Home, team2Home, team1, team2, sched):
            if team1Home: #Put team2 in to game 1
                game1.home_team = team2
                team1OldOpponent = game1.away_team
            else:
                game1.away_team = team2
                team1OldOpponent = game1.home_team
            if team2Home: #Put team1 in to game 2
                game2.home_team = team1
                team2OldOpponent = game2.away_team
            else:
                game2.away_team = team1
                team2OldOpponent = game2.home_team
            #Add the remove team one's old opponent from it's opponent list, and do the same with team 2
            team1Opponents = sched.getOpponentListForTeam(team1)
            team2Opponents = sched.getOpponentListForTeam(team2)
            team1Opponents.discard(team1OldOpponent)
            team2Opponents.discard(team2OldOpponent)
            team1Opponents.add(team2OldOpponent)
            team2Opponents.add(team1OldOpponent)
            return True
        else:
            return False
 
#If team 1 is not already playing team 2's opponent at some point in the season AND
#Team 2 is not playing team 1's opponent at some point in the season
def swapWontViolateOpponentConstraint(game1, game2, team1Home, team2Home, team1, team2, sched):
    team1Opponents = sched.getOpponentListForTeam(team1)
    team2Opponents = sched.getOpponentListForTeam(team2)
    team1Opponent = game1.away_team if team1Home else  game1.away_team
    team2Opponent = game2.away_team if team2Home else game2.away_team
    
    return team1Opponent not in team2Opponents and team2Opponent not in team1Opponents
      
    
# Simple local minimizer that returns the input
# Note: BasinHopping is a global minimizer that runs several local minimizers
# TODO: In the future, enhance this to actually locally minimize
def noop_min(fun, x0, args, **options):
    return optimize.OptimizeResult(x=x0, fun=fun(x0), success=True, nfev=1)

# This function generates a score for the provided schedule in [0, 1]
def score_schedule_cost(sched):
    if sched == None:
        return 0
    else:
        return sched.item(0).calculate_cost()

#accept_test: A function to decide whether or not to accept the step (for validating rules maybe?)
my_schedule_take_step = ScheduleTakeStep()
initial_schedule = generate_random_schedule(game_days, nfl_teams)

# Note: this function minimizes the cost (1 - score) of the schedule
def optimize_schedule():
    optimizer_result = optimize.basinhopping(score_schedule_cost, \
                                             initial_schedule, \
                                             minimizer_kwargs=dict(method=noop_min), \
                                             take_step=my_schedule_take_step)
    sched = optimizer_result.x.item(0)
    serialize_schedule(sched)
    return sched

# DEBUG
# nfl_schedule = optimize_schedule()
# print(nfl_schedule)