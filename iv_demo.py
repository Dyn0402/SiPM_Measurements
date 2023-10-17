#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 16 7:38 PM 2023
Created in PyCharm
Created as SiPM_Measurements/iv_demo

@author: Dylan Neff, Dylan
"""

import numpy as np
import matplotlib.pyplot as plt

import visa
import DList as DL
import numpy as np
import time
import winsound
import matplotlib.pyplot as plt


# Main function to be run.
def main():
    power_address = 'GPIB0::6::INSTR'
    pico_address = 'GPIB0::22::INSTR'

    rm = visa.ResourceManager()
    power = rm.open_resource(power_address)
    pico = rm.open_resource(pico_address)

    pico.write('$A')  # Get an initial reading to filter out bad first point.

    power.write("OUTPut ON")
    power.write("VOLTage 0")

    pause = 0.01  # s Should be realistically optimized based on speed of I response to change in V

    vs, i_vals = np.linspace(40, 42.5, 2000), []
    for v in np.linspace(40, 42.5, 2000):
        set_power_v(power, v)
        time.sleep(pause)
        i_vals.append(read_pico_i(pico))
        print(f'V={v:0.2f}, I={i_vals[-1]:0.2f}')

    shut_down(power)

    plt.plot(vs, i_vals)
    plt.grid()
    plt.xlabel('Bias Voltage (V)')
    plt.ylabel('SiPM Current (A)')
    plt.show()

    print('donzo')


# Set voltage of power supply to V.
def set_power_v(power, v):
    power.write("VOLTage {0}".format(v))


# Read current of picoammeter.
def read_pico_i(pico):
    i = pico.query('A$')
    if 'ODCI' in i:
        i = 'overflow'
    else:
        i = float(i.strip('NDCI'))

    return i


# Shut down measurement tools.
def shut_down(power):
    power.write("VOLTage 0")
    power.write("OUTPut OFF")


if __name__ == '__main__':
    main()
