from bottle import route, run, template, request, redirect
from wtforms import Form, SubmitField
from posts.RaceTraining.get_strava_data import gather_training_seasons


class MyForm(Form):
    hi = SubmitField('Get Strava Data')


redirect_url = 'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:8080&response_type=code&scope=activity:read_all'


@route('/')
def home():
    if 'code=' in request.url:
        for el in request.url.split('&'):
            if 'code=' in el:
                code = el.split('=')[-1]
        gather_training_seasons(code)
        return template('<b>Hello {{w}}!</b>', w='World')
    else:
        return redirect(redirect_url)


run(host='localhost', port=8080, debug=True, reloader=True)



