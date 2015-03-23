from flask import render_template, flash, redirect, request
from app import app
from .forms import SummonerSearchForm
import sys
sys.path.append("/Users/chris/Projects/lol/projects/winprob/wpmodel/")
import winprob


@app.route('/')
@app.route('/index', methods=('GET', 'POST'))
def index():
    image = None
    form = SummonerSearchForm()
    if form.validate_on_submit():
        image = winprob.get_last_game_winprob(form.region.data, form.summoner.data)
    return render_template('index.html', 
                           form=form, 
                           image=image)

@app.route('/success')
def success():
    winprob.get_last_game_winprob
