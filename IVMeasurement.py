# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import visa
import DList as DL
import numpy as np
import time
import winsound


# Main function to be run.
def main():
    rm, power, pico, led, params, save_params = initialize()
    measure(power, pico, led, params, save_params)
    shut_down(power, pico, led)
    print("donzo")
    winsound.Beep(1000, 400)  # Computer beeps once measurement has finished.


# Initialize program parameters and instruments.
def initialize():
    rm, power, pico, led = get_instruments()
    
    # Initialization of instruments optional.
    initialize_power(power)
    initialize_led(led)
    initialize_pico(pico)
    
    save_params = initialize_save()
    params = set_parameters()

    return rm, power, pico, led, params, save_params


# Initialize power supply and ammeter on GPIB via
# VISA and instruments' hard coded address.
def get_instruments():
    led_address = 'GPIB0::5::INSTR'
    power_address = 'GPIB0::6::INSTR'
#    multiAddress = 'GPIB0::16::INSTR'
    pico_address = 'GPIB0::22::INSTR'
    
    rm = visa.ResourceManager()
    power = rm.open_resource(power_address)
    pico = rm.open_resource(pico_address)
    led = rm.open_resource(led_address)

    return rm, power, pico, led


# Initialize the power supply.
def initialize_power(power):
    power.write("OUTPut ON")
    power.write("VOLTage 0")
    
    
# Initialize the LED's power supply.
def initialize_led(led):
    led.write("OUTPut ON")
    

# Initialize multimeter.
def initialize_multi(multi):
    multi.write("FUNCtion 'CURRent'")


# Initialize Picoammeter.
def initialize_pico(pico):
    pico.write('$A')  # Get an initial reading to filter out bad first point.


# Set Save Parameters. Choose where to save output file and enter SiPM chip info.
def initialize_save():
    print("Select output folder for saved data: ")
    main_dir = DL.ChooseDirectory()  # Choose directory to output data from GUI.
    si_pmv = raw_input("Enter SiPM Chip Voltage: ")
    si_pmn = raw_input("Enter SiPM Chip Number: ")
    
    save_params = {"MainDir": main_dir, "SiPMV": si_pmv, "SiPMN": si_pmn}
    
    return save_params


# Set program parameters as dictionary.
def set_parameters():
    v_max = 68.0  # V Maximum voltage for range.
    v_min = 65.0  # V Minimum voltage for range.
    v_step = -0.025  # V Step size for voltage iteration.
    i_reads = 10  # Number of current readings per V.
    led_levels = [2.5, 3.5]  # V LED levels to be run. For each LED level, a separate I-V measurement will be taken.
    break_i = 1.8e-3  # Amps If current on pico exceeds BreakI, measurement will stop. To avoid overflow/damage.
    # Notes to be added to the output text file.
    notes = 'Notes: Precision SiPM Breakdown voltage measurement. ' \
            'SiPM is first heated for 7 minutes then run down while hot. This is the run down data. Exposed Chip.'
    
    time0 = time.time()  # Sets initial time
    
    # Place all parameter values in a dictionary to be used when needed.
    params = {"VMax": v_max, "VMin": v_min, "VStep": v_step,
              "LEDLevels": led_levels, "IReads": i_reads,
              "BreakI": break_i, "Time0": time0, 'Notes': notes}
    
    return params
    

# Take measurement of Current vs Voltage.
def measure(power, pico, led, params, save_params):
    v_step, v_start, v_end = set_v_loop(params)  # Get loop parameters from Params.
    
    # Iterate through LED levels.
    for v_led in params["LEDLevels"]:
        start = time.time()  # For each LED level run, start a timer.
        data = [[], [], [], []]  # [[Time],[SetVoltage],[OutputVoltage],[Current]]
        set_led_v(led, v_led)  # Set LED voltage to VLED.
        time0 = time.time()  # Start timer used for time data points.
        
        # Iterate over the voltage range, taking current measurements at each step and recording.
        for V in np.arange(v_start, v_end, v_step):
            set_power_v(power, V)  # Set bias voltage to V at each step.
            
            # Make/record all data readings for this voltage step.
            flag = read(pico, data, V, power, time0, params["IReads"], params["BreakI"])
            
            if flag == "Break":
                break  # If current is too close to limit, stop increasing V.
                
        save_data(data, v_led, params, save_params)  # After each LED run, save all data to text file.
        
        print("LED {1}V Time: {0}".format(time.time()-start, v_led))

    return data


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
def read(pico, data, v, power, time0, i_reads, break_i):
    flag = ""  # Set a flag in case current exceeds BreakI.
    
    # Take data IReads times at this voltage step.
    for j in range(i_reads):
        t = time.time()
        power_v = read_power_v(power)  # Read voltage from power supply.
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
            data[3].append(i)

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


