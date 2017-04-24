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
    #cs = pd.DataFrame(columns = col)
    #sl = pd.DataFrame(columns = col)
    #cr = pd.DataFrame(columns = col)
    #cl = pd.DataFrame(columns = col)
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
