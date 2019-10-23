#! /usr/bin/env python
# coding: latin-1
# e.g.
#  python monitor.py -n 10 -s 4 -T 28 -g 4
# datetime: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
# subplots: https://matplotlib.org/devdocs/gallery/subplots_axes_and_figures/subplots_demo.html
# locator:  https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-locators.html
#           https://stackoverflow.com/questions/37219655/matplotlib-how-to-specify-time-locators-start-ticking-timestamp
# axis:     https://matplotlib.org/3.1.1/api/axes_api.html#axis-labels-title-and-legend
import os, sys, time, datetime
import socket
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Button
from utils import warning, checkGUIMode
from plotter import setTimeAxisMinorLocators
import yocto_commands as YOCTO
from yocto_commands import connectYoctoMeteo, disconnectYoctoMeteo



def monitor(ymeteo1=None,ymeteo2=None,**kwargs):
  """Start monitoring."""
  
  # SETTINGS
  batchmode = kwargs.get('batch',      False    )
  logname   = kwargs.get('out',      "data_yocto.dat" )
  dtime     = kwargs.get('dtime',         -1    )
  nsamples  = kwargs.get('nsamples',      -1    )
  tstep     = kwargs.get('tstep',          4    )
  twidth    = kwargs.get('twidth',      1000    )
  ymin      = kwargs.get('ymin',           8.   )
  ymax      = kwargs.get('ymax',          40.   )
  dtback    = datetime.timedelta(days=2) # load only 1-day backlog for plot
  dtwidth   = datetime.timedelta(seconds=twidth)
  dtmargin  = datetime.timedelta(seconds=0.15*twidth)
  title     = "YoctoMeteo monitor"
  if nsamples>0 and dtime<0:
    dtime   = tstep*nsamples
  
  # BATCH MODE
  if batchmode:
    
    # START MONITORING
    with open(logname,'a+') as logfile:
      logger = csv.writer(logfile)
      print "Monitoring YoctoMeteo..."
      tval   = datetime.datetime.now()
      tstop  = tval + datetime.timedelta(seconds=dtime) if dtime>0 else None 
      if not ymeteo1:
        temp_YM1 = -1
        dewp_YM1 = -1
      if not ymeteo2:
        temp_YM2 = -1
        dewp_YM2 = -1
      print "  %20s: %10s %10s %10s %10s"%("timestamp","temp YM1","temp YM2","dewp YM1","dewp YM2")
      while not tstop or tstop>tval:
        tval    = datetime.datetime.now()
        if ymeteo1:
          temp_YM1 = ymeteo1.getTemp()
          dewp_YM1 = ymeteo1.getDewp()
        if ymeteo2:
          temp_YM2 = ymeteo2.getTemp()
          dewp_YM2 = ymeteo2.getDewp()
        else:
          temp_YM2 = -1.
          dewp_YM2 = -1.
        print "  %20s: %10.3f %10.3f %10.3f %10.3f"%(tval.strftime(tformat),temp_YM1,temp_YM2,dewp_YM1,dewp_YM2)
        logger.writerow([tval.strftime(tformat),temp_YM1,temp_YM2,dewp_YM1,dewp_YM2])
        time.sleep(tstep)
      print "Monitoring finished!"
  
  # GUI WINDOW
  else:
    
    # LOAD PREVIOUS DATA
    tformat = '%d-%m-%Y %H:%M:%S'
    tvals   = [ ]
    tempvals_YM1, tempvals_YM2, dewpvals_YM1, dewpvals_YM2 = [ ], [ ], [ ], [ ]
    if os.path.isfile(logname):
      print "Loading old monitoring data from '%s'..."%(logname)
      with open(logname,'r') as logfile:
        logreader = csv.reader(logfile)
        tnow   = datetime.datetime.now()
        tback  = tnow - dtback
        for stamp, temp_YM1, temp_YM2, dewp_YM1, dewp_YM2, air, dry, run in logreader:
          tval = datetime.datetime.strptime(stamp,tformat)
          if tval<tback: continue
          temp_YM1, temp_YM2, dewp_YM1, dewp_YM2 = float(temp_YM1), float(temp_YM2), float(dewp_YM1), float(dewp_YM2)
          tvals.append(tval)
          tempvals_YM1.append(temp_YM1)
          tempvals_YM2.append(temp_YM2)
          dewpvals_YM1.append(dewp_YM1)
          dewpvals_YM2.append(dewp_YM2)
          for yval in [temp_YM1,temp_YM2,dewp_YM1,dewp_YM2]:
            if   yval<ymin: ymin = yval
            elif yval>ymax: ymax = yval
    
    # MONITOR DATA
    with open(logname,'a+') as logfile:
      logger = csv.writer(logfile)
      
      # PLOT PARAMETERS
      tnow = datetime.datetime.now()
      tmin = tnow - dtwidth + dtmargin
      tmax = tnow + dtmargin
      
      # PLOT
      plt.ion()
      #fig, axes = plt.subplots(2, sharex=True) #, gridspec_kw={'hspace': 0}
      fig   = plt.figure(figsize=(10,6),dpi=100)
      grid  = gridspec.GridSpec(2,1,height_ratios=[1,3],hspace=0.04,left=0.07,right=0.96,top=0.92,bottom=0.16)
      
      ### STATUS SUBPLOT
      ##axis1 = plt.subplot(grid[0])
      ##axis1.set_title(title,fontsize=20) #,pad=10
      ##axis1.title.set_position([.5, 1.05])
      ##axis1.axis([tmin, tmax, -0.2, 1.2])
      ##axis1.xaxis.set_tick_params(which='both',labelbottom=False)
      ###axis1.set_yticks([0,1],['OFF','ON'])
      ##axis1.set_yticks([0,1])
      ##axis1.set_yticklabels(['OFF','ON'],fontsize=14)
      ###axis2.yaxis.set_tick_params(fontsize=14)
      ##axis1.grid(axis='x',which='minor',linewidth=0.2)
      ##axis1.grid(axis='x',which='major',linewidth=0.4,color='darkred',linestyle='--',dashes=(6,5))
      ##axis1.grid(axis='y',which='major',linewidth=0.2)
      ##airline, = axis1.plot(tvals,airvals,color='red',marker='o',label="Compr. air",linewidth=3,markersize=3)
      ##dryline, = axis1.plot(tvals,dryvals,color='blue',marker='^',label="Dryer",linewidth=2,markersize=2)
      ##legend1  = axis1.legend(loc='center left',framealpha=0.8,fontsize=13)
      ##legend1.get_frame().set_linewidth(0)
      
      # TEMPERATURE SUBPLOT
      axis2 = plt.subplot(grid[1]) #,sharex=axis1)
      axis2.axis([tmin, tmax, ymin, ymax])
      setTimeAxisMinorLocators(axis2,twidth)
      axis2.xaxis.set_major_locator(mdates.HourLocator(byhour=[0,12]))
      #axis2.xaxis.set_major_locator(mdates.DayLocator())
      axis2.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M:%S"))
      axis2.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
      axis2.yaxis.set_tick_params(labelsize=14)
      axis2.xaxis.set_tick_params(labelsize=12,pad=-0.05,which='minor')
      axis2.xaxis.set_tick_params(labelsize=12,pad=14,labelcolor='#520000')
      axis2.callbacks.connect('xlim_changed',setTimeAxisMinorLocators)
      #axis2.set_xlabel("Time",fontsize=16)
      axis2.set_ylabel("Temperature [$^\circ$C]",fontsize=16)
      axis2.grid(axis='x',which='minor',linewidth=0.2)
      axis2.grid(axis='x',which='major',linewidth=0.4,color='darkred',linestyle='--',dashes=(6,5))
      axis2.grid(axis='y',which='major',linewidth=0.2)
      templine_YM1, = axis2.plot(tvals,tempvals_YM1,'--',dashes=(5,5),color='blue',label="Temp. YM1",linewidth=0.5) #,marker='^',markersize=1
      templine_YM2, = axis2.plot(tvals,tempvals_YM2,'--',dashes=(5,5),color='limegreen',label="Temp. YM2",linewidth=0.5) #,marker='v',markersize=1
      dewpline_YM1, = axis2.plot(tvals,dewpvals_YM1,color='blue',marker='^',label="Dewpoint YM1",linewidth=1,markersize=5)
      dewpline_YM2, = axis2.plot(tvals,dewpvals_YM2,color='limegreen',marker='v',label="Dewpoint YM2",linewidth=1,markersize=4)
      legorder = [templine_YM1,templine_YM2,dewpline_YM1,dewpline_YM2]
      legend2  = axis2.legend(legorder,[l.get_label() for l in legorder],loc='upper left',framealpha=0.8,fontsize=13)
      legend2.get_frame().set_linewidth(0)
      axis1 = axis2
      
      # BUTTONS
      def zoomout(event):
        tmin, tmax = [mdates.num2date(t).replace(tzinfo=None) for t in axis1.get_xlim()]
        swidth   = 1.50*(tmax-tmin).total_seconds()
        newwidth = datetime.timedelta(seconds=swidth)
        axis1.set_xlim([tmax-newwidth,tmax])
        setTimeAxisMinorLocators(axis2,swidth)
        fig.canvas.draw()
      zoomoutframe  = plt.axes([0.07,0.01,0.14,0.06])
      zoomoutbutton = Button(zoomoutframe,'Zoom out',color='0.80',hovercolor='0.90')
      zoomoutbutton.on_clicked(zoomout)
      
      # START MONITORING
      print "Monitoring YoctoMeteo..."
      print "  %20s: %10s %10s %10s %10s"%("timestamp","temp YM1","temp YM2","dewp YM1","dewp YM2")
      tval  = datetime.datetime.now()
      tstop = tval + datetime.timedelta(seconds=dtime) if dtime>0 else None
      if not ymeteo1:
        temp_YM1 = -1
        dewp_YM1 = -1
      if not ymeteo2:
        temp_YM2 = -1
        dewp_YM2 = -1
      while not tstop or tstop>tval:
        if not plt.fignum_exists(fig.number):
          print "Monitor was closed!"
          break
        tval    = datetime.datetime.now()
        tvals.append(tval)
        if ymeteo1:
          temp_YM1 = ymeteo1.getTemp()
          dewp_YM1 = ymeteo1.getDewp()
          dewpvals_YM1.append(dewp_YM1)
          tempvals_YM1.append(temp_YM1)
          dewpline_YM1.set_xdata(tvals)
          dewpline_YM1.set_ydata(dewpvals_YM1)
          templine_YM1.set_xdata(tvals)
          templine_YM1.set_ydata(tempvals_YM1)
        if ymeteo2:
          temp_YM2 = ymeteo2.getTemp()
          dewp_YM2 = ymeteo2.getDewp()
          dewpvals_YM2.append(dewp_YM2)
          tempvals_YM2.append(temp_YM2)
          dewpline_YM2.set_xdata(tvals)
          dewpline_YM2.set_ydata(dewpvals_YM2)
          templine_YM2.set_xdata(tvals)
          templine_YM2.set_ydata(tempvals_YM2)
        print "  %20s: %10.3f %10.3f %10.3f %10.3f"%(tval.strftime(tformat),temp_YM1,temp_YM2,dewp_YM1,dewp_YM2)
        logger.writerow([tval.strftime(tformat),temp_YM1,temp_YM2,dewp_YM1,dewp_YM2])
        if (tval+dtmargin)>tmax:
          #print "  Resetting x-axis range..."
          tmin, tmax = [mdates.num2date(t).replace(tzinfo=None) for t in axis1.get_xlim()]
          axis1.set_xlim([tval-(tmax-tmin-dtmargin),tval+dtmargin])
        fig.canvas.draw()
        #fig.canvas.flush_events()
        twait = tstep-(datetime.datetime.now()-tval).total_seconds() # compensate latency
        if twait>0:
          plt.pause(twait)
        #time.sleep(tstep)
      
      print "Monitoring finished!"
      plt.show(block=True)
      #plt.waitforbuttonpress()
  


