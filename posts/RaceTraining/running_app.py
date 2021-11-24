import json
import logging

import plotly
from bottle import route, run, redirect, jinja2_view, request
from wtforms import Form, SubmitField, SelectMultipleField, widgets, HiddenField

from posts.RaceTraining.get_strava_data import gather_training_seasons, get_past_races


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    code = HiddenField()
    option_widget = widgets.CheckboxInput()


class MyForm(Form):
    string_of_files = ['one\r\ntwo\r\nthree\r\n']
    list_of_files = string_of_files[0].split()
    files = [(x, x) for x in list_of_files]
    abc = SelectMultipleField(label='lbl', choices=files)
    hi = SubmitField('Run Analysis')
    # max_effort = SubmitField('Max Effort Analysis')


port = 8888
redirect_url = f'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:{port}&response_type=code&scope=activity:read_all'


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


run(host='localhost', port=port, debug=True, reloader=True)
hi = 'hello'
