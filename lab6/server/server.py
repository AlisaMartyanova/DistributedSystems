import os
import socket
from threading import Thread
from os import walk

clients = []
host = '127.0.0.1' #ec2-18-218-249-95.us-east-2.compute.amazonaws.com 
port = 8800
SEPARATOR = "<SEPARATOR>"
copy = 1

# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        try:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            data = self.sock.recv(1024).decode()
            filename, filesize = data.split(SEPARATOR)
            filename = os.path.basename(filename)

            # check if there exists file with the same name
            filename = check_name(filename)

            with open(filename, "wb") as f:
                bytes_read = True
                while(bytes_read):
                    bytes_read = self.sock.recv(1024)
                    if not bytes_read:
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)

            f.close()
            print("Done Receiving")
        except ValueError:
            print()

        finally:
            self._close()


def check_name(filename):
    global copy
    files = []
    for (dirpath, dirnames, filenames) in walk('./'):
        files.extend(filenames)
        break

    if files.__contains__(filename):
        name, extension = os.path.splitext(filename)
        new_filename = name + '_copy' + str(copy) + extension

        copy += 1

        return new_filename
    else:
        return filename


def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
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
