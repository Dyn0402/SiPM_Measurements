#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on September 03 7:08 PM 2019
Created in PyCharm
Created as SiPM_Measurements/IVMeas_Production.py

@author: Dylan Neff, dylan
"""

import visa
import DList as DL
import numpy as np
import time
import winsound
import matplotlib.pyplot as plt
from scipy import stats
import os

# Set main directory to save files in.
main_dir = 'C:/Users/nuQCD/Desktop/SiPM_Data'


# Main function to be run.
def main():
    while True:
        rm, power, pico, multi, params, save_params = initialize()
        if int(params['VMax']) == 0 and int(save_params['SiPMN']) == 0:
            shut_down(power)
            break
        data, slope, intercept, bias = measure(power, pico, multi, params, save_params)
        shut_down(power)
        plot(data, slope, intercept, bias, params['TargetI'])
        winsound.Beep(1000, 400)  # Computer beeps once measurement has finished.

    print('donzo')


# Initialize program parameters and instruments.
def initialize():
    rm, power, pico, multi = get_instruments()

    # Initialization of instruments optional.
    initialize_power(power)
    initialize_pico(pico)
    initialize_multi(multi)

    save_params = initialize_save()
    params = set_parameters()

    return rm, power, pico, multi, params, save_params


# Initialize power supply and ammeter on GPIB via
# VISA and instruments' hard coded address.
def get_instruments():
    # led_address = 'GPIB0::5::INSTR'
    power_address = 'GPIB0::6::INSTR'
    multi_address = 'GPIB0::16::INSTR'
    pico_address = 'GPIB0::22::INSTR'

    rm = visa.ResourceManager()
    power = rm.open_resource(power_address)
    pico = rm.open_resource(pico_address)
    multi = rm.open_resource(multi_address)

    return rm, power, pico, multi


# Initialize the power supply.
def initialize_power(power):
    power.write("OUTPut ON")
    power.write("VOLTage 0")


# Initialize multimeter.
def initialize_multi(multi):
    # multi.write("FUNCtion 'CURRent'")
    multi.write("FUNCtion 'VOLTage'")


# Initialize Picoammeter.
def initialize_pico(pico):
    pico.write('$A')  # Get an initial reading to filter out bad first point.


# Set Save Parameters. Choose where to save output file and enter SiPM chip info.
def initialize_save():
    save_dir = main_dir
    si_pmn = input("Enter SiPM Chip Number: ")
    overwrite = True

    save_params = {"save_dir": save_dir, "SiPMN": si_pmn, 'overwrite': overwrite}

    return save_params


# Set program parameters as dictionary.
def set_parameters():
    v_max = float(input("Enter Max Voltage: "))  # V Maximum voltage for range.
    v_min = v_max - 3.0  # V Minimum voltage for range.
    v_step = -0.25  # V Step size for voltage iteration.
    i_reads = 1  # Number of current readings per V.
    break_i = 1.8e-3  # Amps If current on pico exceeds BreakI, measurement will stop. To avoid overflow/damage.
    # Notes to be added to the output text file.
    delay = 0.1  # Seconds pause after setting voltage and before read.
    target_current = 1e-4  # Apms Target current all boards should be calibrated to.
    notes = 'Notes: Precision SiPM Breakdown voltage measurement. ' \
            'SiPM is first heated for 7 minutes then run down while hot. This is the run down data. Exposed Chip.'

    time0 = time.time()  # Sets initial time

    # Place all parameter values in a dictionary to be used when needed.
    params = {"VMax": v_max, "VMin": v_min, "VStep": v_step, "IReads": i_reads,
              "BreakI": break_i, "Time0": time0, 'Notes': notes, 'Delay': delay,
              'TargetI': target_current}

    return params


# Take measurement of Current vs Voltage.
def measure(power, pico, multi, params, save_params):
    v_step, v_start, v_end = set_v_loop(params)  # Get loop parameters from Params.

    start = time.time()  # Start a timer.
    data = [[], [], [], [], []]  # [[Time],[SetVoltage],[OutputVoltage],[MultiVoltage],[Current]]
    time0 = time.time()  # Start timer used for time data points.

    # Iterate over the voltage range, taking current measurements at each step and recording.
    for v in np.arange(v_start, v_end, v_step):
        set_power_v(power, v)  # Set bias voltage to V at each step.

        time.sleep(params['Delay'])  # Delay after setting power and before reading.

        # Make/record all data readings for this voltage step.
        flag = read(power, pico, multi, data, v, time0, params["IReads"], params["BreakI"])

        if flag == "Break":
            break  # If current is too close to limit, stop increasing V.

    slope, intercept, bias = get_bias(data, params['TargetI'])  # Perform linear regression and get bias voltage.
    save_data(data, params, save_params, bias)  # After each LED run, save all data to text file.

    print("Time: {0}".format(time.time() - start))

    return data, slope, intercept, bias


# Set measurement loop parameters.
def set_v_loop(params):
    v_step = params["VStep"]

    # If VStep is positive iterate up, otherwise iterate down.
    if v_step > 0:
        v_start = params["VMin"]
        v_end = params["VMax"]
    else:
        v_start = params["VMax"]
        v_end = params["VMin"]

    return v_step, v_start, v_end


# Set voltage of power supply to V.
def set_power_v(power, v):
    power.write("VOLTage {0}".format(v))


# Set voltage of LED power supply to V.
def set_led_v(led, v):
    led.write("VOLTage {0}".format(v))


# Read and record data.
def read(power, pico, multi, data, v, time0, i_reads, break_i):
    flag = ""  # Set a flag in case current exceeds BreakI.

    # Take data IReads times at this voltage step.
    for j in range(i_reads):
        t = time.time()
        power_v = read_power_v(power)  # Read voltage from power supply.
        multi_v = read_multi_v(multi)
        i = read_pico_i(pico)  # Read current from pico.

        # If current is greater than BreakI or is overflow, set flag to break and exit loop. Print warning.
        if i == 'overflow' or i > break_i:
            print("I overflow at time: {0}, output voltage: {1}, current: {2}".format(t - time0, power_v, i))
            flag = "Break"
            break
        else:
            # If no overflow, save time, set Voltage, read Voltage, and read Current to Data.
            data[0].append(t - time0)
            data[1].append(v)
            data[2].append(power_v)
            data[3].append(multi_v)
            data[4].append(i)

    return flag


# Read current of picoammeter.
def read_pico_i(pico):
    i = pico.query('A$')
    if 'ODCI' in i:
        i = 'overflow'
    else:
        i = float(i.strip('NDCI'))

    return i


# Read voltage of power supply.
def read_power_v(power):
    v = power.query('MEASure:VOLTage?')
    v = float(v.strip())

    return v


# Read current of multimeter.
def read_multi_i(multi):
    i = multi.query('FETCh?')
    i = float(i.split(',')[0].strip('ADC'))

    return i


# Read current of multimeter.
def read_multi_v(multi):
    v = multi.query('FETCh?')
    v = float(v.split(',')[0].strip('VDC'))

    return v


# Shut down measurement tools.
def shut_down(power):
    power.write("VOLTage 0")
    power.write("OUTPut OFF")


# Save data to text file.
def save_data(data, params, save_params, bias):
    DL.ChangeDirectory(save_params['save_dir'])  # Change working directory to SaveDir to create output file there.
    file = get_file(save_params, bias)  # Create and open output file.
    write_file(file, data, params, save_params, bias)  # Write Data to output file.
    file.close()  # Close output file.


# Open file to save data. File name is just the current date (arbitrary).
def get_file(save_params, bias):
    # Construct new file path.
    file_path = f'board{save_params["SiPMN"]}_{bias}.txt'

    # If file exists, create one with same path plus a (#) at the end. Avoids overwriting.
    if save_params['overwrite']:
        files = DL.ListFileTypeInDirectory(main_dir, 'txt')
        for file in files:
            if f'board{save_params["SiPMN"]}' in file:
                print(f'Overwriting {file}')
                os.remove(file)
        print(files)
    else:
        i = 1
        while DL.CheckForFile(file_path):
            file_path = f'board{save_params["SiPMN"]}({i}).txt'
            i += 1

    file = open(file_path, "w")  # Create and open this new text file in write mode.

    return file


# Write run data to file.
def write_file(file, data, params, save_params, bias):
    write_info_line(file, params, save_params, bias)  # Write information about run to first two lines.
    write_header_line(file)  # Write headers for data columns on the fourth line.
    write_data(file, data)  # Write data into columns under the headers.


# Write first line with all information on run with
# second line as compact version of this info.
def write_info_line(file, params, save_params, bias):
    # Write all run info readably to the first line.
    si_pm = "SiPM Chip: " + str(params["VMax"]) + "V (max) Board #" + str(save_params["SiPMN"]) \
            + " Bias: " + str(bias) + "V"
    led = "LED Voltage: 75V"
    v = "Voltage from " + str(params["VMin"]) + "V to " + str(params["VMax"]) + "V with steps " + \
        str(params["VStep"]) + "V"
    i = "Number of current readings per voltage step: " + str(params["IReads"])
    notes = params['Notes']

    file.write(si_pm + " | " + led + " | " + v + " | " + i + " | " + notes + "\n")

    # Write same run info in a compact form to second line to be extracted easily when reading the data file.
    compact = "Compact: {0} {1} {2} {3} {4} {5} {6} {7}\n".format(params["VMax"], save_params["SiPMN"], bias, 75,
                                                                  str(params["VMin"]), str(params["VMax"]),
                                                                  str(params["VStep"]), str(params["IReads"]))

    file.write(compact)


# Skip third line, write fourth line with data column headers.
def write_header_line(file):
    file.write("\n")
    file.write("Time from start (s)\tSet Power Voltage (V)\tPower Supply Voltage Reading\t"
               "Multimeter Voltage Reading\tPico Current (A)")
    file.write("\n")


# Write data to file starting on fifth line.
def write_data(file, data):
    # Iterate over total number of data points.
    for i in range(len(data[0])):
        # Iterate over number of data columns.
        for j in range(len(data)):
            # Write data points, separated by tabs for each column.
            file.write('{0}\t'.format(data[j][i]))
        file.write('\n')


# Perform linear regression on data and solve for bias voltage that gives target current
def get_bias(data, target):
    slope, intercept, r_value, p_value, std_err = stats.linregress(data[3], data[4])
    bias = (target - intercept) / slope

    return slope, intercept, bias


# Plot data with linear regression
def plot(data, slope, intercept, bias, target):
    fig, ax = plt.subplots()
    textstr = '\n'.join((
        r'$\mathrm{slope}=%.3e$' % (slope,),
        r'$\mathrm{intercept}=%.2e$' % (intercept,),
        r'$\mathrm{bias}=%.3e$' % (bias,)))

    ax.plot(data[3], data[4], 'ob')
    ax.plot(data[3], slope * np.asarray(data[3]) + intercept, '-r')
    ax.plot(bias, target, '*g', markersize=12)
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in upper left in axes coords
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    plt.show()


# Tells python to run main() function if this program is run directly.
# (As opposed to being imported as a module, in which case, main will not run.)
if __name__ == "__main__":
    main()
