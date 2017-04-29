def main():
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
    crescent = ['NO & NE','AGS SOUTH','EAST END','ATLANTA NORTH','ATLANTA SOUTH',
                'NORCROSS','GREENVILLE-ATLANTA','SALISBURY-GREENVILLE',
                'MONTVIEW-SALISBURY','ALEXANDRIA-MONTVIEW','MID-ATLANTIC']
    #cr_id = [207390,
    capitol_limited = ['METROPOLITAN','CUMBERLAND','KEYSTONE','PITTSBURGH','P&W',
                       'FORT WAYNE LINE','CLEVELAND LINE','CHICAGO LINE']
    

    col = ['latitude','longitude','subdiv']
    eb = open(local+'my_routes.geojson','w')
    eb.write('{"type":"FeatureCollection",\n"features": [\n')
    

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
            eb.write('{"type":"Feature",\n')
            eb.write('"properties":{"route": "Empire Builder"},\n')
            eb.write('"geometry": {\n"type": "LineString",\n')
            eb.write('"coordinates": [\n')
            for pair in cc:
                if ebtally == 0:
                    eb.write(str(pair))
                    ebtally = 1
                else:
                    eb.write(',\n'+str(pair))
            eb.write(']\n}\n}\n') #end of pair list, geometry, feature

        if sub in coast_starlight:
            cstally = 0
            cc = feature['geometry']['coordinates']
            if subtally == 0:
                subtally = 1
            else:
                eb.write(',\n')
            eb.write('{"type":"Feature",\n')
            eb.write('"properties":{"route": "Coast Starlight"},\n')
            eb.write('"geometry": {\n"type": "LineString",\n')
            eb.write('"coordinates": [\n')
            for pair in cc:
                if cstally == 0:
                    eb.write(str(pair))
                    cstally = 1
                else:
                    eb.write(',\n'+str(pair))
            eb.write(']\n}\n}\n') #end of pair list, geometry, feature

        if sub in sunset_limited:
            sltally = 0
            cc = feature['geometry']['coordinates']
            if subtally == 0:
                subtally = 1
            else:
                eb.write(',\n')
            eb.write('{"type":"Feature",\n')
            eb.write('"properties":{"route": "Sunset Limited"},\n')
            eb.write('"geometry": {\n"type": "LineString",\n')
            eb.write('"coordinates": [\n')
            for pair in cc:
                if sltally == 0:
                    eb.write(str(pair))
                    sltally = 1
                else:
                    eb.write(',\n'+str(pair))
            eb.write(']\n}\n}\n') #end of pair list, geometry, feature

        if sub in crescent:
            crtally = 0
            cc = feature['geometry']['coordinates']
            if subtally == 0:
                subtally = 1
            else:
                eb.write(',\n')
            eb.write('{"type":"Feature",\n')
            eb.write('"properties":{"route": "Crescent"},\n')
            eb.write('"geometry": {\n"type": "LineString",\n')
            eb.write('"coordinates": [\n')
            for pair in cc:
                if crtally == 0:
                    eb.write(str(pair))
                    crtally = 1
                else:
                    eb.write(',\n'+str(pair))
            eb.write(']\n}\n}\n') #end of pair list, geometry, feature

        if sub in capitol_limited:
            cltally = 0
            cc = feature['geometry']['coordinates']
            check = cc[0]
             #must be west of Philly and not SW of Fort Wayne
            if check[0] < -75:
                westofphilly = True
            else:
                westofphilly = False
            if check[0] < -85 and check[1] < 41:
                swoffortwayne = True
            else:
                swoffortwayne = False
            if westofphilly and not swoffortwayne:
                if subtally == 0:
                    subtally = 1
                else:
                    eb.write(',\n')
                eb.write('{"type":"Feature",\n')
                eb.write('"properties":{"route": "Capitol Limited"},\n')
                eb.write('"geometry": {\n"type": "LineString",\n')
                eb.write('"coordinates": [\n')
                for pair in cc:
                    if cltally == 0:
                        eb.write(str(pair))
                        cltally = 1
                    else:
                        eb.write(',\n'+str(pair))
                eb.write(']\n}\n}\n') #end of pair list, geometry, feature


    eb.write(']\n') #end of FeaturesCollection list
    eb.write('}')
    eb.close()
