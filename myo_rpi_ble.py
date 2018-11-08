#!/usr/bin/env python

# Charles Lambelet - 20.07.18
# charles.lambelet88@gmail.com

# Connect Myo to Raspberry Pi 3/Zero W with Python over BLE
import pexpect
import time
import serial
# import common
# import filtering

from common import *
from filtering import *

ser = serial.Serial(
   # port='/dev/ttyAMA0',   # use ttyAMA0 when not using bluetooth on RPi3/Zero W
   port='/dev/ttyS0',      # use miniUART and leave main UART to bluetooth module
   baudrate=115200,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS,
   timeout=1
   )

if ser.isOpen():
    ser.close()
ser.open()
ser.isOpen()


# function to connect to the Myo.
def connect(child, device):
    '''Function to connect to the Myo'''
    print("Connecting to "),
    print(device),
    child.sendline("connect {0}".format(device))
    child.expect("Connection successful", timeout=5)
    print(" Connected!")


# function to disconnect from the Myo.
def disconnect(child, device):
    '''Function to disconnect from the Myo'''
    print("Disconnecting to "),
    print(device),
    child.sendline("disconnect {0}".format(device))
    print(" Disonnected!")


# function to get the name of the Myo.
def get_name(child):
    '''Function to get the name of the Myo'''
    child.sendline("char-read-hnd 0x03")
    child.expect("Characteristic value/descriptor:", timeout=10)
    # look for end of line with \r\n
    child.expect("\r\n", timeout=10)
    # get returned string (space separated) up to expected string pattern
    name_str = child.before
    # remove all spaces in string
    name_str = name_str.replace(' ', '')
    # decode hex string into ASCII
    name_myo = name_str.decode('hex')
    print("Device name: "),
    print(name_myo)


# function to get firmware version.
def get_firmware(child):
    '''Function to get the firmware version'''
    child.sendline("char-read-hnd 0x17")
    child.expect("Characteristic value/descriptor:", timeout=10)
    child.expect("\r\n", timeout=10)
    fw_str = child.before
    # remove last space in string (= 1 character)
    fw_str = fw_str[:-1]
    # replace spaces in string with \x ("\" is escape character)
    fw_str = fw_str.replace(' ', r'\x').decode('string-escape')
    # decode string with unpack() function
    v0, v1, v2, v3 = unpack('4h', fw_str)
    print('Firmware version: %d.%d.%d.%d' % (v0, v1, v2, v3))


# function to get battery level.
def get_battery_level(child):
    '''Function to get the battery level'''
    child.sendline("char-read-hnd 0x0011")
    child.expect("Characteristic value/descriptor:", timeout=10)
    child.expect("\r\n", timeout=10)
    print("Battery percentage: "),
    # convert hex string into int and then into float
    print(float(int(child.before, 16))),
    print("%")


# function to make Myo vibrate from 1 to 3 seconds
def vibrate(child, length):
    '''Function to make the Myo vibrate for length seconds'''
    print("The Myo will vibrate during " + str(length) + " second(s)")
    # change duration of vibration in command string
    string = 'char-write-req 0x19 03010' + str(length)
    child.sendline(string)


# function to change color of logo and line
# first 3B are for logo and last 3B are for line
# use RGB color code in hex to assign desired color to logo and line
# for instance: logo = 0000ff (blue) and line = ff0000 (red)
# logo and line must be string type
def set_leds(child, logo, line):
    '''Function to change color and intensity of logo and line of Myo'''
    string = 'char-write-req 0x19 0606' + str(logo) + str(line)
    child.sendline(string)


# function to start sending raw data and pose notifications
def start_raw(child):
    '''Sending this sequence for v1.0 firmware seems to enable both raw data and
    pose notifications.
    '''

    # enable IMU data
    # child.sendline("char-write-req 0x1d 0100")
    # start sending raw data (IMU (if enabled above) and EMG)
    child.sendline("char-write-req 0x28 0100")
    child.sendline("char-write-req 0x19 0103010100")
    child.sendline("char-write-req 0x19 0103010101")   # without this command the Myo disconnects after about 1 min.


