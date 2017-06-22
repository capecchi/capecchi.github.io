# >>> import CSVdownload as scrape
# >>> scrape.main()

def main():
    us_urls  = ['http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=12%2F16%2F16',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=2%2F17%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=4%2F21%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=6%2F23%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=8%2F25%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=USA&StartDate=10%2F27%2F17']
               
    intl_urls = ['http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=12%2F15%2F16',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=2%2F16%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=4%2F20%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=6%2F22%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=8%2F24%2F17',\
                'http://www.marathonguide.com/races/races.cfm?Sort=RaceDate&Place=Intl&StartDate=10%2F26%2F17']

    urls = us_urls
    for url in intl_urls: urls.append(url)

    #print(len(urls))
    #stop
    import urllib
    from bs4 import BeautifulSoup
    import requests
    import numpy as np
    from geopy.geocoders import Nominatim
    import coords2geojson_points
    import os
    
    cities = []
    countries = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        #print(r.text)

        for f in soup.find_all('td'):
            string = str(f)
            city = '<td class="titletext" valign="top" width="120">'
            cntry = '<td class="titletext" valign="top" width="130">'
            if string[:47] == city:
                cities.append(string[47:-5])
                #print(string[47:-5])
                #stop
            if string[:47] == cntry:
                countries.append(string[47:-5])

    if 0:
        for i in np.arange(len(cities)):
            print(cities[i]+', '+countries[i])
        stop



    #FIND COORDINATES OF CITIES
    fsav ='C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/OppositeDay/arrays.npz'
    if not os.path.isfile(fsav):
        coords = np.array([])
        places = np.array([])
        np.savez(fsav,coords=coords,places=places)
    else:
        dat = np.load(fsav)
        coords = dat['coords']
        places = dat['places']
        #cities = dat['cities']
        #countries = dat['countries']
        
    for i in np.arange(len(cities)):
    #for i in np.arange(10):
        place = cities[i]+', '+countries[i]
        if place not in places:
            print(place)
            geolocator = Nominatim()
            location = geolocator.geocode(place)
            if str(location) != 'None':
                if len(coords) == 0:
                    coords = np.array([[location.longitude,location.latitude]])
                    places = np.array(place)
                else:
                    coords = np.append(coords,[[location.longitude,location.latitude]],axis=0)
                    places = np.append(places,place)
                #print(coords,places)
            np.savez(fsav,coords=coords,places=places)

    coords = np.array(coords)
    anti_coords = np.array(coords)
    anti_coords[:,0] += 180.
    anti_coords[:,0] = np.where(anti_coords[:,0] > 180.,anti_coords[:,0]-360.,anti_coords[:,0])
    anti_coords[:,1] = coords[:,1]*(-1)

    #print(coords)
    #print(anti_coords)
    #stop

    fn ='C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/OppositeDay/marathons'
    anti_fn ='C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/OppositeDay/anti_marathons'
    coords2geojson_points.main(coords,fn,places)
    coords2geojson_points.main(anti_coords,anti_fn,places)
