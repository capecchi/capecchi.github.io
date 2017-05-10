def main(ptA, iarr, ptB, fn, level, iredund,arrive=True):
    import numpy as np
    import coords2linestring
    import json
    import route_builder
    import os

    level += 1
    
    #IF LEVEL TOO HIGH- tie off and save as partial file
    if level >= 20:
        print('TOO HIGH----------------------------')
        j = 1
        local = 'C:/Python34/America_By_Train/'
        rb = local+'route_builder/'
        ftype = '.npz'
        append = ''
        fn = 'partial'
        ftest = rb+fn+append+ftype
        print('tied off at: ',ptA[-1])
        #stop
        while os.path.isfile(ftest):
            append = '_'+str(j)
            ftest = rb+fn+append+ftype
            j += 1
        fn = rb+fn+append
        np.savez(fn,ptA=ptA,iarr=iarr)

    #If not too high, keep going down the rabbit hole
    else:
        print(len(ptA),'- level',level, ptA[-1])
            
        local = 'C:/Python34/America_By_Train/'
        direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/posts/AmericaByTrain/'

        with open(direc+'amtrak.geojson') as f:
            data = json.load(f)
        feats = data['features']

        f=np.load(local+'endpts.npz')
        index = f['index']
        strt = f['strt']
        end = f['end']
        cid = f['cid']

        building = 1    
        while building:

            #FIND SEGMENTS THAT SHARE CURRENT PATH ENDPOINT (originally < 1.e-25)
            last = ptA[-1]
            strt_dist = [ (p[0]-last[0])**2+(p[1]-last[1])**2 for p in strt ]
            isps = np.array([],dtype=int)
            for i in index:
                if strt_dist[i] < 1.e-10: isps = np.append(isps,i)
            
            end_dist = [ (p[0]-last[0])**2+(p[1]-last[1])**2 for p in end ]
            ieps = np.array([],dtype=int)
            for i in index:
                if end_dist[i] < 1.e-10: ieps = np.append(ieps,i)

            #REMOVE SEGMENTS ALREADY USED OR REDUNDANT
            if len(isps) > 0:
                isps2 = np.array([],dtype=int)
                for i in isps:
                    if i not in iarr:
                        if i not in iredund: isps2 = np.append(isps2,i)
                isps = isps2
            if len(ieps) > 0:
                ieps2 = np.array([],dtype=int)
                for i in ieps:
                    if i not in iarr:
                        if i not in iredund: ieps2 = np.append(ieps2,i)
                ieps = ieps2

            #END, BUILD, OR BIFURCATE
            npts = len(isps) + len(ieps) #number of start and endpoints found

            if npts == 0: #end of route found
                building = 0
                if not arrive: coords2linestring.main(ptA,fn,ptB=False)    

            if npts == 1: #no bifurcation
                if len(isps) == 1:
                    cc = feats[isps[0]]['geometry']['coordinates']
                    iarr = np.append(iarr,isps[0])
                if len(ieps) == 1:
                    cc = feats[ieps[0]]['geometry']['coordinates']
                    cc = cc[::-1] #reverse order
                    iarr = np.append(iarr,ieps[0])
                for pair in cc:
                    ptA = np.append(ptA,[pair],axis=0)
                if ptA[-1][0] == ptB[0] and ptA[-1][1] == ptB[1]:
                    building = 0 #found desired endpoint                
                    coords2linestring.main(ptA,fn,ptB=True)    


            if npts > 1: #track bifurcation
                building = 0
                if len(isps) > 0:
                    for sp in isps:
                        ptA2 = ptA
                        iarr2 = iarr
                        iarr2 = np.append(iarr2,sp)
                        cc = feats[sp]['geometry']['coordinates']
                        for pair in cc:
                            ptA2 = np.append(ptA2,[pair],axis=0)
                        if ptA2[-1][0] == ptB[0] and ptA2[-1][1] == ptB[1]:
                            coords2linestring.main(ptA2,fn,ptB=True)
                        else:
                            route_builder.main(ptA2,iarr2,ptB,fn,level,iredund,arrive=arrive)
                            print('up for air-')
                if len(ieps) > 0:
                    for ep in ieps:
                        ptA2 = ptA
                        iarr2 = iarr
                        iarr2 = np.append(iarr2,ep)
                        cc = feats[ep]['geometry']['coordinates']
                        cc = cc[::-1]
                        for pair in cc:
                            ptA2 = np.append(ptA2,[pair],axis=0)
                        if ptA2[-1][0] == ptB[0] and ptA2[-1][1] == ptB[1]:
                            coords2linestring.main(ptA2,fn,ptB=True)
                        else:
                            route_builder.main(ptA2,iarr2,ptB,fn,level,iredund,arrive=arrive)
                            print('up for air--')
