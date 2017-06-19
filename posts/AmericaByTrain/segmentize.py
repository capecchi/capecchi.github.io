#Segmentize is meant to go through and link all the track segments between
#junctions making it easier to recursively find all the routes I'm looking for

def main(newdata=False,
         cont=False,
         newredund=False,
         arrive=True):
    import json
    import numpy as np
    import os
    import route_builder
    import glob
    import find_redundancy

    local = 'C:/Python34/America_By_Train/'
    rb = local+'route_builder/'
    direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/AmericaByTrain/'

    #arrow.py contains the code for creating the files endpts.npz and redundant.npy
    f=np.load(local+'endpts.npz')
    index = f['index']
    strt = f['strt']
    end = f['end']
    cid = f['cid']
    stpaul = f['stpaul']
    eb_block = f['eb_block']
    seattle = f['seattle']
    la = f['la']
    cs_block = f['cs_block']
    palmsprings = f['palmsprings']
    neworleans_end = f['neworleans_end']
    sl_block = f['sl_block']
    neworleans_start = f['neworleans_start']
    philly = f['philly']
    cr_block = f['cr_block']
    dc = f['dc']
    chicago = f['chicago']
    cl_block = f['cl_block']

#I really don't want to do this so I'm not gonna-- (it needs editing below here)
    print('finding segments')
    ptA = [stpaul]
    iredund = np.load(local+'redundant.npy')
    #for i in eb_block: iredund = np.append(iredund,i)
    iarr = np.array([],dtype=int)
    level = 0
    with np.load(partials[0]) as f:
        ptA = f['ptA']
        iarr = f['iarr']
    os.remove(partials[0])
    route_builder.main(ptA,iarr,seattle,rb+'empire_builder',level,\
                       iredund,arrive=arrive)
