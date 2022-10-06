'''
this is Linux/MacOS version:
--no-fuse
ConnectToDB
table view
identify Linux or MacOS for USB info
create log file and check_flash_error
Passing serial number to DFU_mac_writter.py and occu_mac_generator.py
'''
import subprocess
import shlex
import os
import time
import random
import pprint
import pandas as pd
from tabulate import tabulate
import argparse
import sys
import re

ImagineVersion = "Treeline-imagine-occuspace-eMMC-v99.01.08.tsv"

# add arg about use fuse mac function or not
parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("--no-fuse", help="not run fuse mac fuction",action="store_true")
args = parser.parse_args()

# Find the path of STM programmer and image path from home and root directory(MacOS)
def find(name): 
    home = os.path.expanduser("~")
    for root, dirs, files in os.walk(home):
        if name in files:
            return os.path.join(root, name)  #find the first file
    for root, dirs, files in os.walk("/"):
        if name in files:
            return os.path.join(root, name)
    print(f"couldn't find {name}")
    os.exit(0)

# Connect to database, need to have MFA first
def connectDB():
    os.environ["AWS_PROFILE"]="occu-dev"
    sh_path = find("connect-to-instance.sh")
    process = subprocess.Popen([sh_path, "-d", "rds-training-tunnel-instance"])
    print("Start connect to DB")
    return


def id_platform_scan_STMboards():

    boards_plugged_in = []
    if sys.platform.startswith("linux"):
        print("linux")
        command = "lsusb -d 0483:df11 -v"
        USBinfo = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['grep', '-i', 'iserial'], stdin=USBinfo.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        USBinfo.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
        out, err = proc2.communicate()
        result = out.decode('utf-8')
        for device in result.split('\n'):
            serial_number = device.strip(" iSerial3 ")
            if len(serial_number) <= 1:
                continue
            print(serial_number)
            boards_plugged_in.append(serial_number)
        return boards_plugged_in

    elif sys.platform == "darwin":
        print("mac")
        USBinfo = subprocess.Popen('lsusb', stdout=subprocess.PIPE).stdout.read()
        USBinfo=USBinfo.decode('utf-8')
        for device in USBinfo.split('\n'):
            if "STMicroelectronics" in device:
                split_STMdevice = device.split("Serial: ") # split_STMdevice[1] is the serial number
                serial_number = split_STMdevice[1]
                print(serial_number)
                boards_plugged_in.append(serial_number)
            else:
                continue
        return boards_plugged_in

# GetOrder function will return the hubs' power up order
def getOrder(serial_info: dict):
    if len(serial_info) == 0:
        return 1
    else:
        max_order = 0
        for k in serial_info:
            order = serial_info[k]["Order"][0]
            if max_order < order:
                max_order = order

        # Check whether we have boards plugged in from previous run so order is always 0-7
        if max_order >= 8:
            order = len(serial_info)
            return order
        return max_order + 1

# Use subprocess to run the flash command in background, and print the serial number of current board that's flashing
def flash_board(serial_number: str):
    command = f"{STM32cubeprogrammerPath} -c port=usb sn={serial_number}  -w {ImagineVersion}"
    # overwrite log file with sn number
    log = open(f'{serial_number}.log', 'w')
    process = subprocess.Popen(shlex.split(command),cwd=ImagePath,stdout=log ,universal_newlines=True )
    print (f'Started flashing board {serial_number}')
    return process

# A fake mac address generator, will generator a random mac address, this function will be replaced by real fuse mac python script
def fuse_mac(serial_number: str):
    command = f"python3 occu_mac_generator.py --sn {serial_number}"
    try:
        output = subprocess.check_output(shlex.split(command))
        mac = output.decode('utf-8').split("04:d9:21:")
        return mac[1]
    except subprocess.SubprocessError:
        print("Failed to fuse MAC address")
        return False

# Use process poll() to return the process's exit code if the process has finished. The poll() method will return None if the process is still running
def check_board_flashing_status(process):
    #print(process.pid)
    if process.poll() is None: # Means we are still flashing
        print("Board is still flashing")
        return "Flashing"
    else:
        print("Board is done flashing")
        return "Completed Flashing"

