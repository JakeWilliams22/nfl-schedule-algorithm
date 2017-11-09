import os
import flask as Flask
from flask_cors import CORS

from src.schedule import *
from src.schedule_optimizer import *

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

# Test endpoint
@app.route('/')
def hello():
    return 'Hello World!'

"""
Get an optimized schedule
GET: Return an optimized schedule while starting with a random schedule
POST: Return an optimized schedule while starting with the provided schedule
"""
@app.route('/generate-optimized-schedule', methods=["GET", "POST"])
def generate_optimized_schedule():
    if Flask.request.method == "GET":
        nfl_schedule = optimize_schedule()

        # Serialize schedule for future access
        loaded_sched_text = load_schedule()
        loaded_sched = json_to_sched(loaded_sched_text)
        with open('data/schedule.json', 'w') as outfile:
            json.dump(nfl_schedule, outfile, default=json_default)
        
        return json.dumps(nfl_schedule, default=json_default)

    elif Flask.request.method == "POST":
        uploadedSched = Flask.request.values.get('schedule')
        nfl_schedule = optimize_schedule(json_to_sched(uploadedSched))
        print(nfl_schedule)
        # Serialize schedule for future access
        with open('data/schedule.json', 'w') as outfile:
            json.dump(nfl_schedule, outfile, default=json_default)
        return json.dumps(nfl_schedule, default=json_default)

"""
Generates a random schedule
"""
@app.route('/generate-schedule')
def generate_schedule():
    nfl_schedule = generate_random_schedule(game_days, nfl_teams)
    return json.dumps(nfl_schedule, default=json_default)

"""
Returns the most recently generated schedule without generating another schedule
"""
@app.route('/view-schedule')
def view_schedule():
  schedule = load_schedule()
  return schedule

"""
Main method starts the Flask server
"""
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)
