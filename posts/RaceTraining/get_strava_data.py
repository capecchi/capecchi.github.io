import plotly
from stravalib import unithelper
import numpy as np
import matplotlib.pyplot as plt
from stravalib.client import Client
import datetime
from collections import OrderedDict
import plotly.graph_objs as go
from plotly import tools


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
    dist = [unithelper.miles(r.distance).num for r in runs]
    cum = np.cumsum(dist)
    return days_before, dist, cum


def gather_training_seasons(code, matplotlib=False):
    races = OrderedDict({'TC Marathon 2014': datetime.datetime(2014, 10, 5),
                         'Madison Marathon 2014': datetime.datetime(2014, 11, 9),
                         'TC Marathon 2015': datetime.datetime(2015, 10, 4),
                         'Superior 50k 2018': datetime.datetime(2018, 5, 19),
                         'Driftless 50k 2018': datetime.datetime(2018, 9, 29),
                         'Superior 50k 2019': datetime.datetime(2019, 5, 18),
                         'Elkhorn 50m 2019': datetime.datetime(2019, 9, 3)})
    # races = OrderedDict({'Superior 50k 2019': datetime.datetime(2019, 5, 18)})
    wks_18 = datetime.timedelta(weeks=18)
    day_1 = datetime.timedelta(days=1)
    wks_1 = datetime.timedelta(weeks=1)

    ref_day = min(datetime.datetime.now(), races[list(races.keys())[-1]])
    days_to_race = datetime.timedelta(days=(races[list(races.keys())[-1]] - ref_day).days)

    if matplotlib:
        w, h = plt.figaspect(.5)
        dist_fig = plt.figure('dist', figsize=(w, h))
        cum_fig = plt.figure('cum', figsize=(w, h))
        wk_fig = plt.figure('week_previous', figsize=(w, 2 * h))
        dax = dist_fig.add_subplot(111)
        cax = cum_fig.add_subplot(111)
        wax1 = wk_fig.add_subplot(211)
        wax2 = wk_fig.add_subplot(212)

        for k, v in races.items():
            print(k)
            days_before, dist, cum = get_training_data(code, v - wks_18, v + day_1)
            wdb, wd, wc = get_training_data(code, v - days_to_race - wks_1, v - days_to_race + day_1)
            if v > datetime.datetime.today():  # read: if race day is after today, ie in the future, then solid line plot
                dax.plot(days_before, dist, 'o-', label=k)
                cax.plot(days_before, cum, 'o-', label=k)
                wax1.plot(wdb, wd, 'o-', label=k)
                wax2.plot(wdb, wc, 'o-')
            else:
                dax.plot(days_before, dist, 'o--', label=k, alpha=0.5)
                cax.plot(days_before, cum, 'o--', label=k, alpha=0.5)
                wax1.plot(wdb, wd, 'o--', label=k, alpha=0.5)
                wax2.plot(wdb, wc, 'o--', alpha=0.5)
            cax.annotate(f'{cum[-1]}', (days_before[-1], cum[-1]))
            try:
                wax2.annotate(f'{wc[-1]}', (wdb[-1], wc[-1]))
            except IndexError:
                pass

        dax.set_xlabel('Days Before Race')
        dax.set_ylabel('Distance (miles)')
        cax.set_xlabel('Days Before Race')
        cax.set_ylabel('Cumulative (miles)')
        wax1.set_ylabel('Distance (miles)')
        wax2.set_ylabel('Cumulative (miles)')
        wax2.set_xlabel('Runs over prior week')
        dax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fancybox=True)
        cax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fancybox=True)
        wax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fancybox=True)

        img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
        plt.figure('dist')
        plt.savefig(f'{img_path}rta_dist.png', transparent=True)
        print('saved dist image')
        plt.figure('cum')
        plt.savefig(f'{img_path}rta_cum.png', transparent=True)
        print('saved cum image')
        plt.figure('week_previous')
        plt.savefig(f'{img_path}rta_week.png', transparent=True)
        print('saved weekly image')
    else:
        dist_traces = []
        cum_traces = []
        wk_traces = []
        d_ann = {'x': [], 'y': []}
        # c_ann = {'x': [], 'y': []}
        # w_ann = {'x': [], 'yd': [], 'yc': []}
        colors = plotly.colors.DEFAULT_PLOTLY_COLORS
        for i, (k, v) in enumerate(races.items()):
            print(k)
            if v > datetime.datetime.today():  # read: if race day is after today, ie in the future, then solid line plot
                op = 1.
            else:
                op = 0.5
            days_before, dist, cum = get_training_data(code, v - wks_18, v + day_1)
            wdb, wd, wc = get_training_data(code, v - days_to_race - wks_1, v - days_to_race)
            # d_ann['x'].append(days_before[-1])
            # c_ann['x'].append(days_before[-1])
            # w_ann['x'].append(wdb[-1])
            # d_ann['y'].append(dist[-1])
            # c_ann['y'].append(cum[-1])
            # w_ann['yd'].append(wd[-1])
            # w_ann['yc'].append(wc[-1])
            dist_traces.append(go.Scatter(
                x=days_before,
                y=dist,
                opacity=op,
                name=k,
                mode='lines+markers'
            ))
            cum_traces.append(go.Scatter(
                x=days_before,
                y=cum,
                opacity=op,
                name=k,
                mode='lines+markers'
            ))
            wk_traces.append(go.Scatter(
                x=wdb,
                y=wd,
                yaxis='y2',
                opacity=op,
                name=k,
                mode='lines+markers',
                marker=dict(
                    color=colors[i]
                )
            ))
            wk_traces.append(go.Scatter(
                x=wdb,
                y=wc,
                opacity=op,
                name=k,
                mode='lines+markers',
                marker=dict(
                    color=colors[i]
                ),
                showlegend=False
            ))

        # append annotation traces
        dist_traces.append(go.Scatter(
            x=[t.x[-1] for t in dist_traces if len(t.x) > 0],
            y=[t.y[-1] for t in dist_traces if len(t.y) > 0],
            text=[f'{round(t.y[-1], 1)}' for t in dist_traces if len(t.y) > 0],
            mode='text',
            textposition='middle left',
            showlegend=False,
            hoverinfo='none'
        ))
        cum_traces.append(go.Scatter(
            x=[t.x[-1] for t in cum_traces if len(t.x) > 0],
            y=[t.y[-1] for t in cum_traces if len(t.y) > 0],
            text=[f'{round(t.y[-1], 1)}' for t in cum_traces if len(t.y) > 0],
            mode='text',
            textposition='middle left',
            showlegend=False,
            hoverinfo='none'
        ))
        wk_annotations = {'dx': [t.x[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y2')],
                          'dy': [t.y[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y2')],
                          'dt': [f'{round(t.y[-1], 1)}' for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y2')],
                          'cx': [t.x[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis is None)],
                          'cy': [t.y[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis is None)],
                          'ct': [f'{round(t.y[-1], 1)}' for t in wk_traces if (len(t.x) > 0 and t.yaxis is None)]}
        wk_traces.append(go.Scatter(
            x=wk_annotations['dx'],
            y=wk_annotations['dy'],
            text=wk_annotations['dt'],
            yaxis='y2',
            mode='text',
            textposition='middle left',
            showlegend=False,
            hoverinfo='none',
        ))
        wk_traces.append(go.Scatter(
            x=wk_annotations['cx'],
            y=wk_annotations['cy'],
            text=wk_annotations['ct'],
            mode='text',
            textposition='middle left',
            showlegend=False,
            hoverinfo='none',
        ))

        dlayout = go.Layout(
            xaxis=dict(
                title='Days before race'
            ),
            yaxis=dict(
                title='Distance (miles)',
                hoverformat='.2f'
            ),
        )
        clayout = go.Layout(
            # legend=dict(orientation='h'),
            xaxis=dict(
                title='Days before race'
            ),
            yaxis=dict(
                title='Cumulative (miles)'
            )
        )

        wlayout = go.Layout(
            # legend=dict(orientation='h'),
            xaxis=dict(
                title='Prior week training',
            ),
            yaxis=dict(
                title='Distance (miles)',
                domain=[0, 0.45],
            ),
            yaxis2=dict(
                title='Cumulative training distance (miles)',
                domain=[0.55, 1]
            )
        )

        dist_fig = go.Figure(data=dist_traces, layout=dlayout)
        cum_fig = go.Figure(data=cum_traces, layout=clayout)
        wk_fig = go.Figure(data=wk_traces, layout=wlayout)
        return dist_fig, cum_fig, wk_fig
