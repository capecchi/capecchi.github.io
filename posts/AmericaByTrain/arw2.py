def main(newdata=False,
         verbose=False):
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
    eb = open(local+'empire_builder.geojson','w')
    eb.write('{"type":"FeatureCollection",\n"features": [\n')
    cs = open(local+'coast_starlight.geojson','w')
    cs.write('{"type":"FeatureCollection",\n"features": [\n')
    sl = open(local+'sunset_limited.geojson','w')
    sl.write('{"type":"FeatureCollection",\n"features": [\n')
    cr = open(local+'crescent.geojson','w')
    cr.write('{"type":"FeatureCollection",\n"features": [\n')
    cl = open(local+'capitol_limited.geojson','w')
    cl.write('{"type":"FeatureCollection",\n"features": [\n')
    

    i = 1
    nn = len(data['features'])

    ebsubtally = 0
    cssubtally = 0
    slsubtally = 0
    crsubtally = 0
    clsubtally = 0
    for feature in data['features']:
        if verbose: print(i,'/',nn)
        i += 1
        sub = feature['properties']['SUBDIV']
        if sub in empire_builder:
            ebtally = 0
            cc = feature['geometry']['coordinates']
            if ebsubtally == 0:
                ebsubtally = 1
            else:
                eb.write(',\n')
            eb.write('{"type":"Feature",\n')
            eb.write('"properties":{},\n')
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
            if cssubtally == 0:
                cssubtally = 1
            else:
                cs.write(',\n')
            cs.write('{"type":"Feature",\n')
            cs.write('"properties":{},\n')
            cs.write('"geometry": {\n"type": "LineString",\n')
            cs.write('"coordinates": [\n')
            for pair in cc:
                if cstally == 0:
                    cs.write(str(pair))
                    cstally = 1
                else:
                    cs.write(',\n'+str(pair))
            cs.write(']\n}\n}\n') #end of pair list, geometry, feature

        if sub in sunset_limited:
            sltally = 0
            cc = feature['geometry']['coordinates']

            check = cc[0]
             #must be south of santa barbara
            if check[1] < 34.420831:
                southofsantabarbara = True
            else:
                southofsantabarbara = False
            if southofsantabarbara:
                if slsubtally == 0:
                    slsubtally = 1
                else:
                    sl.write(',\n')
                sl.write('{"type":"Feature",\n')
                sl.write('"properties":{},\n')
                sl.write('"geometry": {\n"type": "LineString",\n')
                sl.write('"coordinates": [\n')
                for pair in cc:
                    if sltally == 0:
                        sl.write(str(pair))
                        sltally = 1
                    else:
                        sl.write(',\n'+str(pair))
                sl.write(']\n}\n}\n') #end of pair list, geometry, feature

        if sub in crescent:
            crtally = 0
            cc = feature['geometry']['coordinates']
            if sub == 'MID-ATLANTIC':
                if crsubtally == 0:
                    crsubtally = 1
                else:
                    cr.write(',\n')
                cr.write('{"type":"Feature",\n')
                cr.write('"properties":{},\n')
                cr.write('"geometry": {\n"type": "LineString",\n')
                cr.write('"coordinates": [\n')
                for pair in cc:
                    if pair[1] < 39.955790:
                        southofphilly = True
                    else: southofphilly = False
                    if southofphilly:
                        if crtally == 0:
                            cr.write(str(pair))
                            crtally = 1
                        else:
                            cr.write(',\n'+str(pair))
                cr.write(']\n}\n}\n') #end of pair list, geometry, feature
            else: #not mid-atlantic subdiv                   
                if crsubtally == 0:
                    crsubtally = 1
                else:
                    cr.write(',\n')
                cr.write('{"type":"Feature",\n')
                cr.write('"properties":{},\n')
                cr.write('"geometry": {\n"type": "LineString",\n')
                cr.write('"coordinates": [\n')
                for pair in cc:
                    if crtally == 0:
                        cr.write(str(pair))
                        crtally = 1
                    else:
                        cr.write(',\n'+str(pair))
                cr.write(']\n}\n}\n') #end of pair list, geometry, feature

        if sub in capitol_limited:
            cltally = 0
            cc = feature['geometry']['coordinates']
            check = cc[0]
            if check[0] < -75.181975: westofphilly = True
            else: westofphilly = False
            if westofphilly:
                if clsubtally == 0:
                    clsubtally = 1
                else:
                    cl.write(',\n')
                cl.write('{"type":"Feature",\n')
                cl.write('"properties":{},\n')
                cl.write('"geometry": {\n"type": "LineString",\n')
                cl.write('"coordinates": [\n')
                for pair in cc:
                    if cltally == 0:
                        cl.write(str(pair))
                        cltally = 1
                    else:
                        cl.write(',\n'+str(pair))
                cl.write(']\n}\n}\n') #end of pair list, geometry, feature


    eb.write(']\n') #end of FeaturesCollection list
    eb.write('}')
    eb.close()
    cs.write(']\n') #end of FeaturesCollection list
    cs.write('}')
    cs.close()
    sl.write(']\n') #end of FeaturesCollection list
    sl.write('}')
    sl.close()
    cr.write(']\n') #end of FeaturesCollection list
    cr.write('}')
    cr.close()
    cl.write(']\n') #end of FeaturesCollection list
    cl.write('}')
    cl.close()
