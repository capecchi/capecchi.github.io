import json

import plotly
import stravalib
from bottle import run, redirect, jinja2_view, request, get, post
from wtforms import Form, SubmitField, SelectMultipleField, widgets, HiddenField, StringField

from posts.RaceTraining.app_tools import *
from posts.RaceTraining.fig_tools import fig_architect

# todo: weight before race plot
# todo: add races to weight history as in my weekly mileage plot
# todo: tidy plot of splits
# todo: implement new shoe tracking system- colors? labels?


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    code = HiddenField()
    option_widget = widgets.CheckboxInput()


class MyForm(Form):
    races = get_past_races()
    races.update({'Past 18 weeks': datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)})
    race_options = [(r, r) for r in races.keys()]
    runs = MultiCheckboxField(label='Race Options', choices=race_options)
    docode = SubmitField('Run Analysis')
    # noplot = [('rdist', 'Distance vs. Weeks Before'), ('rpace', 'Pace vs. Weeks Before')]
    plot_options = [('rcumdist', 'Distance vs. Weeks Before (cumulative)'),
                    ('rcumcal', 'Calories vs. Weeks Before (cumulative)'), ('rpvd', 'Pace vs. Distance'),
                    ('rswt', 'Manual Data Analysis (sweatrate, shoe mileage, fluid/calorie intake vs mileage)'),
                    ('rcalbytype', 'Calories by Activity Type over past 18 weeks (cumulative)'),
                    ('weighthistory', 'Weight history')]
    # deprecated options: ('rwk', 'Current Week'),
    code = HiddenField()
    message = StringField(render_kw={'readonly': True})
    plots = MultiCheckboxField(choices=plot_options)


def do_prepopulate(form: MyForm, code):
    if form.runs.data is None and form.plots.data is None:
        form.runs.data = ['Past 18 weeks']
        form.plots.data = ['rswt', 'calbytype']
    form.code.data = code
    form.message = 'select races/plot options'


port = 8888
redirect_url = f'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:{port}&response_type=code&scope=activity:read_all'
form = MyForm()


@post('/')
@jinja2_view('home.html')
def submit():
    try:
        global form
        form = MyForm(request.forms)
        df, sho, races = update_data_file(form.code.data, races2analyze=form.runs.data)
        graphs, message = fig_architect(df, sho, races, plots=form.plots.data)
        # graphs, message = gather_training_seasons(form.code.data, races2analyze=form.runs.data, plots=form.plots.data)
        form.message = message
        ids = [f'graph-{i}' for i, _ in enumerate(graphs)]
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        return {'form': form, 'ids': ids, 'graphs': graphJSON}
    except stravalib.exc.Fault:
        return redirect(redirect_url)


@get('/')
@jinja2_view('home.html')
def load_in():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if 'code=' in request.url:
        for el in request.url.split('&'):
            if 'code=' in el:
                code = el.split('=')[-1]
        global form
        do_prepopulate(form, code)
        return {'form': form}
    else:
        return redirect(redirect_url)


run(host='localhost', port=port, debug=True, reloader=True)
hi = 'hello'
