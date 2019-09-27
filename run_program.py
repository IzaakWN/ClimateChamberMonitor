#! /usr/bin/env python
# coding: latin-1
# e.g.
#  python run_program.py -p 2 -r 1
import os, sys, time, datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
from utils import warning, checkGUIMode
from monitor import monitor
from commands import connectClimateChamber, sendSimServCmd, unpackSimServData
import yocto_commands as YOCTO
from yocto_commands import connectYoctoMeteo, disconnectYoctoMeteo
from argparse import ArgumentParser
description = '''Run program in climate chamber.'''
parser = ArgumentParser(prog="run_program",description=description,epilog="Good luck!")
parser.add_argument('-p', '--program',   dest='prgmid', type=int, default=2, action='store',
                                         help="program number" )
parser.add_argument('-r', '--nruns',     dest='nruns', type=int, default=1, action='store',
                                         help="number of program runtroughs" )
parser.add_argument('-n', '--nsamples',  dest='nsamples', type=int, default=-1, action='store',
                                         help="number of data readings; -1 for indefinite monitoring (until monitor window closes or monitoring is interrupted)" )
parser.add_argument('-s', '--stepsize',  dest='stepsize', type=int, default=10, action='store',
                                         help="sampling frequency of data reading in seconds" )
parser.add_argument('-w', '--width',     dest='twidth', type=float, default=1000, action='store',
                                         help="width of time axis in seconds" )
parser.add_argument('-o', '--output',    dest='output', type=str, default="monitor.dat", action='store',
                                         help="output log file with monitoring data (csv format)" )
parser.add_argument('-b', '--batch',     dest='batchmode', default=False, action='store_true',
                                         help="monitor in batch mode (no GUI window)" )
parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                         help="set verbose" )
args = parser.parse_args()


def checkProgram(chamber,prgmid):
  """Check whether a program with given number exists,
  and return name if it does, otherwise None."""
  nprgm = sendSimServCmd(chamber,'GET PRGM NUM')
  assert prgmid<=nprgm, "Did not find program %d out of %d available programs"%(prgmid,nprgm)
  return True
  

def startProgram(chamber,prgmid,nruns=1):
  """Start manual run."""
  checkProgram(chamber,prgmid)
  print "Starting program %s..."%(prgmid)
  sendSimServCmd(chamber,'START PRGM',[prgmid,nruns])
  time.sleep(2)
  prgmname = str(sendSimServCmd(chamber,'GET PRGM NAME')[0])
  print "Started pogram '%s'"%(prgmname)
  

def stopProgram(chamber):
  """Stop manual run."""
  print "Stopping program..."
  sendSimServCmd(chamber,'STOP PRGM')
  

def main(args):
  
  # CHECKS
  args.batchmode = not checkGUIMode(args.batchmode)
  
  # CONNECT
  print "Connecting to climate chamber..."
  chamber = connectClimateChamber()
  ymeteo1 = connectYoctoMeteo(YOCTO.ymeteo1)
  ymeteo2 = connectYoctoMeteo(YOCTO.ymeteo2)
  
  # RUN & MONITOR
  prgmid    = args.prgmid
  nruns     = args.nruns
  startProgram(chamber,prgmid,nruns)
  monitor(chamber,ymeteo1,ymeteo2,batch=args.batchmode,out=args.output,
                 nsamples=args.nsamples,tstep=args.stepsize,twidth=args.twidth)
  stopProgram(chamber)
  
  # DISCONNECT
  print "Closing connection..."
  chamber.disconnect()
  disconnectYoctoMeteo()
  

if __name__ == '__main__':
  main(args)
  
