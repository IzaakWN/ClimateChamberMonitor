#! /usr/bin/env python
# coding: latin-1
import os, sys, time, datetime
import socket
from commands import connectClimateChamber, executeSimServCmd, unpackSimServData,\
                     getRunStatus, checkActiveWarnings, openActiveWarnings,\
                     getTemp, getSetp, getDewp, getAir, getDryer


def getCurrentStatus(**kwargs):
  """Get current status."""
  
  # SETTINGS
  ip       = kwargs.get(ip,    '130.60.164.144' )
  logname  = kwargs.get('out', "status.txt"     )
  tformat  = '%d-%m-%Y %H:%M:%S'
  
  # CONNECT
  print "Connecting to climate chamber..."
  client = connectClimateChamber(ip=ip)
  
  # WRITE STATUS
  with open(logname,'w+') as logfile:
    tnow = datetime.datetime.now()
    if client==None:
      string  = "Climate chamber not found in network (%s)."%(ip)
      string += "\n  time stamp:  %s"%(tval.strftime(tformat))
    else:
      string  = "Climate chamber's currect status (%s):"%(ip)
      string += "\n  time stamp:  %s"%(tval.strftime(tformat))
      string += "\n  setpoint:    %8.3f"%(getSetp(client))
      string += "\n  temperature: %8.3f"%(getTemp(client))
      string += "\n  dewpoint:    %8.3f"%(getDewp(client))
      string += "\n  compr. air:  %3s"%('ON' if getAir(client)==1 else 'OFF')
      string += "\n  dryer:       %3s"%('ON' if getDryer(client)==1 else 'OFF')
      string += "\n  alarms:      %d"%(checkActiveWarnings(client,1))
      string += "\n  warnings:    %d"%(checkActiveWarnings(client,2))
      string += "\n  messages:    %d"%(checkActiveWarnings(client,4))
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
  parser.add_argument('-o', '--output',    dest='output', type=str, default="monitor.dat", action='store',
                                           help="output log file with monitoring data (csv format)" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  main(args)
  
