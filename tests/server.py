import socket
import time

HOST = '127.0.0.1'
PORT = 65432

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is running. Waiting for client...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                time.sleep(2)  # Every 2 seconds
                message = "ADD_BALL"
                print(f"Sending: {message}")
                conn.sendall(message.encode())

if __name__ == "__main__":
    main()
