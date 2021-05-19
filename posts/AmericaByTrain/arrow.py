#Amtrak Recursive ROute Writer (ARROW)
#cont- does not write initial .npz file, relies on existing partials

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

    local = 'F:/Python34/America_By_Train/'
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
        stpaul_iarr_cid = 182614 #mark eastern segment as redundant so we only search west
        portland_cid = 266301 #block southern route to Portland
        seattleid = 241310 #keep south pt
        laid = 211793 #keep south pt
        palmspringsid = 263261 #keep west pt
        neworleansid_end = 178659 #keep east pt NOTE does not connect to neworleans_start
        neworleansid_start = 243859 #keep south or east pt
        phillyid = 204870 #keep north pt
        dcid = 164103 #keep south pt
        chicagoid = 253079 #keep north pt
        
        eb_block = np.array([],dtype=int)
        cs_block = np.array([],dtype=int)
        sl_block = np.array([],dtype=int)
        cr_block = np.array([],dtype=int)
        cl_block = np.array([],dtype=int)
        
        for i in index:
            cid = feats[i]['properties']['FRAARCID']
            coords = feats[i]['geometry']['coordinates']
            c1 = coords[0]
            c2 = coords[-1]
            if cid == stpaulid:
                if c1[0] > c2[0]: stpaul = c1
                else: stpaul = c2
            if cid == stpaul_iarr_cid or cid == portland_cid:
                eb_block = np.append(eb_block,i)
            if cid == seattleid:
                if c1[1] < c2[1]: seattle = c1
                else: seattle = c2
            if cid == laid:
                if c1[1] < c2[1]: la = c1
                else: la = c2
            if cid == seattleid or cid == portland_cid or cid == 189128\
               or cid == 244148 or cid == 254149:
                cs_block = np.append(cs_block,i)
            if cid == palmspringsid:
                if c1[0] < c2[0]: palmsprings = c1
                else: palmsprings = c2
            if cid == neworleansid_end:
                if c1[0] > c2[0]: neworleans_end = c1
                else: neworleans_end = c2
            if cid == 263258 or cid == 266284 or cid == 178673:
                sl_block = np.append(sl_block,i)
            if cid == neworleansid_start:
                if c1[0] > c2[0]: neworleans_start = c1
                else: neworleans_start = c2
            if cid == phillyid:
                if c1[1] > c2[1]: philly = c1
                else: philly = c2
            if cid == 243812 or cid == 204623 or cid == 169919 or cid == 169921\
               or cid == 125491 or cid == 164053 or cid == 275062 or cid == 261822:
                cr_block = np.append(cr_block,i)
            if cid == dcid:
                if c1[1] < c2[1]: dc = c1
                else: dc = c2
            if cid == chicagoid:
                if c1[1] > c2[1]: chicago = c1
                else: chicago = c2
            if cid == 252822 or cid == 164114 or cid == 252939 or cid == 152297\
               or cid == 197933 or cid == 197961 or cid == 192650 or cid == 192649\
               or cid == 253070 or cid == 256677 or cid == 193489 or cid == 266257\
               or cid == 266676:
                cl_block = np.append(cl_block,i)
        cid = [feats[i]['properties']['FRAARCID'] for i in index]

        if newredund:
            #Identify redundant track segments
            fraarcid = [feats[i]['properties']['FRAARCID'] for i in index]
            iredund = np.array([],dtype=int)
            np.save(local+'redundant',iredund)
            redundant = find_redundancy.main(index,strt,end,fraarcid,local)        

        #SAVE STUFF
        np.savez(local+'endpts',index=index,strt=strt,end=end,cid=cid,
                 stpaul=stpaul,seattle=seattle,la=la,palmsprings=palmsprings,
                 neworleans_end=neworleans_end,neworleans_start=neworleans_start,
                 philly=philly,dc=dc,chicago=chicago,eb_block=eb_block,
                 cs_block=cs_block,sl_block=sl_block,cr_block=cr_block,cl_block=cl_block)
        print('saved endpts arrays and city GPS coords')

    else:
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

    #EMPIRE BUILDER
    if 1:
        print('finding EMPIRE BUILDER routes')
        ptA = [stpaul]
        iredund = np.load(local+'redundant.npy')
        #for i in eb_block: iredund = np.append(iredund,i)
        iarr = np.array([],dtype=int)
        if not cont: np.savez(rb+'partial',ptA=ptA,iarr=iarr)
        partials = glob.glob(rb+'*.npz')
        while len(partials) > 0:
            level = 0
            with np.load(partials[0]) as f:
                ptA = f['ptA']
                iarr = f['iarr']
            os.remove(partials[0])
            route_builder.main(ptA,iarr,seattle,rb+'empire_builder',level,\
                               iredund,arrive=arrive)
            partials = glob.glob(rb+'*.npz')

    #COAST STARLIGHT
    if 0:
        print('finding COAST STARLIGHT routes')
        ptA = [seattle]
        ptB = la
        iredund = np.load(local+'redundant.npy')
        for i in cs_block:
            iredund = np.append(iredund,i)
        iarr = np.array([],dtype=int)
        if not cont: np.savez(rb+'partial',ptA=ptA,iarr=iarr)
        partials = glob.glob(rb+'*.npz')
        while len(partials) > 0:
            level = 0
            with np.load(partials[0]) as f:
                ptA = f['ptA']
                iarr = f['iarr']
            os.remove(partials[0])
            route_builder.main(ptA,iarr,ptB,rb+'coast_starlight',level,\
                               iredund,arrive=arrive)
            partials = glob.glob(rb+'*.npz')

    #SUNSET LIMITED
    if 0:
        print('finding SUNSET LIMITED routes')
        ptA = [palmsprings]
        ptB = neworleans_end
        iredund = np.load(local+'redundant.npy')
        for i in sl_block:
            iredund = np.append(iredund,i)
        iarr = np.array([],dtype=int)
        if not cont: np.savez(rb+'partial',ptA=ptA,iarr=iarr)
        partials = glob.glob(rb+'*.npz')
        while len(partials) > 0:
            level = 0
            with np.load(partials[0]) as f:
                ptA = f['ptA']
                iarr = f['iarr']
            os.remove(partials[0])
            route_builder.main(ptA,iarr,ptB,rb+'sunset_limited',\
                               level,iredund,arrive=arrive)
            partials = glob.glob(rb+'*.npz')

    #CRESCENT
    if 0:
        print('finding CRESCENT routes')
        ptA = [neworleans_start]
        ptB = philly
        iredund = np.load(local+'redundant.npy')
        for i in cr_block:
            iredund = np.append(iredund,i)
        iarr = np.array([],dtype=int)
        if not cont: np.savez(rb+'partial',ptA=ptA,iarr=iarr)
        partials = glob.glob(rb+'*.npz')
        while len(partials) > 0:
            level = 0
            with np.load(partials[0]) as f:
                ptA = f['ptA']
                iarr = f['iarr']
            os.remove(partials[0])
            route_builder.main(ptA,iarr,ptB,rb+'crescent',level,iredund,arrive=arrive)
            partials = glob.glob(rb+'*.npz')

    #CAPITOL LIMITED
    if 0:
        print('finding CAPITOL LIMITED routes')
        ptA = [dc]
        ptB = chicago
        iredund = np.load(local+'redundant.npy')
        for i in cl_block:
            iredund = np.append(iredund,i)
        iarr = np.array([],dtype=int)
        if not cont: np.savez(rb+'partial',ptA=ptA,iarr=iarr)
        partials = glob.glob(rb+'*.npz')
        while len(partials) > 0:
            level = 0
            with np.load(partials[0]) as f:
                ptA = f['ptA']
                iarr = f['iarr']
            os.remove(partials[0])
            route_builder.main(ptA,iarr,ptB,rb+'capitol_limited',level,\
                               iredund,arrive=arrive)
            partials = glob.glob(rb+'*.npz')






