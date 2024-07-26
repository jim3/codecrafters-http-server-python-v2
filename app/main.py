import socket


def parse_request(req):
    print(f"HTTP Request: ${req}")
    req_str = " ".join(req).split(" ")
    req_target = req_str[1]

    if req_target == "/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"


def handle_connection(conn, data):
    print(f"Raw request: {data}")
    req = data.decode("utf-8").split("\r\n")
    response = parse_request(req)
    print("Return value of response: ", response)
    conn.sendall(response)


def main():
    print("Logs from your program will appear here!")
    HOST = "127.0.0.1"
    PORT = 4221

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()  # create a listener socket
        conn, addr = s.accept()
        with conn:
            print(f"Connection from {addr} has been established...")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
                handle_connection(conn, data)


if __name__ == "__main__":
    main()
