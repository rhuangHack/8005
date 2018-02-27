# Selectors_echo server 

import selectors
import select
import socket
import sys
import logging
import os

logging.basicConfig(filename='./error.log', filemode='w', level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S')


class ETepoll(selectors.EpollSelector):
    def register(self, fileobj, events, data=None):
        key = selectors._BaseSelectorImpl.register(self, fileobj, events, data)
        epoll_events = 0
        if events & selectors.EVENT_READ:
            epoll_events |= select.EPOLLIN
        if events & selectors.EVENT_WRITE:
            epoll_events |= select.EPOLLOUT
        try:
            self._epoll.register(key.fd, epoll_events|select.EPOLLET)
        except BaseException:
            super().unregister(fileobj)
            raise
        return key

# comment the selectors version
#myselect = selectors.EpollSelector()


# override selectors.EpollSelector
myselect = ETepoll()
keep_running = True
lost = 0

# for cpu proformance task
def count(num):
    print("start cpu task...")
    x = 1
    y = 1
    c = 0
    while c < num:
        c += 1
        x += x
        y += y

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

    print('read({})'.format(client_address))
    data = connection.recv(1024)
    if data:
        # A readable client has data
        s = data.decode()
        print("the string len of received is : %d" % len(s))
        logging.info("received string length is : %d" % len(s))
        
        if len(data) < 1024:
            print(' received {!r}'.format(data))
        print(' received {!r}i bytes'.format(len(data)))
        logging.info("received data length is : %d" % len(data))
        logging.info("received data from %s is : %s" % (client_address, data))

        
        count(port)

        try:
            connection.sendall(data)
        except BrokenPipeError:
            pass
        #connection.send(data)
        logging.info("sent data length is : %d" % len(data))
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


port = int(sys.argv[1])
server_address = (socket.gethostname(), port)
print('starting up on {} port {}'.format(*server_address))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
#server.settimeout(15)
server.bind(server_address)
server.listen(5)

# for selectors 
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
