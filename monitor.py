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
import socket
import csv
from plotter import setTimeAxisMinorLocators
from commands import connectClimateChamber, executeSimServCmd, unpackSimServData,\
                     forceWarmUp, stopClimateBox, checkActiveWarnings, openActiveWarnings,\
                     getRunStatus
from yocto_commands import connectYoctoMeteo

def importMatPlotLib():
  import matplotlib.pyplot as plt
  import matplotlib.dates as mdates
  import matplotlib.gridspec as gridspec
  from matplotlib.widgets import Button


def monitor(chamber,ymeteo1,ymeteo2,sensor,**kwargs):
  """Start monitoring."""
  
  # SETTINGS
  batchmode = kwargs.get('batch',      False    )
  logname   = kwargs.get('out',      "data.dat" )
  dtime     = kwargs.get('dtime',         -1    )
  nsamples  = kwargs.get('nsamples',      -1    )
  tstep     = kwargs.get('tstep',          4    )
  twidth    = kwargs.get('twidth',      1000    )
  ymin      = kwargs.get('ymin',          10    )
  ymax      = kwargs.get('ymax',          40    )
  dtback    = datetime.timedelta(days=2) # load only 1-day backlog for plot
  dtwidth   = datetime.timedelta(seconds=twidth)
  dtmargin  = datetime.timedelta(seconds=0.15*twidth)
  title     = "Climate chamber monitor"
  if nsamples>0 and dtime<0:
    dtime   = tstep*nsamples
  
  # BATCH MODE
  if batchmode:
    
    # START MONITORING
    with open(logname,'a+') as logfile:
      logger = csv.writer(logfile)
      print "Monitoring climate chamber..."
      tval   = datetime.datetime.now()
      tstop  = tval + datetime.timedelta(seconds=dtime) if dtime>0 else None 
      print "  %14s: %8s %8s %8s %8s %8s %8s"%("timestamp","temp","setp","temp YM1","temp YM2","dewp YM1","dewp YM2")
      while not tstop or tstop>tval:
        tval     = datetime.datetime.now()
        temp     = chamber.getTemp()
        setp     = chamber.getSetp()
        temp_YM1 = ymeteo1.getTemp()
        temp_YM2 = ymeteo2.getTemp()
        dewp_YM1 = ymeteo1.getDewp()
        dewp_YM2 = ymeteo2.getDewp()
        air      = chamber.getAir()
        dry      = chamber.getDryer()
        run      = 0
        updateStatus()
        checkWarnings()
        print "  %14s: %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f"%(tval.strftime(tformat),temp,setp,temp_YM1,temp_YM2,dewp_YM1,dewp_YM2)
        logger.writerow([tval.strftime(tformat),temp,setp,temp_YM1,temp_YM2,dewp_YM1,dewp_YM2,air,dry,run])
        time.sleep(tstep)
      print "Monitoring finished!"
    
  # GUI WINDOW
  else:
    
    # LOAD PREVIOUS DATA
    tformat    = '%d-%m-%Y %H:%M:%S'
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
      
      # STATUS SUBPLOT
      axis1 = plt.subplot(grid[0])
      axis1.set_title(title,fontsize=20) #,pad=10
      axis1.title.set_position([.5, 1.05])
      axis1.axis([tmin, tmax, -0.2, 1.2])
      axis1.xaxis.set_tick_params(which='both',labelbottom=False)
      #axis1.set_yticks([0,1],['OFF','ON'])
      axis1.set_yticks([0,1])
      axis1.set_yticklabels(['OFF','ON'],fontsize=14)
      #axis2.yaxis.set_tick_params(fontsize=14)
      axis1.grid(axis='x',which='minor',linewidth=0.2)
      axis1.grid(axis='y',which='major',linewidth=0.2)
      airline, = axis1.plot(tvals,airvals,color='red',marker='o',label="Compr. air",linewidth=2,markersize=4)
      dryline, = axis1.plot(tvals,dryvals,color='blue',marker='^',label="Dryer",linewidth=1,markersize=4)
      axis1.legend(loc='center left',framealpha=0,fontsize=14)
      
      # TEMPERATURE SUBPLOT
      axis2 = plt.subplot(grid[1],sharex=axis1)
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
      axis2.grid(axis='x',which='major',color='darkred',linewidth=1,linestyle='--')
      axis2.grid(axis='y',which='major',linewidth=0.2)
      templine, = axis2.plot(tvals,tempvals,color='red',marker='o',label="Temperature",linewidth=2,markersize=5)
      setpline, = axis2.plot(tvals,setpvals,color='darkgrey',marker='.',label="Target temp.",linewidth=0.5,markersize=5)
      dewpline_YM1, = axis2.plot(tvals,dewpvals,color='blue',marker='^',label="Dewpoint 1",linewidth=1,markersize=5)
      dewpline_YM2, = axis2.plot(tvals,dewpvals,color='purple',marker='^',label="Dewpoint 2",linewidth=1,markersize=5)
      axis2.legend(loc='upper left',framealpha=0,fontsize=14)
      
      # TEXT
      statustext = plt.text(0.98,0.98,"UNSET",horizontalalignment='right',verticalalignment='top',
                            transform=axis2.transAxes,fontweight='bold')
      statuscolors = { 'Manual': 'saddlebrown', 'Program': 'navy', 'Not': 'darkgreen' }
      def updateStatus():
        status = getRunStatus(chamber)
        statustext.set_text(status)
        for key in statuscolors:
          if key in status:
            statustext.set_color(statuscolors[key]); break
      updateStatus()
      
      # BUTTONS
      def zoomout(event):
        tmin, tmax = [mdates.num2date(t).replace(tzinfo=None) for t in axis1.get_xlim()]
        swidth   = 1.50*(tmax-tmin).total_seconds()
        newwidth = datetime.timedelta(seconds=swidth)
        axis1.set_xlim([tmax-newwidth,tmax])
        setTimeAxisMinorLocators(axis2,swidth)
        fig.canvas.draw()
      def checkWarnings():
        nwarn = checkActiveWarnings(chamber)
        if nwarn>0:
          messagebutton.active = True
          messageframe.set_visible(True)
          messagebutton.color = 'orange'
          messagebutton.label.set_text("%d warning%s!"%(nwarn,'s' if nwarn>1 else ''))
          messagebutton.label.set_fontweight('bold')
        else:
          messagebutton.active = False
          messageframe.set_visible(False)
      zoomoutframe  = plt.axes([0.07,0.01,0.14,0.06])
      zoomoutbutton = Button(zoomoutframe,'Zoom out',color='0.80',hovercolor='0.90')
      zoomoutbutton.on_clicked(zoomout)
      stopframe     = plt.axes([0.22,0.01,0.14,0.06])
      stopbutton    = Button(stopframe,'Stop Run',color='red')
      stopbutton.label.set_fontweight('bold')
      stopbutton.on_clicked(lambda e: stopClimateBox(chamber))
      plt.setp(stopframe.spines.values(),linewidth=2,color='darkred')
      warmframe     = plt.axes([0.37,0.01,0.14,0.06])
      warmbutton    = Button(warmframe,'Force warm',color='red')
      warmbutton.label.set_fontweight('bold')
      warmbutton.on_clicked(lambda e: forceWarmUp(chamber))
      plt.setp(warmframe.spines.values(),linewidth=2,color='darkred')
      messageframe  = plt.axes([0.52,0.01,0.15,0.06])
      messagebutton = Button(messageframe,'No warnings',color='orange')
      messagebutton.on_clicked(lambda e: openActiveWarnings(chamber))
      plt.setp(messageframe.spines.values(),linewidth=2,color='red')
      checkWarnings()
      
      # START MONITORING
      print "Monitoring climate chamber..."
      print "  %14s: %8s %8s %8s %8s %8s %8s"%("timestamp","temp","setp","temp YM1","temp YM2","dewp YM1","dewp YM2")
      tval  = datetime.datetime.now()
      tstop = tval + datetime.timedelta(seconds=dtime) if dtime>0 else None 
      while not tstop or tstop>tval:
        if not plt.fignum_exists(fig.number):
          print "Monitor was closed!"
          break
        temp     = chamber.getTemp()
        setp     = chamber.getSetp()
        temp_YM1 = ymeteo1.getTemp()
        temp_YM2 = ymeteo2.getTemp()
        dewp_YM1 = ymeteo1.getDewp()
        dewp_YM2 = ymeteo2.getDewp()
        air      = chamber.getAir()
        dry      = chamber.getDryer()
        air      = chamber.getAir()
        dry      = chamber.getDryer()
        run      = 0
        tvals.append(tval)
        tempvals.append(temp)
        setpvals.append(setp)
        dewpvals.append(dewp)
        airvals.append(air)
        dryvals.append(dry)
        runvals.append(run)
        # TODO: interlock
        updateStatus()
        checkWarnings()
        print "  %14s: %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f"%(tval.strftime(tformat),temp,setp,temp_YM1,temp_YM2,dewp_YM1,dewp_YM2)
        logger.writerow([tval.strftime(tformat),temp,setp,temp_YM1,temp_YM2,dewp_YM1,dewp_YM2,air,dry,run])
        templine.set_xdata(tvals)
        templine.set_ydata(tempvals)
        setpline.set_xdata(tvals)
        setpline.set_ydata(setpvals)
        dewpline.set_xdata(tvals)
        dewpline.set_ydata(dewpvals)
        dewpline.set_xdata(tvals)
        dewpline.set_ydata(dewpvals)
        airline.set_xdata(tvals)
        airline.set_ydata(airvals)
        dryline.set_xdata(tvals)
        dryline.set_ydata(dryvals)
        if (tval+dtmargin)>tmax:
          #print "  Resetting x-axis range..."
          tmin, tmax = [mdates.num2date(t).replace(tzinfo=None) for t in axis1.get_xlim()]
          axis1.set_xlim([tval-(tmax-tmin-dtmargin),tval+dtmargin])
        fig.canvas.draw()
        #fig.canvas.flush_events()
        plt.pause(tstep)
        #time.sleep(tstep)
      
      print "Monitoring finished!"
      plt.show(block=True)
      #plt.waitforbuttonpress()
  

def main(args):
  
  # OPTIONAL IMPORTS
  if not args.batchmode:
    importMatPlotLib()
  
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
  print "Connecting to climate chamber..."
  chamber = connectClimateChamber()
  ymeteo1 = connectYoctoMeteo('METEOMK1-28B37')
  ymeteo2 = connectYoctoMeteo('METEOMK1-28AF9')
  
  # MONITOR
  monitor(chamber,ymeteo1,ymeteo2,**kwargs)
  
  # DISCONNECT
  print "Closing connection..."
  chamber.close()
  

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
  parser.add_argument('-w', '--width',     dest='twidth', type=float, default=1000, action='store',
                                           help="width of time axis in seconds" )
  parser.add_argument('-o', '--output',    dest='output', type=str, default="monitor.dat", action='store',
                                           help="output log file with monitoring data (csv format)" )
  parser.add_argument('-b', '--batch',     dest='batchmode', default=False, action='store_true',
                                           help="monitor in batch mode (no GUI window)" )
  parser.add_argument('-v', '--verbose',   dest='verbose', default=False, action='store_true',
                                           help="set verbose" )
  args = parser.parse_args()
  main(args)
  
