import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cbook as cbook
import os

matplotlib.use('TkAgg')  # allows plotting in debug mode
clrs = plt.rcParams['axes.prop_cycle'].by_key()['color']

"""
We have the jpg for the park map and are trying to figure out the gps coord extent
I've mapped GPS coords from google maps on 2 pts which we'll use to fix the jpg
pt1- military ridge meets the paved access path (yellow/orange intersection)
pt2- upper right where Ryan Road and Woodchuck Crossing meet
"""
use_map_from_maintenance_crew = False  # this one seems to be garbage
use_alltrails_map = True

p1 = [-89.846061, 43.019124]
p2 = [-89.829524, 43.036090]

guess1 = [-89.85, -89.825, 43.015, 43.036]  # lon1, lon2, lat1, lat2

if use_map_from_maintenance_crew:
    parkmap = f'{os.getcwd()}/BMSP trail maintenance segments.jpg'

    # in map coords:
    p1m = [-89.83802, 43.01650]
    p2m = [-89.82633, 43.03374]
    scalex = (p2[0] - p1[0]) / (p2m[0] - p1m[0])
    scaley = (p2[1] - p1[1]) / (p2m[1] - p1m[1])

    guess2 = [guess1[0], (guess1[1] - guess1[0]) * scalex + guess1[0], guess1[2],
              (guess1[3] - guess1[2]) * scaley + guess1[2]]

    # scale should be right, now just shift pts into place:
    p1m = [-89.83304, 43.01648]
    shiftx, shifty = p1[0] - p1m[0], p1[1] - p1m[1]
    guess3 = [guess2[0] + shiftx, guess2[1] + shiftx, guess2[2] + shifty, guess2[3] + shifty]

    # guess 3 is good enough for gov't work! :)
    # guess3 = [-89.863021, -89.82765530282295, 43.017644, 43.03831024129931]

if use_alltrails_map:
    parkmap = f'{os.getcwd()}/alltrailsmap.png'

    # in map coords:
    p1m = [-89.83711, 43.01693]
    p2m = [-89.82726, 43.03469]
    scalex = (p2[0] - p1[0]) / (p2m[0] - p1m[0])
    scaley = (p2[1] - p1[1]) / (p2m[1] - p1m[1])

    guess2 = [guess1[0], (guess1[1] - guess1[0]) * scalex + guess1[0], guess1[2],
              (guess1[3] - guess1[2]) * scaley + guess1[2]]

    # scale should be right, now just shift pts into place:
    p1m = [-89.82841, 43.01683]
    shiftx, shifty = p1[0] - p1m[0], p1[1] - p1m[1]
    guess3 = [guess2[0] + shiftx, guess2[1] + shiftx, guess2[2] + shifty, guess2[3] + shifty]

if __name__ == '__main__':
    with cbook.get_sample_data(parkmap) as photo:
        image = plt.imread(photo)
    plt.imshow(image, extent=guess3)
    for p in [p1, p2]:
        plt.plot(p[0], p[1], 'o')
    a = 1
