import json
import logging
import datetime
import plotly
from bottle import run, redirect, jinja2_view, request, get, post
from wtforms import Form, SubmitField, SelectMultipleField, widgets, HiddenField, TextField

from posts.RaceTraining.get_strava_data import gather_training_seasons, get_past_races


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    code = HiddenField()
    option_widget = widgets.CheckboxInput()


class MyForm(Form):
    races = get_past_races()
    races.update({'Past 18 weeks': datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)})
    race_options = [(r, r) for r in races.keys()]
    runs = MultiCheckboxField(label='Race Options', choices=race_options)
    #todo: can only hit button once, validation code expires or something
    docode = SubmitField('Run Analysis')
    plot_options = [('rdist', 'Distance vs. Days Before'), ('rcum', 'Cumulative Distance vs. Days Before'),
                    ('rwk', 'Current Week'), ('rpace', 'Pace vs. Days Before'),
                    ('rcal', 'Calories (cumulative) vs. Days Before'), ('rsvd', 'Speed vs. Distance'),
                    ('rswt', 'Sweat Rate Histogram'),
                    ('calbytype', 'Calories (cumulative) by Activity Type over past 18 weeks')]
    code = HiddenField()
    message = TextField('butt')
    plots = MultiCheckboxField(choices=plot_options)


def do_prepopulate(form: MyForm, code):
    form.runs.data = ['Past 18 weeks']
    form.plots.data = ['rswt', 'calbytype']
    form.code.data = code


port = 8888
redirect_url = f'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:{port}&response_type=code&scope=activity:read_all'


@post('/')
@jinja2_view('home.html')
def submit():
    form = MyForm(request.forms)
    graphs, message = gather_training_seasons(form.code.data, races2analyze=form.runs.data, plots=form.plots.data)
    form.message = message
    ids = [f'graph-{i}' for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return {'form': form, 'ids': ids, 'graphs': graphJSON}


@get('/')
@jinja2_view('home.html')
def load_in():
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    if 'code=' in request.url:
        for el in request.url.split('&'):
            if 'code=' in el:
                code = el.split('=')[-1]
        form = MyForm()
        do_prepopulate(form, code)
        return {'form': form}
    else:
        return redirect(redirect_url)


run(host='localhost', port=port, debug=True, reloader=True)
hi = 'hello'
