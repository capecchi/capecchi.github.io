def main(test=False):
    import pandas as pd
    import numpy as np
    import os

    def csv_list(direc):
        csvs = []
        for file in os.listdir(direc):
            if file.endswith(".csv") and 'test' not in file:
                csvs.append(file)
        return csvs

    local_direc = 'C:/Python34/Air_Quality/csv/'
    web_direc = 'C:/Users/Owner/Documents/GitHub/capecchi.github.io/projects/AirQuality/'
    csv_cols = ['location','city','country','parameter','value','latitude','longitude']
    static_cols = ['location','city','country','parameter','value','latitude','longitude','num_records']
    check_cols = ['parameter','latitude','longitude']
    daily_csvs = csv_list(local_direc)

    if test: daily_csvs = ['test1.csv','test2.csv']

    compsav = web_direc+'static_scanned'
    if os.path.isfile(compsav+'.npy'):
        scanned = np.load(compsav+'.npy')
        print(scanned)
        build = pd.read_csv(web_direc+'static_master.csv')
    else: scanned = []
        
    build = pd.DataFrame(columns=static_cols)
    for d in daily_csvs: #go through every daily csv file
        if d in scanned:
            print(d+' has already been scanned')
        else:
            print(d+' is being scanned now')
            df = pd.read_csv(local_direc+d,usecols=csv_cols)
            add = pd.DataFrame({'num_records':np.ones(len(df),dtype=np.int)})
            df = pd.concat([df,add],axis=1) #add num_records column of 1s
            rows = np.arange(len(df))
            for r in rows:
                ro = df.iloc[r:r+1]
                build_temp = pd.concat([build,ro],ignore_index=True)
                dup = list(build_temp.duplicated(subset=check_cols,keep=False))
                if dup[-1] == True: #repeat location/param
                    irow = dup.index(True) #index of duplicate row
                    #add 1 to #records for this location
                    #print(build.iloc[irow])
                    add_rec = build['num_records'].iloc[irow] + 1
                    build['num_records'].set_value(irow,add_rec,takeable=True)
                    new_val = build['value'].iloc[irow]+ro['value'].iloc[0]
                    build['value'].set_value(irow,new_val,takeable=True)
                else: #row is not repeated, new location/param
                    build = build_temp
            #mark csv as scanned and save
            scanned = np.append(scanned,d)
            #print(scanned)
            np.save(compsav,scanned)
            build.to_csv(web_direc+'static_master.csv',index=False)
            
    brows = np.arange(len(build))
    for r in brows: #go through and divide by #records
        av = build['value'].iloc[r]/build['num_records'].iloc[r]
        build['value'].set_value(r,av,takeable=True)

    build.to_csv(web_direc+'static_master.csv',index=False)
    print('Saved:: static_master.csv')
    
