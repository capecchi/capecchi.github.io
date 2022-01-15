---
layout: post
title: Race Training
date: 2019-04-03
excerpt: Analyzing my historical training efforts
#image: /images/posts/abt_bar.png
tags: StravaAPI
active: True
---

I ran my first marathon in 2006. I've gone through a few GPS watches over the intervening years, recording run after run after run, but that's it... The watch would be useful in that it told me how far and fast I just ran, but that's all I used it for. Well early 2019 I found out Strava has an API available to the public and put together a few routines to pull together my data for a little more in depth analysis.
Since GitHub (which hosts this site) is a static host, I can't dynamically make calls to the Strava API. Instead I run a `localhost` session to pull updated data, create the plots you see below and embed them as .html sources in an <iframe> element. So although they're not updated dynamically, they are still interactive.

Using the Strava API I can grab activities and access the attributes; distance and time arrays, calories, etc. One of the first things that came to mind was to compare my training efforts between different races.
So with a list of races and their corresponding race date, I the data 18 weeks prior to and including race day. By looking at how my current effort compares, I can more realistically assess my readiness level for the upcoming race. The cumulative distance I find both the easiest to read and the most helpful in assessing my race-readiness and have recently added a cumulative calories analysis as well which includes any activity (e.g. cycling, swimming).

<iframe src="/images/posts/rta_cum.html" height="500" width="100%"></iframe>

I keep playing with this code, and started thinking about how pace varies with distance. I know if I train for a 5k I'll increase my pace as I get fitter. I also know I can run a 5k faster than a 10k. I've focused a lot on the former point, trying to improve my pace for a given distance, but never really considered the second point. At any given point of time (read: fixed level of fitness) there's a limit to how fast I can run a 5k, 10k, or any other distance. What does this curve of max-effort vs distance look like?

