#!/usr/bin/env python3

from random import sample

def adc_daq(number_of_samples=100, sps='ADS1256_3750SPS', gain = 'ADS1256_GAIN_1'):

    channels=zeros([2,number_of_samples], dtype=int32)

    channels[0]=sample(range(1000), number_of_samples)
    channels[1]=sample(range(1000), number_of_samples)

    return channels