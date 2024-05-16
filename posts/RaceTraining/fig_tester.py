import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from posts.RaceTraining.app_tools import *
from fig_tools import *

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

races2analyze = ['Superior 50k 2018', 'Driftless 50k 2018', 'Superior 50k 2019', 'Batona (virtual) 33M 2020',
                 'Dirty German (virtual) 50k 2020', 'Stone Mill 50M 2020', 'Shawangunk Ridge 30M 2022',
                 'Black Forest 100k 2022', 'Frosty Fat Sass 6H 2023', 'Naked Bavarian 40M 2023', 'Zion 100M 2023',
                 'Hyner 50k 2024', 'Worlds End 100k 2024', 'Eastern States 100M 2024', 'Black Forest 100k 2024']

fn = get_training_data_file()
races = get_past_races(racekeys=races2analyze)
df = pd.read_excel(fn, sheet_name='data', engine='openpyxl')
df = df.sort_values(by=['Date'])  # put in chronological order


def test_weighthist_fig():
    f1, f2 = create_weighthist_fig(df, races)
    f1.show()
    # f2.show()


def test_cumulative_v_weeks2race():
    fig = cumulative_v_weeks2race(df, races)
    fig.show()


def test_pace_v_dist_and_duration_splits_wklyavg():
    f1, f2, f3, f4 = pace_v_dist_and_duration_splits_wklyavg(df, races)
    f1.show()
    f2.show()
    # f3.show()
    f4.show()


def man_fig_tester():
    sho = pd.read_excel(fn, sheet_name='shoes', engine='openpyxl')
    f1, f2, f3 = create_rman_fig(df, sho, consumption=True)
    # f1.show()
    # f2.show()
    f3.show()


if __name__ == '__main__':
    # test_cumulative_v_weeks2race()
    # test_weighthist_fig()
    # test_pace_v_dist()
    # test_pace_v_dist_and_duration_splits_wklyavg()
    man_fig_tester()
