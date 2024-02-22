from bottle import run, redirect, request, get

from posts.RaceTraining.app_tools import *

port = 8000
redirect_url = f'https://www.strava.com/oauth/authorize?client_id=34049&redirect_uri=http://localhost:{port}&response_type=code&scope=activity:read_all'


def add_time_col(code):
    # add elapsed time columns
    time_arr = []

    client = get_client(code)

    fn = get_training_data_file()
    sho = pd.read_excel(fn, sheet_name='shoes', engine='openpyxl')
    df = pd.read_excel(fn, sheet_name='data', engine='openpyxl', index_col='runid')  # use runid as index

    for runid in df.index:
        if not np.isfinite(df.at[runid, 'Elapsed Time (sec)']):
            print(f'updating runid: {runid}')
            try:
                act = client.get_activity(runid)
                elaps_sec = int(act.elapsed_time.total_seconds())
                df.at[runid, 'Elapsed Time (sec)'] = elaps_sec
            except:
                print(f'*failed to update {runid}*')

    with pd.ExcelWriter(fn) as writer:
        df.to_excel(writer, sheet_name='data', index=True)
        sho.to_excel(writer, sheet_name='shoes', index=False)

    print('--> DATA FILE UPDATED <--')


def do_updates(code):
    # add type, calories, pace columns
    type_arr, cals_arr, pace_arr = [], [], []

    client = get_client(code)

    fn = get_training_data_file()
    sho = pd.read_excel(fn, sheet_name='shoes', engine='openpyxl')
    df = pd.read_excel(fn, sheet_name='data', engine='openpyxl', index_col='runid')  # use runid as index

    for runid in df.index:
        pass
        # if not np.isfinite(df.at[runid, 'Split Shift (min/mile)']) and df.at[runid, 'Dist (mi)'] > 2:
        #     print(f'updating runid: {runid}')
        #     try:
        #         act = client.get_activity(runid)
        #         splits = client.get_activity(act.id).splits_standard
        #         minpmil = [60. / unithelper.miles_per_hour(s.average_speed).num if unithelper.miles_per_hour(
        #             s.average_speed).num > 0 else np.nan for s in splits]  # min per mile pace
        #         firsthalf_av, secondhalf_av = np.nanmean(minpmil[0:int(len(minpmil) / 2)]), np.nanmean(
        #             minpmil[int(len(minpmil) / 2):])  # get av pace for first/second half of act
        #         df.at[runid, 'Split Shift (min/mile)'] = secondhalf_av - firsthalf_av
        #     except:
        #         break

    # with pd.ExcelWriter(fn) as writer:
    #     df.to_excel(writer, sheet_name='data', index=True)
    #     sho.to_excel(writer, sheet_name='shoes', index=False)

    logging.info('--> DATA FILE UPDATED <--')


@get('/')
def load_in():
    if 'code=' in request.url:
        for el in request.url.split('&'):
            if 'code=' in el:
                code = el.split('=')[-1]
                # do_updates(code)
                add_time_col(code)
    else:
        return redirect(redirect_url)


run(host='localhost', port=port, debug=True, reloader=True)
