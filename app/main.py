import socket
import argparse
import os
import threading
import select

import sys

BUFF_SZ = 1024
ENC = "utf-8"


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
    # get the file name
    filename = "".join(req_target[7:].split(" "))

    full_path = os.path.join(
        directory, filename
    )  # create the full path so you can read the fle

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


def post_filename(req, directory):
    print(f"inside post_filename: HTTP Request: {req}")
    req_str = " ".join(req).split(" ")
    req_target = req_str[1]
    # get the file name
    filename = "".join(req_target[7:].split(" "))

    # create the full path so you can read the fle
    full_path = os.path.join(directory, filename)
    print("full_path: ", full_path)

    # get the request body
    req_body = req[5]

    # write the contents of the request body to the file
    with open(full_path, "wt") as file:
        print("req_body: ", req_body)
        file.write(req_body)

    # return status code
    return f"HTTP/1.1 201 Created\r\n\r\n".encode("utf-8")


# routes
def parse_request(req, directory):
    print(f"HTTP Request: {req}")
    req_str = " ".join(req).split(" ")  # Split the request into words
    req_target = req_str[1]  # Extract the request target path
    req_method = req_str[0]

    if req_method == "POST":
        result = post_filename(req, directory)
        print("in parse_request", result)
        return result

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
        print("see if get_filename is called..."), result
        return result
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"


def handle_connection(conn, data, directory):
    data = conn.recv(BUFF_SZ)
    print(f"Raw request: {data}")
    req = data.decode(ENC).split("\r\n")
    response = parse_request(req, directory)

    print("Return value of response: ", response)
    conn.sendall(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str)
    args = parser.parse_args()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    try:
        while True:
            conn, address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_connection, args=(conn, address, args.directory)
            )
            client_thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
