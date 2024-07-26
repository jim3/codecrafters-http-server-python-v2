import socket


# HTTP request parsing
def parse_request(req):
    print(f"HTTP Request: {req}")
    req_str = " ".join(req).split(" ")
    print("req_str: ", req_str)
    req_target = req_str[1]
    print("req_target: ", req_target)  # /user-agent
    user_agent = req_str[6]
    print(f"user_agent:  {user_agent}") # the value of user-agent
    
    if req_target == "/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    elif req_target.startswith("/echo"):
        res_body = "".join(req_target[6:].split(" "))
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(res_body)}\r\n\r\n{res_body}".encode(
            "utf-8"
        )
    elif req_target.startswith("/user-agent"):
        # u_agent = "".join(req_target[6:].split("\r\n"))
        print(
            f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode(
                "utf-8"
            )
        )
        
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode(
            "utf-8"
        )
    # --------------------------------------------- #
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"


def handle_connection(conn, data):
    print(f"Raw request: {data}")
    req = data.decode("utf-8").split("\r\n")
    response = parse_request(req)
    print("Return value of response: ", response)
    conn.sendall(response)


def main():
    HOST = "127.0.0.1"
    PORT = 4221
    print("Logs from your program will appear here!")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
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
