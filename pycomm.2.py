import argparse
import socket
import struct
import sys

import pika
import serial as pyserial
import time
import datetime
from iobl import parser
import data_pb2
PORT = 8077
"""
Waits for ACTIVATE message from webserver. Returns the starting time and the webserver address.
"""
def waitForActivate():
    print("Waiting for ACTIVATE...")
    #send a multicast message, turning on the servers    
    multicast_group = '225.2.2.5'
    port = 41214
    group = socket.inet_aton(multicast_group)
    payload = 'ACTIVATE'
    mreq = struct.pack('4sL', group, socket.INADDR_ANY) # socket option - add IGMP membership
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.bind(('',41214)) #bind nada
    data, address = sock.recvfrom(1024)
    
    return (time.time(), address)


            
def printEvent(event):
    device_id_dec = int(event[12:19])
    print("dec: " + str(device_id_dec))
    device_id_dec = device_id_dec >> 4
    device_id = hex(device_id_dec)
    print(device_id)

def decode_serial(msg_byte):
    device_id_dec = int(msg_byte[12:19])
    print("dec: " + str(device_id_dec))
    device_id_dec = device_id_dec >> 4
    device_id = hex(device_id_dec)
    return {
    "dec" :device_id_dec,
    "hex" : device_id
    }
    
def sendToAddress(msg_byte, addr, time_init):
    house_rooms = {
    "0x1699a": "entrance",
    "0x169d6": "room1",
    "0x16a31": "room2",
    "0x169c6": "kitchen",
    "0x1929c": "bathroom",
    "0x169d2": "bedroom"
    }
    decoded = decode_serial(msg_byte)
    data = data_pb2.Data()
    data.Location = house_rooms[decoded["hex"]] or "unknown"
    data.Entity_Id = decoded["dec"]
    data.Timestamp = str(time.time() - time_init)
    protobuf_data = data.SerializeToString()
    print(addr)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(addr)
        s.settimeout(1.0)
        s.sendall(protobuf_data)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', '-s', help="serial port, defaults to /dev/ttyACM0", action="store")
    args = parser.parse_args()
    serial_port = args.serial or "/dev/ttyACM0"
    
    time_t0, address = waitForActivate()
    log_file_name = "pycomm-" +datetime.datetime.utcnow().isoformat().replace('-', '').replace(':','').replace('.','') + '.txt'
    print("STARTING    EXPERIMENT")
    with pyserial.Serial(serial_port) as serial:
        print(serial.name)
        while True:
            try:
                from_serial = bytes()
                while(serial.in_waiting):
                    from_serial += serial.read(1)
                
                if(from_serial == bytes()): # if empty
                    pass
                else:
                    sendToAddress(from_serial, (address[0], PORT), time_t0)
                    printEvent(from_serial)
            except KeyboardInterrupt:
                print("Bye!")
                break

if __name__ == "__main__":
    main()