I found some literature on this: See this paper ([Formenti 2005](https://www.researchgate.net/publication/7696487_Human_locomotion_on_snow_Determinants_of_economy_and_speed_of_skiing_across_the_ages)) for the corrected and extended equations put forth in this paper ([Minetti 2004]((https://journals.biologists.com/jeb/article/207/8/1265/15058?casa_token=fbwAai80r5cAAAAA:h-YYnutqdIby2GJrDtoiHGnYR4XeZHv-gHkj12aXIRnIRFhI4B5vfX_vVJ2k4VunMZ6WdQ))).

They give the maximum sustainable speed as

$$
s = \frac{3.6}{C}\left(\frac{W_{mech}}{E_f} - W_{BASMET}\right)
$$

Where $$E_f$$ is the efficiency of muscle contraction, $$W_{BASMET}$$ is the basal metabolic power, and $$C$$ is a constant related to energy movement cost (J/kg/m).

The maximum sustainable long-term mechanical effort ($$W_{mech}$$, in Watts) is then related to the duration of exercise ($$t$$, in seconds) by

$$
W_{mech} = A \frac{0.085 \left(\frac{t}{3600}\right)^2-\frac{3.908 t}{3600} +91.82}{100} \left(1-
  \frac{\tau}{t} \left(1-e^{-\frac{t}{\tau}}\right) \right)+ \frac{B}{t}
$$

Where $$A$$ is the maximum long-term mechanical work, $$B$$ is the mechanical equivalent of the available energy from anaerobic sources, and $$\tau$$ is the time constant describing the inertia of the system.

The curve is surprisingly linear over the distances I cover in my training. It turns out that for the equations above, the exponential quickly goes to zero as $$t$$ gets large (even by an hour), as does the $$B/t$$ term, and the $$t^2$$ term only starts to matter for large $$t$$ (many hours).

Plotting my (average) Speed vs Distance for my race training analysis I can include the equation above, using the same values for the parameters as were used in the 2004 paper. Note these values are the estimated human maximum so it shouldn't be surprising that my data falls comfortably below this line. **Way** below this line. I chose to plot Pace vs. Distance as it's the more relatable metric, in which case my data falls above the max-effort curve.

The really interesting thing to me though, is to use this data to help guide my next long run. I start strong on a long run then fall to pieces near the end. It would be great to use this data to help set my goal pace. I've spent a while thinking about how best to do this and have landed on the following treatment.
I'll simplify the equations above and simply fit to a quadratic, but I'll allow for the parabola to be tilted and offset in the rotated $$x$$ direction. The function below is fed into scipy.minimize, the result of which is a rotated-shifted parabola that sits nicely atop my data. Note the heavy $$dist^4$$ weighting given to the points. This is necessary as the majority of my runs are short and slow. Fitting this curve I really only care about the fastest runs at each distance. A filter to discard points far from the max-effort might improve the fit, but for now weighting heavily towards longer runs gives a good fit.

```py
def minfunc(fit):  # rotated-shifted parabola
    r = np.sqrt(bdist ** 2 + bspeed ** 2)
    th = np.arctan2(bspeed, bdist)
    x2, y2 = r * np.cos(th - fit[1]) - fit[2], r * np.sin(th - fit[1])  # rotate pts by -theta, shift x2 by fit[2]
    ydiff_0offset = y2 - fit[0] * x2 ** 2
    offset = max(ydiff_0offset)  # offset necessary so that curve is always >= data
    ydiff = y2 - (fit[0] * x2 ** 2 + offset)
    return np.sum(ydiff ** 2 * bdist ** 4)  # weight pts strongly by bdist
```

I struggled for a while to think of the best way to fit a curve to data with the constraint that it necessarily sit above the data (max effort has to be greater than or equal to existing efforts). The minimization above simply removes a degree of freedom (the $$r$$ offset value) and instead dynamically fixes this value during the minimization such that the difference $$curve-data$$ is everywhere positive.

<iframe src="/images/posts/rta_pvd.html" height="500" width="100%"></iframe>

A few things to note. Obviously the human-achievable curve is well beyond my performance, no surprise. But I do note that the slope of the human-achievable curve is shallower than mine, meaning my max pace suffers more for higher mileage. However, there are numerous complicating factors. My runs (especially the longer ones) are often done on trails, over very uneven and technical terrain, hardly ideal for setting a max pace. Many of my shorter runs also include two furry companions who, while being quite capable of matching my moving pace, are likely to stop for potty breaks. Hydration, nutrition, and rest impact my performance, as does the fact that I'm rarely *trying* for a max-paced run. With that in mind though, this is a very cool way to set goal paces for distances I haven't run in a long time, and (I think) a pretty insightful look into my training data.

Another common metric to monitor is your weekly total. So with a little processing I can see this trend in my data as well. Below is my weekly running total for the past number of years, a running 7 day average of my weekly totals (to reduce the variability and show me more of an average effort), and the individual runs that contribute to the totals.

<iframe src="/images/posts/rta_wklyav.html" height="500" width="100%"></iframe>

The most recent addition to the analysis is actually one that utilizes external data. Garmin has the capability of tracking gear usage so you can manage how many miles are on your shoes, but you have to update this data manually in the app. It'd be better if it asked you at the end of each activity, but c'est la vie. I submitted this feedback to Garmin, but while we wait for them to implement my ideas we'll make a workaround. I created a spreadsheet (I know, I know... a spreadsheet). Now whenever I run this code it looks in there and compares all my runs (rather just those since I began this manual-entry analysis) to the list of runs in the spreadsheet. If a run is in the app but not in my spreadsheet it pops up a window asking for a variety of information... which shoes I was wearing, pre-and post-run weight if I measured, how much fluid I drank, how many calories (and which kind) were consumed. It takes time to build up this data, but a clear dependence on ambient temperature is apparent, and gives me an idea of my fluid loss.

<iframe src="/images/posts/rta_man.html" height="800" width="100%"></iframe>
