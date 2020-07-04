---
layout: post
title: Alexa-enabled coffee maker
date: 2020-06-16
excerpt: The best part of waking up, now smart
#image: /images/posts/abt_bar.png
active: False
tags: Alexa
---

I'm hacking my coffee maker. We routinely set it up for the morning so that we can just get up and hit the button, but I want to take that further. The goal here is to utilize an ESP8266 to connect to the internet and when given a signal, turn the coffee maker on. The signal can either be Alexa or set to a specific time.

The first step is to figure out how the coffee maker works, and where we run into our first problem. For some reason they used a pair of *triangular drive* screws! Who has a triangular screwdriver? But... after some thinking... what's a hexagon if not a triangle with its corners cut off? And everyone has a set of hex keys! So I got the bottom off after a little fussing.

The next puzzle is to figure out how the switch works- I'll need to power the board (12V?) and send a switch signal (?V) when asked. The switch sits at 5V and shorts while toggle is pressed. The LED sits at 0V and jumps to 2V when switch is toggled. The coffee maker does turn itself off which must send another switch signal when the all the water is gone. The solution is to power the ESP8266 with the 5V line going to the switch and to wire an output pin to the other switch terminal. The output will sit at 0V (so we'll have 5V across switch = open) and when given a signal we'll raise the output pin to 5V (0V across switch = closed). The question now is whether I can run the ESP8266s I have on hand with 5V; right now I'm running them off of 3.3V.
