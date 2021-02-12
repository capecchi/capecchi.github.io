import logging

from bottle import route, run, redirect, jinja2_view, request
from stravalib import Client

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
        client_id = 34049
        client_secret = '2265a983040000b3b865a0fc333f41cd701dcb5f'
        client = Client()
        client.authorization_url(34049, 'https://localhost:8080', scope='activity:read_all')
        token_response = client.exchange_code_for_token(client_id, client_secret, code)
        a=1
    else:
        return redirect(redirect_url)


run(host='localhost', port=8080, debug=True, reloader=True)
hi = 'hello'
