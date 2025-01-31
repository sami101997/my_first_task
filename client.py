import socket
import cv2
import struct
import threading
import numpy as np

# Client configuration
SERVER_IP = "192.168.1.8"  # Replace with the server IP
PORT = 2020

def send_video(sock, cap):
    """Send video frames to the server."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()

        # Send frame size followed by the frame data
        sock.sendall(struct.pack("I", len(frame_data)) + frame_data)

def receive_video(sock):
    """Receive and display video frames from the server."""
    while True:
        # Receive frame size
        data = sock.recv(4)
        if not data:
            break

        frame_size = struct.unpack("I", data)[0]

        # Receive the frame data
        frame_data = b""
        while len(frame_data) < frame_size:
            frame_data += sock.recv(1024)

        # Decode and display the frame
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        if frame is not None:
            cv2.imshow("Client Side", frame)

        if cv2.waitKey(1) & 0xFF == 13:  # Break on Enter key
            break

# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, PORT))

# Start video capture
cap = cv2.VideoCapture(0)

# Start threads for sending and receiving video
send_thread = threading.Thread(target=send_video, args=(sock, cap))
receive_thread = threading.Thread(target=receive_video, args=(sock,))

send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

# Cleanup
cap.release()
cv2.destroyAllWindows()
sock.close()
