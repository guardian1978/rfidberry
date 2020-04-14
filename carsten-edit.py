#!/usr/bin/env python

import time
from sys import exit
import shlex, subprocess
#from subprocess import Popen
#from subprocess import PIPE
import drumhat
import serial
import sys
from operator import xor

leds = [False, False, False, False, False, False, False, False]

def get_rfid_data():
    ser = serial.Serial("/dev/ttyAMA0")
    ser.baudrate = 9600
    daten = ser.read(14)
    ser.close()
    daten = daten.replace("\x02", "start")
    daten = daten.replace("\x03", "stop")
    print(daten)
    daten = daten.replace("start","")
    daten = daten.replace("stop","")
    print "Id:", daten
    return daten

def write_tag(tag):
    #print("open file")
    f = open("tags.py", "a")
    #print("write to file")
    #print(tag)
    f.write(tag + '\n')
    #print("close file")
    f.close()
    #print("go back")
    return 0
    
def hit_handler(event):
    print("Hit on pad: {}".format(event.pad))
    if event.pad == 8:
        subprocess.call(["mpc", "toggle"])
        leds[event.pad-1] = not leds[event.pad-1]
        update_led(event.pad, leds[event.pad-1])
    elif event.pad == 3:
        subprocess.call(["mpc", "next"])
    elif event.pad == 6:
        subprocess.call(["mpc", "prev"])
    elif event.pad == 7:
        leds[event.pad-1] = not leds[event.pad-1]
        update_led(event.pad, leds[event.pad-1])
        AlbumId = get_rfid_data()
        leds[event.pad-1] = not leds[event.pad-1]
        update_led(event.pad, leds[event.pad-1])
        albumtitle = find_album(AlbumId)
        if albumtitle != -1:
            print albumtitle
            load_album(albumtitle)
    elif event.pad == 2:
        leds[event.pad-1] = not leds[event.pad-1]
        update_led(event.pad, leds[event.pad-1])
        
        TestId = get_rfid_data()
        write_tag(TestId)
        #f = open("inventary.py", "a")
        #f.write("%s\r\n", TestId)
        #f.close()
        print("Id written to inventary file.")
        albumtitle = find_album(TestId)

        leds[event.pad-1] = not leds[event.pad-1]
        update_led(event.pad, leds[event.pad-1])
        if albumtitle != -1:
            print albumtitle

def load_album(albumtitle):
    subprocess.call(["mpc", "stop"])
    leds[7] = False
    update_led(8, leds[7])
    subprocess.call(["mpc", "clear"])
    #p1 = Popen(["mpc", "search", "album", albumtitle], stdout = PIPE)
    #p2 = Popen(["mpc", "add"], stdin = p1.stdout)
    #p1.stdout.close()
    #output = p2.communicate()[0]
    #p1 = Popen(["mpc", "load", albumtitle], stdout = PIPE)
    subprocess.call(["mpc", "load", albumtitle])
    leds[7] = True
    update_led(8, leds[7])
    subprocess.call(["mpc", "play"])

def find_album(Id):
    print(Id)
    from inventary import albums
    try:
        album = albums[Id]
        print(album)
        return album
    except KeyError:
        print("Oops! Id not known")
        return -1
    

def update_led(pad, status):
    print("Turn LED on Pad %d to %r") %(pad, status)
    if status == True:
        drumhat.led_on(pad)
    else:
        drumhat.led_off(pad)


drumhat.on_hit(drumhat.PADS, hit_handler)

try:
    drumhat.auto_leds = False
    drumhat.all_off()
    pads = drumhat.PADS
    while True:
       time.sleep(1)

except KeyboardInterrupt:
    exit()
