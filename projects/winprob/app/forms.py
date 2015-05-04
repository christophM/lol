from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

class SummonerSearchForm(Form):
    region = SelectField(u'Region', choices=[('euw', 'EUW'), 
                                             ('na', 'NA'), 
                                             ('eune', 'EUNE'), 
                                             ('br', 'BR'),
                                             ('tr', 'TR'),
                                             ('ru', 'RU'),
                                             ('lan', 'LAN'),
                                             ('las', 'LAS'), 
                                             ('oce', 'OCE')
                                         ])
    summoner = StringField('Summoner Name')

