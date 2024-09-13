import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pickle
from pace_predictor_method_development import extract_coords_gpx, smooth_run_coords_distwindow
import os

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

datadirec = 'C:/Users/willi/PyCharmProjects/capecchi.github.io/posts/PacePredictor/data/'
rundirec = f'{datadirec}create_model_data/'
fpkl = f'{datadirec}pace_model.p'


def pkl_test():
    a = [1, 2, 3, 4, 5]
    b = ['fuk', 'a', 'duk']

    with open(fpkl, 'wb') as fn:
        pickle.dump([a, b], fn)

    with open(fpkl, 'rb') as fn:
        a1, b1 = pickle.load(fn)

    stp = 1


def check_runs():
    gpx_model_files = os.listdir(f'{rundirec}')
    gpx_model_files = [f for f in gpx_model_files if f.endswith('.gpx')]
    for gpx in gpx_model_files:
        print(f'{gpx}')
        run_coords = extract_coords_gpx(f'{rundirec}{gpx}')  # # [lon, lat, elev, dcum, dstep, tcum, tstep]
        # NEED to smooth since elev only records rounded to the meter
        coords = smooth_run_coords_distwindow(run_coords, 10)  # dist window halfwidth in [m]
        plt.plot(coords[:, 5], coords[:, 2])
        a = 1


if __name__ == '__main__':
    check_runs()
