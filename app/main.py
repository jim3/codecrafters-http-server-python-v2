import socket
import select
import argparse
import os


def echo(req):
    req_str = " ".join(req).split(" ")  # Split the request into words
    req_target = req_str[1]  # Extract the request target
    res_body = "".join(req_target[6:].split(" "))
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(res_body)}\r\n\r\n{res_body}".encode(
        "utf-8"
    )


def user_agent(req):
    req_str = " ".join(req).split(" ")  # Split the request into words
    user_agent = req_str[6]  # Extract the user-agent string
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode(
        "utf-8"
    )


def get_filename(req, directory):
    req_str = " ".join(req).split(" ")
    req_target = req_str[1]
    filename = "".join(req_target[7:].split(" "))
    full_path = os.path.join(directory, filename)
    # Check if the file exists
    if not os.path.exists(full_path):
        return b"HTTP/1.1 404 Not Found\r\n\r\n"

    with open(full_path, "rt") as file:
        data = file.read()
        print("results of data: ", data)
        res_body = data
    return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(res_body)}\r\n\r\n{res_body}".encode(
        "utf-8"
    )


def parse_request(req, directory):
    print(f"HTTP Request: {req}")
    print(directory)
    req_str = " ".join(req).split(" ")  # Split the request into words
    req_target = req_str[1]  # Extract the request target path
    print("req_target: ", req_target)

    # Handle endpoints
    if req_target == "/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    elif req_target.startswith("/echo"):
        result = echo(req)
        return result
    elif req_target.startswith("/user-agent"):
        result = user_agent(req)
        return result
    elif req_target.startswith("/files"):
        result = get_filename(req, directory)
        print("result of get_filename call ->"), result
        return result
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"


def handle_connection(conn, data, directory):
    print(f"Raw request: {data}")
    req = data.decode("utf-8").split("\r\n")
    print("directory value: ", directory)
    response = parse_request(req, directory)
    print("Return value of response: ", response)
    conn.sendall(response)


def main():
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--directory",
        type=str,
        default="/tmp/data/codecrafters.io/http-server-tester/",
        help="Directory where files are stored",
    )
    args = parser.parse_args()
    s = socket.socket()
    HOST = "127.0.0.1"
    PORT = 4221
    s.bind((HOST, PORT))
    s.listen(5)  # Queue up to 5 requests
    inputs = [s]  # list of sockets
    while True:
        try:
            print("Waiting for request...")
            rs, ws, es = select.select(inputs, [], [])
            for r in rs:
                if r is s:
                    conn, addr = r.accept()
                    inputs.append(conn)
                else:
                    data = r.recv(1024)
                    if not data:
                        inputs.remove(r)
                        r.close()
                    else:
                        handle_connection(r, data, args.directory)
        except KeyboardInterrupt:
            break

    s.close()


if __name__ == "__main__":
    main()
