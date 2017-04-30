#want to organize featurecollection linestrings into order
#and write single feature

def sort(triplets):
    import numpy as np
    import math
    #triplets = (long,lat,order) -> (x,y,i)
    #math.atan2(y,x) is quantrant sensitive -pi to pi

    #PLAN: tweak this slightly to check direction- follow to one end,
    #then when min dist pt occurs behind, switch chain and continue.
    #Must also organize order array alongside as this will tell us what
    #order to open the linestrings

    pt = triplets[-1]
    test_trip = triplets[:-1]
    testdist = [ (pt[0]-t[0])**2+(pt[1]-t[1])**2 for t in test_trip ]
    imax = np.argmax(testdist)
    chain = [triplets[imax]]
    del triplets[imax]
    #chain = triplets[np.where(testdist == np.max(testdist))]
    #triplets = triplets[np.where(testdist != np.max(testdist))]
    direc = 'nan'

    while len(triplets) >=1:
        last = chain[-1]
        print(len(chain),len(triplets))
        dist = [ (last[0]-t[0])**2+(last[1]-t[1])**2 for t in triplets ]
        theta = [ math.atan2(t[1]-last[1],t[0]-last[0]) for t in triplets ]
        imin = np.argmin(dist)

        #print(len(triplets), np.min(dist))
        if direc == 'nan': #no direction established yet
            nextpt = [triplets[imin]]
            chain = np.concatenate([chain,nextpt])
            del triplets[imin]
        else: #compare with current heading
            nextdirec = theta[imin]
            diff = np.min([(direc - nextdirec) % (2*np.pi),
                           (nextdirec - direc) % (2*np.pi) ])
            if diff >= np.pi/2: #nextpt behind current direction
                chain = chain[::-1]
            else:
                nextpt = [triplets[imin]]
                chain = np.concatenate([chain,nextpt])
                del triplets[imin]
                direc = nextdirec

    return chain

def dist(c1,c2):
    dist = (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2
    return dist

def main():
    import numpy as np
    import json
    
    local = 'C:/Python34/America_By_Train/'
    geos = ['empire_builder','coast_starlight','sunset_limited','crescent','capitol_limited']

    #going to write one master file featurecollection
    master = open(local+'route_master.geojson','w')
    master.write('{"type":"FeatureCollection",\n"features": [\n{\n')

    firstgeo = True
    for g in geos:

        geo = open(local+g+'_ls.geojson','w')
        geo.write('{"type":"LineString",\n')
        geo.write('"coordinates":[\n')
        
        with open(local+g+'.geojson') as f:
            data = json.load(f)
        features = data['features']
        nn = len(features)
        order = np.arange(nn) #index array of features
        longlatord = []

        for i in order:
            ls = features[i]['geometry']['coordinates'] #pick a linestring
            avlat = 0
            avlong = 0
            ncoords = len(ls)
            if ncoords != 0:
                for p in ls:
                    avlat = avlat + p[1]
                    avlong = avlong + p[0]
                longlatord.append([avlong/ncoords,avlat/ncoords,i])

        chain = sort(longlatord)

        #write one linestring for each route and one master geojson
        if firstgeo: firstgeo = False
        else: master.write(',\n')
        master.write('{"type":"Feature",\n"properties":{\n')
        master.write('"route":"'+g+'"\n},\n"geometry":{\n"type":"LineString",\n')
        master.write('"coordinates": [\n')                     
        ls_num = 1
        coords = []
        for triplet in chain: #for each linestring
            i = int(triplet[2])
            temp_coords = []
            feature = features[i]     
            cc = feature['geometry']['coordinates']
            for pair in cc:
                temp_coords.append(pair)

            if ls_num == 2:
                #first check first ls
                testpt = temp_coords[0]
                if dist(coords[0],testpt) < dist(coords[-1],testpt):
                    coords = coords[::-1] #reverse since 1st pt was closer to next ls than last pt
            if ls_num >=2:
                #check new ls orientation
                testpt = coords[-1]
                if dist(temp_coords[0],testpt) > dist(temp_coords[-1],testpt):
                    temp_coords = temp_coords[::-1]
            for pair in temp_coords:
                coords.append(pair)

        tally = 0
        for pair in coords:
            if tally == 0:
                master.write('['+str(pair[0])+','+str(pair[1])+']')
                geo.write('['+str(pair[0])+','+str(pair[1])+']')
                tally = 1
            else:
                master.write(',\n['+str(pair[0])+','+str(pair[1])+']')
                geo.write(',\n['+str(pair[0])+','+str(pair[1])+']')

        master.write(']\n}\n}') #end coordinates, geometry, feature
        geo.write(']\n}')#end geometry, LineString
        geo.close()
        
    #after all geojsons scanned close out master file
    master.write('\n]\n}') #end features [] and feature collection
    master.close()
                
