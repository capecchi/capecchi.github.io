def main(newdata=False):
    import json
    import pandas as pd
    import numpy as np
    import os

    local = 'C:/Python34/America_By_Train/'
    fsav = local+'temp'
    direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/projects/AmericaByTrain'
    with open('amtrak.geojson') as f:
        data = json.load(f)

    empire_builder = ['C&M','WATERTOWN','TOMAH','RIVER','ST PAUL','STAPLES',
                      'HILLSBORO','DEVILS LAKE','GLASGOW','MILK RIVER',
                      'HI LINE','KOOTENAI RIVER','COLUMBIA RIVER','SCENIC']
    coast_starlight = ['SEATTLE','BROOKLYN','CASCADE','BLACK BUTTE','VALLEY',
                       'MARTINEZ','NILES','COAST','SANTA BARBARA','VENTURA']
    sunset_limited = ['ALHAMBRA','YUMA','GILA','LORDSBURG','VALENTINE',
                      'SANDERSON','DEL RIO','GLIDDEN','LAFAYETTE']
    crescent = ['NO & NE','AGS SOUTH','ATLANTA NORTH','ATLANTA SOUTH',
                'NORCROSS','GREENVILLE-ATLANTA','SALISBURY-GREENVILLE',
                'MONTVIEW-SALISBURY','ALEXANDRIA-MONTVIEW','MID-ATLANTIC']
    #cr_id = [207390,
    capitol_limited = ['METROPOLITAN','CUMBERLAND','KEYSTONE','PITTSBURGH','P&W',
                       'FORT WAYNE LINE','CLEVELAND LINE','CHICAGO LINE']
    

    col = ['latitude','longitude','subdiv']
    eb = open(local+'empire_builder.geojson','w')
    eb.write('{"type":"FeatureCollection",\n"features": [\n')
    #eb.write('{"type":"LineString",\n')
    #eb.write('"coordinates":[\n')
    #cs = open(local+'coast_starlight.geojson','w')
    #cs.write('{"type":"LineString",\n')
    #cs.write('"coordinates":[\n')
    #sl = open(local+'sunset_limited.geojson','w')
    #sl.write('{"type":"LineString",\n')
    #sl.write('"coordinates":[\n')
    #cr = open(local+'crescent.geojson','w')
    #cr.write('{"type":"LineString",\n')
    #cr.write('"coordinates":[\n')
    #cl = open(local+'capitol_limited.geojson','w')
    #cl.write('{"type":"LineString",\n')
    #cl.write('"coordinates":[\n')


    i = 1
    nn = len(data['features'])

    subtally = 0
    for feature in data['features']:
        print(i,'/',nn)
        i += 1
        sub = feature['properties']['SUBDIV']
        if sub in empire_builder:
            ebtally = 0
            cc = feature['geometry']['coordinates']
            if subtally == 0:
                subtally = 1
            else:
                eb.write(',\n')
                subtally += 1
            eb.write('{"type":"Feature",\n')
            eb.write('"geometry": {\n"type": "LineString",\n')
            eb.write('"coordinates": [\n')
            for pair in cc:
                if ebtally == 0:
                    eb.write(str(pair))
                    ebtally = 1
                else:
                    eb.write(',\n'+str(pair))
            eb.write(']\n') #end of pair list
            eb.write('}\n') #end of geometry
            eb.write('}\n') #end of feature

    eb.write(']\n') #end of FeaturesCollection list
    eb.write('}')
    eb.close()