# Shut down measurement tools.
def shut_down(power, pico, led):
    power.write("VOLTage 0")
    led.write("VOLTage 0")
    power.write("OUTPut OFF")
    led.write("OUTPut OFF")
    
    
# Save data to text file.
def save_data(data, v_led, params, save_params):
    save_dir = get_save_folder(save_params, v_led)  # Construct path to save folder.
    DL.ChangeDirectory(save_dir)  # Change working directory to SaveDir to create output file there.
    file = get_file(params)  # Create and open output file.
    write_file(file, data, v_led, params, save_params)  # Write Data to output file.
    file.close()  # Close output file.

    
# Get folder path to save data file or create
# path if folder doesn't exist.
def get_save_folder(save_params, v_led):
    si_pm_name = "SiPM " + save_params["SiPMV"] + "V#" + save_params["SiPMN"]
    # If folder does not exist, create it. Return path either way.
    si_pm_folder = DL.GetFolder(si_pm_name, save_params["MainDir"])
    led_name = "LED " + str(v_led) + "V"
    led_folder = DL.GetFolder(led_name, si_pm_folder)  # If folder does not exist, create it. Return path either way.
    
    return led_folder


# Open file to save data. File name is just the current date (arbitrary).
def get_file(params):
    # Construct new file path.
    day = time.strftime("%d")
    month = time.strftime("%m")
    year = time.strftime("%y")
    date = month + "-" + day + "-" + year
    file_path = date + ".txt"
    
    # If file exists, create one with same path plus a (#) at the end. Avoids overwriting.
    i = 1
    while DL.CheckForFile(file_path):
        file_path = date + "({0})".format(str(i)) + ".txt"
        i += 1
    
    file = open(file_path, "w")  # Create and open this new text file in write mode.
    
    return file


# Write run data to file.
def write_file(file, data, v_led, params, save_params):
    write_info_line(file, v_led, params, save_params)  # Write information about run to first two lines.
    write_header_line(file)  # Write headers for data columns on the fourth line.
    write_data(file, data)  # Write data into columns under the headers.
    

# Write first line with all information on run with
# second line as compact version of this info.
def write_info_line(file, v_led, params, save_params):
    # Write all run info readably to the first line.
    si_pm = "SiPM Chip: " + save_params["SiPMV"] + "V #" + save_params["SiPMN"]
    led = "LED Voltage: " + str(v_led) + "V"
    v = "Voltage from " + str(params["VMin"]) + "V to " + str(params["VMax"]) + "V with steps " + \
        str(params["VStep"]) + "V"
    i = "Number of current readings per voltage step: " + str(params["IReads"])
    notes = params['Notes']
    
    file.write(si_pm + " | " + led + " | " + v + " | " + i + " | " + notes + "\n")
    
    # Write same run info in a compact form to second line to be extracted easily when reading the data file.
    compact = "Compact: {0} {1} {2} {3} {4} {5} {6}\n".format(save_params["SiPMV"], save_params["SiPMN"], str(v_led),
                                                              str(params["VMin"]), str(params["VMax"]),
                                                              str(params["VStep"]), str(params["IReads"]))
    
    file.write(compact)
    
    
# Skip third line, write fourth line with data column headers.
def write_header_line(file):
    file.write("\n")
    file.write("Time from start (s)\tSet Power Voltage (V)\tOutput Power Voltage\tPico Current (A)")
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
        

# Tells python to run main() function if this program is run directly.
# (As opposed to being imported as a module, in which case, main will not run.)
if __name__ == "__main__":
    main()
