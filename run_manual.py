#! /usr/bin/env python
# coding: latin-1
# e.g.
#  python run_manual.py -T 28 -g 4
import os, sys, time, datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
from monitor import monitor
from commands import connectClimateChamber, executeSimServCmd, unpackSimServData
from argparse import ArgumentParser
description = '''Manually run climate chamber.'''
parser = ArgumentParser(prog="run_manual",description=description,epilog="Good luck!")
parser.add_argument('-T', '--target',    dest='target', type=float, default=20.0, action='store',
                                         help="target temperature in degrees Celsius" )
parser.add_argument('-g', '--gradient',  dest='gradient', type=float, default=5.0, action='store',
                                         help="gradient in K/min." )
#parser.add_argument('-r', '--run',       dest='run', default=False, action='store_true',
#                                         help="manual run" )
parser.add_argument('-t', '--time',      dest='dtime', type=int, default=-1, action='store',
                                         help="duration of data taking in seconds" )
parser.add_argument('-n', '--nsamples',  dest='nsamples', type=int, default=-1, action='store',
                                         help="number of data readings; -1 for indefinite monitoring (until monitor window closes or monitoring is interrupted)" )
parser.add_argument('-s', '--stepsize',  dest='stepsize', type=int, default=8, action='store',
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


def startManualRun(client,target=20.0,gradient=2):
  """Start manual run."""
  assert isinstance(target,float) or isinstance(target,int), "Target temperature (%s) is not a number!"%(target)
  print "Setting up manual run with target temperature = %.1f and gradient %.1f K/min..."%(target,gradient)
  executeSimServCmd(client,'SET CTRL_VAR SETPOINT',[1,target])
  executeSimServCmd(client,'SET GRAD_UP VAL', [1,gradient])
  executeSimServCmd(client,'SET GRAD_DWN VAL',[1,gradient])
  executeSimServCmd(client,'SET DIGI_OUT VAL', [7,1]) # AIR1  ON
  executeSimServCmd(client,'SET DIGI_OUT VAL',[8,0])  # DRYER OFF
  print "Starting manual run..."
  executeSimServCmd(client,'START MANUAL',[1,1])
  

def stopManualRun(client):
  """Stop manual run."""
  print "Stopping manual run..."
  executeSimServCmd(client,'START MANUAL',[1,0])
  

def main(args):
  
  # CHECKS
  args.batchmode = not checkGUIMode(args.batchmode)
  
  # CONNECT
  print "Connecting to climate chamber..."
  client = connectClimateChamber()
  
  # RUN & MONITOR
  target   = args.target
  gradient = args.gradient
  startManualRun(client,target=target,gradient=gradient)
  monitor(client,batch=args.batchmode,out=args.output,
                 nsamples=args.nsamples,tstep=args.stepsize,twidth=args.twidth)
  stopManualRun(client)
  
  # DISCONNECT
  print "Closing connection..."
  client.close()
  

if __name__ == '__main__':
  main(args)
  
