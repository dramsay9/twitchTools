import pickle
import socket
import struct
import cv2
from deepface import DeepFace
from gaze_tracking import GazeTracking
import numpy as np
import time


HOST = ''
PORT = 5057

payload_size = struct.calcsize("L")

def connect():
    global s, conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    s.bind((HOST, PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    conn, addr = s.accept()

connect()

while True:
    try:
        data = b''
        # Retrieve message size
        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Extract frame
        frame = pickle.loads(frame_data)

        ##############
        # Echo it back
        ##############

        # Serialize frame
        data = pickle.dumps(frame)
        # Send message length first
        message_size = struct.pack("L", len(data))
        # Then data
        conn.sendall(message_size + data)
    except:
        print('ERROR, reset connection')
        connect()
