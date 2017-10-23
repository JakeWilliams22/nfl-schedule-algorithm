import os
import flask as Flask
from flask_cors import CORS

from src.schedule import *
from src.schedule_optimizer import *

app = Flask.Flask(__name__, static_url_path='')
CORS(app)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/generate-optimized-schedule', methods=["GET", "POST"])
def generate_optimized_schedule():
    if Flask.request.method == "GET":
        nfl_schedule = optimize_schedule()
        loaded_sched_text = load_schedule()
        loaded_sched = json_to_sched(loaded_sched_text)
        with open('data/schedule.json', 'w') as outfile:
          json.dump(nfl_schedule, outfile, default=json_default)
        return json.dumps(nfl_schedule, default=json_default)
    elif Flask.request.method == "POST":
        uploadedSched = Flask.request.values.get('schedule')
        print(json_to_sched(uploadedSched))
        nfl_schedule = optimize_schedule(json_to_sched(uploadedSched))
        with open('data/schedule.json', 'w') as outfile:
            json.dump(nfl_schedule, outfile, default=json_default)
        print(nfl_schedule)
        return json.dumps(nfl_schedule, default=json_default)
        
@app.route('/generate-schedule')
def generate_schedule():
    nfl_schedule = generate_random_schedule(game_days, nfl_teams)
    return json.dumps(nfl_schedule, default=json_default)

@app.route('/view-schedule')
def view_schedule():
  schedule = load_schedule()
  return schedule
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)
