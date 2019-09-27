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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import yocto_commands as YOCTO
from yocto_commands import connectYoctoMeteo
import numpy as np


def setTimeAxisMinorLocators(axis,twidth=None):
  """Help function to set time locators."""
  if twidth==None:
    tmin, tmax = [mdates.num2date(t).replace(tzinfo=None) for t in axis.get_xlim()]
    twidth = (tmax - tmin).total_seconds()
  if twidth>700:
    axis.xaxis.set_minor_locator(mdates.MinuteLocator(interval=int(twidth/400)))
  elif twidth>400:
    axis.xaxis.set_minor_locator(mdates.MinuteLocator())
  elif twidth>200:
    axis.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=[0,30]))
  elif twidth>135:
    axis.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=[0,20,40]))
  elif twidth>80:
    axis.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=[i*10 for i in xrange(6)]))
  else:
    axis.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=[i*2 for i in xrange(30)]))
  

def plotter(**kwargs):
  """Start monitoring."""
  
  # SETTINGS
  batchmode = kwargs.get('batch',  False      )
  logname   = kwargs.get('log',    "data.dat" )
  figname   = kwargs.get('name',   "plot"     )
  title     = kwargs.get('title',  None       )
  twidth    = kwargs.get('twidth', 1000       )
  ymin      = kwargs.get('ymin',     10       )
  ymax      = kwargs.get('ymax',     40       )
  dtback    = datetime.timedelta(days=2) # load only 1-day backlog for plot
  dtwidth   = datetime.timedelta(seconds=twidth)
  dtmargin  = datetime.timedelta(seconds=0.02*twidth)
  if title==None:
    title = "Climate chamber monitor"
  
  # LOAD PREVIOUS DATA
  tformat   = '%d-%m-%Y %H:%M:%S'
  tlast     = None
  tvals, tempvals, setpvals = [ ], [ ], [ ]
  tempvals_YM1, tempvals_YM2, dewpvals_YM1, dewpvals_YM2 = [ ], [ ], [ ], [ ]
  runvals, airvals, dryvals = [ ], [ ], [ ]
  if os.path.isfile(logname):
    print "Loading old monitoring data from '%s'..."%(logname)
    with open(logname,'r') as logfile:
      logreader = csv.reader(logfile)
      tnow   = datetime.datetime.now()
      tback  = tnow - dtback
      for stamp, temp, setp, temp_YM1, temp_YM2, dewp_YM1, dewp_YM2, air, dry, run in logreader:
        tval = datetime.datetime.strptime(stamp,tformat)
        if tval<tback: continue
        temp, setp = float(temp), float(setp)
        temp_YM1, temp_YM2, dewp_YM1, dewp_YM2 = float(temp_YM1), float(temp_YM2), float(dewp_YM1), float(dewp_YM2)
        air, dry, run = int(air), int(dry), int(run)
        tvals.append(tval)
        tempvals.append(temp)
        setpvals.append(setp)
        tempvals_YM1.append(temp_YM1)
        tempvals_YM2.append(temp_YM2)
        dewpvals_YM1.append(dewp_YM1)
        dewpvals_YM2.append(dewp_YM2)
        airvals.append(air)
        dryvals.append(dry)
        runvals.append(run)
        if not tlast or tlast<tval:
          tlast = tval
        for yval in [temp,temp_YM1,temp_YM2,dewp_YM1,dewp_YM2]:
          if   yval<ymin: ymin = yval
          elif yval>ymax: ymax = yval
  
  # PLOT PARAMETERS
  tmin = tlast - dtwidth + dtmargin
  tmax = tlast + dtmargin
  
  # PLOT
  print "Making plot '%s'..."%figname
  fig   = plt.figure(figsize=(10,6),dpi=100)
  grid  = gridspec.GridSpec(2,1,height_ratios=[1,3],hspace=0.04,left=0.07,right=0.96,top=0.92,bottom=0.08)
  
  # STATUS SUBPLOT
  axis1 = plt.subplot(grid[0])
  axis1.set_title(title,fontsize=20) #,pad=10
  axis1.title.set_position([.5,1.05])
  axis1.axis([tmin,tmax,-0.2,1.2])
  axis1.xaxis.set_tick_params(which='both',labelbottom=False)
  #axis1.set_yticks([0,1],['OFF','ON'])
  axis1.set_yticks([0,1])
  axis1.set_yticklabels(['OFF','ON'],fontsize=14)
  #axis2.yaxis.set_tick_params(fontsize=14)
  axis1.grid(axis='x',which='minor',linewidth=0.2)
  axis1.grid(axis='x',which='major',linewidth=0.4,color='darkred',linestyle='--',dashes=(6,5))
  axis1.grid(axis='y',which='major',linewidth=0.2)
  airline, = axis1.plot(tvals,airvals,color='red',marker='o',label="Compr. air",linewidth=3,markersize=4)
  dryline, = axis1.plot(tvals,dryvals,color='blue',marker='v',label="Dryer",linewidth=2,markersize=4)
  legend1  = axis1.legend(loc='center left',framealpha=0.8,fontsize=14)
  legend1.get_frame().set_linewidth(0)
  
  # TEMPERATURE SUBPLOT
  axis2 = plt.subplot(grid[1],sharex=axis1)
  axis2.axis([tmin, tmax, ymin, ymax])
  setTimeAxisMinorLocators(axis2,twidth)
  axis2.xaxis.set_major_locator(mdates.HourLocator(byhour=[0,12]))
  #axis2.xaxis.set_major_locator(mdates.DayLocator())
  axis2.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M:%S"))
  axis2.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
  axis2.yaxis.set_tick_params(labelsize=14)
  axis2.xaxis.set_tick_params(labelsize=12,pad=4,which='minor')
  axis2.xaxis.set_tick_params(labelsize=12,pad=18,labelcolor='#520000')
  #axis2.set_xlabel("Time",fontsize=16)
  axis2.set_ylabel("Temperature [$^\circ$C]",fontsize=16)
  axis2.grid(axis='x',which='minor',linewidth=0.2)
  axis2.grid(axis='x',which='major',linewidth=0.4,color='darkred',linestyle='--',dashes=(6,5))
  axis2.grid(axis='y',which='major',linewidth=0.2)
  setpline, = axis2.plot(tvals,setpvals,color='darkgrey',marker='.',label="Target temp.",linewidth=0.5,markersize=4)
  templine_YM1, = axis2.plot(tvals,tempvals_YM1,'--',dashes=(5,5),color='blue',label="Temp. YM1",linewidth=0.5) #,marker='^',markersize=1
  templine_YM2, = axis2.plot(tvals,tempvals_YM2,'--',dashes=(5,5),color='limegreen',label="Temp. YM2",linewidth=0.5) #,marker='v',markersize=1
  templine, = axis2.plot(tvals,tempvals,color='red',marker='o',label="Temperature",linewidth=2,markersize=4)
  dewpline_YM1, = axis2.plot(tvals,dewpvals_YM1,color='blue',marker='^',label="Dewpoint YM1",linewidth=1,markersize=5)
  dewpline_YM2, = axis2.plot(tvals,dewpvals_YM2,color='limegreen',marker='v',label="Dewpoint YM2",linewidth=1,markersize=4)
  legorder = [templine,setpline,templine_YM1,templine_YM2,dewpline_YM1,dewpline_YM2]
  legend2  = axis2.legend(legorder,[l.get_label() for l in legorder],loc='upper left',framealpha=0.8,fontsize=13)
  legend2.get_frame().set_linewidth(0)
  
  #fig.canvas.draw()
  #plt.show(block=True)
  fig.savefig(figname+".png",dpi=200)
  fig.savefig(figname+".pdf",dpi=200)
  

def main(args):
  
  # MONITOR
  plotter(log=args.input,name=args.output,
          twidth=args.twidth,title=args.title,batch=args.batchmode)
  

if __name__ == '__main__':
  from argparse import ArgumentParser
  description = '''Plot climate chamber monitoring data.'''
  parser = ArgumentParser(prog="plotter",description=description,epilog="Good luck!")
  parser.add_argument('-w', '--width',     dest='twidth', type=float, default=2400, action='store',
                                           help="width of time axis in seconds" )
  parser.add_argument('-i', '--input',     dest='input', type=str, default="monitor.dat", action='store',
                                           help="input log file with monitoring data (csv format)" )
  parser.add_argument('-o', '--output',    dest='output', type=str, default="plot", action='store',
                                           help="name of output plot (png and pdf)" )
  parser.add_argument('-t', '--title',     dest='title', type=str, default=None, action='store',
                                           help="title of the plot" )
  parser.add_argument('-b', '--batch',     dest='batchmode', default=False, action='store_true',
                                           help="monitor in batch mode (no GUI window)" )
  parser.add_argument('-m', '--monitor',   dest='monitor', default=False, action='store_true',
                                           help="monitor warnings and alarms" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  main(args)
  
