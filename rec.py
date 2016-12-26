#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class
import time
import re
import speech_recognition as sr

def get_entries(entries, alt={}, mult=1):
    out = []
    sre = ''
    prob = 1/len(entries)
    for entry in entries:
        out = out + [(entry, alt.get(entry, prob*mult))]
        sre = sre + entry + '|'
    print (out)
    return re.compile('^(%s)' % sre[0:-1]), out

# this is called from the background thread
def callback(recognizer, audio):
    # recognize speech using Sphinx
    import pyautogui
    try:
        said = ''
        if recognizer.command_mode == 'direction':
            entries = ['front to back', 'side to side', 'up and down']
            entries_re, entries_kv = get_entries(entries)
            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
            m = entries_re.match(said)
            if m: 
                print ("%s\n" % m.group(0))
                recognizer.command_mode = 'to_waiting'

        if recognizer.command_mode == 'modify':
            entries = ['big letter', 'control', 'modify']
            entries_re, entries_kv = get_entries(entries)
            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
            m = entries_re.match(said)
            if m: 
                cmd = m.group(0)
                if cmd == 'big letter':
                    pyautogui.keyDown('shift')
                if cmd == 'control':
                    pyautogui.keyDown('ctrl')
                if cmd == 'modify':
                    pyautogui.keyDown('alt')
                print ("%s\n" % m.group(0))
                recognizer.command_mode = 'to_waiting'

        if recognizer.command_mode == 'control':
            entries = ['direction', 'modify']
            entries_re, entries_kv = get_entries(entries)
            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
            m = entries_re.match(said)
            if m: 
                print ("%s\n" % m.group(0))
                recognizer.command_mode = m.group(0)

        if recognizer.command_mode == 'waiting':
            entries = ['control', 'end']
            entries_re, entries_kv = get_entries(entries)
            said = recognizer.recognize_sphinx(audio, keyword_entries=entries_kv)
            m = entries_re.match(said)
            if m: 
                print ("%s\n" % m.group(0))
                if m.group(0) == 'end':
                    pyautogui.keyUp(key_down)
                else:
                    recognizer.command_mode = 'control'

        if recognizer.command_mode == 'to_waiting':
            recognizer.command_mode = 'waiting'

        print("Sphinx thinks you said " + said)
        time.sleep(1)
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))

r = sr.Recognizer()
m = sr.Microphone()

with m as source:
    r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening

r.command_mode = 'waiting' 
stop_listening = r.listen_in_background(m, callback)

print("Say something")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_listening()
    print("Quit")