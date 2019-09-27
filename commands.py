#! /usr/bin/env python
# coding: latin-1
import os, sys
import socket
sys.path.append(os.path.dirname(__file__))
from utils import warning
if 'DISPLAY' in os.environ:
  import Tkinter
  from tkMessageBox import askyesno, showinfo
  root = Tkinter.Tk(); root.withdraw() # import before matplotlib

# CLIMATE CHAMBER IP
defaultip = '130.60.164.198' #'169.254.219.152'

# SIMSERV COMMAND
# CMD + SR + CBR + CR
# CMD + SR + CBR + SR + ARG + CR
# CMD = Command No. (5-digit)
# CBR = Chamber index
# ARG = Argument 1-4

# SEPARATORS
SR = b'\xb6' # separator character (ASCII code 182)
CR = b'\r'   # carriage return terminator (ASCII code 13)
LF = b'\n'   # line feed newline (ASCII code 10)

# RESPONSE CODES
err_dict = {
   1: "Command is accepted and executed.",
  -5: "Command number transmitted is unidentified!",
  -6: "Too few or incorrect parameters entered!",
  -8: "Data could not be read!",
}

# COMMAND DICT
cmd_dict = { }
cmd_dict['GET'] = {
  'CHAMBER': {
    'INFO':    99997,
    'STATUS':  10012, # 1: test not running, 3: test running,
                      # +4: warnings present, +8: alarms present
  },
  'CTRL_VAR': {
    'NUM':           11018,
    'NAME':          11026,
    'UNIT':          11023,
    'SETPOINT':      11002,
    'VAL':           11004, # read actual value (e.g. temperature)
    'INPUT_LIM_MIN': 11007,
    'INPUT_LIM_MAX': 11009,
    'WARN_LIM_MIN':  11016,
    'WARN_LIM_MAX':  11017,
    'ALARM_LIM_MIN': 11014,
    'ALARM_LIM_MAX': 11015,
  },
  'CTRL_VAL': {
    'NUM':           13007,
    'NAME':          13011,
    'UNIT':          13010,
    'SETPOINT':      13005,
    'INPUT_LIM_MIN': 13002,
    'INPUT_LIM_MAX': 13004,
  },
  'MEAS_VAL': {
    'NUM':           12012,
    'NAME':          12019,
    'UNIT':          12016,
    'VAL':           12002,
    'WARN_LIM_MIN':  12010,
    'WARN_LIM_MAX':  12011,
    'ALARM_LIM_MIN': 12008,
    'ALARM_LIM_MAX': 12009,
  },
  'DIGI_IN': {
    'NUM':           15004,
    'NAME':          15005,
    'VAL':           15002,
  },
  'DIGI_OUT': {
    'NUM':           14007,
    'NAME':          14010, # No.
    'VAL':           14003, # No.+1
  },
  'MSG': { # MESSAGES
    'NUM':           17002,
    'NAME':          17007,
    'TYPE':          17005, # 1: alarm, 2: warning, 4: info
    'CATEGORY':      17111, # 1: AlarmStop
    'TEXT':          17007,
    'STATUS':        17009, # 0: not active, 1: active
  },
  'ERROR': {
    'PLC_LIST':      17012, # No. active PLC errors, separated by <SR>
    'ID_LIST':       17012, # No. active ID errors, separated by <SR>
  },
  'GRAD_UP': { 
    'VAL':           11066,
  },
  'GRAD_DWN': { 
    'VAL':           11070,
  },
  'PRGM':{ # PROGRAM
    'NUM':           19204, # number of the program running
    'NAME':          19031,
    'LOOPS':         19004, # 1: number of runthroughs, 2: number of loops
    'LOOPS_DONE':    19006, # 1: number of runthroughs, 2: number of loops
    'START_DATE':    19207, # YYYY-MM-DD-hh-mm-ss
    'LEAD_TIME':     19009, # pre-run time in seconds
    'ACTIVE_TIME':   19021, # program runtime in seconds
    'STATUS':        19210, # 0: not running, 1: running, +2: pauses, +4: waiting for actual value
                            # 8: stops, 16: waiting for start time, +32 pause via PLC
  },
}
cmd_dict['SET'] = {
  'CTRL_VAR': { 
    'SETPOINT':      11001,
  },
  'CTRL_VAL': { 
    'SETPOINT':      13006,
  },
  'DIGI_OUT': { 
    'VAL':           14001, # No.+1
  },
  'GRAD_UP': { 
    'VAL':           11068,
  },
  'GRAD_DWN': { 
    'VAL':           11072,
  },
  'PRGM':{
    'NUM':           19204, # number of the program running
    'CTRL':          19209, # 1 + <2: Pause, 4: Resume>
    'LOOPS':         19003, # <No.> + 0
    'START_DATE':    19208, # 1 + <YYYY-MM-DD-hh-mm-ss>
    'LEAD_TIME':     19010, # 1 + <pre-run time in seconds>
    'NAME':          19031,
    'NAME':          19031,
  },
}
cmd_dict['START'] = {
  'MANUAL':          14001, #start manual mode: 1 + <0: off, 1: on> 
  'PRGM':            19014, # <No.> + <number of runthroughs>
}
cmd_dict['STOP'] = {
  'PRGM':            19015, # stop currently running program
}
cmd_dict['RESET'] = {
  'ERROR':           17012, # reset all errors
}

