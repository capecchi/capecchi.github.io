import datetime

from bottle import run, jinja2_view, get, post, request
from wtforms import Form, SubmitField, SelectMultipleField, widgets
from posts.RaceTraining.get_strava_data import get_past_races


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MyForm(Form):
    races = get_past_races()
    races.update({'Past 18 weeks': datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)})
    race_options = [(r, r) for r in races.keys()]
    runs = MultiCheckboxField(label='Race Options', choices=race_options)
    docode = SubmitField('Run Analysis')
    plot_options = [('rdist', 'Distance vs. Days Before'), ('rcum', 'Cumulative Distance vs. Days Before'),
                    ('rwk', 'Current Week'), ('rpace', 'Pace vs. Days Before'),
                    ('rcal', 'Calories (cumulative) vs. Days Before'), ('rsvd', 'Speed vs. Distance'),
                    ('rswt', 'Sweat Rate Histogram'),
                    ('calbytype', 'Calories (cumulative) by Activity Type over past 18 weeks')]
    plots = MultiCheckboxField(choices=plot_options)


port = 8000


def do_prepopulate(form: MyForm):
    form.runs.data = ['Past 18 weeks']
    form.plots.data = ['rswt', 'calbytype']


@post('/')
@jinja2_view('test_app.html')
def submit():
    form = MyForm(request.forms)
    return {'form': form}


@get('/')
@jinja2_view('test_app.html')
def home():
    form = MyForm()
    do_prepopulate(form)
    return {'form': form}
    # '''
    # <form action="/" method="post">
    #     check: <input name="cheeeck" type="text" />
    #     <input value="do go now" type="submit" />
    # '''


run(host='localhost', port=port, debug=True, reloader=True)
# hi = 'hello'
