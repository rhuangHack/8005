# Selectors_echo server 

import selectors
import socket

import logging
import os

logging.basicConfig(filename='./error.log', filemode='w', level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S')

myselect = selectors.EpollSelector()
keep_running = True
lost = 0

def read(connection, mask):
    global lost
    "Callback for read event"
    global keep_running

    try:
        client_address = connection.getpeername()
    except OSError as e:
        #if e.errno != errno.ENOTCONN:
        logging.error("connection lost error number : %s" % e.errno)
        if e.errno == 107:
            lost += 1
        print("***************** CONN LOST ****************")
        myselect.unregister(connection)
        connection.close()
        return
    except ConnectionResetError as ex:
        logging.error("Errno 104 Connection reset by peer...")
        if ex.errno == 104:
            lost += 1
        print("***************** CONN LOST ****************")
        myselect.unregister(connection)
        connection.close()
        return

    print('read({})'.format(client_address))
    data = connection.recv(1024)
    if data:
        # A readable client has data
        print(' received {!r}'.format(data))
        connection.sendall(data)
    else:
        # interpret empty result as closed connection
        print(' closing')
        myselect.unregister(connection)
        connection.close()
        # Tell the main loop to stop
        ##keep_running = False

def accept(sock, mask):
    "Callback for new connections"
    new_connection, addr = sock.accept()
    print('accept({})'.format(addr))
    new_connection.setblocking(False)
    myselect.register(new_connection, selectors.EVENT_READ, read)


server_address = (socket.gethostname(), 10000)
print('starting up on {} port {}'.format(*server_address))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.settimeout(15)
server.bind(server_address)
server.listen(5)

myselect.register(server, selectors.EVENT_READ, accept)

old = 0
while keep_running:
    print('waiting for I/O ..............heart beat')
    for key, mask in myselect.select(timeout=1):
        callback = key.data
        callback(key.fileobj, mask)

    if lost != old:
        old = lost
        print("lost %d connections from beginning" % lost)
        logging.warn("lost %d connections from beginning" % lost)

print('shutting down')
myselect.close()
