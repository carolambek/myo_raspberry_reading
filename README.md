# Overview

This project allows to read raw data from the Myo armband with the Raspberry Pi 3 or Zero W. The code uses the bluez library to connect via bluetooth low energy (BLE) the Myo to the Raspberry.

The reading protocol is based on the work of dzhu (https://github.com/dzhu/myo-raw).

# Requirements

- python >=2.7
- bluez 5.43
- pexpect
- serial
- numpy
- Raspberry Pi 3 or Zero W

# Included files

## myo_rpi_ble.py (read raw EMG/IMU data)

myo_rpi_ble.py must be launched on the Raspberry and it reads raw data from the Myo armband. It uses the pexpect library to spaw It implements the following functions:

- connect() & disconnect(): to connect/disconnect from the Myo.
- get_name(): to get the name assigned to the Myo.
- get_firmware(): to get the firmware of the Myo.
- get_battery_level(): to get the actual battery level of the Myo.
- vibrate(): to make the vibrate the Myo from 1 to 3 seconds.
- set_leds(): to change the color of the logo (see comments in code for more info)
- start_raw(): to initialize collection of raw EMG data at about 50Hz.
- start_raw_fast(): to initialize collection of raw EMG data at about 200Hz (depends on RPi).
- collect_raw(): to collect raw EMG data at about 50Hz (must be used with start_raw()).
