from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

class SummonerSearchForm(Form):
    region = SelectField(u'Region', choices=[('euw', 'Europe West'), 
                                             ('na', 'North America'), 
                                             ('eune', 'Europe Nordic & East'), 
                                             ('br', 'Brazil'),
                                             ('tr', 'Turkey'),
                                             ('ru', 'Russia'),
                                             ('lan', 'Latin America North'),
                                             ('las', 'Latin America South'), 
                                             ('oce', 'Oceania')
                                         ])
    summoner = StringField('Summoner Name')

