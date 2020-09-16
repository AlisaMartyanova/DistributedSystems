import socket               # Import socket module
import sys
from pathlib import Path

import tqdm as tqdm

s = socket.socket()         # Create a socket object

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<image> <host> <port>")
    sys.exit(1)

SEPARATOR = "<SEPARATOR>"
image, host, port = sys.argv[1:4]
filesize = Path(image).stat().st_size

s.connect((host, int(port)))
s.send(f"{image}{SEPARATOR}{filesize}".encode())

# progress bar
progress = tqdm.tqdm(range(filesize), f"Sending {image}",
                     unit="B", unit_scale=True,
                     unit_divisor=1024)
f = open(image,'rb')
# print('Sending...')
l = f.read(1024)
for _ in progress:
    # print('Sending...')
    s.send(l)
    l = f.read(1024)
    progress.update(len(l))

f.close()
print("Done Sending")
s.shutdown(socket.SHUT_WR)

s.close()

