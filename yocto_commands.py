# Author: Izaak Neutelings (September, 2019)
# -*- coding: utf-8 -*-
#
# Sources:
#  https://www.yoctopuce.com/EN/products/yocto-meteo/doc.html
#  https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html
import os, sys
from math import log
sys.path.append(os.path.join(os.path.dirname(__file__),"yoctolib_python","Sources"))
from yocto_api import YAPI, YRefParam, YModule
from yocto_humidity import YHumidity
from yocto_temperature import YTemperature
from yocto_pressure import YPressure

# YOCTO METEO MODULES:
ymeteo1 = 'METEOMK1-28B37'
ymeteo2 = 'METEOMK1-28AF9'

# SHORT HAND COMMANDS
getYMTemp = lambda m: m.temp.get_currentValue()
getYMPres = lambda m: m.pres.get_currentValue()
getYMHumi = lambda m: m.humi.get_currentValue()
getYMDewp = lambda m: computeDewPoint(m.temp.get_currentValue(),m.humi.get_currentValue())

# YOCTO METEO CLASS
class YoctoMeteo(YModule):
  def getTemp(self):    return getYMTemp(self)
  def getHumi(self):    return getYMHumi(self)
  def getDewp(self):    return getYMDewp(self)
  def getPres(self):    return getYMPres(self)
  def close(self):      return disconnectYoctoMeteo(self)
  def disconnect(self): return disconnectYoctoMeteo(self)
  

def connectRaspberryPi(ip):
  """Connect RaspberryPi."""
  

def findYoctoMeteo(fatal=False):
  """Find YoctoMeteo module, if available."""
  sensor = YHumidity.FirstHumidity()
  if sensor:
    module = sensor.get_module()
    return module
  elif fatal:
    raise IOError("No YoctoMeteo module connected. Please check the USB cable!")
  return False
  

def connectYoctoMeteo(target='any'):
  """Connect Yocto Meteo."""
  
  # SETUP the API to use local USB devices
  errmsg = YRefParam()
  if YAPI.RegisterHub('usb',errmsg)==YAPI.SUCCESS:
    
    # RETRIEVE any humidity sensor
    if target=='any':
      sensor = YHumidity.FirstHumidity()
      if not sensor:
        warning("No module connected. Please check the USB cable!")
        return None
      module = sensor.get_module()
      target = module.get_serialNumber()
    else:
      module = YModule.FindModule(target)
    if not module.isOnline():
      warning("Device not connected. Please check the USB cable!")
      return None
    
    # ASSIGN sensors
    module.humi  = YHumidity.FindHumidity(target+'.humidity')
    module.pres  = YPressure.FindPressure(target+'.pressure')
    module.temp  = YTemperature.FindTemperature(target+'.temperature')
    module.__class__ = YoctoMeteo
    return module
  else:
    warning("init error %s. Please check the USB cable!"%errmsg.value)
    return None
  

def disconnectYoctoMeteo(*args):
  """Disconnect Yocto Meteo."""
  YAPI.FreeAPI()
  

def computeDewPoint(T,RH):
  """Compute the dewpoint."""
  # Magnus formula
  # https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
  a, b, c = 6.1121, 18.678, 257.14
  gamma   = log(RH/100) + (b*T)/(c+T)
  Tdewp   = (c*gamma)/(b-gamma)
  return Tdewp
  
