def main(newdata = False):
    import json
    import numpy as np
    import os
    import route_builder
    import glob

    local = 'C:/Python34/America_By_Train/'
    rb = local+'route_builder/'
    direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/AmericaByTrain/'

    if newdata or not os.path.isfile(local+'endpts.npz'):

        with open(direc+'amtrak.geojson') as f:
            data = json.load(f)
        feats = data['features']
        index = np.arange(len(feats))
        strt = []
        end = []
        for i in index:
            cc = feats[i]['geometry']['coordinates']
            strt.append(cc[0])
            end.append(cc[-1])


        #NEED route GPS endpoints to look for
        fcoords = local
        #fraarcid
        stpaulid = 182592 #keep east pt
        stpaul_iarr_cid = 182614 #mark eastern segment as used so we only search west
        seattleid = 241310 #keep south pt
        laid = 211793 #keep south pt
        palmspringsid = 263261 #keep west pt
        neworleansid_end = 178659 #keep east pt NOTE does not connect to neworleans_start
        neworleansid_start = 243859 #keep south or east pt
        phillyid = 204870 #keep north pt
        dcid = 164103 #keep south pt
        chicagoid = 253079 #keep north pt
        stpaul_iarr = np.array([],dtype=int)
        
        for i in index:
            cid = feats[i]['properties']['FRAARCID']
            coords = feats[i]['geometry']['coordinates']
            c1 = coords[0]
            c2 = coords[-1]
            if cid == stpaulid:
                if c1[0] > c2[0]: stpaul = c1
                else: stpaul = c2
            if cid == stpaul_iarr_cid:
                stpaul_iarr = np.append(stpaul_iarr,i)
            if cid == seattleid:
                if c1[1] < c2[1]: seattle = c1
                else: seattle = c2
            if cid == laid:
                if c1[1] < c2[1]: la = c1
                else: la = c2
            if cid == palmspringsid:
                if c1[0] < c2[0]: palmsprings = c1
                else: palmsprings = c2
            if cid == neworleansid_end:
                if c1[0] > c2[0]: neworleans_end = c1
                else: neworleans_end = c2
            if cid == neworleansid_start:
                if c1[0] > c2[0]: neworleans_start = c1
                else: neworleans_start = c2
            if cid == phillyid:
                if c1[1] > c2[1]: philly = c1
                else: philly = c2
            if cid == dcid:
                if c1[1] < c2[1]: dc = c1
                else: dc = c2
            if cid == chicagoid:
                if c1[1] > c2[1]: chicago = c1
                else: chicago = c2

        np.savez(local+'endpts',index=index,strt=strt,end=end,
                 stpaul=stpaul,seattle=seattle,la=la,palmsprings=palmsprings,
                 neworleans_end=neworleans_end,neworleans_start=neworleans_start,
                 philly=philly,dc=dc,chicago=chicago,stpaul_iarr=stpaul_iarr)
        print('saved endpts arrays and city GPS coords')

    else:
        f=np.load(local+'endpts.npz')
        index = f['index']
        strt = f['strt']
        end = f['end']
        stpaul = f['stpaul']
        stpaul_iarr = f['stpaul_iarr']
        seattle = f['seattle']
        la = f['la']
        palmsprings = f['palmsprings']
        neworleans_end = f['neworleans_end']
        neworleans_start = f['neworleans_start']
        philly = f['philly']
        dc = f['dc']
        chicago = f['chicago']
        
    #BUILD ALL THE ROUTES FROM A TO B
    #ptA either [[long,lat]] or [[long,lat],...]

    #EMPIRE BUILDER
    #put an npy file in /rb to start with
    ptA = [stpaul]
    iarr = stpaul_iarr
    np.savez(rb+'partial',ptA=ptA,iarr=iarr)

    partials = glob.glob(rb+'*.npz')
    while len(partials) > 0:
        level = 0
        with np.load(partials[0]) as f:
            ptA = f['ptA']
            iarr = f['iarr']
        os.remove(partials[0])
        route_builder.main(ptA, iarr, seattle, rb+'empire_builder', level)
        partials = glob.glob(rb+'*.npz')






