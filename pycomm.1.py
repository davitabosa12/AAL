import argparse
import socket
import struct
import sys

import pika
import serial as pyserial
import time
from iobl import parser
import data_pb2
def waitForActivate():
    print("Waiting for ACTIVATE...")
    #send a multicast message, turning on the servers    
    multicast_group = '225.2.2.5'
    port = 41214
    group = socket.inet_aton(multicast_group)
    payload = 'ACTIVATE'
    mreq = struct.pack('4sL', group, socket.INADDR_ANY) # prevents network flood
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.bind(('',41214)) #bind nada
    sock.recv(1024)
    return time.time()


    
    

            
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



def sendToRabbitMQ(msg_byte, channel, time_init):
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
    
    data.Location = house_rooms[decoded["hex"]]
    data.Entity_Id = decoded["dec"]
    data.Timestamp = str(time.time() - time_init)
    to_rabbit = data.SerializeToString()
    print("Sending to RabbitMQ...")
    channel.basic_publish(exchange='', routing_key='location', body= to_rabbit)
    print("Sent: {}", to_rabbit)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', '-s', help="serial port", action="store")
    parser.add_argument('--gateway', '-g', help="gateway's address", type= str)
    args = parser.parse_args()
    if(args.gateway == None):
        parser.print_help()
        quit()
    serial_port = args.serial or "ttyACM0"
    gateway = args.gateway
    credentials = pika.PlainCredentials('user', 'aalgreat')
    amqp_params = pika.ConnectionParameters(host=gateway, credentials=credentials, socket_timeout=1)
    try:
        connection = pika.BlockingConnection(
            parameters= amqp_params
        )
    except pika.exceptions.AMQPConnectionError as e:
        print("Can't connect to {}", gateway)
        print(e)
        quit()
    channel = connection.channel()
    
    time_t0 = waitForActivate()
    print("STARTING    EXPERIMENT")
    with pyserial.Serial('/dev/' + serial_port) as serial:
        print(serial.name)
        while True:
            try:
                from_serial = bytes()
                while(serial.in_waiting):
                    from_serial += serial.read(1)
                
                if(from_serial == bytes()):
                    pass
                else:
                    printEvent(from_serial)
                    sendToRabbitMQ(from_serial, channel, time_t0)
            except KeyboardInterrupt:
                print("Bye!")
                break

if __name__ == "__main__":
    main()
