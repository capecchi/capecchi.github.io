import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
import gpxpy
import matplotlib.cbook as cbook

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

"""
my phone's geotagging coords seem off. this routine is simply to test our extent, computed from geosync_map
compared to my gps watch
"""

use_map_from_maintenance_crew = False  # this one seems to be garbage
use_alltrails_map = True

# First put up the park map using extent from geosync_map
if use_map_from_maintenance_crew:
    parkmap = f'{os.getcwd()}/BMSP trail maintenance segments.jpg'
    extent = [-89.863021, -89.82765530282295, 43.017644, 43.03831024129931]  # see geosync_map
if use_alltrails_map:
    parkmap = f'{os.getcwd()}/alltrailsmap.png'
    extent = [-89.867651, -89.82567891878173, 43.017294, 43.03735514864866]
with cbook.get_sample_data(parkmap) as photo:
    image = plt.imread(photo)
plt.imshow(image, extent=extent)

# Then overlay some gpx to see if it makes sense
for f in [f'{os.getcwd()}/Lunch_Hike.gpx', f'{os.getcwd()}/Lunch_Trail_Run.gpx']:
    gpx_file = open(f, 'r')
    gpx = gpxpy.parse(gpx_file)
    for t in gpx.tracks:
        for s in t.segments:
            coords = np.array([[p.longitude, p.latitude] for p in s.points])
            plt.plot(coords[:, 0], coords[:, 1])
plt.show()

# ASSESSMENT- alltrails map seems ok, other one seems pretty bunk :)

if __name__ == '__main__':
    pass