# function to start sending raw data and pose notifications
def start_raw_fast(child):
    '''Sending this sequence for v1.0 firmware enables fast data transfer
    at 200Hz.
    '''

    # enable IMU data
    # child.sendline("char-write-req 0x1d 0100")
    # disable IMU data
    child.sendline("char-write-req 0x1d 0000")
    # enable on/off arm notifications
    # child.sendline("char-write-req 0x24 0200")
    # disable on/off arm notifications
    child.sendline("char-write-req 0x24 0000")

    # to get raw EMG signals, we subscribe to the four EMG notifications
    # characteristics by writing a 0x0100 command to the corresponding handles.
    child.sendline("char-write-req 0x2c 0100")  # Suscribe to EmgData0Characteristic
    child.sendline("char-write-req 0x2f 0100")  # Suscribe to EmgData1Characteristic
    child.sendline("char-write-req 0x32 0100")  # Suscribe to EmgData2Characteristic
    child.sendline("char-write-req 0x35 0100")  # Suscribe to EmgData3Characteristic
    # bytes sent to handle 0x19 (command characteristic) have the following
    # format: [command, payload_size, EMG mode, IMU mode, classifier mode]
    # according to the Myo BLE specification, the commands are:
    # 0x01 -> set EMG and IMU
    # 0x03 -> 3 bytes of payload
    # 0x02 -> send 50Hz filtered signals
    # 0x01 -> send IMU data streams
    # 0x01 -> send classifier events
    # child.sendline("char-write-req 0x19 0103020101")
    child.sendline("char-write-req 0x19 0103020000")

    # enable battery notifications
    # child.sendline("char-write-req 0x12 0110")
    # disable battery notifications
    child.sendline("char-write-req 0x12 0010")


# function to collect raw data
def collect_raw(child):
    '''Function to collect raw date at low sampling rate'''
    # for IMU data
    # child.expect("Notification handle = 0x001c value:", timeout=10)
    # for EMG data
    child.expect("Notification handle = 0x0027 value:", timeout=10)
    child.expect("\r\n", timeout=10)
    emg_str = child.before
    # emg_str looks like this: cc 00 2f 00 40 00 bb 01 14 01 f9 00 63 00 65 00 00
    # remove two last spaces and last byte in string (= 4 characters)
    emg_str = emg_str[:-4]
    # emg_str looks like this: cc 00 2f 00 40 00 bb 01 14 01 f9 00 63 00 65 00
    # replace spaces in string with \x ("\" is escape character)
    emg_str = emg_str.replace(' ', r'\x').decode('string-escape')
    # decode string with unpack() function (see common.py)
    emg_raw = unpack('8h', emg_str)
    # print(emg_raw)

    return emg_raw


# function to collect raw data at 200Hz
# received packets look like: Notification handle = 0x002b value: ff 01 06 31 12 0f 01 ff 00 01 03 eb 05 f0 fd 00
# there are 4 different attributes to look for: 0x002b, 0x002e, 0x0031, 0x0034
# it seems these attributes are not always coming in the same order...
# def collect_raw_fast(child):
#     '''Function to collect raw date at high sampling rate (200Hz)'''
#     i = child.expect(["Notification handle = 0x002b value:",
#                       "Notification handle = 0x002e value:",
#                       "Notification handle = 0x0031 value:",
#                       "Notification handle = 0x0034 value:"], timeout=10)
#     if i == 0:
#         child.expect("\r\n", timeout=10)
#         emg_str0 = child.before
#         # remove last space at the end of the string (= 1 character)
#         emg_str0 = emg_str0[:-1]
#         # print(emg_str0)
#         # replace spaces in string with \x ("\" is escape character) to use unpack() function.
#         emg_str0 = emg_str0.replace(' ', r'\x').decode('string-escape')
#         # decode string with unpack() function (see common.py)
#         emg_raw0a = unpack('8b', emg_str0[:8])
#         emg_raw0b = unpack('8b', emg_str0[8:])
#         print("emg_raw0a: ", emg_raw0a)
#         print("emg_raw0b: ", emg_raw0b)
#
#         return [emg_raw0a, emg_raw0b]
#
#     elif i == 1:
#         child.expect("\r\n", timeout=10)
#         emg_str1 = child.before
#         # remove last space at the end of the string (= 1 character)
#         emg_str1 = emg_str1[:-1]
#         # print(emg_str1)
#         # replace spaces in string with \x ("\" is escape character) to use unpack() function.
#         emg_str1 = emg_str1.replace(' ', r'\x').decode('string-escape')
#         # decode string with unpack() function (see common.py)
#         emg_raw1a = unpack('8b', emg_str1[:8])
#         emg_raw1b = unpack('8b', emg_str1[8:])
#         print("emg_raw1a: ", emg_raw1a)
#         print("emg_raw1b: ", emg_raw1b)
#
#     elif i == 2:
#         child.expect("\r\n", timeout=10)
#         emg_str2 = child.before
#         # remove last space at the end of the string (= 1 character)
#         emg_str2 = emg_str2[:-1]
#         # print(emg_str2)
#         # replace spaces in string with \x ("\" is escape character) to use unpack() function.
#         emg_str2 = emg_str2.replace(' ', r'\x').decode('string-escape')
#         # decode string with unpack() function (see common.py)
#         emg_raw2a = unpack('8b', emg_str2[:8])
#         emg_raw2b = unpack('8b', emg_str2[8:])
#         print("emg_raw2a: ", emg_raw2a)
#         print("emg_raw2b: ", emg_raw2b)
#
#     elif i == 3:
#         child.expect("\r\n", timeout=10)
#         emg_str3 = child.before
#         # remove last space at the end of the string (= 1 character)
#         emg_str3 = emg_str3[:-1]
#         # print(emg_str3)
#         # replace spaces in string with \x ("\" is escape character) to use unpack() function.
#         emg_str3 = emg_str3.replace(' ', r'\x').decode('string-escape')
#         # decode string with unpack() function (see common.py)
#         emg_raw3a = unpack('8b', emg_str3[:8])
#         emg_raw3b = unpack('8b', emg_str3[8:])
#         print("emg_raw3a: ", emg_raw3a)
#         print("emg_raw3b: ", emg_raw3b)


