import plotly
from stravalib import unithelper
import numpy as np
import matplotlib.pyplot as plt
from stravalib.client import Client
import datetime
from collections import OrderedDict
import plotly.graph_objs as go
import stravalib.exc


def get_client(code):
    client_id = 34049
    client_secret = '2265a983040000b3b865a0fc333f41cd701dcb5f'

    client = Client()
    client.authorization_url(34049, 'http://localhost:8080', scope='activity:read_all')
    token_response = client.exchange_code_for_token(client_id, client_secret, code)
    client.access_token = token_response['access_token']
    client.refresh_token = token_response['refresh_token']
    return client


def get_training_data(client, after=datetime.date.today() - datetime.timedelta(days=7), before=datetime.date.today()):
    race_day = before - datetime.timedelta(days=1)

    activities = client.get_activities(after=after, before=before)
    try:
        activities = list(activities)
        runs = [act for act in activities[::-1] if act.type == 'Run']  # reverse order so they're chronological
        days_before = [(r.start_date_local.date() - race_day.date()).days for r in runs]
        dist = [unithelper.miles(r.distance).num for r in runs]
        cum = np.cumsum(dist)
        pace = [60. / unithelper.miles_per_hour(r.average_speed).num for r in runs]  # min/mile
        return days_before, dist, cum, pace
    except stravalib.exc.Fault:
        return None, None, None, None


