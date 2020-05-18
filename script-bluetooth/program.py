# file: rfcomm-server.py

# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

from bluetooth import *

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1] 

print ("Waiting for connection on RFCOMM channel " + str(port))

client_sock, client_info = server_sock.accept()
print ("Accepted connection from ", client_info)

try:
    while True:
        data = client_sock.recv(1024)
        if len(data) == 0: break
        print ("received " + data)
except IOError:
    pass

print ("disconnected")

client_sock.close()
server_sock.close()
print ("all done")