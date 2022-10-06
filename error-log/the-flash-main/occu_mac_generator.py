import random
import hubdata.db as db
from DFU_mac_writter import *
import argparse

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("--sn",type=str)
args = parser.parse_args()

occu_mac = '04:d9:21:'

new_occu_mac = False

while new_occu_mac == False:
    
    # Generate mac address
    numbers = list(range(16**6))
    hex_num = hex(random.choice(numbers))[2:].zfill(6)
    mac = "{}{}{}:{}{}:{}{}".format(occu_mac,*hex_num)
    name = mac.replace(':','')
    
    # Check if MAC address is already registered in the DB
    query = """
    SELECT 
        *
    FROM
        inventory
    WHERE
        name = 'waitz{name}'
    """.format(name=name)
    print(query)
    db.check_connection()
    with db.connection.cursor() as cursor:
        cursor.execute(query)
        if cursor.rowcount == 0:
            new_occu_mac = True
            
print(mac)

import os
os.system(f"python3 DFU_mac_writter.py {mac} --sn {args.sn}")

print(mac)
