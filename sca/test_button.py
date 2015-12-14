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

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(23, GPIO.FALLING)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(24, GPIO.FALLING)

while (True):
    if GPIO.event_detected(24):
        #reschedule = 1
        print("black - reschedule!")
        #break
    if GPIO.event_detected(23):
        #reschedule = 0
        print("red - no reschedule!")
        #break

GPIO.cleanup()