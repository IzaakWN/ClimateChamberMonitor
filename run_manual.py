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
from utils import warning, checkGUIMode
from monitor import monitor
from commands import connectClimateChamber, sendSimServCmd, unpackSimServData
import yocto_commands as YOCTO
from yocto_commands import connectYoctoMeteo, disconnectYoctoMeteo
from argparse import ArgumentParser
description = '''Manually run climate chamber.'''
parser = ArgumentParser(prog="run_manual",description=description,epilog="Good luck!")
parser.add_argument('-T', '--target',    dest='target', type=float, default=20.0, action='store',
                                         help="target temperature in degrees Celsius" )
parser.add_argument('-g', '--gradient',  dest='gradient', type=float, default=5.0, action='store',
                                         help="gradient in K/min (>3.2 cooling, >3.5 heating)" )
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
parser.add_argument('-D', '--no-dryer',  dest='nodryer', default=False, action='store_true',
                                         help="turn OFF dryer (by default ON)" )
parser.add_argument('-A', '--no-air',    dest='noair', default=False, action='store_true',
                                         help="turn OFF compressed air (by default ON)" )
parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                         help="set verbose" )
args = parser.parse_args()


def startManualRun(chamber,target=20.0,gradient=3,air=True,dryer=True):
  """Start manual run."""
  assert isinstance(target,float) or isinstance(target,int), "Target temperature (%s) is not a number!"%(target)
  print "Setting up manual run with target temperature = %.1f and gradient %.1f K/min..."%(target,gradient)
  sendSimServCmd(chamber,'SET CTRL_VAR SETPOINT',[1,target])
  sendSimServCmd(chamber,'SET GRAD_UP VAL', [1,gradient])
  sendSimServCmd(chamber,'SET GRAD_DWN VAL',[1,gradient])
  sendSimServCmd(chamber,'SET DIGI_OUT VAL', [7,int(air)]) # AIR1  ON
  sendSimServCmd(chamber,'SET DIGI_OUT VAL',[8,int(dryer)])  # DRYER ON
  print "Starting manual run..."
  sendSimServCmd(chamber,'START MANUAL',[1,1])
  

def stopManualRun(chamber):
  """Stop manual run."""
  print "Stopping manual run..."
  sendSimServCmd(chamber,'START MANUAL',[1,0])
  

def main(args):
  
  # CHECKS
  args.batchmode = not checkGUIMode(args.batchmode)
  
  # CONNECT
  print "Connecting to climate chamber..."
  chamber = connectClimateChamber()
  ymeteo1 = connectYoctoMeteo(YOCTO.ymeteo1)
  ymeteo2 = connectYoctoMeteo(YOCTO.ymeteo2)
  
  # RUN & MONITOR
  target   = args.target
  gradient = args.gradient
  airon    = not args.noair
  dryeron  = not args.nodryer
  startManualRun(chamber,target=target,gradient=gradient,air=airon,dryer=dryeron)
  monitor(chamber,ymeteo1,ymeteo2,batch=args.batchmode,out=args.output,
                 nsamples=args.nsamples,tstep=args.stepsize,twidth=args.twidth)
  stopManualRun(chamber)
  
  # DISCONNECT
  print "Closing connection..."
  chamber.disconnect()
  disconnectYoctoMeteo()
  

if __name__ == '__main__':
  main(args)
  