# SHORT HAND COMMANDS
getDewp  = lambda c: 18.0
getTemp  = lambda c: float(sendSimServCmd(c,'GET CTRL_VAR VAL',[1])[0])
getSetp  = lambda c: float(sendSimServCmd(c,'GET CTRL_VAR SETPOINT',[1])[0])
getAir   = lambda c: int(sendSimServCmd(c,'GET DIGI_OUT VAL',[7])[0])
getDryer = lambda c: int(sendSimServCmd(c,'GET DIGI_OUT VAL',[8])[0])
startRun = lambda c: sendSimServCmd(client,'START MANUAL',[1,1])
stopRun  = lambda c: sendSimServCmd(client,'START MANUAL',[1,0])

# CLIMATE CHAMBER CLASS
class ClimateChamber(socket.socket):
  __slots__ = ()
  def getTemp(self):    return getTemp(self)
  def getSetp(self):    return getSetp(self)
  def getAir(self):     return getAir(self)
  def getDryer(self):   return getDryer(self)
  def startRun(self):   return startRun(self)
  def stopRun(self):    return stopRun(self)
  def disconnect(self): return self.close()
  def sendSimServCmd(self,*args,**kwargs):
    return sendSimServCmd(self,*args,**kwargs)
  def forceWarmUp(self,*args,**kwargs):
    return forceWarmUp(self,*args,**kwargs)
  def stop(self,*args,**kwargs):
    return stopClimateChamber(self,*args,**kwargs)
  

def sendSimServCmd(client, cmdstr, args=[ ], chamber=1, verbose=False):
  """Execute command from given string."""
  command = createSimServCmdFromString(cmdstr,args,chamber=chamber,verbose=verbose)
  client.send(command)
  data = client.recv(512)
  return unpackSimServData(data)
  

def createSimServCmdFromString(cmdstr, args=[ ], chamber=1, verbose=False):
  """Execute command from given string."""
  cmdid    = cmd_dict
  commands = cmdstr.split()
  for command in commands:
    assert isinstance(cmdid,dict), "Command '%s' not in dictionary: %s"%(command,cmdid)
    assert command in cmdid, "cmdid is not a dictionary: %s"%(cmdid)
    cmdid = cmdid[command]
  assert isinstance(cmdid,int), "Command ID '%s' is not an integer!"%(cmdid)
  if verbose:
    print "Command ID = %s ('%s')"%(cmdid,cmdstr)
  command = ceateSimServCmd(cmdid,args,chamber=chamber,verbose=verbose)
  return command
  

def ceateSimServCmd(cmdID, arglist=[ ], chamber=1, verbose=False):
  """Create valid simserv command with separators."""
  cmd = str(cmdID).encode('ascii') # command ID
  cmd = cmd+SR+str(chamber).encode('ascii') # chamber index, b'1'
  for arg in arglist:
    cmd = cmd + SR
    cmd = cmd + str(arg).encode('ascii')
  cmd = cmd + CR
  if verbose:
    print "simserv command = '%r'"%(cmd)
  return cmd
  

def unpackSimServData(data):
  """Format for output."""
  list = data.rstrip(CR+LF).split(SR)
  assert len(list)>0, "Unknown data output: '%s'"%list
  code = int(list[0])
  if code!=1:
    warning("ERROR! %s (%s)"%(err_dict.get(code,'UNKNOWN ERROR (%s)!'%code),code))
  output = [o.decode() for o in list[1:]]
  return output
  

def connectClimateChamber(ip=defaultip,port=2049):
  """Connect to climate chamber via give IP address."""
  try:
    socket.inet_aton(ip)
  except socket.error:
    raise IOError("Socket error! Could not find IP %s!"%ip)
  client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # create stream socket
  result = client.connect((ip,port)) # connect to protocol server
  client.__class__ = ClimateChamber
  return client
  

