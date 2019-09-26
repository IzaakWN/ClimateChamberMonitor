#! /usr/bin/env python
# coding: latin-1
import os, sys, time, datetime
import socket
sys.path.append(os.path.dirname(__file__))
from commands import connectClimateChamber, sendSimServCmd, unpackSimServData, defaultip\
                     getRunStatus, checkActiveWarnings, getActiveWarnings
import yocto_commands as YOCTO
from yocto_commands import connectYoctoMeteo


def addRow(col1,col2,just=38):
  return '\n    ' + col1.ljust(just) + '  ' + col2.ljust(just)
  

def addTag(logname,tag):
  """Add tag before file extension."""
  if '_'!=tag[0]:
    tag = '_'+tag
  if '.' in logname:
    parts = logname.split('.')
    parts[-2] += tag
    logname = '.'.join(parts)
  else:
    logname = logname + tag
  return logname
  

def writeMessages(logname,messages,tag=""):
  """Write messages to file."""
  if tag:
    logname = addTag(logname,tag)
  with open(logname,'w+') as logfile:
    tnow = datetime.datetime.now()
    logfile.write(tnow.strftime('%d-%m-%Y %H:%M:%S'))
    for message in messages:
      logfile.write('\n'+message)
  

def getCurrentStatus(**kwargs):
  """Get current status."""
  
  # SETTINGS
  ip       = kwargs.get('ip',  '130.60.164.144' )
  logname  = kwargs.get('out', "status.txt"     )
  tformat  = '%d-%m-%Y %H:%M:%S'
  
  # CONNECT
  print "Connecting to climate chamber..."
  chamber = connectClimateChamber(ip=ip)
  ymeteo1 = connectYoctoMeteo(YOCTO.ymeteo1)
  ymeteo2 = connectYoctoMeteo(YOCTO.ymeteo2)
  
  # GET STATUS
  print "Checking status..."
  tnow = datetime.datetime.now()
  nalarms, nwarns, nmsgs = 0, 0, 0
  if chamber==None:
    string  = "  Climate chamber not found in network."
    string += addRow("IP address:  %s"%(ip),
                     "compr. air:  ")
    string += addRow("time stamp:  %s"%(tnow.strftime(tformat)),
                     "dryer:       ")
    string += addRow("setpoint:    ",
                     "alarms:      ")
    string += addRow("temperature: ",
                     "warnings:    ")
    string += addRow("temp. YM1:   ",
                     "messages:    ")
    string += addRow("temp. YM2:   ","")
    string += addRow("dewp. YM1:   ","")
    string += addRow("dewp. YM2:   ","")
  else:
    temp_YM1, temp_YM2, dewp_YM1, dewp_YM2 = "", "", "", ""
    if ymeteo1:
      temp_YM1 = "%.3f"%ymeteo1.getTemp()
      dewp_YM1 = "%.3f"%ymeteo1.getDewp()
    if ymeteo2:
      temp_YM2 = "%.3f"%ymeteo2.getTemp()
      dewp_YM2 = "%.3f"%ymeteo2.getDewp()
    nalarms  = checkActiveWarnings(chamber,type=1)
    nwarns   = checkActiveWarnings(chamber,type=2)
    nmsgs    = checkActiveWarnings(chamber,type=4)
    string   = "  Climate chamber's currect status: %s"%(getRunStatus(chamber))
    string  += addRow("IP address:  %s"%(ip),
                      "compr. air:  %4s"%('ON' if chamber.getAir()==1 else 'OFF'))
    string  += addRow("time stamp:  %s"%(tnow.strftime(tformat)),
                      "dryer:       %4s"%('ON' if chamber.getDryer()==1 else 'OFF'))
    string  += addRow("setpoint:    %8.3f"%(getSetp(chamber)),
                      "alarms:      %4d"%nalarms)
    string  += addRow("temperature: %8.3f"%(chamber.getTemp()),
                      "warnings:    %4d"%nwarns)
    string  += addRow("temp. YM1:   %8s"%(temp_YM1),
                      "messages:    %4d"%nmsgs)
    string  += addRow("temp. YM2:   %8s"%(temp_YM2),"")
    string  += addRow("dewp. YM1:   %8s"%(dewp_YM1),"")
    string  += addRow("dewp. YM2:   %8s"%(dewp_YM2),"")
  print "Status check finished!"
  
  # WRITE STATUS
  if logname:
    with open(logname,'w+') as logfile:
      print "Writing to '%s'"%logname
      print string
      print "Writing status to '%s'..."%logname
      logfile.write(string)
    if nalarms>0:
      messages = getActiveWarnings(chamber,type=1)
      writeMessages(logname,messages,tag="alarms")
    if nwarns>0:
      messages = getActiveWarnings(chamber,type=2)
      writeMessages(logname,messages,tag="warnings")
    if nmsgs>0:
      messages = getActiveWarnings(chamber,type=4)
      writeMessages(logname,messages,tag="messages")
  
  # DISCONNECT
  print "Closing connection..."
  chamber.disconnect()
  disconnectYoctoMeteo()
  

def main(args):
  
  # CHECK STATUS
  getCurrentStatus(out=args.output)
  

if __name__ == '__main__':
  from argparse import ArgumentParser
  description = '''Monitor climate chamber.'''
  parser = ArgumentParser(prog="monitor",description=description,epilog="Good luck!")
  parser.add_argument('-o', '--output',    dest='output', type=str, default="status.txt", action='store',
                                           help="output log file with monitoring data (csv format)" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  main(args)
  
