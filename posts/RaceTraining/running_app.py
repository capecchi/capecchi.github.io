import json
import plotly
from bottle import route, run, template, redirect, view, jinja2_view, request
from wtforms import Form, SubmitField, HiddenField, StringField
from posts.RaceTraining.get_strava_data import gather_training_seasons
import logging


class MyForm(Form):
    hi = SubmitField('Update Strava Data')
    # txt = StringField(default='mystring')
    # code = HiddenField()
    # training_analysis = SubmitField('Training Analysis')
    # max_effort = SubmitField('Max Effort Analysis')


redirect_url = 'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:8080&response_type=code&scope=activity:read_all'


@route('/')
@jinja2_view('home.html')
def home():

    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    if 'code=' in request.url:
        for el in request.url.split('&'):
            if 'code=' in el:
                code = el.split('=')[-1]
        graphs = gather_training_seasons(code)
        ids = [f'graph-{i}' for i, _ in enumerate(graphs)]
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        return {'form': MyForm(), 'ids': ids, 'graphs': graphJSON}
    else:
        return redirect(redirect_url)


run(host='localhost', port=8080, debug=True, reloader=True)
