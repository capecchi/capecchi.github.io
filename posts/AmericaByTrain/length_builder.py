#pep : current path endpoint (for finding next segment(s))
#ipath : array of indices on this path
#iredund : if available, indices to ignore (from previous juncture analyses)
#pl : path length to reach


def main(pep, ipath, iredund, pl, index, strt, end, cid, rb):
    import numpy as np
    import length_builder

#IDEA: at junction, scan all paths out for certain distance (100m?)
#    and if any reconnect, add one path to iarr to eliminate quick doubles

    #IF LENGTH REACHED
    if len(ipath) == pl:
        #print('path finished, length = ',len(ipath))
        paths = np.load(rb+'path_temp.npy')
        if len(paths) == 0: paths = [ipath]
        else: paths = np.append(paths,[ipath],axis=0)
        np.save(rb+'path_temp',paths)
        
    #If not, keep going
    else:
        building = 1    
        while building:
            strt_dist = [(pep[0]-p[0])**2+(pep[1]-p[1])**2 for p in strt]
            end_dist = [(pep[0]-p[0])**2+(pep[1]-p[1])**2 for p in end]
            isps = np.array([],dtype=int)
            ieps = np.array([],dtype=int)
            for i in index:
                if strt_dist[i] < 1.e-25: isps = np.append(isps,i)
                if end_dist[i] < 1.e-25: ieps = np.append(ieps,i)
            iredund = np.load(rb+'redundant.npy')

            if len(isps) > 0:
                isps2 = np.array([],dtype=int)
                for i in isps:
                    if i not in iredund and i not in ipath: isps2 = np.append(isps2,i)
                isps = isps2
            if len(ieps) > 0:
                ieps2 = np.array([],dtype=int)
                for i in ieps:
                    if i not in iredund and i not in ipath: ieps2 = np.append(ieps2,i)
                ieps = ieps2

            isegs = np.append(isps,-(ieps+1))
            npts = len(isegs) #number of segments found

            if npts == 0: #end of route found
                building = 0

            if npts == 1: #no bifurcation
                ii = isegs[0]
                if ii >= 0: #was a start-pt
                    pep = end[ii]
                    ipath = np.append(ipath,ii)
                else: #was an end-pt
                    pep = strt[abs(ii)-1]
                    ipath = np.append(ipath,abs(ii)-1)
                if len(ipath) == pl:
                    building = 0
                    length_builder.main(pep,ipath,iredund,pl,index,strt,end,cid,rb)

            if npts > 1: #track bifurcation
                building = 0
                for ii in isegs:
                    if ii >= 0:
                        pep = end[ii]
                        ipath2 = np.append(ipath,ii)
                    else:
                        pep = strt[abs(ii)-1]
                        ipath2 = np.append(ipath,abs(ii)-1)
                    length_builder.main(pep,ipath2,iredund,pl,index,strt,end,cid,rb)



