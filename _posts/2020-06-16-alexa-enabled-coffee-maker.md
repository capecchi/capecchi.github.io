---
layout: post
title: Alexa-enabled coffee maker
date: 2020-06-16
excerpt: The best part of waking up, now smart
#image: /images/posts/abt_bar.png
active: False
tags: Alexa ESP8266 adafruit
---

I'm hacking my coffee maker. We routinely set it up for the morning so that we can just get up and hit the button, but I want to take that further. The goal here is to utilize an ESP8266 to connect to the internet and when given a signal, turn the coffee maker on. The signal can either be Alexa or set to a specific time.

The first step is to figure out how the coffee maker works, and where we run into our first problem. For some reason they used a pair of *triangular drive* screws?! Who has a triangular screwdriver? But... after some thinking... what's a hexagon if not a triangle with its corners cut off? And everyone has a set of hex keys! So I got the bottom off after a little fussing.

The next puzzle is to figure out how the existing circuitry controls the coffee maker; the 110V AC wall power is converted to a 5V DC which controls the logic circuitry. The coffee maker does turn itself off when the all the water is gone so an initial "turn on" signal (5V) to the coffee maker should suffice. The existing circuitry is shown below in black.

![image](/images/posts/alexacoffee_circuit.png)
**Relevant coffee maker circuitry (black=existing, blue=Alexa-enabled addition make with circuit-diagram.org)**

To create our Alexa-controlled switch we can power the ESP8266 off of the 5V line, but need an LD1117V33 voltage regulator to get the 3.3V needed. Since the input to the rest of the circuitry is expecting 5V when the switch is closed we need to use the 3.3V output of the ESP8266 to control an N-channel MOSFET also running off the 5V line. So when we send a signal to the ESP8266 we'll raise the output pin to 3.3V (also the gate of the MOSFET), which will connect the source to the drain of the MOSFET, putting 5V into the coffee maker!
