def sort_coords(pairs):
    import numpy as np
    #(long,lat) -> (x,y)
    #math.atan2(y,x) is quantrant sensitive
    
    test = pairs[0]
    pairs = pairs[1:]
    testdist = [ (test[0]-p[0])**2+(test[1]-p[1])**2 for p in pairs ]
    chain = pairs[np.where(testdist == np.max(testdist))]
    pairs = pairs[np.where(testdist != np.max(testdist))]

    while len(pairs) >=1:
        last = chain[-1]
        dist = [ (last[0]-p[0])**2+(last[1]-p[1])**2 for p in pairs ]
        print(len(pairs), np.min(dist))

        if np.min(dist) >= 10: #reached an end with pts remaining
            chain = chain[::-1]
        else:
            nextpt = pairs[np.where(dist == np.min(dist))]
            chain = np.concatenate([chain,nextpt])
            pairs = pairs[np.where(dist != np.min(dist))]

    return chain

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
    crescent = ['NO & NE','AGS SOUTH','EAST END','ATLANTA NORTH','ATLANTA SOUTH',
                'NORCROSS','GREENVILLE-ATLANTA','SALISBURY-GREENVILLE',
                'MONTVIEW-SALISBURY','ALEXANDRIA-MONTVIEW','MID-ATLANTIC']
    #cr_id = [207390,
    capitol_limited = ['METROPOLITAN','CUMBERLAND','KEYSTONE','PITTSBURGH','P&W',
                       'FORT WAYNE LINE','CLEVELAND LINE','CHICAGO LINE']
    

    col = ['latitude','longitude','subdiv']
    eb = open(local+'empire_builder.geojson','w')
    eb.write('{"type":"LineString",\n')
    eb.write('"coordinates":[\n')
    cs = open(local+'coast_starlight.geojson','w')
    cs.write('{"type":"LineString",\n')
    cs.write('"coordinates":[\n')
    sl = open(local+'sunset_limited.geojson','w')
    sl.write('{"type":"LineString",\n')
    sl.write('"coordinates":[\n')
    cr = open(local+'crescent.geojson','w')
    cr.write('{"type":"LineString",\n')
    cr.write('"coordinates":[\n')
    cl = open(local+'capitol_limited.geojson','w')
    cl.write('{"type":"LineString",\n')
    cl.write('"coordinates":[\n')


    if newdata or not os.path.isfile(local+'coords.npz'):
        i = 1
        nn = len(data['features'])

        eb_coords = []
        cs_coords = []
        sl_coords = []
        cr_coords = []
        cl_coords = []
        for feature in data['features']:
            print(i,'/',nn)
            i += 1
            sub = feature['properties']['SUBDIV']
            if sub in empire_builder:
                cc = feature['geometry']['coordinates']
                for pair in cc:
                    eb_coords.append(pair)
            if sub in coast_starlight:
                cc = feature['geometry']['coordinates']
                for pair in cc:
                    cs_coords.append(pair)
            if sub in sunset_limited:
                cc = feature['geometry']['coordinates']
                for pair in cc:
                    sl_coords.append(pair)
            if sub in crescent:
                cc = feature['geometry']['coordinates']
                for pair in cc:
                    cr_coords.append(pair)
            if sub in capitol_limited:
                cc = feature['geometry']['coordinates']
                for pair in cc:
                    cl_coords.append(pair)
        np.savez(local+'coords',eb_coords=eb_coords,cs_coords=cs_coords,
                sl_coords=sl_coords,cr_coords=cr_coords,cl_coords=cl_coords)

    f = np.load(local+'coords.npz')
    eb_coords = f['eb_coords']
    cs_coords = f['cs_coords']
    sl_coords = f['cl_coords']
    cr_coords = f['cr_coords']
    cl_coords = f['cl_coords']

    if newdata or not os.path.isfile(local+'eb_sorted.npy'):
        eb_sorted = sort_coords(eb_coords)
        np.save(local+'eb_sorted',eb_sorted)
    if newdata or not os.path.isfile(local+'cs_sorted.npy'):    
        cs_sorted = sort_coords(cs_coords)
        np.save(local+'cs_sorted',cs_sorted)
    if newdata or not os.path.isfile(local+'sl_sorted.npy'):
        sl_sorted = sort_coords(sl_coords)
        np.save(local+'sl_sorted',ls_sorted)
                
        cr_sorted = sort_coords(cr_coords)
        cl_sorted = sort_coords(cl_coords)
        np.savez(local+'sorted',eb_sorted=eb_sorted,cs_sorted=cs_sorted,
                 sl_sorted=sl_sorted,cr_sorted=cr_sorted,cl_sorted=cl_sorted)

    f = np.load(local+'sorted.npz')
    eb_sorted = f['eb_sorted']
    cs_sorted = f['cs_sorted']
    sl_sorted = f['sl_sorted']
    cr_sorted = f['cr_sorted']
    cl_sorted = f['cl_sorted']

    print('writing to .geojson')
    #WRITE to .geojson file
    tally = 0
    for pair in eb_sorted:
        if tally == 0:
            eb.write('['+str(pair[0])+','+str(pair[1])+']')
            ebtally = 1
        else:
            eb.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    eb.write(']\n}')
    eb.close()

    tally = 0
    for pair in cs_sorted:
        if tally == 0:
            cs.write('['+str(pair[0])+','+str(pair[1])+']')
            ebtally = 1
        else:
            cs.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    cs.write(']\n}')
    cs.close()
    
    tally = 0
    for pair in sl_sorted:
        if tally == 0:
            sl.write('['+str(pair[0])+','+str(pair[1])+']')
            sltally = 1
        else:
            sl.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    sl.write(']\n}')
    sl.close()
    
    tally = 0
    for pair in cr_sorted:
        if tally == 0:
            cr.write('['+str(pair[0])+','+str(pair[1])+']')
            crtally = 1
        else:
            cr.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    cr.write(']\n}')
    cr.close()
    
    tally = 0
    for pair in cl_sorted:
        if tally == 0:
            cl.write('['+str(pair[0])+','+str(pair[1])+']')
            cltally = 1
        else:
            cl.write(',\n['+str(pair[0])+','+str(pair[1])+']')
    cl.write(']\n}')
    cl.close()