def main(args):
  
  # CHECKS
  args.batchmode = not checkGUIMode(args.batchmode)
  
  # PARAMETERS
  kwargs = {
    'batch':     args.batchmode,
    'out':       args.output,    # name of log file
    'dtime':     args.dtime,     # duration of datataking
    'nsamples':  args.nsamples,  # number of readings
    'tstep':     args.stepsize , # seconds
    'twidth':    args.twidth,    # width of time axis in seconds
  }
  
  # CONNECT
  print "Connecting to YoctoMeteo..."
  ymeteo1 = connectYoctoMeteo(YOCTO.ymeteo1)
  ymeteo2 = connectYoctoMeteo(YOCTO.ymeteo2)
  
  # MONITOR
  monitor(ymeteo1,ymeteo2,**kwargs)
  
  # DISCONNECT
  print "Closing connection..."
  disconnectYoctoMeteo()
  


if __name__ == '__main__':
  from argparse import ArgumentParser
  description = '''Monitor climate chamber.'''
  parser = ArgumentParser(prog="monitor",description=description,epilog="Good luck!")
  parser.add_argument('-t', '--time',      dest='dtime', type=int, default=-1, action='store',
                                           help="duration of data taking in seconds" )
  parser.add_argument('-n', '--nsamples',  dest='nsamples', type=int, default=-1, action='store',
                                           help="number of data readings; -1 for indefinite monitoring (until monitor window closes or monitoring is interrupted)" )
  parser.add_argument('-s', '--stepsize',  dest='stepsize', type=int, default=10, action='store',
                                           help="sampling frequency of data reading in seconds" )
  parser.add_argument('-w', '--width',     dest='twidth', type=float, default=1200, action='store',
                                           help="width of time axis in seconds" )
  parser.add_argument('-o', '--output',    dest='output', type=str, default="monitor_yocto.dat", action='store',
                                           help="output log file with monitoring data (csv format)" )
  parser.add_argument('-b', '--batch',     dest='batchmode', default=False, action='store_true',
                                           help="monitor in batch mode (no GUI window)" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  main(args)
  

