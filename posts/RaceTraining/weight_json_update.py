"""
This routine is automatically triggered by update_weight_fig.yml when change is detected in weights.json
Weight is no longer recorded after a run, rather by Alexa prompt: "Alexa tell weight logger I weigh __ pounds"
"""

import json
import plotly.graph_objs as go
import numpy as np
import datetime
# from app_tools import get_past_races
day_1 = datetime.timedelta(days=1)
now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

direc, run_locally = '', False
if run_locally:
    direc = 'C:/Users/willi/PycharmProjects/capecchi.github.io/'
jweight = f'{direc}posts/RaceTraining/weights.json'
jraces = f'{direc}posts/RaceTraining/races.json'
races2analyze = ['Superior 50k 2018', 'Driftless 50k 2018', 'Superior 50k 2019', 'Batona (virtual) 33M 2020',
                 'Dirty German (virtual) 50k 2020', 'Stone Mill 50M 2020', 'Queens Half 2022',
                 'Shawangunk Ridge 30M 2022', 'Black Forest 100k 2022', 'Frosty Fat Sass 6H 2023',
                 'Naked Bavarian 40M 2023', 'Zion 100M 2023', 'Hyner 50k 2024', 'Worlds End 100k 2024',
                 'Teanaway 100M 2024', 'Black Forest 100k 2024 (DNF)', 'Grand Canyon R3 2025', 'Superior 100M 2025',
                 'TC Marathon 2025', 'Past 18 weeks']
# races = get_past_races(racekeys=races2analyze)
img_path = f'{direc}/images/posts/'


def update_weighthist_fig():
    fmt = '%Y-%m-%dT%H:%M:%S.%f'
    with open(jweight, 'r') as file:
        data = json.load(file)
        weight_date_arr = [datetime.datetime.strptime(d['timestamp'].split('.')[0], fmt) for d in data]
        weight_arr = [d['weight'] for d in data]
    with open(jraces, 'r') as file:
        races = json.load(file)
    for k in races.keys():
        races[k] = datetime.datetime.strptime(races[k], fmt)

    # remove races before we have weight history data
    [races.pop(k) for k in list(races.keys()) if races[k] < min(weight_date_arr)]
    # remove races in the future
    [races.pop(k) for k in list(races.keys()) if races[k] > now]
    if 'Past 18 weeks' in races.keys():
        races.pop('Past 18 weeks')
    race_dates = [races[k] for k in races.keys()]

    # x-arrays are decimal days since start of weight data
    xweights = [(da - min(weight_date_arr)).total_seconds() / 60 / 60 / 24. for da in weight_date_arr]
    xraces = [(races[k] - min(weight_date_arr)).total_seconds() / 60 / 60 / 24. for k in races.keys()]
    yraces = np.interp(xraces, xweights, weight_arr)  # interpolated weights on race days

    dsec = (weight_date_arr[-1] - weight_date_arr[0]).total_seconds()  # seconds between first/last weight value
    ndays = int(dsec / 60 / 60 / 24)  # convert elapsed sec to elapsed num of days
    xx = np.linspace(0, dsec, num=ndays)  # seconds array
    yy = np.interp(xx / 60 / 60 / 24., xweights, weight_arr)
    xd = [min(weight_date_arr) + datetime.timedelta(seconds=x) for x in xx]

    nday_avg = 21
    avg_x = xd[nday_avg - 1:]
    avg_y = np.zeros_like(avg_x)
    for i in np.arange(len(avg_x)):  # ascending weights for forward date array
        avg_y[i] = np.average(yy[i:i + nday_avg], weights=np.arange(1, nday_avg + 1))

    traces = [go.Scatter(x=avg_x, y=avg_y, mode='lines', name=f'{nday_avg} day WMA'),
              go.Scatter(x=weight_date_arr, y=weight_arr, mode='markers', showlegend=False),
              go.Scatter(x=race_dates, y=yraces, mode='markers', showlegend=False,
                         marker=dict(color='red', line=dict(width=1)))]
    playout = go.Layout(xaxis=dict(title='Date'), yaxis=dict(title='Weight (lb)'),
                        legend=dict(x=1, y=1, bgcolor='rgba(0,0,0,0)', xanchor='right', orientation='h'))
    weight_fig = go.Figure(data=traces, layout=playout)
    for i in range(len(race_dates)):
        weight_fig.add_annotation(text=list(races.keys())[i], x=race_dates[i], y=yraces[i], textangle=-45)
    # weight_fig.show()
    weight_fig.write_html(f'{img_path}rta_weighthist.html')
    print('saved weight history image')


if __name__ == '__main__':
    update_weighthist_fig()