# simpler version of collect_raw_fast()
def collect_raw_fast(child):
    '''Function to collect raw date at high sampling rate (200Hz)'''
    i = child.expect(["Notification handle = 0x002b value:",
                      "Notification handle = 0x002e value:",
                      "Notification handle = 0x0031 value:",
                      "Notification handle = 0x0034 value:"], timeout=10)
    if i == 0 or i == 1 or i == 2 or i == 3:
        child.expect("\r\n", timeout=10)
        emg_str = child.before
        # remove last space at the end of the string (= 1 character)
        emg_str = emg_str[:-1]
        # print(emg_str)
        # replace spaces in string with \x ("\" is escape character) to use unpack() function.
        emg_str = emg_str.replace(' ', r'\x').decode('string-escape')
        # decode string with unpack() function (see common.py)
        emg_raw_a = unpack('8b', emg_str[:8])
        emg_raw_b = unpack('8b', emg_str[8:])
        # print("emg_raw_a: ", emg_raw_a)
        # print("emg_raw_b: ", emg_raw_b)

        return [emg_raw_a, emg_raw_b]


# function to put the Myo in different sleep mode (0 or 1).
# 0: the myo will go to sleep  mode after some inactivity.
# 1: the myo will not go into sleep mode at all.
def sleep_mode(child, mode):
    '''Function to put the Myo in different sleep mode'''
    string = 'char-write-req 0x19 09010' + str(mode)
    child.sendline(string)


def power_off(child):
    child.sendline("char-write-req 0x19 0400")


def main():
    counter = 0
    exitFlag = 0
    init_filt_var()

    DEVICE = "C8:6A:29:68:43:FB"

    print("Myo address:"),
    print(DEVICE)

    # Run gatttool interactively.
    print("Run gatttool...")
    child = pexpect.spawn("gatttool -I")

    connect(child, DEVICE)

    set_leds(child, 'ff00ff', '0000ff')  # set logo to magenta (ff00ff) and line to blue (0000ff)
    get_name(child)
    get_firmware(child)
    get_battery_level(child)

    # vibrate(child, 3)

    sleep_mode(child, 1)  # prevent to go into sleep mode

    # start_raw(child)  # sampling rate is about 50 data (8 EMG channels) per second
    start_raw_fast(child)  # sampling rate is about 200 data (8 EMG channels) per second

    tStart = time.time()

    try:
        while not exitFlag:
            # rawData = collect_raw(child)
            rawData = collect_raw_fast(child)
            # filtData = data_filtering(rawData)
            print(rawData[0])
            print(rawData[1])
            # diffData = filtData[3] - filtData[7]
            #
            # # set the sampling rate in second. 0.007s with Arduino MEGA and 0.005s with Arduino DUE and Teensy
            # if time.time() - tStart > 0.005:
            #     # send raw data
            #     # ser.write('%s,%s,%s,%s,%s,%s,%s,%s,' % (rawData[0], rawData[1], rawData[2], rawData[3], rawData[4], rawData[5], rawData[6], rawData[7]))
            #     # send filtered data
            #     # ser.write('%s,%s,%s,%s,%s,%s,%s,%s,' % (filtData[0], filtData[1], filtData[2], filtData[3], filtData[4], filtData[5], filtData[6], filtData[7]))
            #
            #     # ser.write('%s' % diffData)
            #
            #     tStart = time.time()

            # on RPi3: 2000 samples in about 10s on average => 200Hz
            # on RPi0: 2000 samples in about 13.5s on average => 148Hz
            # if counter == 1000:
            #     print(time.time() - tStart)
            #     tStart = time.time()
            #     counter = 0
            #
            # counter = counter + 1

        ser.close()

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        disconnect(child, DEVICE)
        exitFlag = 1
        print("exitFlag", exitFlag)

    finally:
        print("Finished")
        exitFlag = 1


if __name__ == "__main__":
    main()
