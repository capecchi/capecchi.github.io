---
layout: post
title: Opposite Day
date: 2017-06-19
excerpt: What's 8,000 miles under your feet
image: /images/posts/oppositeday_bar.png
tags: geojson Carto marathons
active: True
---

Ever wonder what's on the other side of the world? Or hear the phrase "dig a hole straight through to China"? I just returned from my honeymoon in Thailand which, having a 12 hour time difference from US Central Time, got me thinking about this sort of thing. Turns out if you live in the US you'd dig through to China if you maintained the same latitude. Digging straight through the core would end up having you surface somewhere in the Indian Ocean. It's difficult to comprehend how big the world is, and it can be somewhat flabbergasting to think that if you could peer through the earth you could actually see people... upside down and almost 8,000 miles away.

So what is around the world? I decided to have some fun with this by taking the data from my Suunto sport watch and imagining a mirror image of myself running the same route but on the opposite side of the world. Easy enough...

Suunto lets you download your data in a number of formats, and in this case I used the GPX format which I manipulated using the Python module `gpxpy`. I read in the lat/long coordinates from the file and created three arrays of coordinates; one the unperturbed lat/long pairs, another the antipode (exactly the opposite point on the globe), and the third the "northern" opposite where I did the rotation around the world but kept the same latitude.
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

There don't appear to be too many places where this could work. The options seem to be New Zealand-Spain, Hawaii-Botswana, or somewhere in South America-Southeast Asia/China. To investigate this further I wanted to add markers of as many marathons as possible. To do this I developed a web scraper (similar to that written for my [Air Quality](/2017/air-quality) post) to pull the city and country from the marathons listed for 2017 on [MarathonGuide.com](http://www.marathonguide.com). I then used the Python package `geopy` to provide the latitude/longitude coordinates for each location and added the marathon locations and their antipodes as layers to the map. By plotting the ghost-marathons, it appears there are actually a few feasible options (hovering over the gray dudes gives you the corresponding marathon location).

New bucket-list item; ghost-run the Christchurch New Zealand marathon in northern Spain.

Sooooo... I wanted to see how far I could carry this idea, and it turns out to be quite a challenge. I have multiple tabs open trying to find a decent place to run. Ideally the ghost marathon would overlay a city and I could adapt the route to existing streets. That way I'm not breaking any laws, and less likely to get in trouble. I added layers to the map above where I rotated 180 degrees but kept the same latitude, my thinking being that the global land mass is predominantly located in the norther hemisphere so while it may not be as cool, I figured it'd be more likely that a marathon in the norther hemisphere would coincide with another city 180 degrees away. You can poke around like I did, but it's still surprisingly difficult to find good options. In fact I think my best option is still the Spain-New Zealand overlap.

The best option I've found so far is running the Madrid marathon in New Zealand. I traced out the 2020 route (which is cancelled due to Covid-19) and after downloading as a .gpx file and manipulating into a .geojson, I added it to both maps above. The first map (I think) is better since I used satellite imagery as the basemap so you can see the kind of terrain I'd be running on. And it looks... doable! The land looks beautiful, most of it seems open, it's near a bunch of roads which makes it accessible, and there don't seem to be any farms I'd be running through that might cause legal issues. Of course one issue is the timing.

My goal is to run at the exact time of the marathon so that I'd be running directly under all the other athletes- but the Madrid marathon start times for 2020 are 8:45a (elite) up to 9:20a (wave 3) on November 15th. As of this writing (29 Sept 2020) Madrid is in the Central European Daylight Time (UTC +2) and will revert to Central European Time (UTC +1) on October 25th. New Zealand began daylight savings on September 3rd (UTC +13), and won't revert to New Zealand Standard Time (UTC +12) until April 4th 2021. So at race time Madrid will be off of daylight savings (and so UTC +1), and New Zealand will be on (so UTC +13). So, perhaps unsurprisingly, on November 15th, race day, New Zealand will be 12 hours ahead of Madrid, and a 9a start in Madrid will be a 9p start for me! According to timeanddate.com, on November 15th the sun sets at 8:10p with Civil, Nautical, and Astronomical twilight ending respectively at 8:41p, 9:19p, and 10:01p. With a 9p start I'm looking to finish around 2a, so I'm gonna need a headlamp.
