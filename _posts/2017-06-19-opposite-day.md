---
layout: post
title: Opposite Day
date: 2017-06-19
excerpt: What's 8,000 miles under your feet
tags:
---

Ever wonder what's on the other side of the world? Or hear the phrase "dig a hole straight through to China"? I just returned from my honeymoon in Thailand which, having a 12 hour time difference from US Central Time, got me thinking about this sort of thing. It's difficult to comprehend how big the world is, and it can be somewhat flabbergasting to think that if you could peer through the earth you could actually see people... upside down and almost 8,000 miles away.

So what is around the world? I decided to have some fun with this by imagining an inverse-me running the same routes that I run around here. By taking the data from my Suunto sport watch I can imagine a mirror image of myself running the same route I did but on the opposite side of the world. Easy enough...

Suunto lets you download your data in a number of formats, and in this case I used the GPX format which I manipulated using the Python module `gpxpy`. I read in the lat/long coordinates from the file and created three arrays of coordinates; one the unperturbed lat/long pairs, another the polar opposite, and the third the "northern" opposite where I did the reflection across the global axis instead of the global center thereby keeping the same latitude.
```py
gpx_file = open(file,'r')
gpx = gpxpy.parse(gpx_file)
for t in gpx.tracks:
    for s in t.segments:
        coords = [[p.longitude,p.latitude] for p in s.points]
        opposite_coords = [[p.longitude+180.,-p.latitude] for p in s.points]
        north_opposite_coords = [[p.longitude+180.,p.latitude] for p in s.points]
```
I then saved these coordinate arrays as geojson LineStrings using the same modules I developed for my [Amtrak](/2017/america-by-train) post.

This method, applied to the Twin Cities Marathon I ran in 2015, shows that inverse-me would be getting pretty wet swimming his marathon somewhere between Australia and the Kerguelen Islands. Northern inverse-me would be running across the dunes in the western reaches of the Gobi desert in the northwestern part of China, pretty much equidistant from Kazakhstan and Mongolia.

[![image](/images/posts/oppositeday.png)](/posts/OppositeDay)
***(click the map for an interactive version)***

After musing on this for a while I began to wonder if it might be possible to run a marathon on the opposite side of the world. Somehow it struck me as interesting to think of a marathon being conducted somewhere, with thousands of people filling the streets, while I run the exact same course at the exact same time, but 8,000 miles directly through the entire planet. It seems like "ghost-running" is a good name for that. So I immediately sought out Boston's antipode, as I feel that there could be no better marathon to ghost-run. Alas, it's still asea in the Indian Ocean.

The quest then became to find somewhere I could feasibly imagine a ghost-run scenario. The logical question that follows, I believe, is where are there antipodes that are both on land? That seems like a good place to start. I found a world map json file online, rotated it 180 degrees and flipped it across the equator to get the map shown below. It was striking to me how little overlap there is between the land and ghost-land masses.

[![image](/images/posts/oppositeday_antiworld.png)](/posts/OppositeDay/anti_world)
***(click the map to explore)***

There don't appear to not be too many places where this could work. The options seem to be New Zealand-Spain, Hawaii-Botswana, or somewhere in South America-Southeast Asia/China. To investigate this further I wanted to add markers of as many marathons as possible. To do this I developed a web scraper (similar to that written for my [Air Quality](/2017/air-quality) post) to pull the city and country from the international marathons listed on [MarathonGuide.com](http://www.marathonguide.com/races/races.cfm?place=Intl) for 2017 (I could do the same for the marathons they have in the US, but we already know any marathon in the US will end up somewhere in the Indian Ocean). I then used the Python package `geopy` to provide the latitude/longitude coordinates for each location and added the marathon locations and their antipodes as layers to the map. By plotting the ghost-marathons, it appears there are actually a few feasible options (hovering over the gray dudes gives you the corresponding marathon location).

New bucket-list item; ghost-run the Christchurch New Zealand marathon in northern Spain.
