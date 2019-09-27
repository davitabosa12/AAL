
'''
WEBSERVER 3
Server using direct TCP calls WITHOUT protobuf.
'''

import csv
import threading
import argparse
from datetime import datetime

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO

import data_pb2
import time
import socket
import struct
import datetime
import json
legrand_received = 0
tapir_received = 0
#with open("log.csv") as csv_file:
#    csv_reader = csv.reader(csv_file, delimiter=';')
#    line_count = 0
#    data_bytes = []
#    print("Reading...")
#    for row in csv_reader:
#        
#        data_to_send = data_pb2.Data()
#
#        data_to_send.Entity_Id = 101
#        data_to_send.Location = row[2]
#        data_to_send.Timestamp = row[0]
#
#        data_bytes.append(data_to_send.SerializeToString())
#    print('Data read.')

def log_timestamp(message, file_log, time_t0):    
    with open(file_log, 'a') as log_file:
        log_file.write(message)
# Setup arguments
        
time_t0 = 0

parser = argparse.ArgumentParser()
parser.add_argument('--gateway', '-g', help="gateway's address", type= str)

args = parser.parse_args()


print('Starting Flask server...')
app = Flask(__name__)
print("Starting Socket.io...")
socketio = SocketIO(app)

@app.route('/static/<path:path>')
def handle_static(path):
    send_from_directory('static', path)

@app.route('/')
def handle_index():
    return render_template('index.html')


def startExperiment():
    print("Turning on servers...")
    #send a multicast message, turning on the servers    
    multicast_group = ('225.2.2.5', 41214)
    payload = 'ACTIVATE'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.5) # 2.5s of timeout
    
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 64)
    sock.sendto(bytes(payload, 'utf8'), multicast_group)
    time_t0 = time.time()
    print("Done.")
    return ("wslog/wslog-" +datetime.datetime.utcnow().isoformat().replace('-', '').replace(':','').replace('.','') + '.txt', time_t0)



def send_new_position(data_byte):
    socketio.emit('new_position', data_byte)
    print(f'Sending position to client: {data_byte}')




file_log, time_t0 = startExperiment()

def parse_json(msg):
    
    
    return json.loads(msg)

def parse_legrand(msg_byte):
    device_id_dec = int(msg_byte[12:19])
    device_id_dec = device_id_dec >> 4
    device_id = hex(device_id_dec)
    data = {
        'Location' : "not defined",
        'Entity_Id' : device_id,
        'Timestamp' : ""
    }
    return data



def received(body):
    print(f'Message received: {body}')
    header, msg = body.split(b'\n', 1) # only 1 split necessary
    global tapir_received
    global legrand_received
    if(header == b'JSON'):
        data = parse_json(msg)
        tapir_received += 1
        msg_to_log = f'[TAPIR {tapir_received}] '
    elif(header == b'LEGRAND'):
        data = parse_legrand(msg)
        legrand_received += 1
        msg_to_log = f'[LEGRAND {legrand_received}] '
    else:
        data = None
        raise Exception('asd')
        pass #exception, not supported data type

    
    to_client = {
        'Location': data['Location'],
        'Entity_Id': data['Entity_Id'],
        'Timestamp': data['Timestamp']
    }
    #Data read. Log timestamp;
    current_time = time.time() # time in seconds since 01 January 1970 (fpu)
    msg_to_log += f"\t {str(current_time - time_t0)} \t {str(to_client)}\n"
    log_timestamp(msg_to_log, file_log, time_t0)
    send_new_position(to_client)


PORT = 8077 #default TCP port for log and RF info listening

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr = ('0.0.0.0', PORT) # the server address
tcp_socket.bind(addr)
tcp_socket.listen(1)
def readTCP():
    try:
        while (True):
            print(f"Listening for Widget info on port {PORT}...")
            connection, client_addr = tcp_socket.accept()
            try:
                print(f"Connection from {client_addr}...")
                data = ""
                while (True):
                    chunk = connection.recv(1000)
                    if(chunk):
                        data += str(chunk, 'utf8')
                    else:
                        break
            finally:
                connection.close()
            # log the data...
            received(bytes(data, 'utf8'))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    



async_server = threading.Thread(target=readTCP)
async_server.daemon = True
async_server.start()


print("Starting Flask App...")
socketio.run(app, host='0.0.0.0')
