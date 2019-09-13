#! /usr/bin/env python
# coding: latin-1
# e.g.
#  python monitor.py -n 10 -s 4 -T 28 -g 4
# csv:      https://docs.python.org/2/library/csv.html
# datetime: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
# subplots: https://matplotlib.org/devdocs/gallery/subplots_axes_and_figures/subplots_demo.html
# locator:  https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-locators.html
#           https://stackoverflow.com/questions/37219655/matplotlib-how-to-specify-time-locators-start-ticking-timestamp
# axis:     https://matplotlib.org/3.1.1/api/axes_api.html#axis-labels-title-and-legend
import os, sys, time, datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
from monitor import setTimeAxisMinorLocators


def monitor(**kwargs):
  """Start monitoring."""
  
  # SETTINGS
  batchmode = kwargs.get('batch',      False    )
  logname   = kwargs.get('out',      "data.dat" )
  figname   = kwargs.get('figname',  "plot"     )
  twidth    = kwargs.get('twidth',      1000    )
  ymin      = kwargs.get('ymin',          10    )
  ymax      = kwargs.get('ymax',          40    )
  dtback    = datetime.timedelta(days=1) # load only 1-day backlog for plot
  dtwidth   = datetime.timedelta(seconds=twidth)
  dtmargin  = datetime.timedelta(seconds=0.02*twidth)
  
  # LOAD PREVIOUS DATA
  tformat   = '%d-%m-%Y %H:%M:%S'
  tlast     = None
  tvals, tempvals, dewpvals, setpvals = [ ], [ ], [ ], [ ]
  runvals, airvals, dryvals = [ ], [ ], [ ]
  if os.path.isfile(logname):
    print "Loading old monitoring data..."
    with open(logname,'r') as logfile:
      logreader = csv.reader(logfile)
      tnow   = datetime.datetime.now()
      tback  = tnow - dtback
      for stamp, temp, setp, dewp, air, dry, run in logreader:
        tval = datetime.datetime.strptime(stamp,tformat)
        if tval<tback: continue
        tvals.append(tval)
        tempvals.append(temp)
        setpvals.append(setp)
        dewpvals.append(dewp)
        airvals.append(air)
        dryvals.append(dry)
        runvals.append(run)
        if not tlast or tlast<tval:
          tlast = tval
  
  # PLOT PARAMETERS
  tmin = tlast - dtwidth + dtmargin
  tmax = tlast + dtmargin
  
  # PLOT
  print "Making plot '%s'..."%figname
  fig   = plt.figure(figsize=(10,6),dpi=100)
  grid  = gridspec.GridSpec(2,1,height_ratios=[1,3],hspace=0.04,left=0.07,right=0.96,top=0.93,bottom=0.08)
  
  # STATUS SUBPLOT
  axis1 = plt.subplot(grid[0])
  axis1.set_title('Monitoring')
  axis1.axis([tmin, tmax, -0.2, 1.2])
  axis1.xaxis.set_tick_params(which='both',labelbottom=False)
  #axis1.set_yticks([0,1],['OFF','ON'])
  axis1.set_yticks([0,1])
  axis1.set_yticklabels(['OFF','ON'],fontsize=14)
  #axis2.yaxis.set_tick_params(fontsize=14)
  axis1.grid(axis='x',which='minor',linewidth=0.2)
  axis1.grid(axis='y',which='major',linewidth=0.2)
  airline, = axis1.plot(tvals,airvals,color='red',marker='o',label="Compr. air",linewidth=2,markersize=4)
  dryline, = axis1.plot(tvals,dryvals,color='blue',marker='v',label="Dryer",linewidth=1,markersize=4)
  axis1.legend(loc='center left',framealpha=0)
  
  # TEMPERATURE SUBPLOT
  axis2 = plt.subplot(grid[1],sharex=axis1)
  axis2.axis([tmin, tmax, ymin, ymax])
  setTimeAxisMinorLocators(axis2,twidth)
  axis2.xaxis.set_major_locator(mdates.HourLocator(byhour=[0,12]))
  #axis2.xaxis.set_major_locator(mdates.DayLocator())
  axis2.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M:%S"))
  axis2.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
  axis2.yaxis.set_tick_params(labelsize=14)
  axis2.xaxis.set_tick_params(pad=2,which='minor')
  axis2.xaxis.set_tick_params(pad=16)
  #axis2.set_xlabel("Time",fontsize=16)
  axis2.set_ylabel("Temperature [$^\circ$C]",fontsize=16)
  axis2.grid(axis='x',which='minor',linewidth=0.2)
  axis2.grid(axis='x',which='major',color='darkred',linewidth=1,linestyle='--')
  axis2.grid(axis='y',which='major',linewidth=0.2)
  templine, = axis2.plot(tvals,tempvals,color='red',marker='o',label="Temperature",linewidth=2,markersize=5)
  setpline, = axis2.plot(tvals,setpvals,color='darkgrey',marker='.',label="Target temp.",linewidth=0.5,markersize=5)
  dewpline, = axis2.plot(tvals,dewpvals,color='blue',marker='v',label="Dummy dewpoint",linewidth=1,markersize=5)
  axis2.legend(loc='upper left',framealpha=0)
  
  #fig.canvas.draw()
  #plt.show(block=True)
  fig.savefig(figname+".png")
  fig.savefig(figname+".pdf")
  

def main(args):
  
  # PARAMETERS
  kwargs = {
    'batch':     args.batchmode,
    'out':       args.output,    # name of log file
    'twidth':    args.twidth,    # width of time axis in seconds
  }
  
  # MONITOR
  monitor(**kwargs)
  

if __name__ == '__main__':
  from argparse import ArgumentParser
  description = '''Monitor climate chamber.'''
  parser = ArgumentParser(prog="monitor",description=description,epilog="Good luck!")
  parser.add_argument('-w', '--width',     dest='twidth', type=float, default=2400, action='store',
                                           help="width of time axis in seconds" )
  parser.add_argument('-o', '--output',    dest='output', type=str, default="monitor.dat", action='store',
                                           help="output log file with monitoring data (csv format)" )
  parser.add_argument('-b', '--batch',     dest='batchmode', default=False, action='store_true',
                                           help="monitor in batch mode (no GUI window)" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  main(args)
  
