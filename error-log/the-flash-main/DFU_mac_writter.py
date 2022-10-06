import argparse
import subprocess
import struct

STM32CubeProgCLI = 'STM32_Programmer_CLI'
TSV = 'occuspace-rev_a12-v01.05.tsv'

def macParser(raw_mac:str):
    mac = raw_mac.split(':')

    # check length
    if len(mac) != 6:
        print("Wrong length for MAC address.")
        exit(-1)

    # check valid values
    try:
        bytearray.fromhex(''.join(str(x) for x in mac))
    except Exception as e:
        print(e)
        exit(-1)

    # parse to hex
    word1 = mac[0:4]
    word1 = word1[::-1]
    word1 = ''.join(str(x) for x in word1)

    word2 = mac[4:len(mac)]
    word2 = word2[::-1]
    word2 = ''.join(str(x) for x in word2)
    return word1, word2

def cubeprog(cmds:list, error_msg='Error during opertation'):
    #ret = subprocess.run([STM32CubeProgCLI, '-c', f'port={args.port}'] + cmds)
    ret = subprocess.run([STM32CubeProgCLI, '-c', f'port=usb', f'sn={args.serial_number}'] + cmds)
    #ret = subprocess.run([STM32CubeProgCLI, '-c', f'port={args.port}'] + cmds, capture_output=True)
    #print(ret.stdout.decode())
    if ret.returncode:
        print(error_msg)
        exit(-1)
    return ret

def getMacFromOtp(out):
    w1 = None
    w2 = None
    lines = out.splitlines()
    for line in lines:
        line = line.decode().split(' ')
        line = [x for x in line if x]
        if len(line) == 8:
            if line[0] == '57':
                w1 = line
            elif line[0] == '58':
                w2 = line
    if w1 != None:
        print(f'\tOTP 0x39: {w1[1]}, Permanent Lock: {w1[7]}')
    if w2 != None:
        print(f'\tOTP 0x3A: {w2[1]}, Permanent Lock: {w2[7]}')
        print(f'\tMAC Address: {parseMac(w1[1], w2[1])}')

def parseMac(w1,w2):
    _w1 = struct.unpack('BBBBBB', int(w1, 0).to_bytes(6, 'little'))
    _w2 = struct.unpack('BBBBBB', int(w2, 0).to_bytes(6, 'little'))
    return '{0:02x}:{1:02x}:{2:02x}:{3:02x}:{4:02x}:{5:02x}'.format(_w1[0], _w1[1], _w1[2], _w1[3], _w2[0], _w2[1])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to write eth MAC address over DFU')
    parser.add_argument('mac', type=str, help='MAC address in format 12:34:56:78:9a:bc')
   # parser.add_argument('-p', '--port', type=str, default="usb1", help='Port from STM32CubeProgrammer. Default: USB1')
    parser.add_argument('--sn', type=str, help='serial_number from STM32CubeProgrammer.')
    parser.add_argument('-l', '--lock', action='store_true', help='Lock OTP. WARNING: Enabling this will not allow further MAC changes')

    args = parser.parse_args()

    w1, w2 = macParser(args.mac)

    # Flash to RAM to access U-Boot
    cubeprog(['-w', TSV])

    # Get current values
    ret = cubeprog(['-otp', 'displ'])
    #print("\nInitial OTP for eth MAC")
    #getMacFromOtp(ret.stdout)

    # Write OTP
    print("\nWritting OTP")
    cmd_mac = [['-otp', 'program', 'wordId=0x39', f'value=0x{w1}'], ['-otp', 'program', 'wordId=0x3A', f'value=0x0000{w2}']]
    if args.lock:
        for cmd in cmd_mac:
            print(f"\tWARNING: {cmd[2]}: {cmd[3]} with Protection Lock enabled")
            cubeprog(cmd + ['pl=1'])
    else:
        for cmd in cmd_mac:
            print(f"\t{cmd[2]}: {cmd[3]}")
            cubeprog(cmd)

    # Show MAC from OTP
    ret = cubeprog(['-otp', 'displ'])
    #print("\nCurrent OTP for eth MAC")
    #getMacFromOtp(ret.stdout)
    