def gather_training_seasons(code, matplotlib=False):
    races = OrderedDict({'TC Marathon 2014': datetime.datetime(2014, 10, 5),
                         'Madison Marathon 2014': datetime.datetime(2014, 11, 9),
                         'TC Marathon 2015': datetime.datetime(2015, 10, 4),
                         'Superior 50k 2018': datetime.datetime(2018, 5, 19),
                         'Driftless 50k 2018': datetime.datetime(2018, 9, 29),
                         'Superior 50k 2019': datetime.datetime(2019, 5, 18),
                         'Dirty German 50k': datetime.datetime(2020, 5, 9)})
    # 'Shawangunk Ridge 50M': datetime.datetime(2020, 9, 12)})
    # races = OrderedDict({'Superior 50k 2019': datetime.datetime(2019, 5, 18),
    #                      'Dirty German 50k': datetime.datetime(2020, 5, 9)})
    wks_18 = datetime.timedelta(weeks=18)
    day_1 = datetime.timedelta(days=1)
    wks_1 = datetime.timedelta(weeks=1)

    ref_day = min(datetime.datetime.now(), races[list(races.keys())[-1]])
    days_to_race = datetime.timedelta(days=(races[list(races.keys())[-1]] - ref_day).days)
    client = get_client(code)

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
            days_before, dist, cum, pace = get_training_data(client, v - wks_18, v + day_1)
            wdb, wd, wc, wp = get_training_data(client, v - days_to_race - wks_1, v - days_to_race + day_1)
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
        pace_traces = []
        wk_traces = []
        pc_v_dist_traces = []
        colors = plotly.colors.DEFAULT_PLOTLY_COLORS
        for i, (k, v) in enumerate(races.items()):
            print(k)
            if v > datetime.datetime.today():  # read: if race day is after today, ie in the future, then solid line plot
                width = 3
            else:
                width = 2
            op = (i + 1.) / len(races.items())
            days_before, dist, cum, pace = get_training_data(client, v - wks_18, v + day_1)
            wdb, wd, wc, wp = get_training_data(client, v - days_to_race - wks_1, v - days_to_race)
            pc_v_dist_traces.append(go.Scatter(x=dist, y=pace, mode='markers', line=dict(width=width), name=k))
            dist_traces.append(go.Scatter(
                x=days_before,
                y=dist,
                opacity=op,
                name=k,
                mode='lines+markers',
                line=dict(
                    width=width)
            ))
            cum_traces.append(go.Scatter(
                x=days_before,
                y=cum,
                opacity=op,
                name=k,
                mode='lines+markers',
                line=dict(
                    width=width)
            ))
            pace_traces.append(go.Scatter(
                x=days_before,
                y=pace,
                opacity=op,
                name=k,
                mode='lines+markers',
                line=dict(width=width),
                hovertemplate='pace: %{y:.2f}<br>dist:%{text}',
                text=['{:.2f}'.format(d) for d in dist]

            ))
            wk_traces.append(go.Scatter(
                x=wdb,
                y=wd,
                yaxis='y2',
                opacity=op,
                name=k,
                mode='lines+markers',
                marker=dict(
                    color=colors[i]),
                line=dict(
                    width=width)

            ))
            wk_traces.append(go.Scatter(
                x=wdb,
                y=wc,
                opacity=op,
                name=k,
                mode='lines+markers',
                marker=dict(
                    color=colors[i]),
                line=dict(
                    width=width),
                showlegend=False
            ))
            wk_traces.append(go.Scatter(
                x=wdb,
                y=wp,
                yaxis='y3',
                opacity=op,
                name=k,
                mode='lines+markers',
                marker=dict(
                    color=colors[i]),
                line=dict(
                    width=width),
                showlegend=False,
                hovertemplate='pace: %{y:.2f}<br>dist:%{text}',
                text=['{:.2f}'.format(d) for d in wd]
            ))

        # append annotation traces
        dist_arr = [t.y[-1] for t in dist_traces if len(t.y) > 0]
        dist_traces.append(go.Scatter(
            x=[t.x[-1] for t in dist_traces if len(t.x) > 0],
            y=dist_arr,
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
        pace_traces.append(go.Scatter(
            x=[t.x[-1] for t in pace_traces if len(t.x) > 0],
            y=[t.y[-1] for t in pace_traces if len(t.y) > 0],
            text=[f'{round(t.y[-1], 1)}' for t in pace_traces if len(t.y) > 0],
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
                          'ct': [f'{round(t.y[-1], 1)}' for t in wk_traces if (len(t.x) > 0 and t.yaxis is None)],
                          'px': [t.x[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y3')],
                          'py': [t.y[-1] for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y3')],
                          'pt': [f'{round(t.y[-1], 1)}' for t in wk_traces if (len(t.x) > 0 and t.yaxis == 'y3')]
                          }
        wk_traces.append(go.Scatter(
            x=wk_annotations['dx'],
            y=wk_annotations['dy'],
            text=wk_annotations['dt'],
            mode='text',
            textposition='middle left',
            showlegend=False,
            hoverinfo='none',
        ))
        wk_traces.append(go.Scatter(
            x=wk_annotations['px'],
            y=wk_annotations['py'],
            text=wk_annotations['pt'],
            yaxis='y3',
            mode='text',
            textposition='middle left',
            showlegend=False,
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

        pc_v_dist_layout = go.Layout(xaxis=dict(title='Distance (miles)'), yaxis=dict(title='Pace (min/mile)', hoverformat='.2f'))
        dlayout = go.Layout(
            xaxis=dict(
                title='Days before race'
            ),
            yaxis=dict(
                title='Distance (miles)',
                hoverformat='.2f'
            ),
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)')
        )
        clayout = go.Layout(
            # legend=dict(orientation='h'),
            xaxis=dict(
                title='Days before race'
            ),
            yaxis=dict(
                title='Cumulative (miles)'
            ),
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)')
        )
        playout = go.Layout(
            # legend=dict(orientation='h'),
            xaxis=dict(
                title='Days before race'
            ),
            yaxis=dict(
                title='Pace (min/mile)'
            ),
            legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)')
        )
        wlayout = go.Layout(
            legend=dict(orientation='h', y=1.1),
            xaxis=dict(
                title='Prior week training',
            ),
            yaxis=dict(
                title='Distance',
                domain=[0., .3],
            ),
            yaxis2=dict(
                title='Cumulative',
                domain=[0.35, 0.65]
            ),
            yaxis3=dict(
                title='Pace',
                domain=[0.7, 1.],
            ),
        )

        dist_fig = go.Figure(data=dist_traces, layout=dlayout)
        cum_fig = go.Figure(data=cum_traces, layout=clayout)
        pace_fig = go.Figure(data=pace_traces, layout=playout)
        wk_fig = go.Figure(data=wk_traces, layout=wlayout)
        pc_v_dist_fig = go.Figure(data=pc_v_dist_traces, layout=pc_v_dist_layout)

        # save stuff
        img_path = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/images/posts/'
        dist_fig.write_html(f'{img_path}rta_dist.html')
        print('saved dist image')
        cum_fig.write_html(f'{img_path}rta_cum.html')
        print('saved cum image')
        wk_fig.write_html(f'{img_path}rta_week.html')
        print('saved week image')
        pace_fig.write_html(f'{img_path}rta_pace.html')
        print('saved pace image')

        return dist_fig, cum_fig, wk_fig, pace_fig, pc_v_dist_fig
