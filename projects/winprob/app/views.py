from flask import render_template, flash, redirect, request
from app import app
from .forms import SummonerSearchForm
import sys
sys.path.append("/Users/chris/Projects/lol/projects/winprob/wpmodel/")
import winprob


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
        img_data = winprob.get_last_game_winprob(form.region.data, form.summoner.data, console=False)
    return render_template('match.html', 
                           form=form, 
                           img_data=img_data)


