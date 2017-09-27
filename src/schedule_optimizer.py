from scipy import optimize
from .schedule import *
from .schedule_score import *

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

            games.append(Game(home_team, away_team, game_time, broadcaster))
            nfl_sched.add_game(day, Game(home_team, away_team, game_time, broadcaster))

    return nfl_sched

class ScheduleTakeStep(object):
    # Optional constructor
    #def __init__(self):
    
    # TODO: This function should generate a different schedule given a schedule
    def __call__(self, sched):
        return generate_random_schedule(game_days, nfl_teams)

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
    return optimizer_result.x.item(0)

# DEBUG
#nfl_schedule = optimize_schedule()
#print(nfl_schedule)