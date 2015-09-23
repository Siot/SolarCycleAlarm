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
from os import path
import time
import argparse
import configparser
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(23, GPIO.FALLING)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(24, GPIO.FALLING)

def perform_command(ear, readFile, cmd, expect):
  import select
  os.write(ear, (cmd+"\n").encode())
  output = ""
  startQuery = time.perf_counter()
  while expect not in output: #Añadir tmeout!! por si expect no aparece nunca
    if time.perf_counter()-startQuery > 10:
      return "Query timeout"
    while select.select([readFile], [], [], 0.05)[0]: # give mplayer time to answer...
      output = readFile.readline()
  return output

selfpath = path.abspath(path.dirname(__file__)) + "/"

config = configparser.ConfigParser()
config.read(selfpath + "config")

parser = argparse.ArgumentParser()
parser.add_argument("alarmName")
args = parser.parse_args()
section = args.alarmName
automute = float(config.get(section, 'AutoMute'))*60
#print("automute: "+ str(automute))

mpListen_r, mpListen_w = os.pipe()
mpSays_r, mpSays_w = os.pipe()
mpStdout = os.fdopen(mpSays_r)

volume = config.get(section, 'Volume')
cmd = "mplayer -slave -quiet -ao alsa -nolirc -noconsolecontrols -loop 0 -softvol -volume " + volume + " " + selfpath + config.get(section,'SoundFile')
#print(cmd)
player = Popen(cmd.split(), stdin=mpListen_r, stdout=mpSays_w)

#no empezar a contar el tiempo hasta que no empieza a sonar realmente, ANS_pause=no
output = perform_command(mpListen_w, mpStdout, 'get_property pause', 'ANS_')
#print(output)

if "Query timeout" not in output:
  startAlarm=time.perf_counter()
  while (time.perf_counter()-startAlarm < automute) and (True):
    time.sleep(1)
    if GPIO.event_detected(24):
      reschedule = 1
      #print("reschedule!")
      break
    if GPIO.event_detected(23):
      reschedule = 0
      #print("no reschedule!")
      break

os.write(mpListen_w, "quit\n".encode())

if reschedule == 1:
  cmd = Popen(["echo","python",selfpath + "bell.py",section],stdout=PIPE)
  repeatTime = config.get(section, 'RepeatTime')
  Popen(["at", "now", "+", repeatTime ,"minutes"],stdin=cmd.stdout)
  #print("rescheduled")

GPIO.cleanup()
