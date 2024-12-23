import json

import plotly
import stravalib
from bottle import run, redirect, jinja2_view, request, get, post
from wtforms import Form, SubmitField, SelectMultipleField, widgets, HiddenField, StringField
from posts.RaceTraining.app_tools import *
from posts.RaceTraining.fig_tools import fig_architect

# todo: Chunk data on max effort curves into years instead of races
# todo: FIX markdown(s). deactivate one of them, make sure all plots work, and update fit method description
# todo: allow for split mileage between shoes (Zion = 50Zion + 50Smaug)
# todo: implement new shoe tracking system- colors? labels?
# todo: for calories, maybe add more inputs since I always use tailwind, gus, etc, put entry fields for those for auto-calculation
# NOTE: pip install chardet -- I think this is what caused the issues with running the app

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
    plot_options = [('rcumdist', 'Distance vs. Weeks Before (cumulative)'),
                    ('rpvd', 'Pace vs. Distance'),
                    ('rswt', 'Manual Data Analysis (sweatrate, shoe mileage, fluid/calorie intake vs mileage)'),
                    ('rcalbytype', 'Calories by Activity Type over past 18 weeks (cumulative)'),
                    ('weighthistory', 'Weight history')]
    code = HiddenField()
    message = StringField(render_kw={'readonly': True})
    plots = MultiCheckboxField(choices=plot_options)


def do_prepopulate(form: MyForm, code):
    if form.runs.data is None and form.plots.data is None:
        form.runs.data = ['Superior 50k 2018', 'Driftless 50k 2018', 'Superior 50k 2019', 'Batona (virtual) 33M 2020',
                          'Dirty German (virtual) 50k 2020', 'Stone Mill 50M 2020', 'Queens Half 2022',
                          'Shawangunk Ridge 30M 2022', 'Black Forest 100k 2022', 'Frosty Fat Sass 6H 2023',
                          'Naked Bavarian 40M 2023', 'Zion 100M 2023', 'Hyner 50k 2024', 'Worlds End 100k 2024',
                          'Teanaway 100M 2024', 'Black Forest 100k 2024', 'Past 18 weeks']
        form.plots.data = ['rcumdist', 'rpvd', 'rswt', 'calbytype', 'weighthistory']
    form.code.data = code
    form.message = 'select races/plot options'


port = 8888
redirect_url = f'http://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:{port}&response_type=code&scope=activity:read_all'
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
