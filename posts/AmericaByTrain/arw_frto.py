def build_a_route(froma,tob):
    import json
    import pandas as pd
    import numpy as np
    import os

    local = 'C:/Python34/America_By_Train/'
    fsav = local+'temp'
    direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/projects/AmericaByTrain'
    with open('amtrak.geojson') as f:
        data = json.load(f)
    
    col = ['latitude','longitude','tofranode','frfranode']
    nextid = 0
    tally = 0
    coords = []
    nextid = froma

    data = data['features']
    
    while nextid != tob:
        #print(len(coords))
        looking = 1
        i = 0
        while looking:
            if data[i]['properties']['FRFRANODE'] == nextid:
                for pair in data[i]['geometry']['coordinates']:
                    coords.append(pair)
                looking = 0
                nextid = data[i]['properties']['TOFRANODE']
                subdiv = data[i]['properties']['SUBDIV']
            i += 1
            if i == len(data):
                print('Scanned entire geojson without finding the next segment')
                print('Last segment had TOFRANODE = ',nextid)
                print('Last coords = ',coords[-1])
                
                stop

        #seg = data['features'][data['features']['properties']['frfranode'] == nextid ]
        #for pair in seg['geometry']['coordinates']:
        #    coords.append(pair)
        #nextid = seg['properties']['tofranode']

    return coords

def main():

    eb_frto = [259198,214934] #St. Paul to Seattle
    eb_frto = [215425,259198] #_near_ Seattle to St. Paul
    cs_frto = [214934,258767] #Seattle to LA

    eb_coords = build_a_route(eb_frto[0],eb_frto[1])

    eb = open(local+'empire_builder.geojson','w')
    eb.write('{"type":"LineString",\n')
    eb.write('"coordinates":[\n')
    tally = 0
    for pair in eb_coords:
        if tally == 0:
            eb.write('['+str(pair[0])+','+str(pair[1])+']')
            ebtally = 1
        else:
            eb.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    eb.write(']\n}')
    eb.close()
    
