# ********************************************************************
#
#  $Id: helloworld.py 32630 2018-10-10 14:11:07Z seb $
#
#  An example that show how to use a  Yocto-Meteo
#
#  You can find more information on our web site:
#   Yocto-Meteo documentation:
#      https://www.yoctopuce.com/EN/products/yocto-meteo/doc.html
#   Python API Reference:
#      https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html

import os, sys
sys.path.append(os.path.join("yoctolib_python","Sources"))
from yocto_api import YAPI, YRefParam, YModule
from yocto_humidity import YHumidity
from yocto_temperature import YTemperature
from yocto_pressure import YPressure



def connectRaspberryPi(ip):
  """Connect RaspberryPi."""
  
  



def connectYoctoMeteo(target='any'):
  """Connect Yocto Meteo."""
  
  # SETUP the API to use local USB devices
  errmsg = YRefParam()
  assert YAPI.RegisterHub('usb',errmsg)==YAPI.SUCCESS, "init error %s. Please check the USB cable!"%errmsg.value
  
  # RETRIEVE any humidity sensor
  if target=='any':
    sensor = YHumidity.FirstHumidity()
    assert sensor, "No module connected. Please check the USB cable!"
    module = sensor.get_module()
    target = module.get_serialNumber()
  else:
    module = YModule.FindModule(target)
  assert module.isOnline(), "Device not connected. Please check the USB cable!"
  
  # ASSIGN sensors
  module.humi = YHumidity.FindHumidity(target+'.humidity')
  module.pres = YPressure.FindPressure(target+'.pressure')
  module.temp = YTemperature.FindTemperature(target+'.temperature')
  
  return module
  


def disconnectYoctoMeteo():
  """Disconnect Yocto Meteo."""
  YAPI.FreeAPI()
  


getYMTemp = lambda m: m.temp.get_currentValue()
getYMPres = lambda m: m.pres.get_currentValue()
getYMHumi = lambda m: m.humi.get_currentValue()
#YAPI.Sleep(1000)