import socket
import cv2
import struct
import threading
import numpy as np

# Server configuration
HOST = "192.168.1.8"  # Replace with your server IP
PORT = 2020

def send_video(conn, cap):
    """Send video frames to the client."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()

        # Send frame size followed by the frame data
        conn.sendall(struct.pack("I", len(frame_data)) + frame_data)

def receive_video(conn):
    """Receive and display video frames from the client."""
    while True:
        # Receive frame size
        data = conn.recv(4)
        if not data:
            break

        frame_size = struct.unpack("I", data)[0]

        # Receive the frame data
        frame_data = b""
        while len(frame_data) < frame_size:
            frame_data += conn.recv(1024)

        # Decode and display the frame
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        if frame is not None:
            cv2.imshow("Server Side", frame)

        if cv2.waitKey(1) & 0xFF == 13:  # Break on Enter key
            break

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server listening on {HOST}:{PORT}")

# Accept client connection
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

# Start video capture
cap = cv2.VideoCapture(0)

# Start threads for sending and receiving video
send_thread = threading.Thread(target=send_video, args=(conn, cap))
receive_thread = threading.Thread(target=receive_video, args=(conn,))

send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

# Cleanup
cap.release()
cv2.destroyAllWindows()
conn.close()
server_socket.close()
