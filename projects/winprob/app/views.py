from flask import render_template, flash, redirect, request
from app import app
from .forms import SummonerSearchForm
import sys
sys.path.append("/Users/chris/Projects/lol/projects/winprob/wpmodel/")
import winprob
import visualize
import events
import model


PREDICTION_MODEL_PATH = "/Users/chris/Projects/lol/projects/winprob/model-serialized/wp-pipeline.pkl"
wp =  model.WinProbabilityPipeline()
wp.from_file(PREDICTION_MODEL_PATH)

## TODO
# - create WinProbabilityPipeline when initializing the app (__ini__.py ?)
# - add additional information about the mach
# - 


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
        img_data = visualize.get_winprobability_string_png(match.timestamps, match.winprob)
        top_events = events.summarize_important_events(match)
        player = match.get_participant_summary()
        return render_template('match.html', 
                               form=form, 
                               img_data=img_data, 
                               match=match, 
                               events=top_events,
                               player=player,
                               summonerName=form.summoner.data)
    else:
        return render_template('index.html', 
                               form=form)


