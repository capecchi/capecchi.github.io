---
layout: post
title: World Air Quality Map
date: 2017-04-09
excerpt: Mapping air quality data from around the world.
image: /images/posts/aggregate_data.png
project: true
tags: Mapbox web-scraper pollution geojson
---

[![image](/images/posts/aggregate_data.png)](/projects/AirQuality/world_data)
***click the map for an interactive version (NOTE: data for this project is still being processed and may change slightly)***

Data does not tell its own story. My graduate thesis project, towards which I worked meticulously for over five years, essentially boils down to around 8 billion numbers in various arrays. The mere record of these numbers would surely not have persuaded my thesis committee to grant me my PhD. The point is, of course, not that I *have* the numbers, but what the numbers mean: These numbers, in this arrangement, arriving in this order means-- something. It's a human task to turn data into information.

A few weeks ago I found a database of air quality measurements from locations around the world. The data, available at [OpenAQ](https://openaq-data.s3.amazonaws.com/index.html), offers almost daily data beginning in June of 2015. I decided to create a map to visualize this data to get a sense of what the mountain of spreadsheets had to show. I had never built a web scraper before, nor done much coding in Python, so I took this as an opportunity to learn a few new skills in the process.

The key to writing a program to download the right files comes down to getting an array of the file names. Here we use the Python package BeautifulSoup to parse the page. In this case, the CSV files were given <key> tags in the site HTML, making them easy to pluck out.
```py
def find_csvs(url):

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        csv_names = []
        for f in soup.find_all('key'):
            string = str(f)
            name = string[5:len(f)-7] #remove <key> and </key>
            if name[len(name)-3:] == "csv":
                csv_names.append(name)

        return csv_names
```
After some slight string editing we're returned a string array of CSV names and can download them easily.

Now having the data on hand, the question becomes how best to present it. In this case I consider there to be two natural questions that arise. First, how does air quality differ from place to place? And second, how does it vary in time? To answer the first question, the data was aggregated into a single file, creating an average of all records taken at each location for each pollutant ("aggregate-average"). For the second, I chose to group the data by month so as to produce an average concentration per pollutant per location per month ("monthly-average")- this choice was made to increase the amount of data available (as not all locations reported data daily) while still maintaining an appreciable number of temporal bins over which to view changes concentration levels.

These monthly and aggregate averages were computed in Python. The following code snippet highlights the important aspects of the data processing:
```py
for d in daily_csvs: #go through every daily csv file
    df = pd.read_csv(d,usecols=csv_cols)
    add = pd.DataFrame({'num_records':np.ones(len(df),dtype=np.int)})
    df = pd.concat([df,add],axis=1) #add num_records column of 1s
    df.dropna(axis=0,inplace=True) #drop any rows with NaN values
    rows = np.arange(len(df))
    for r in rows:
        ro = df.iloc[r:r+1]
        if ro['value'].iloc[0] >= 0: #ignore negative values
            build_temp = pd.concat([build,ro],ignore_index=True)
            dup = list(build_temp.duplicated(subset=\
                  ['parameter','latitude','longitude'],keep=False))
            if dup[-1] == True: #repeat location/param
                irow = dup.index(True) #index of duplicate row
                #add 1 to #records for this location
                num_rec = build['num_records'].iloc[irow] + 1
                build['num_records'].set_value(irow,num_rec,takeable=True)
                #compute running average
                new_val = build['value'].iloc[irow]*((num_rec-1.0)/num_rec)+\
                          ro['value'].iloc[0]*(1.0/num_rec)
                build['value'].set_value(irow,new_val,takeable=True)
            else: #row is not repeated, new location/param, keep as appended
                build = build_temp

    scanned = np.append(scanned,d)
    np.save('static_scanned',scanned) #track scanned files
    build.to_csv('static_master.csv',index=False) #save running averages
```
This process keeps a running average of the concentration of each pollutant for each location. Two steps included above are needed in order to clean the data. First, there are entries lacking latitude/longitude information; these are avoided with a simple call to drop any rows containing `NaN` values. Second, there are numerous entries throughout the dataset that contain negative concentrations (which obviously do not reflect the actual pollutant levels). OpenAQ responded to my query regarding this by stating that they archive the raw data recorded by each location and do not correct for any instrument drift or periods of instrument malfunction. This being the case, for the purposes of this visualization we simply ignore negative values.

A similar routine is run to produce the monthly-averaged data, with an added stipulation that rows are only combined if they have the same parameter, location, and *year-month*.

I created the map visualization using the Mapbox API which required converting the data into a geojson file format, accomplished using this online [converter tool](http://www.convertcsv.com/csv-to-geojson.htm). The style was formatted following this [example](https://www.mapbox.com/mapbox-gl-js/example/timeline-animation/). The visualization of the aggregate data (above) required a simple filter applied to the slider setting that selected only the data for the pollutant selected (mainly to avoid the overlapping icons that would result from displaying multiple pollutant records at each location). In order to show the change in concentrations with time, I added a second slider/filter. Two event listeners are added that update the variables `iparam` and `iym` whenever a slider is moved.
```javascript
document.getElementById('slider1').addEventListener('input', function(e) {
    var iparam = parseInt(e.target.value, 10);
    var iym = parseInt(document.getElementById('slider2').value);
    filterBy(iparam,iym);
});
```
These variables are passed to a function `filterBy` that applies the filters to the map and displays only the relevant data.
```javascript
function filterBy(iparam,iym) {

    var filter1 = ['==', 'parameter', params[iparam]];
    var filter2 = ['==', 'year-month',ym[iym]];

    map.setFilter('pollution-circles', ["all",filter1,filter2]);
    map.setFilter('pollution-labels', ["all",filter1,filter2]);
  }
```
The resulting map is shown below and shows how pollutant concentrations vary in time for each location.
[![image](/images/posts/aggregate_data.png)](/projects/AirQuality/world_monthly_data)
***click the map for interactive version***

So here we have both maps working, giving us a visual understanding of the two questions posed earlier- one to show how concentrations vary around the world, another to show how those levels vary with time.
