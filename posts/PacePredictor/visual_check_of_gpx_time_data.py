import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from posts.PacePredictor.pace_predictor_method_development import extract_coords_gpx

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

# gpx1 = 'vis_check/teanaway_coros_support.gpx'
gpx1 = 'vis_check/teanaway_coros.gpx'
# gpx2 = 'vis_check/teanaway_strava.gpx'
gpx2 = 'data/teanaway_100.gpx'
# coords1 = extract_coords_gpx(gpx1, plot=False, raw=True)  # [lon, lat, elev, dcum, dstep, tcum, tstep]
# coords1 = extract_coords_gpx(gpx1, raw=False)
coords2 = extract_coords_gpx(gpx1, raw=True)
# plt.plot(coords1[:, 5], coords1[:, 2], label='dup removed')
plt.plot(coords2[:, 5], coords2[:, 2]+100, label='raw')
plt.legend()
plt.show()

if __name__ == '__main__':
    pass
