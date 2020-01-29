#!/usr/bin/python3
# -*- coding:utf-8 -*-

import time
import ADS1256
import RPi.GPIO as GPIO
from numpy import zeros, int32, mean

def adc_daq(number_of_samples, sps):
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()

    channels=zeros([2,number_of_samples], dtype=int32)

    for i in range(number_of_samples):
        channels[0][i]=ADC.ADS1256_GetChannalValue(0)
        channels[1][i]=ADC.ADS1256_GetChannalValue(1)
    
    GPIO.cleanup()
    print("DAQ done\n")
    return channels

if __name__ == "__main__":
    c=adc_daq(100,'ADS1256_3750SPS')
    print(mean(c[0])*5.0/0x7fffff)
    pass
    