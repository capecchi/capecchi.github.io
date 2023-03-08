import datetime

import matplotlib.pyplot as plt
import numpy as np

from posts.RaceTraining.app_tools import get_training_data_file, get_past_races
import pandas as pd


def datetime_troubleshooting():
    fn = get_training_data_file()
    df = pd.read_excel(fn, sheet_name='data', engine='openpyxl')
    weightdf = df.dropna(axis=0, how='any', subset=['Date', 'End Weight (lb)'])
    date_arr = list(weightdf['Date'].values)
    races = get_past_races()
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for rd in [races[k] for k in races.keys()]:
        print((rd-now).days)
        print(rd)
        print(rd-min(date_arr))
        print(min(date_arr))


def compare_temp_methods(client, runids, temps):
    # TEMPORARY routine to compare temp recording methods- delete later
    from meteostat import Hourly, Point
    for runid in runids:
        act = client.get_activity(runid)
        pt = Point(act.start_latlng.lat, act.start_latlng.lon, np.mean([act.elev_low, act.elev_high]))
        dat = Hourly(pt, act.start_date_local, act.start_date_local + act.elapsed_time)
        dat = dat.fetch()
        a = 1


def temp_history_test():
    from meteostat import Hourly, Point
    lon, lat, alt = -77.56772441661252, 41.462899053757894, 476.94935091933206  # bft center (alt in [m])
    strt = datetime.datetime(2022, 10, 2, 0, 0, 0, 0)  # midnight
    end = datetime.datetime(2022, 10, 2, 17, 45, 0, 0)  # 5:45p
    bft = Point(lat, lon, alt)
    dat = Hourly(bft, strt, end)
    dat = dat.fetch()
    plt.plot(dat['temp'])
    plt.show()


def color_test():
    import plotly
    import plotly.graph_objs as go
    traces = []
    # rb = plotly.colors.sequential.RdBu_r
    rb = plotly.colors.colorscale_to_colors(plotly.colors.PLOTLY_SCALES['RdBu'])
    randn = np.random.normal(3., 1., 1000)
    dx = 6. / len(rb)
    for i, col in enumerate(rb):
        traces.append(
            go.Histogram(x=randn[np.where((randn >= i * dx) & (randn < (i + 1) * dx))],
                         xbins=dict(start=0, end=6.0, size=0.2),
                         marker_color=rb[i]))
    fig = go.Figure(data=traces, layout=go.Layout(barmode='stack'))
    fig.show()


def rect_on_histogram_test():
    import plotly.graph_objs as go
    x = [5, 7, 10, 3, 4]
    y = ['a', 'b', 'c', 'd', 'e']
    traces = [go.Bar(x=x, y=y, orientation='h', showlegend=False)]
    fig = go.Figure(data=traces)
    barwidth = 0.8
    fig.add_shape(type='rect', x0=6, y0=1 - barwidth / 2., x1=7, y1=1 + barwidth / 2.,
                  line=dict(width=2, color='black'))
    fig.show()


if __name__ == '__main__':
    # temp_history_test()
    # rect_on_histogram_test()
    # color_test()
    datetime_troubleshooting()
    a = 1
