import logging
import numpy as np

from bottle import route, run, redirect, jinja2_view, request
from stravalib import Client

port = 8080
redirect_url = f'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:{port}&response_type=code&scope=activity:read_all'
fp = 'C:/Users/Owner/Desktop/strava_info.npz'

@route('/')
@jinja2_view('home.html')
def home():
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    if 'code=' in request.url:
        for el in request.url.split('&'):
            if 'code=' in el:
                code = el.split('=')[-1]
        ff = np.load(fp)
        client_id = int(ff['id'])
        client_secret = str(ff['secret'])
        client = Client()
        client.authorization_url(34049, f'https://localhost:{port}', scope='activity:read_all')
        token_response = client.exchange_code_for_token(client_id, client_secret, code)
        a = 1
    else:
        return redirect(redirect_url)


run(host='localhost', port=port, debug=True, reloader=True)
hi = 'hello'
