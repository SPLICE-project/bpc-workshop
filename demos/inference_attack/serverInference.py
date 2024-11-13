import socket

def start_server(host='', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))

        print(f"Server listening on {host}:{port}")
        
        while True:
            data, addr = s.recvfrom(1024)
            print(f"Received from {addr}: {data.decode()}")

if __name__ == "__main__":
    start_server()