def forceWarmUp(client,target=24,gradient=1):
  """Force warm up."""
  if int(sendSimServCmd(client,'GET PRGM STATUS')[0])!=0:
    sendSimServCmd(client,'STOP PRGM')
  assert isinstance(target,float) or isinstance(target,int),u"Target temperature (%s\u00b0C) is not a number!"%(target)
  warning(u"Force warm up to target temperature %.1f\u00b0C with a gradient of %.1f K/min..."%(target,gradient))
  sendSimServCmd(client,'SET CTRL_VAR SETPOINT',[1,target])
  sendSimServCmd(client,'SET GRAD_UP VAL', [1,gradient])
  sendSimServCmd(client,'SET GRAD_DWN VAL',[1,gradient])
  print "Turning on compressed air and dryer..."
  sendSimServCmd(client,'SET DIGI_OUT VAL',[7,1]) # AIR1  ON
  sendSimServCmd(client,'SET DIGI_OUT VAL',[8,1]) # DRYER ON
  print u"Starting forced warm-up to %.3f\u00b0C..."%target
  sendSimServCmd(client,'START MANUAL',[1,1])
  warning("Please turn the climate box off yourself!")
  

def forceWarmUpEvent(client,**kwargs):
  """Force warm up."""
  if askyesno("Verify","Really force warm-up?"):
    forceWarmUp(client,**kwargs)
  else:
    print "Abort force warm-up!"
  

def stopClimateChamber(client):
  """Stop climate box."""
  pgmstatus = int(sendSimServCmd(client,'GET PRGM STATUS')[0])
  temp = getTemp(client)
  warning(u"Stop running at temperature %.1f\u00b0C (no warm-up)..."%(temp))
  if pgmstatus!=0:
    sendSimServCmd(client,'STOP PRGM')
  else:
    sendSimServCmd(client,'START MANUAL',[1,0])
  

def stopClimateChamberEvent(client):
  """Stop climate box."""
  pgmstatus = int(sendSimServCmd(client,'GET PRGM STATUS')[0])
  if askyesno("Verify","Really stop %s?"%("manual run" if pgmstatus==0 else "program")):
    stopClimateChamber(client)
  else:
    print "Abort interuption!"
  

def checkActiveWarnings(client,**kwargs):
  nmsg = int(sendSimServCmd(client,'GET MSG NUM')[0])
  nactive = 0
  if nmsg>0:
    for i in xrange(1,nmsg+1):
      status = int(sendSimServCmd(client,'GET MSG STATUS',[i])[0])
      mtype  = int(sendSimServCmd(client,'GET MSG TYPE',[i])[0])
      if status==1 and mtype & kwargs.get('type',3): # alarm or warning
        nactive += 1
  return nactive
  

def checkInterlock(client,temp,dewp):
  """Check if the dewpoint has reach the temperature."""
  if temp-dewp<5:
    warning(u"INTERLOCK! Dewpoint (%.2f\u00b0C) %s temperature (%.2f\u00b0C)!"%(dewp,"higher than" if dewp>temp else "within 5\u00b0C of",temp))
    #forceWarmUp(client)
  

def getActiveWarnings(client,**kwargs):
  """Get active messages; by default alarms and warnings only."""
  nmsg = int(sendSimServCmd(client,'GET MSG NUM')[0])
  messages = [ ]
  for i in xrange(1,nmsg+1):
    status  = int(sendSimServCmd(client,'GET MSG STATUS',[i])[0])
    mtype   = int(sendSimServCmd(client,'GET MSG TYPE',[i])[0])
    if status==1 and mtype & kwargs.get('type',3): # alarm or warning
      message = str(sendSimServCmd(client,'GET MSG TEXT',[i])[0])
      mtext = "ALARM!" if mtype & 1 else "Warning!" if mtype & 2 else "Info:"
      messages.append("%s %s"%(mtext,message))
  return messages
  

def openActiveWarnings(client,**kwargs):
  """Open active messages; by default alarms and warnings only."""
  print "MESSAGES NOT TESTED!"
  nmsg = int(sendSimServCmd(client,'GET MSG NUM')[0])
  messages = getActiveWarnings(client,**kwargs)
  if messages:
    allmessages = "Found the following active alarms/warnings:"+"\n  ".join(messages)
    print allmessages
    showinfo("Found active warnings",allmessages)
  

def getRunStatus(client):
  """Get the name of the running program."""
  prgmid   = int(sendSimServCmd(client,'GET PRGM NUM')[0])
  prgmname = "Not running"
  if prgmid>0:
    # TODO: check program status
    prgmname = "Program '%s'"%(str(sendSimServCmd(client,'GET PRGM NAME',[prgmid])[0]))
  elif int(sendSimServCmd(client,'GET CHAMBER STATUS')[0])>1:
    prgmname = "Manual run"
  return prgmname
  
