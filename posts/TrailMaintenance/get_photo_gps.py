import os

# from PIL import Image
# from PIL.ExifTags import TAGS
from GPSPhoto import gpsphoto
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cbook as cbook

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

parkmap = f'{os.getcwd()}/BMSP trail maintenance segments.jpg'
with cbook.get_sample_data(parkmap) as photo:
    image = plt.imread(photo)
extent = [-89.863021, -89.82765530282295, 43.017644, 43.03831024129931]  # see geosync_map
plt.imshow(image, extent=extent)

photos = os.listdir(f'{os.getcwd()}/downed_trees/')
# latlon = []
for ph in photos:
    data = gpsphoto.getGPSData(f'{os.getcwd()}/downed_trees/{ph}')
    # latlon.append([data['Latitude'], data['Longitude']])
    plt.plot(data['Longitude'], data['Latitude'], 'rd')

# Looks like phone gps is pretty unreliable?

if __name__ == '__main__':
    pass
