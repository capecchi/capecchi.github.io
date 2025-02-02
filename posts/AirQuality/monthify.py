def main(test=False,
        reverse=False):
    import pandas as pd
    import numpy as np
    import os

    def csv_list(direc):
        csvs = []
        for file in os.listdir(direc):
            if file.endswith(".csv") and 'test' not in file:
                csvs.append(file)
        return csvs

    direc = "C:/Python34/Air_Quality/"
    csvdirec = direc+'csv/'
    col_names = ['location','city','country','utc','local','parameter','value','unit','latitude','longitude']
    csvs = csv_list(csvdirec)

    month_csvs = []
    for f in csvs:
        ym = f[:7]
        if ym+'.csv' not in month_csvs:
            month_csvs.append(ym+'.csv')

    if test: month_csvs = os.listdir(direc+'monthly_csvs/')
    if reverse: month_csvs = month_csvs[::-1]
    for ym in month_csvs: #for each month
        fsav = direc+'monthly_csvs/'+ym
        if os.path.isfile(fsav):
                print(fsav," already exists")
        else: #compile daily data for this month
            relevant = []
            for file in csvs: #find daily csv files from that month
                if ym[:7] in file:
                    relevant.append(file)
            all_month_data = pd.concat(pd.read_csv(csvdirec+r,usecols=col_names) for r in relevant)#create one month dataframe
            all_month_data.dropna(axis=0,inplace=True) #drop any rows with NaN values
            all_month_data = all_month_data[all_month_data.value >= 0] #keep only positive values
            wrong = all_month_data[ all_month_data['unit'] == 'ppm' ]
            if len(wrong) != 0:
                right = all_month_data[ all_month_data['unit'] != 'ppm' ]
                wrong['value'] = wrong['value']*1145.0
                all_month_data = pd.concat([right,wrong],axis=0)
            all_month_data = all_month_data.drop('unit',axis=1)

            #drop duplicates
            sub =['parameter','latitude','longitude']
            month_data = all_month_data.drop_duplicates(subset=sub)
            month_data = month_data.rename(columns={"utc":"year-month","local":"num_records"})
            unique_rows = np.arange(len(month_data['location']))

            #update each unique entry with average of monthly measurements from that location
            for r in unique_rows:
                print(r+1,'/',len(unique_rows))
                multiple_records = all_month_data[ all_month_data[sub[0]] == month_data[sub[0]].iloc[r] ]
                multiple_records = multiple_records[ multiple_records[sub[1]] == month_data[sub[1]].iloc[r] ]
                multiple_records = multiple_records[ multiple_records[sub[2]] == month_data[sub[2]].iloc[r] ]
                av_val = np.mean(multiple_records['value'])
                month_data['value'].set_value(r,av_val,takeable=True)
                month_data['year-month'].set_value(r,ym[:7],takeable=True)
                month_data['num_records'].set_value(r,len(multiple_records),takeable=True)

            month_data.to_csv(fsav,index=False)
            print('Saved:: /monthly/'+ym) #end of if file not present


    month_master = pd.concat(pd.read_csv(direc+'monthly_csvs/'+f,\
                                         encoding='latin-1') for f in month_csvs)
    month_master.to_csv(direc+'month_master.csv',index=False)
    print('Saved:: month_master.csv')

    params = ['pm10','pm25','no2','so2','co','o3','bc']

    for p in params:
        param_df = month_master[ month_master['parameter'] == p ]
        param_df.to_csv(direc+p+'_master.csv',index=False)
        

#main()
