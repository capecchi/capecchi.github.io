---
layout: post
title: America By Train
date: 2016-03-15
excerpt: A three week rail journey around the states
tags: Carto
---

[![image](/images/posts/america_by_train.png)](/projects/AmericaByTrain)

Early last year I found myself in an unusual situation. I was nearing the end of my graduate research project, but was still missing the bulk of the experimental data I needed. I had already designed the experiment, modeled and built the diagnostic, and tested what I could, but I was waiting on the scintillator for my neutron detector to be built by the manufacturer. With mounting impetus to move towards graduation I found I had little to do in the lab, but plenty to do in writing my thesis. So I grabbed my laptop, a mountain of research papers, bought myself an Amtrak rail pass, and took off for a three week trip around the United States.

...I'll fill out this portion later, describing the adventures of the trip. For now, I'm developing that data/mapping visuals that will accompany it.

**Addendum: Data and Mapping for this post**

I wanted to create a visualization for this post using CartoDB because I knew it offered a lot of interesting ways to incorporate pictures and text blurbs into a map, but also because I haven't used it before and wanted to familiarize myself with it.

With that as my ultimate goal, the first step was acquiring data to plot the Amtrak routes, as I wanted these as the basis over which I applied my trip narrative. A simple google search leads to numerous links from which one can easily download a geojson file containing the Amtrak routes. Upon inspection, I found that this file contains every Amtrak route, but notably lacks an easy way to segment the tracks by which trains operate on them. The Empire Builder, for example, runs from Chicago to Seattle across the northern states, but the data lacks a property identifying any given segment as belonging to this particular train. Instead, a property is included that identifies a *subdivision*.

Using CartoDB I can add overlay labels which reveal which subdivisions are part of each train. Each route only contains a dozen or so subdivisions, so creating a string array in Python was not too difficult. From there it took some finagling, but with a careful use of syntax I could successfully write a geojson file for each route, writing in each subdivision as a feature with LineString geometry in a FeatureCollection object using the code below.
```Python
#initiate the file
eb = open(local+'empire_builder.geojson','w')
eb.write('{"type":"FeatureCollection",\n"features": [\n')

#add each subdivision's LineString geometry as a new feature
subtally = 0
for feature in data['features']:
    sub = feature['properties']['SUBDIV']
    if sub in empire_builder:
        tally = 0
        cc = feature['geometry']['coordinates']
        if subtally == 0:
            subtally = 1
        else:
            eb.write(',\n')
        eb.write('{"type":"Feature",\n')
        eb.write('"properties":{},\n')
        eb.write('"geometry": {\n"type": "LineString",\n')
        eb.write('"coordinates": [\n')
        for pair in cc:
            if tally == 0:
                eb.write(str(pair))
                tally = 1
            else:
                eb.write(',\n'+str(pair))
        eb.write(']\n}\n}\n') #end of pair list, geometry, feature

#end and close the file
eb.write(']\n') #end of FeaturesCollection list
eb.write('}')
eb.close()
```
This code, when applied to the five different routes I travelled, results in five geojson files ready to be uploaded and mapped.

A careful look at the routes does reveal gaps in most of the routes. This, in my opinion, is the result of yet another flaw in the data. Not only is there no 'ROUTE' property, there is not even a 'SUBDIV' property for all of the LineString elements. This is definitely something I would clean up if I were to spend more time with the data, but each route contains around 12,000 gps coordinates, and that's good enough for the purposes here.
