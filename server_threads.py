import socket
import os
from threading import Thread


clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    def _accept_filename(self):
        data = self.sock.recv(1024)
        if data:
            data = data.decode("utf-8")
            print("filename accepted - {}".format(data))
            f = open(data)
            f.close()
            self.sock.send(b"filename accepted")

            return data

    def _accept_file(self, filename):
        file_data = ""
        while True:
            print("accepting file")
            data = self.sock.recv(1024)
            if data:
                data = data.decode("utf-8")
                if data == "EOF":
                    break
                file_data += data
        if not os.path.exists("./accepted"):
            os.makedirs("./accepted")

        copy_count = -1
        # print(filename)
        for f in os.listdir("./accepted"):
            if f.find(filename.split('.')[0]) != -1:
                copy_count = max(copy_count, 0)
                if f.find("copy") != -1:
                    print(f)
                    copy_count = max(copy_count, int(f.split("copy")[1].split(".")[0]))
        if copy_count != -1:
            print(copy_count)
            parts = filename.split(".")
            filename = f"{parts[0]}_copy{copy_count+1}.{parts[1]}"

        with open(f"accepted/{filename}", "w") as f:
            print("file saved")
            f.write(file_data)

    def _echo_start_transfer(self):
        self.sock.send(b"start")

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            data = self.sock.recv(1024)
            if data:
                data_str = data.decode("utf-8")
                if data_str == "file_transfer":
                    self._echo_start_transfer()
                    filename = self._accept_filename()
                    self._accept_file(filename)
            else:
                # if we got no data – client has disconnected
                self._close()
                # finish the thread
                return


def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()