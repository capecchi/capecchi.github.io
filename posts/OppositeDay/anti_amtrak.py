def main():
    import json
    import glob
    import coords2geojson

    local = 'C:/Python34/America_By_Train/finished_routes/'
    webdir = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/OppositeDay/'

    rts = glob.glob(local+'*.geojson')
    rts = [rts[3],rts[1],rts[4],rts[2],rts[0]]
    #print(rts)
    #stop
    allcoords = []
    
    for r in rts:
        with open(r) as f:
            data = json.load(f)
        coords = data['geometry']['coordinates']
        #print(len(coords))

        i = 0
        for c in coords: #long,lat
            c[0] = c[0]+180.
            c[1] = -c[1]
            if i % 3 == 0: allcoords.append(c)
            i += 1

    coords2geojson.main(allcoords,webdir+'anti_amtrak')
