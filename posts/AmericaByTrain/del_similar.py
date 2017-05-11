def main():
    import json
    import glob
    import numpy as np
    import os
    
    rb = 'C:/Python34/America_By_Train/route_builder/'
    geos = glob.glob(rb+'*.geojson')
    size = [(f,os.path.getsize(f)) for f in geos]
    size.sort(key=lambda filename: filename[1],reverse=True)
    geos = [g[0] for g in size] #ordered largest to smallest

    index = np.arange(len(geos))
    i = 0
    while i < len(index):
        with open(geos[i]) as f:
            data = json.load(f)
        print(geos[i])
        coords = data['geometry']['coordinates']
        others = np.delete(geos,i)
        perc = np.array([])
        for o in others:
            print(o)
            with open(o) as f:
                data2 = json.load(f)
            coords2 = data2['geometry']['coordinates']
            unique = [c for c in coords if c not in coords2]
            perc = len(unique)/len(coords)
            print(perc)
            if perc < 0.005:
                num = 1
                fn = rb+'duplicates/duplicate'+str(num)+'.geojson'
                while os.path.isfile(fn):
                    num += 1
                    fn = rb+'duplicates/duplicate'+str(num)+'.geojson'
                if 0:
                    os.rename(o,fn)
                    print('moved',o,'--to--',fn)
                if 1:
                    os.remove(o)
                    print('deleted',o)
        geos = glob.glob(rb+'*.geojson')
        size = [(f,os.path.getsize(f)) for f in geos]
        size.sort(key=lambda filename: filename[1],reverse=True)
        geos = [g[0] for g in size] #ordered largest to smallest
        index = np.arange(len(geos))
        i += 1
