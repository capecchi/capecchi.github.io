def main():
    import json
    import pandas as pd
    import numpy as np

    local = 'C:/Python34/America_By_Train/'
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
    eb.write('{"type":"LineString",\n')
    eb.write('"coordinates":[\n')
    cs = open(local+'empire_builder.geojson','w')
    cs.write('{"type":"LineString",\n')
    cs.write('"coordinates":[\n')
    sl = open(local+'empire_builder.geojson','w')
    sl.write('{"type":"LineString",\n')
    sl.write('"coordinates":[\n')
    cr = open(local+'empire_builder.geojson','w')
    cr.write('{"type":"LineString",\n')
    cr.write('"coordinates":[\n')
    cl = open(local+'empire_builder.geojson','w')
    cl.write('{"type":"LineString",\n')
    cl.write('"coordinates":[\n')
    

    ebtally = 0
    i = 1
    nn = len(data['features'])
    for feature in data['features']:
        print(i,'/',nn)
        i += 1
        sub = feature['properties']['SUBDIV']

        if sub in empire_builder: #NEED to somehow sort the points
            coord_list = feature['geometry']['coordinates']
            for pair in coord_list:
                if ebtally == 0:
                    eb.write(str(pair))
                    ebtally = 1
                else:
                    eb.write(',\n'+str(pair))
    eb.write(']\n}')
    eb.close()

    cstally = 0
    i = 1
    nn = len(data['features'])
    for feature in data['features']:
        print(i,'/',nn)
        i += 1
        sub = feature['properties']['SUBDIV']

        if sub in coast_starlight:
            coord_list = feature['geometry']['coordinates']
            for pair in coord_list:
                if cstally == 0:
                    cs.write(str(pair))
                    cstally = 1
                else:
                    cs.write(',\n'+str(pair))
    cs.write(']\n}')
    cs.close()

    sltally = 0
    i = 1
    nn = len(data['features'])
    for feature in data['features']:
        print(i,'/',nn)
        i += 1
        sub = feature['properties']['SUBDIV']

        if sub in sunset_limited:
            coord_list = feature['geometry']['coordinates']
            for pair in coord_list:
                if sltally == 0:
                    sl.write(str(pair))
                    sltally = 1
                else:
                    sl.write(',\n'+str(pair))
    sl.write(']\n}')
    sl.close()

    crtally = 0
    i = 1
    nn = len(data['features'])
    for feature in data['features']:
        print(i,'/',nn)
        i += 1
        sub = feature['properties']['SUBDIV']

        if sub in crescent: #NEED to somehow sort the points
            coord_list = feature['geometry']['coordinates']
            for pair in coord_list:
                if crtally == 0:
                    cr.write(str(pair))
                    crtally = 1
                else:
                    cr.write(',\n'+str(pair))
    cr.write(']\n}')
    cr.close()

    cltally = 0
    i = 1
    nn = len(data['features'])
    for feature in data['features']:
        print(i,'/',nn)
        i += 1
        sub = feature['properties']['SUBDIV']

        if sub in capitol_limited: #NEED to somehow sort the points
            coord_list = feature['geometry']['coordinates']
            for pair in coord_list:
                if cltally == 0:
                    cl.write(str(pair))
                    cltally = 1
                else:
                    cl.write(',\n'+str(pair))
    cl.write(']\n}')
    cl.close()
