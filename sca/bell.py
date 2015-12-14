#! /usr/bin/python

# Copyright (C) 2015 Llorenç Garcia Martinez
#
# This file is part of Solar Cycle Alarm.
#
# Solar Cycle Alarm program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Solar Cycle Alarm program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from subprocess import Popen, PIPE
import os
from os import path
import configparser
import argparse
import time
import math
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(23, GPIO.FALLING)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(24, GPIO.FALLING)

class Main:
    def __init__(self):
        print("START")
        self.selfpath = path.abspath(path.dirname(__file__)) + "/"
        print(self.selfpath)
        parser = argparse.ArgumentParser()
        parser.add_argument("alarmName")
        args = parser.parse_args()
        self.section = args.alarmName

        self.config = configparser.ConfigParser()
        self.config.read(self.selfpath + "config")
        loop = self.config.get(self.section, 'Loop')
        self.audiofile = self.selfpath + self.config.get(self.section, 'SoundFile')
        print(self.audiofile)
        self.volume = float(self.config.get(self.section, 'Volume'))
        
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        audiosink = Gst.ElementFactory.make("alsasink", "alsasink")
        self.player.set_property("audio-sink", audiosink)

        if os.path.exists(self.audiofile):
            if(loop == '1'):
                self.player.connect("about-to-finish",self._loop)

            self.player.set_property("volume", self.volume)
            self.player.set_property("uri", "file://" + self.audiofile)
            self.player.set_state(Gst.State.PAUSED)
            bus = self.player.get_bus()
            
            if(loop == '1' ):
                automute = float(self.config.get(self.section, 'AutoMute'))*60
            else:
                bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ASYNC_DONE)
                automute = math.ceil(self.player.query_duration(Gst.Format.TIME)[1]/1000000000)

            self.player.set_state(Gst.State.PLAYING)
            
            startAlarm=time.perf_counter()
            while (time.perf_counter()-startAlarm < automute) and (True):
                time.sleep(1)
                if GPIO.event_detected(24):
                  self._reschedule()
                  print("Button repeat")
                  break
                if GPIO.event_detected(23):
                  print("Button stop")
                  break
              

            self.player.set_state(Gst.State.NULL)
            GPIO.cleanup()
        else:
            print("No such file")


        print("END")
    
    def _loop(self, message):
        self.player.set_property("uri", "file://" + self.audiofile)
        self.player.set_property("volume", self.volume)
        
    def _reschedule(self):
        cmd = Popen(["echo","python",self.selfpath + "bell.py",self.section],stdout=PIPE)
        repeatTime = self.config.get(self.section, 'RepeatTime')
        Popen(["at", "now", "+", repeatTime ,"minutes"],stdin=cmd.stdout)
        
        
if __name__ == "__main__":
    Gst.init(None)
    Main()