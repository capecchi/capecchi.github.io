
def main(index,strt,end,cid,local):
    import numpy as np
    import length_builder
    import os
    
    pl = 5 #set num of segments to consider
    #index = np.roll(index,-11705)
    for i in index:
        print(i+1,'/',len(index))
        pep = strt[i]
        strt_dist = [(pep[0]-p[0])**2+(pep[1]-p[1])**2 for p in strt]
        end_dist = [(pep[0]-p[0])**2+(pep[1]-p[1])**2 for p in end]
        isps = np.array([],dtype=int)
        ieps = np.array([],dtype=int)
        for i in index:
            if strt_dist[i] < 1.e-25: isps = np.append(isps,i)
            if end_dist[i] < 1.e-25: ieps = np.append(ieps,i)
        iredund = np.load(local+'redundant.npy')

        if len(isps) > 0:
            isps2 = np.array([],dtype=int)
            for i in isps:
                if i not in iredund: isps2 = np.append(isps2,i)
            isps = isps2
        if len(ieps) > 0:
            ieps2 = np.array([],dtype=int)
            for i in ieps:
                if i not in iredund: ieps2 = np.append(ieps2,i)
            ieps = ieps2

        isegs = np.append(isps,-(ieps+1))
        if len(isegs) > 2: #a linear track should have 2- a split in the track would have 3

            #save temp path file to add paths to as they're completed
            paths = np.array([],dtype=int) #will be array of indices
            np.save(local+'path_temp',paths)
            ipath = np.array([],dtype=int)

            for i in isegs:
                #prepend ipath with other isegs to prevent looping through start
                ipath2 = ipath
                for j in isegs:
                    if j != i:
                        if j >= 0: ipath2 = np.append(ipath2,j)
                        else: ipath2 = np.append(ipath2,abs(j)-1)
                if i >=0: #was a start-pt of segment
                    pep = end[i]
                    ipath2 = np.append(ipath2,i)
                else: #was an end-pt of segment
                    pep = strt[abs(i)-1]
                    ipath2 = np.append(ipath2,abs(i)-1)
                length_builder.main(pep,ipath2,iredund,pl+len(isegs)-1,index,strt,end,cid,local)

            paths = np.load(local+'path_temp.npy')
            print(paths)
            while len(paths[0]) > pl: paths = np.delete(paths,0,1)
            good_rts = np.array([],dtype=int)
            iends = np.array([],dtype=int)
            for ir in np.arange(len(paths)):
                ilast = paths[ir][-1] #last segment in row
                test = np.delete(paths,ir,0)
                test = np.delete(test,len(paths[ir])-1,1)
                if ilast not in test and ilast not in iends: #new end segment
                    good_rts = np.append(good_rts,paths[ir])
                    iends = np.append(iends,ilast)
            ijk = np.array([],dtype=int)
            for r in paths:
                for i in r:
                    if i not in good_rts: iredund = np.append(iredund,i)
            iredund = np.unique(iredund)
#            print(iredund)
#            print(paths)
#            print(pep)
#            for r in paths:
#                print([cid[i] for i in r])
#            stop
            os.remove(local+'path_temp.npy')
            np.save(local+'redundant',iredund)
