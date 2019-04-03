from stravalib import unithelper
import numpy as np
import matplotlib.pyplot as plt
from stravalib.client import Client
import datetime
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.io as pio


def get_training_data(code, after=datetime.date.today() - datetime.timedelta(days=7), before=datetime.date.today()):
    race_day = before - datetime.timedelta(days=1)
    client_id = 34049
    client_secret = '2265a983040000b3b865a0fc333f41cd701dcb5f'

    client = Client()
    client.authorization_url(34049, 'http://localhost:8080', scope='activity:read_all')
    token_response = client.exchange_code_for_token(client_id, client_secret, code)
    client.access_token = token_response['access_token']
    client.refresh_token = token_response['refresh_token']

    activities = client.get_activities(after=after, before=before)
    activities = list(activities)
    runs = [act for act in activities[::-1] if act.type == 'Run']  # reverse order so they're chronological
    days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
    dist = [unithelper.miles(r.distance) for r in runs]
    cum = np.cumsum(dist)
    return days_before, dist, cum


def gather_training_seasons(code):
    races = {'TC Marathon 2014': datetime.datetime(2014, 10, 5),
             'Madison Marathon 2014': datetime.datetime(2014, 11, 9),
             'TC Marathon 2015': datetime.datetime(2015, 10, 4),
             'Superior 50k 2018': datetime.datetime(2018, 5, 19),
             'Driftless 50k 2018': datetime.datetime(2018, 9, 29),
             'Superior 50k 2019': datetime.datetime(2019, 5, 18)}
    wks_18 = datetime.timedelta(weeks=18)
    day_1 = datetime.timedelta(days=1)

    # dist_traces = []
    # cum_traces = []
    # last_week_traces = []
    # for k, v in races.items():
    #     days_before, dist, cum = get_training_data(code, v - wks_18, v + day_1)
    #     dist_traces.append(go.Scatter(
    #         x=days_before,
    #         y=dist,
    #         name=k,
    #     ))
    #     cum_traces.append(go.Scatter(
    #         x=days_before,
    #         y=cum,
    #         name=k,
    #     ))
    # layout = go.Layout(showlegend=True)
    # dist_fig = go.Figure(data=dist_traces, layout=layout)
    # cum_fig = go.Figure(data=cum_traces, layout=layout)
    #
    # img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
    # pio.write_image(dist_fig, f'{img_path}rta_dist.png')
    # pio.write_image(cum_fig, f'{img_path}rta_cum.png')

    w, h = plt.figaspect(.5)
    dist_fig = plt.figure('dist', figsize=(w, h))
    cum_fig = plt.figure('cum', figsize=(w, h))
    dax = dist_fig.add_subplot(111)
    cax = cum_fig.add_subplot(111)

    for k, v in races.items():
        days_before, dist, cum = get_training_data(code, v - wks_18, v + day_1)
        if k == list(races.keys())[-1]:
            dax.plot(days_before, dist, 'o-', label=k)
            cax.plot(days_before, cum, 'o-', label=k)
        else:
            dax.plot(days_before, dist, 'o--', label=k, alpha=0.5)
            cax.plot(days_before, cum, 'o--', label=k, alpha=0.5)

    dax.set_xlabel('Days Before Race')
    dax.set_ylabel('Distance (miles)')
    cax.set_xlabel('Days Before Race')
    cax.set_ylabel('Cumulative (miles)')
    dax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fancybox=True)
    cax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fancybox=True)

    img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
    plt.figure('dist')
    plt.savefig(f'{img_path}rta_dist.png', transparent=True)
    plt.figure('cum')
    plt.savefig(f'{img_path}rta_cum.png', transparent=True)

