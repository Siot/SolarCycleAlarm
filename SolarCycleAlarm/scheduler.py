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

from os import path
from subprocess import call, PIPE, Popen
import ephem
from datetime import datetime, timedelta
#from pytz import timezone
import pytz
import configparser

selfpath = path.abspath(path.dirname(__file__)) + "/"

config = configparser.ConfigParser()
config.read(selfpath + "config")

#set timezone
osLocaltime = path.realpath('/etc/localtime/')
osLocaltime = osLocaltime.replace('/usr/share/zoneinfo/','')
localtime = pytz.timezone(osLocaltime)

#set observer
obs = ephem.Observer()
obs.lat = config.get('DEFAULT', 'Latitude')
obs.long = config.get('DEFAULT', 'Longitude')
obs.date = datetime.now(pytz.utc)+timedelta(days=1)

#calculates next sunrise
sun = ephem.Sun()
riseTime = obs.next_rising(sun).datetime()
riseTime = riseTime.replace(tzinfo=pytz.utc)

#schedule alarms
for section in config.sections():
  tdM=int(config.get(section, 'TimeDeltaMinutes'))
  tdH=int(config.getint(section, 'TimeDeltaHours'))
  alarmTime = riseTime + timedelta(minutes=tdM,hours=tdH)
  alarmTime = alarmTime.astimezone(localtime).strftime("%H:%M")
  #print(alarmTime)
  cmd = Popen(["echo","python",selfpath + "gst_bell.py",section],stdout=PIPE)
  call(["at", alarmTime],stdin=cmd.stdout)
