#!/usr/bin/env python3

from random import sample
from numpy import zeros, int32


def adc_daq(number_of_samples=100, sps="ADS1256_3750SPS", gain="ADS1256_GAIN_1"):

    # print(number_of_samples)

    channels = zeros([2, number_of_samples], dtype=int32)

    ntc_range=3746847
    shunt_range=1733664

    channels[0] = sample(range(ntc_range-1000, ntc_range-1000), number_of_samples)
    channels[1] = sample(range(shunt_range-1000, shunt_range+1000), number_of_samples)

    return channels
