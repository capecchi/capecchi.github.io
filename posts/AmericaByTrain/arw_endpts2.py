def main(newdata = False):
    import json
    import numpy as np
    import os

    local = 'C:/Python34/America_By_Train/'
    direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/AmericaByTrain/'

    with open(direc+'amtrak.geojson') as f:
        data = json.load(f)
    feats = data['features']

    if newdata or not os.path.isfile(local+'endpts.npz'):
        index = np.arange(len(feats))
        strt = []
        end = []
        for i in index:
            cc = feats[i]['geometry']['coordinates']
            strt.append(cc[0])
            end.append(cc[-1])

        np.savez(local+'endpts',index=index,strt=strt,end=end)
        print('saved endpts arrays')
    else:
        f=np.load(local+'endpts.npz')
        index = f['index']
        strt = f['strt']
        end = f['end']

    
