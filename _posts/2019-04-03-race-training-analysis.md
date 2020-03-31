---
layout: post
title: Race Training
date: 2019-04-03
excerpt: Analyzing my historical training efforts
#image: /images/posts/abt_bar.png
tags: StravaAPI
---

GPS watches are amazing, but I have years of underutilized activity data. Thanks to the Strava API though, I can compare how my current training effort compares to races I've done in the past.
Since GitHub (which hosts this site) is a static host, I can't dynamically make calls to the Strava API. Instead I run a `localhost` session to pull updated data, create the plots you see below and embed them as .html sources in an <iframe> element. So although they're not updated dynamically, they are still interactive.

Using the Strava API I can grab activities (and filter by type='Run') between certain dates. I've created a list of races and their corresponding race date, then go through and gather the runs I did in the 18 weeks prior to and including race day. By looking at run distance, cumulative distance, and pace, I can see how my current effort compares, helping me assess more realistically my readiness level for the upcoming race. The cumulative distance I find both the easiest to read and the most helpful in assessing my race-readiness.

<iframe src="/images/posts/rta_cum.html" height="500" width="800"></iframe>
**Cumulative distance run during training**

**March 2020 update**
I've been training for another 50k, and thinking about how pace varies with distance. I know if I train for a 5k I'll increase my pace as I get fitter. I also know I can run a 5k faster than a 10k. I've dealt a lot with the former point, trying to improve my pace for a given distance. The second point though is what interests me. At any given point of time (read: fixed level of fitness) there's a limit to how fast I can run a 5k, 10k, or any other distance. What does this curve of max-effort vs distance look like?

I found some literature on this: See this paper ([Formenti 2005](https://www.researchgate.net/publication/7696487_Human_locomotion_on_snow_Determinants_of_economy_and_speed_of_skiing_across_the_ages)) for the corrected and extended equations put forth in this paper ([Minetti 2004]((https://jeb.biologists.org/content/207/12/2185))).

They give the maximum sustainable speed as
\[
s = \frac{3.6}{C}\left(\frac{W_{mech}}{E_f} - W_{BASMET}\right)
\]
Where $E_f$ is the efficiency of muscle contraction, $W_{BASMET}$ is the basal metabolic power, and $C$ is a constant related to energy movement cost (J/kg/m).

The maximum sustainable long-term mechanical effort ($W_{mech}$, in Watts) to the duration of exercise ($t$, in seconds).


\[
W_{mech} = A \frac{0.085 \left(\frac{t}{3600}\right)^2-\frac{3.908 t}{3600} +91.82}{100} \left(1-
  \frac{\tau}{t} \left(1-e^{-\frac{t}{\tau}}\right) \right)+ \frac{B}{t}
\]

Where $A$ is the maximum long-term mechanical work, $B$ is the mechanical equivalent of the available energy from anaerobic sources, and $\tau$ is the time constant describing the inertia of the system.

The curve is surprisingly linear over the distances I cover in my training. It turns out that for the equations above, the exponential quickly goes to zero as $t$ gets large (even by an hour), as does the $B/t$ term, and the $t^2$ term only starts to matter for large $t$ (many hours).

The really interesting thing to me though, is to use this data to help guide my next long run. I just did a 17 miler a few days ago that started out very well for the first two hours then fell apart thereafter. It would be great to use this data to help set my goal pace. To do so, we'll simplify the above equation and only do a quadratic fit. However, it should be obvious that it's easy to go more *slowly* than your max sustainable effort, so we need to do a fit only to the highest values.

I achieved this by using `scipy.minimize` to write my own minimization function. I landed on
```py
def minfunc(fit):
    y_reduced = yy - (fit[0] * xx ** 2 + fit[1] * xx + fit[2])
    y_weighted = [1000. * y ** 2. if y > 0 else abs(y) for y in y_reduced]
    return np.sum(y_weighted)
```
This penalizes a fit for being above the data (by the magnitude of the distance) but *really* penalizes a fit for being below any data points. The result is the **Bill Max Effort** curve below.

Plotting my (average) Speed vs Distance for my race training analysis I can include the equation above, using the same values for the parameters as were used in the 2004 paper. Note these values are the estimated human maximum so it shouldn't be surprising that my data falls comfortably below this line.

<iframe src="/images/posts/rta_svd.html" height="500" width="800"></iframe>
**Speed vs Distance**
