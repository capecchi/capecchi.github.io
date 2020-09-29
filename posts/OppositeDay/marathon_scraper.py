import os

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

from posts.OppositeDay.df2geojson import df_to_geojson, save_geojson


def scrape4marathons():
    us_urls = ['http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=12%2F16%2F16',
               'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=2%2F17%2F17',
               'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=4%2F21%2F17',
               'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=6%2F23%2F17',
               'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=8%2F25%2F17',
               'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=10%2F27%2F17']

    intl_urls = ['http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=12%2F15%2F16',
                 'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=2%2F16%2F17',
                 'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=4%2F20%2F17',
                 'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=6%2F22%2F17',
                 'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=8%2F24%2F17',
                 'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=10%2F26%2F17']

    urls = us_urls
    for url in intl_urls: urls.append(url)

    cities = []
    countries = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        # print(r.text)

        for f in soup.find_all('td'):
            string = str(f)
            city = '<td class="titletext" valign="top" width="120">'
            cntry = '<td class="titletext" valign="top" width="130">'
            if string[:47] == city:
                cities.append(string[47:-5])
                # print(string[47:-5])
                # stop
            if string[:47] == cntry:
                countries.append(string[47:-5])

    fsav = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/arrays.npz'
    if not os.path.isfile(fsav):
        lat, long, places, noplaces = [], [], [], []  # noplaces for ones w/o lat/long data
        np.savez(fsav, lat=lat, long=long, places=places, noplaces=noplaces)
    else:
        dat = np.load(fsav)
        lat = list(dat['lat'])
        long = list(dat['long'])
        places = list(dat['places'])
        noplaces = list(dat['noplaces'])

    # FIND COORDINATES OF CITIES
    geolocator = Nominatim()
    for i in np.arange(len(cities)):
        place = cities[i] + ', ' + countries[i]
        if place not in places and place not in noplaces:
            print(place)
            foundplace = False
            places2try = [place, cities[i].split(',')[0].strip() + ', ' + countries[i],
                          cities[i].split('&')[0].strip() + ', ' + countries[i],
                          cities[i].split('to')[0].strip() + ', ' + countries[i]]
            for p in places2try:
                location = geolocator.geocode(p)
                if location is not None:
                    long.append(location.longitude)
                    lat.append(location.latitude)
                    places.append(place)
                    foundplace = True
                    break
            if not foundplace:
                noplaces.append(place)
                # if len(coords) == 0:
                #     coords = np.array([[location.longitude, location.latitude]])
                #     places = np.array(place)
                # else:
                #     coords = np.append(coords, [[location.longitude, location.latitude]], axis=0)
                #     places = np.append(places, place)
                # print(coords,places)
    np.savez(fsav, lat=lat, long=long, places=places, noplaces=noplaces)

    anti_lat = [la * -1 for la in lat]
    anti_long = [lo + 180. if lo+180. <= 180 else lo-180. for lo in long]
    # coords = np.array(coords)
    # anti_coords = np.array(coords)
    # anti_coords[:, 0] += 180.
    # anti_coords[:, 0] = np.where(anti_coords[:, 0] > 180., anti_coords[:, 0] - 360., anti_coords[:, 0])
    # anti_coords[:, 1] = coords[:, 1] * (-1)

    cit = [p.split(',')[0] for p in places]  # geotagged places only
    plc = [p.split(',')[1] for p in places]
    df_mar = pd.DataFrame(data={'City': cit, 'Place': plc, 'latitude': lat, 'longitude': long})
    df_anti = pd.DataFrame(data={'City': cit, 'Place': plc, 'latitude': anti_lat, 'longitude': anti_long})
    df_rot = pd.DataFrame(data={'City': cit, 'Place': plc, 'latitude': lat, 'longitude': anti_long})  # keep same lat

    mar_geo = df_to_geojson(df_mar, properties=['City', 'Place'])
    anti_geo = df_to_geojson(df_anti, properties=['City', 'Place'])
    rot_geo = df_to_geojson(df_rot, properties=['City', 'Place'])

    fn = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/marathons2.geojson'
    anti_fn = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/marathons2_opp.geojson'
    rot_fn = 'C:/Users/Owner/PycharmProjects/capecchi.github.io/posts/OppositeDay/marathons2_rot.geojson'
    save_geojson(mar_geo, fn)
    save_geojson(anti_geo, anti_fn)
    save_geojson(rot_geo, rot_fn)
    a = 1
    # coords2geojson_points.main(coords, fn, places)
    # coords2geojson_points.main(anti_coords, anti_fn, places)


if __name__ == '__main__':
    scrape4marathons()
