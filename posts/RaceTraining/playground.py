import datetime

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from posts.RaceTraining.app_tools import get_training_data_file, get_past_races
import pandas as pd
from plotly.offline import iplot


def check_elapsed_time_data():
    fn = get_training_data_file()
    sho = pd.read_excel(fn, sheet_name='shoes', engine='openpyxl')
    df = pd.read_excel(fn, sheet_name='data', engine='openpyxl', index_col='runid')  # use runid as index
    runs = df[(df['Type'] == 'Run')]
    dist = runs['Dist (mi)'].values
    elaps = runs['Elapsed Time (sec)'].values
    elaps_hr = elaps / 60. / 60.
    plt.plot(elaps_hr, dist, 'o')
    plt.xlabel('hrs')
    plt.ylabel('mi')
    plt.show()


def data_toggle2():
    from plotly.subplots import make_subplots
    fig4 = make_subplots(rows=1, cols=2)

    x = list(range(1, 6))
    y2 = [4] * 5
    y1 = [6] * 5
    fig4.add_trace(go.Scatter(x=x, y=y1, line_color='blue'), 1, 1)
    fig4.add_trace(go.Scatter(x=x, y=y2, line_color='red'), 1, 2)
    fig4.update_layout(width=700, height=500,
                       yaxis_range=[0, 10],
                       yaxis2_range=[0, 10]);

    fig4.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        args=[{'y': [y1, y2],
                               'line_color': ['blue', 'red']}],
                        label="A",
                        method="restyle"
                    ),
                    dict(
                        args=[{'y': [y2, y1],
                               'line_color': ['red', 'blue']}],
                        label="B",
                        method="restyle"
                    )],
                showactive=True,
                x=-0.18,
                xanchor="left",
                y=1,
                yanchor="top"
            )
        ]
    )
    fig4.show()


def my_data_toggle():
    x = np.linspace(1, 10)
    y1 = 0.5 * x
    y2 = x
    y1p = y1 ** 2
    y2p = y2 ** 2
    traces = []

    hovertext1 = [f'hi there']
    hover2 = ['hi']
    hovertemp = '%{text}'
    traces.append(go.Scatter(x=x, y=y1, hovertemplate=hovertemp, text=hovertext1, mode='lines+markers'))
    traces.append(go.Scatter(x=x, y=y2, hovertemplate=hovertemp, text=hover2, mode='lines+markers'))
    butt1 = dict(method="restyle",
                 args=[{'y': [y1, y2]}],
                 label="Initial data")
    butt2 = dict(method="restyle",
                 args=[{'y': [y1p, y2p]}],
                 label='data squared')
    lay = go.Layout(xaxis=dict(title='Weeks before race'),
                    yaxis=dict(title='Distance (cumulative miles)'), legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)'),
                    updatemenus=[dict(active=0, buttons=[butt1, butt2])])
    myfig = go.Figure(data=traces, layout=lay)
    myfig.show()


def data_toggle():
    # init_notebook_mode(connected=True)
    x = [1, 2, 3, 4, 5]
    y = [0.1, 0.2, 0.3, 0.4]

    surf_z = np.array([[1001, 1002, 1001, 1000, 1004],  # (4,5)
                       [1002, 1001, 1004, 1002, 1003],
                       [1003, 1000, 1001, 1001, 1004],
                       [1000, 1004, 1000, 1002, 999]])

    matter_r = [[0.0, '#2f0f3d'],
                [0.1, '#4f1552'],
                [0.2, '#72195f'],
                [0.3, '#931f63'],
                [0.4, '#b32e5e'],
                [0.5, '#cf4456'],
                [0.6, '#e26152'],
                [0.7, '#ee845d'],
                [0.8, '#f5a672'],
                [0.9, '#faca8f'],
                [1.0, '#fdedb0']]

    surf = go.Surface(x=x, y=y, z=surf_z, colorscale='Viridis', colorbar_thickness=25)
    button1 = dict(method="restyle",
                   args=[{'z': [surf_z],
                          "colorscale": ['Viridis']}],  # it works with simple 'Viridis', not only ['Viridis']
                   label="Initial data & colorscale")
    button2 = dict(method="restyle",
                   args=[{'z': [surf_z[:3, :3]],
                          "colorscale": [matter_r]}],
                   # with a custom colorscale it doesn't work setting simply, matter_r,
                   # it is MANDATORY  [matter_r]
                   label="Changed data & colorscale")

    fig3 = go.Figure(surf)
    fig3.update_layout(width=800,
                       height=600,
                       updatemenus=[dict(active=0,
                                         buttons=[button1, button2])
                                    ])
    fig3.show()


def datetime_troubleshooting():
    fn = get_training_data_file()
    df = pd.read_excel(fn, sheet_name='data', engine='openpyxl')
    df = df.sort_values(by=['Date'])  # put in chronological order
    weightdf = df.dropna(axis=0, how='any', subset=['Date', 'End Weight (lb)'])
    date_arr = list(weightdf['Date'].values)
    endw_arr = list(weightdf['End Weight (lb)'].values)

    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today = now + datetime.timedelta(days=1)
    days_before = [(pd.Timestamp(val) - now).days for val in date_arr]

    # intx = np.linspace(min(days_before), 0, endpoint=True)
    cs = CubicSpline(days_before, endw_arr)
    xx = np.linspace(min(days_before), 0, endpoint=True)
    dxx = [today - pd.Timedelta(days=abs(xx[i])) for i in np.arange(len(xx))]
    yy = cs(xx)

    avw, minw, maxw = np.mean(endw_arr), min(endw_arr), max(endw_arr)
    xann = [rd for rd in [races[k] for k in races.keys()]]
    intx2 = [(rd - today).days for rd in [races[k] for k in races.keys()]]  # days before today for each race
    yann = cs(intx2)

    inty = np.interp(intx, days_before, endw_arr)
    intd = [now - pd.Timedelta(days=abs(intx[i])) for i in np.arange(len(intx))]

    intx2 = [(rd - today).days for rd in [races[k] for k in races.keys()]]  # days before today for each race
    yann = np.interp(intx2, days_before, endw_arr)  # interpolated weights on race days
    a = 1


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
    # datetime_troubleshooting()
    # data_toggle2()
    my_data_toggle()
    # check_elapsed_time_data()
    a = 1
