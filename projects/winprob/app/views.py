from flask import render_template, flash, redirect, request, Flask
from forms import SummonerSearchForm

import sys
sys.path.append('/home/kuriso/lol/lib/')
sys.path.append("/home/kuriso/lol/projects/winprob/wpmodel/")

import winprob
import events
import model
from constants import PREDICTION_MODEL_PATH

wp =  model.WinProbabilityPipeline()
wp.from_file(PREDICTION_MODEL_PATH)

app = Flask(__name__)
app.config.from_object("config")


@app.route('/')
@app.route('/index')
def index():
    form = SummonerSearchForm()
    return render_template('index.html', 
                           form=form)


@app.route('/match', methods=('GET', 'POST'))
def match():
    image = None
    form = SummonerSearchForm()
    if form.validate_on_submit():
        summoner_name = form.summoner.data.lower()
        match = winprob.get_last_match(region=form.region.data, summonerName=summoner_name)
        match.set_winprob(wp.predict(match.match, match.teamId))
        winprob_line = match.get_winprob()
        top_events = events.summarize_important_events(match)
        player = match.get_participant_summary()
        return render_template('match.html', 
                               form=form, 
                               match=match, 
                               events=top_events,
                               player=player,
                               summonerName=form.summoner.data)
    else:
        return render_template('index.html', 
                               form=form)


