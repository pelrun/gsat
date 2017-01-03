"""----------------------------------------------------------------------------
   device_grbl.py

   Copyright (C) 2013-2017 Wilhelm Duembeg

   This file is part of gsat. gsat is a cross-platform GCODE debug/step for
   Grbl like GCODE interpreters. With features similar to software debuggers.
   Features such as breakpoint, change current program counter, inspection
   and modification of variables.

   gsat is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 2 of the License, or
   (at your option) any later version.

   gsat is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with gsat.  If not, see <http://www.gnu.org/licenses/>.

----------------------------------------------------------------------------"""
try:
    import simplejson as json
except ImportError:
    import json

import re

import modules.device_base as devbase

# -----------------------------------------------------------------------------
# regular expressions
# -----------------------------------------------------------------------------
# -------------
# Grbl

# grbl version, example "Grbl 0.8c ['$' for help]"
gReGrblVersion = re.compile(r'Grbl\s*(.*)\s*\[.*\]')

# status,
# quick re check to avoid multiple checks, speeds things up
gReMachineStatus = re.compile(r'pos', re.I)

# GRBL example "<Run,MPos:20.163,0.000,0.000,WPos:20.163,0.000,0.000>"
gReGRBLMachineStatus = re.compile(r'<(\w+)[,\|].*WPos:([+-]{0,1}\d+\.\d+),([+-]{0,1}\d+\.\d+),([+-]{0,1}\d+\.\d+)')

# grbl ack, example  "ok"
gReGRBLMachineAck = re.compile(r'^ok\s$')

# grbl error, example  "error:20"
gReGRBLMachineError = re.compile(r'^error:(\d+)\s$')


"""----------------------------------------------------------------------------
   gsatDevice_GRBL:

   Device GRBL class.

----------------------------------------------------------------------------"""
class gsatDevice_GRBL(devbase.gsatDeviceBase):
   def __init__(self, cmd_line_options):
      devbase.gsatDeviceBase.__init__(self, cmd_line_options)

   def Encode(self, data):
      # for now do nothing...
      return data

   def Decode(self, data):
      dataDict = {}

      # GRBL status data
      rematch = gReGRBLMachineStatus.match(data)
      # data is expected to be an array of strings as follows
      # statusData[0] : Machine state
      # statusData[1] : Machine X
      # statusData[2] : Machine Y
      # statusData[3] : Machine Z
      # statusData[4] : Work X
      # statusData[5] : Work Y
      # statusData[6] : Work Z

      if rematch is not None:
         statusData = rematch.groups()
         sr = {}

         sr['stat'] = statusData[0]
         sr['posx'] = float(statusData[1])
         sr['posy'] = float(statusData[2])
         sr['posz'] = float(statusData[3])

         dataDict['sr'] = sr

         if self.cmdLineOptions.vverbose:
            print "** gsatDevice_GRBL re GRBL status match %s" % str(statusData)
            print "** gsatDevice_GRBL str match from %s" % str(data.strip())

      ack = gReGRBLMachineAck.search(data)
      if ack is not None:
         if self.cmdLineOptions.vverbose:
            print "** gsatDevice_GRBL found acknowledgement [%s]" % data.strip()
         r = {}
         dataDict['r'] = r
         dataDict['f'] = [0,0,0]

      error = gReGRBLMachineError.search(data)
      if error is not None:
         if self.cmdLineOptions.vverbose:
            print "** gsatDevice_GRBL found error [%s]" % data.strip()

         if 'r' not in dataDict:
            r = {}
            dataDict['r'] = r

         dataDict['f'] = [0,error.group(1),0]


      version = gReGrblVersion.match(data)
      if version is not None:
         if self.cmdLineOptions.vverbose:
            print "** gsatDevice_GRBL found device version [%s]" % version.group(1).strip()

         if 'r' not in dataDict:
            r = {}
            dataDict['r'] = r

         dataDict['r']['fv'] = version.group(1)
         dataDict['f'] = [0,0,0]

      return dataDict

   def GetSetAxisCmd (self):
      return "G92"
      
   def GetDeviceName(self):
      return "GRBL"

   def GetStatus(self):
      return '?\n'

   def InitComm(self):
      return self.GetStatus()