# Compare the boards currently plugged in with all boards ever connected, to find which board is unplugged
def check_board_is_unplugged(serial_info: dict, boards_plugged_in: list):
    boards = serial_info.keys()
    for board in boards:
        count = 0
        for _ in range(3):
            if board not in boards_plugged_in:
                count += 1
            time.sleep(0.5)
        if count == 3:
                order = serial_info[board]["Order"][0]
                if serial_info[board]["State"] != "Unplugged" and serial_info[board]["State"] != "Completed Flashing" and serial_info[board]["State"] != "Finished MAC Fusing":
                    print(f"Board with serial number: {board} has been unplugged prior to completing flashing. It was plugged in order: {order}\nPlease check if there was a flashing error")
                    err = check_flash_error(serial_number)
                    serial_info[board]["State"] = "Unplugged Before Flashing"
                    return board
                else:
                    serial_info[board]["State"] = "Unplugged"
                    mac = serial_info[board]["MAC"]
                    print(f"Board with serial number: {board} has been unplugged and has MAC: {mac}. It was plugged in order: {order}")
                    return board
    return False

# Captures flashing error and returns it if there's one - still in dev
def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

# check if there are error from log file and print it in red
def check_flash_error(serial_number: str):
    file = f"{serial_number}.log"
    newline = False
    with open(file) as file:
        line = (file.readlines() [-10:])
        for line in line:
            if "Error" in line:
                newline = escape_ansi(line)
                print(f"\033[031m{newline}\033[0m")
        if newline:
            return f"\033[031m{newline}\033[0m"
        return

print("Start finding path...")
#STM32cubeprogrammerPath = find("STM32_Programmer_CLI")
#ImagePath = find(ImagineVersion).replace(ImagineVersion, '')
STM32cubeprogrammerPath = "/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin/STM32_Programmer_CLI"
ImagePath = "/Users/jingxiao/Documents/Occuspace/Image/prod_image_08_22"
print("STM32 cube programmer Path:",STM32cubeprogrammerPath)
print("Image Path:",ImagePath)

#connectDB()

serial_info = {}

print("*" * 50)
print("Flashing process begin")
print("*" * 50)
while True:

    boards_plugged_in = id_platform_scan_STMboards()
    for serial_number in boards_plugged_in:

        order = getOrder(serial_info)
        
        if serial_number not in serial_info:
            serial_info[serial_number] = {}
            serial_info[serial_number]["Order"] = order,
            serial_info[serial_number]["State"] = "Plugged In"
            process = flash_board(serial_number)
            serial_info[serial_number]["Process"] = process
            serial_info[serial_number]["State"] = "Flashing"
        else:
            if serial_info[serial_number]["State"] == "Flashing":
                process = serial_info[serial_number]["Process"]
                status = check_board_flashing_status(process)
                order = serial_info[serial_number]["Order"][0]
                err = check_flash_error(serial_number)
                if err:
                    serial_info[serial_number]["State"] = "Error"
                    continue
                serial_info[serial_number]["State"] = status
            elif serial_info[serial_number]["State"] == "Completed Flashing":
                order = serial_info[serial_number]["Order"][0]
                # add arg to use fuse_mac function or not
                if args.no_fuse:
                    print("Mac Fusing has been disabled")
                    print(f"Board: {serial_number} in order {order} won't have it's MAC fused")
                    mac = ("N/A")
                    serial_info[serial_number]["MAC"] = mac
                    print(f"Board with serial number: {serial_number} and order: {order} is done flashing and no MAC was fused. It can now be unplugged")
                else:
                    print("Run fuse mac function")
                    mac = fuse_mac(serial_number)
                    print("Fusing MAC")
                    if not mac:
                        print(f"Board: {serial_number} in order {order} couldn't have it's MAC fused")
                        continue
                    serial_info[serial_number]["MAC"] = mac
                    serial_info[serial_number]["State"] = "Finished MAC Fusing"
                    print(f"Board with serial number: {serial_number} and order: {order} is done flashing and has MAC: {mac}. It can now be unplugged")
            elif serial_info[serial_number]["State"] == "Finished MAC Fusing":
                order = serial_info[serial_number]["Order"][0]
                mac = serial_info[serial_number]["MAC"]
                print(f"Board with serial number: {serial_number} and order: {order} is done flashing and has MAC: {mac}. It can now be unplugged")
          
    board = check_board_is_unplugged(serial_info, boards_plugged_in)
    if board:
        serial_info.pop(board, None)


    headers = ["SN number", "Order", "State", "Process", "Mac"] # make the table header fixed
    df = pd.DataFrame(serial_info).T
    print(tabulate(df, headers=headers, tablefmt='psql'))  # replace "keys" with headers

    time.sleep(5)

