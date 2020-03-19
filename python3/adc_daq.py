#!/usr/bin/python3
# -*- coding:utf-8 -*-

import ADS1256
import RPi.GPIO as GPIO
from numpy import zeros, int32
import obrada
import yaml
from tqdm import trange

def adc_daq(number_of_samples=100, sps='ADS1256_3750SPS', gain = 'ADS1256_GAIN_1'):
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    ADC.ADS1256_ConfigADC(gain = ADS1256.ADS1256_GAIN_E.get(gain), drate = ADS1256.ADS1256_DRATE_E.get(sps))

    channels=zeros([2,number_of_samples], dtype=int32)

    for i in trange(number_of_samples):
        channels[0][i]=ADC.ADS1256_GetChannalValue(0)
        channels[1][i]=ADC.ADS1256_GetChannalValue(1)
    
    GPIO.cleanup()
    print("DAQ done\n")
    return channels

if __name__ == "__main__":
    c=adc_daq()
    with open('config.yaml','r') as f:
        conf=yaml.safe_load(f)
    log=obrada.obrada(config=conf,kanali=c, zeff=conf.get('sps_zeff').get('ADS1256_30000SPS'))
    print(log)
    