import socket

BUFF_SZ = 1024
ENC = "utf-8"


def main():
    print("Logs from your program will appear here!")
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 4221

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()  # create a listener socket
        conn, addr = s.accept()
        with conn:
            print(f"Connection from {addr} has been established...")
            while True:
                data = conn.recv(BUFF_SZ)
                if not data:
                    break
                conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")


if __name__ == "__main__":
    main()
