from bottle import run, jinja2_view, get, post, request
from wtforms import Form, SubmitField, SelectMultipleField, widgets, StringField, HiddenField
from posts.RaceTraining.get_strava_data import get_past_races

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MyForm(Form):
    races = get_past_races()
    race_options = [(r, r) for r in races.keys()]
    runs = MultiCheckboxField(choices=race_options)
    docode = SubmitField('Run Analysis')


port = 8000


@post('/')
@jinja2_view('home.html')
def submit():
    form = MyForm(request.forms)
    return {'form': form}


@get('/')
@jinja2_view('home.html')
def home():
    form = MyForm()
    return {'form': form}
    # '''
    # <form action="/" method="post">
    #     check: <input name="cheeeck" type="text" />
    #     <input value="do go now" type="submit" />
    # '''


run(host='localhost', port=port, debug=True, reloader=True)
# hi = 'hello'
