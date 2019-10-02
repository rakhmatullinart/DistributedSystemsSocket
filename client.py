import socket
import sys
from time import sleep
from math import ceil


def send_file(filename, sock):
    progress = 0
    with open(filename, "rb") as f:
        bytes_count = len(bytearray(f.read()))
        f.seek(0)
        parts = ceil(bytes_count / 1024)
        step = 100 / parts
        print(".. 2%")
        l = f.read(1024)
        while l:
            progress += step
            print("." * int(progress // 2) + f" {int(progress)}%")
            sock.send(l)
            l = f.read(1024)
            sleep(0.5)
    sock.send(b"EOF")


def initiate_file_transfer(ip, port, filename):
    sock = socket.socket()
    sock.connect((ip, int(port)))
    sock.send(b"file_transfer")
    data = sock.recv(1024)
    if data == b"start":
        sock.send(bytes(filename, encoding="utf-8"))
        data = sock.recv(1024)
        sleep(1)
        if data == b"filename accepted":
            send_file(filename, sock)
    sock.close()


if __name__ == "__main__":
    try:
        file_name, ip, port = sys.argv[1:]
        int(port)
    except ValueError:
        print("Not enough arguments")
        print("Usage: python3 send_file.py meme.png <some_ip> <port>")
        exit(1)
    initiate_file_transfer(ip, port, file_name)