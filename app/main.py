import socket
import select
import argparse
import os
import time
import threading


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
    # create the full path so you can read the fle
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


def post_filename(req, directory):
    print(f"post_filename req: {req}")

    code = "201 Created\r\n\r\n"
    status_code = str(code)

    # content type
    content_type = "application/octet-stream"

    # get list of words and extract filename
    req_str = " ".join(req).split(" ")
    req_target = req_str[1]

    # extract the files_route and filename
    files_route = "".join(req_target[1:7].split(" "))
    filename = "".join(req_target[7:].split(" "))  # "apple_applge_etc"

    # the contents of the request body.
    req_body = req[5]
    print("req_body: ", type(req_body))  #  <class 'str'>

    # Remove null bytes from the content
    # file_contents = file_contents.replace("\0", "")

    # join directories w/o using teh file name
    # dir_path = os.path.join(directory, files_route)
    file_path = os.path.join(directory, filename)

    # Join various paths including filename
    full_path = os.path.join(directory, files_route, filename)
    print(f"full_path: {full_path}")

    # Ensure the directory exists
    # print(os.makedirs(os.path.dirname(dir_path), exist_ok=True))

    # Write the contents of the request body to the file
    if file_path:
        with open(full_path, encoding="utf-8") as f:
            f.write(req_body)
            content_length = len(req_body)
            # return [status_code, content_length, req_body]
            # return [status_code, content_type, content_length, req_body]
            print(
                f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n{req_body}".encode(
                    "utf-8"
                )
            )

            # return f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n{req_body}".encode(
            #     "utf-8"
            # )
    else:
        return None

    # Create a response
    # return f"HTTP/1.1 201 Created\r\n\r\n".encode("utf-8")

    # --------------------------------------------- #


# routes
def parse_request(req, directory):
    print(f"HTTP Request: {req}")
    req_str = " ".join(req).split(" ")  # Split the request into words
    # print("req_str_words", req_str)
    req_target = req_str[1]  # Extract the request target path
    # print("req_str_words_req_target: ", req_target)
    req_method = req_str[0]
    # print("req_method is: ", req_method)

    if req_method == "POST":
        result = post_filename(req, directory)
        print("in parse_request", result)
        # return result

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


# orginal version
def handle_connection(conn, data, directory):
    # print(f"Raw request: {data}")
    req = data.decode("utf-8").split("\r\n")
    # print("directory value: ", directory)
    response = parse_request(req, directory)
    print("Return value of response: ", response)
    conn.sendall(response)


# --------------------------------------------- #


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

""" 
# --------------------------------------------- #
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str)
    args = parser.parse_args()
    s = socket.create_server(("localhost", 4221), reuse_port=True)
    s.listen()
    try:
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(
                target=handle_connection, args=(conn, addr, args.directory)
            )
            client_thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        s.close()

 """

# --------------------------------------------- #
