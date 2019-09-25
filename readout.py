#! /usr/bin/env python
# coding: latin-1
import sys, time
import socket
from commands import sendSimServCmd, unpackSimServData

ip     = '130.60.164.144' # '192.168.121.100'
port   = 2049
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # create stream socket
result = client.connect((ip,port)) # connect to protocol server

out = sendSimServCmd(client,'GET CTRL_VAL NUM')
print 'GET CTRL_VAL NUM', out

out = sendSimServCmd(client,'GET CTRL_VAR NUM')
print 'GET CTRL_VAR NUM', out

out = sendSimServCmd(client,'GET CTRL_VAR VAL',[1])
print 'GET CTRL_VAR VAL 1', out

out = sendSimServCmd(client,'GET CTRL_VAR SETPOINT',[1])
print 'GET CTRL_VAR SETPOINT 1', out

out = sendSimServCmd(client,'GET CTRL_VAL SETPOINT',[1])
print 'GET CTRL_VAL SETPOINT 1', out

out = sendSimServCmd(client,'GET CTRL_VAL SETPOINT',[2])
print 'GET CTRL_VAL SETPOINT 2', out

out = sendSimServCmd(client,'GET DIGI_IN NUM')
print 'GET DIGI_IN NUM', out

out = sendSimServCmd(client,'GET DIGI_OUT NUM')
print 'GET DIGI_OUT NUM', out

out = sendSimServCmd(client,'GET DIGI_OUT NAME',[6])
print 'GET DIGI_OUT NAME 6', out

out = sendSimServCmd(client,'GET DIGI_OUT NAME',[7])
print 'GET DIGI_OUT NAME 7', out

out = sendSimServCmd(client,'GET DIGI_OUT VAL',[7]) # No.+1
print 'GET DIGI_OUT VAL 7', out

out = sendSimServCmd(client,'GET DIGI_OUT VAL',[8]) # No.+1
print 'GET DIGI_OUT VAL 8', out

out = sendSimServCmd(client,'GET GRAD_UP VAL',[1])
print 'GET GRAD_UP VAL 1', out

out = sendSimServCmd(client,'GET GRAD_DWN VAL',[1])
print 'GET GRAD_DWN VAL 1', out

out = sendSimServCmd(client,'GET PRGM NUM')
print 'GET PRGM NUM', out

out = sendSimServCmd(client,'GET PRGM NAME',[1])
print 'GET PRGM NAME 1', out

out = sendSimServCmd(client,'GET PRGM STATUS')
print 'GET PRGM STATUS', out

getTemp  = lambda: float(sendSimServCmd(client,'GET CTRL_VAR VAL',[1])[0])
getAir   = lambda: int(sendSimServCmd(client,'GET DIGI_OUT VAL',[7])[0])
getDryer = lambda: int(sendSimServCmd(client,'GET DIGI_OUT VAL',[8])[0])
print 'temp  =', getTemp()
print 'air   =', getAir()
print 'dryer =', getDryer()

client.close()
