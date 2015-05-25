from flask import render_template, flash, redirect, request, Flask, flash, url_for
from forms import SummonerSearchForm
from flask.ext.cache import Cache

import config
app = Flask(__name__)
app.config.from_object("config")

cache = Cache(app,config={'CACHE_TYPE': 'simple'})


import sys
sys.path.append(config.lib_paths["lol"])
sys.path.append(config.lib_paths["wpmodel"])

import winprob
import events
import model


wp =  model.WinProbabilityPipeline()
wp.from_file(config.prediction_model_path)



@app.route('/')
@app.route('/index')
def index():
    form = SummonerSearchForm()
    return render_template('index.html', 
                           form=form)
@app.route("/about")
def about():
    form = SummonerSearchForm()
    return render_template("about.html", form=form)

@cache.memoize(timeout=36000)
def get_summoner_id_cached(region, summoner_name):
    return winprob.get_summoner_id(region, summoner_name)

@cache.memoize(timeout=1800)
def get_last_match_cached(region, summonerId):
    return winprob.get_last_match_id(region, summonerId)

@app.route('/search', methods=('GET', 'POST'))
def search():
    form = SummonerSearchForm()
    if form.validate_on_submit():
        summoner_name = form.summoner.data.lower()
        region = form.region.data
        try: 
            summonerId = get_summoner_id_cached(region, summoner_name)
        except: 
            flash("Could not find summoner with name %s in region %s"  % (summoner_name, region))
            return redirect(url_for("index"))
        try:
            matchId = get_last_match_cached(region, summonerId)
        except:
            flash("Could not find any ranked matches for summoner %s in region %s" % (summoner_name, region))
            return redirect(url_for("index"))

        return redirect(url_for("match", region=region, summonerName=summoner_name,  matchId=matchId))

    else:
        return render_template('index.html', 
                               form=form)




@app.route("/match/<region>/<summonerName>/<matchId>")
@cache.cached(timeout=60)
def match(region, summonerName, matchId):
    form = SummonerSearchForm()
    last_match = winprob.get_last_match(region=region, matchId=matchId, summonerName=summonerName)    
    last_match.set_winprob(wp.predict(last_match.match, last_match.teamId))
    winprob_line = last_match.get_winprob()
    top_events = events.summarize_important_events(last_match)
    player = last_match.get_participant_summary()
    return render_template('match.html', 
                               form=form, 
                               match=last_match, 
                               events=top_events,
                               player=player,
                               summonerName=summonerName)


app.run(debug=True)    
