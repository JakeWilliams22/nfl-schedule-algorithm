import os
from flask import Flask
from flask_cors import CORS

from src.schedule import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/generate-schedule')
def generate_schedule():
    nfl_schedule = generate_random_schedule(game_days, nfl_teams)
    return json.dumps(nfl_schedule, default=json_default)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    #TESTING ONLY! Leave commented in production
    #app.run(host='127.0.0.1', port=port)
