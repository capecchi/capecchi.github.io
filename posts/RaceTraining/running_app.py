import json
import plotly
from bottle import route, run, template, request, redirect, view, jinja2_view
from wtforms import Form, SubmitField
from posts.RaceTraining.get_strava_data import gather_training_seasons

class MyForm(Form):
    hi = SubmitField('Get Strava Data')


redirect_url = 'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:8080&response_type=code&scope=activity:read_all'


@route('/')
@jinja2_view('test.html')
def home():
    if 'code=' in request.url:
        for el in request.url.split('&'):
            if 'code=' in el:
                code = el.split('=')[-1]
        dfig, cfig, wfig = gather_training_seasons(code)
        graphs = [dfig, cfig, wfig]
        ids = [f'graph-{i}' for i, _ in enumerate(graphs)]
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        return {'form': MyForm(), 'ids': ids, 'graphs': graphJSON}
    else:
        return redirect(redirect_url)


run(host='localhost', port=8080, debug=True, reloader=True)



