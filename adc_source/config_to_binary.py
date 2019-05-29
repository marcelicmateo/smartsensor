import sys
import ctypes
import pickle
import numpy as np
#print ("upitnik")
#print(str(sys.argv))


s=sys.argv[1]

k=s.split('_')


sps=ctypes.c_uint(int(k[1]))
nsps=ctypes.c_uint(int(k[2]))
sleep=ctypes.c_uint(int(k[3]))
k=[sps,nsps,sleep]

#print(type(sps))
#print(k)
fun = ctypes.CDLL("/home/pi/smartsensor/adc_source/libfun.so")
#fun.c_dump.argtypes=[ctypes.c_uint]
fun.c_dump(sps,nsps,sleep)
#f = open("/home/pi/smartsensor/adc_source/conf", "wb")
#f.write(sps)
#f.close
