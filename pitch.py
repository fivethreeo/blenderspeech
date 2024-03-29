#!/usr/bin/env python3
#Eng Eder de Souza 01/12/2011
#ederwander
from matplotlib.mlab import find
import matplotlib.pyplot as plt

import pyaudio
import numpy as np
import math


chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5


def Pitch(signal):
    signal = np.fromstring(signal, 'Int16')
    crossing = [math.copysign(1.0, s) for s in signal]
    index = find(np.diff(crossing));
    f0=round(len(index) *RATE /(2*np.prod(len(signal))))
    return f0;


p = pyaudio.PyAudio()
plotdata = bytes()

stream = p.open(format = FORMAT,
channels = CHANNELS,
rate = RATE,
input = True,
output = True,
frames_per_buffer = chunk)

for i in range(0, int(RATE / chunk * RECORD_SECONDS)):
    data = stream.read(chunk)
    plotdata += data
    Frequency=Pitch(data)
    print ("%f Frequency" % Frequency)

plt.figure(1)
plt.title('Signal Wave...')
plt.plot(np.fromstring(plotdata, 'Int16'))
plt.show()