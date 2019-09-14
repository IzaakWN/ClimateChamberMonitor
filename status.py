#! /usr/bin/env python
# coding: latin-1
import os, sys, time, datetime
import socket
from commands import connectClimateChamber, executeSimServCmd, unpackSimServData,\
                     getRunStatus, checkActiveWarnings, openActiveWarnings,\
                     getTemp, getSetp, getDewp, getAir, getDryer

def addRow(string,col1,col2,just=26):
  return string + '\n  ' + col1.ljust(just) + '  ' + col2.ljust(just)

def getCurrentStatus(**kwargs):
  """Get current status."""
  
  # SETTINGS
  ip       = kwargs.get('ip',  '130.60.164.144' )
  logname  = kwargs.get('out', "status.txt"     )
  tformat  = '%d-%m-%Y %H:%M:%S'
  
  # CONNECT
  print "Connecting to climate chamber..."
  client = connectClimateChamber(ip=ip)
  
  # WRITE STATUS
  print "Checking status..."
  with open(logname,'w+') as logfile:
    tnow = datetime.datetime.now()
    if client==None:
      string  = "Climate chamber not found in network."
      string += "\n  IP address:  %s"%(ip)
      string += "\n  time stamp:  %s"%(tnow.strftime(tformat))
    else:
      string  = "Climate chamber's currect status: %s"%(getRunStatus(client))
      addRow(string,"IP address:  %s"%(ip),
                    "compr. air:  %4s"%('ON' if getAir(client)==1 else 'OFF'))
      addRow(string,"time stamp:  %s"%(tnow.strftime(tformat)),
                    "dryer:       %4s"%('ON' if getDryer(client)==1 else 'OFF'))
      addRow(string,"setpoint:    %8.3f"%(getSetp(client)),
                    "alarms:      %4d"%(checkActiveWarnings(client,type=1)))
      addRow(string,"temperature: %8.3f"%(getTemp(client)),
                    "warnings:    %4d"%(checkActiveWarnings(client,type=2)))
      addRow(string,"dewpoint:    %8.3f"%(getDewp(client)),
                    "messages:    %4d"%(checkActiveWarnings(client,type=4)))
    print "Writing to '%s'"%logname
    print string
    logfile.write(string)   
  print "Status check finished!"
  
  # DISCONNECT
  print "Closing connection..."
  client.close()
  

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
  
