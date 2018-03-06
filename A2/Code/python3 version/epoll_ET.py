# Selectors_echo server 

import selectors
import select
import socket
import sys
import logging
import os
import time

logging.basicConfig(filename='./epoll.log', filemode='w', level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S')


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


def read(connection, mask):
    "Callback for read event"
    global lost
    global keep_running
    global conn
    global start
    global n
    global avg

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
        logging.info("received data length is : %d" % len(data))
        
        try:
            connection.sendall(data)
        except BrokenPipeError:
            pass
        logging.info("sent data length is : %d" % len(data))
        current_milli_time = lambda: int(round(time.time() * 1000000))
        end = current_milli_time()
        gap = float((end - start)/1000)
        if n < 1000:
            n += 1
            avg += gap
            print("****** response time is %.3f ms" % gap)
            logging.info("****** response time is %.3f ms" % gap)
        if n == 1000:
            logging.info("------ the current connection is %d " % conn)
            avg = avg/n
            print("****** avg response time is %.3f ms" % avg)
            logging.info("------ avg response time is %.3f ms" % avg)
            avg = 0
            n = 0

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
    global conn
    conn += 1
    new_connection.setblocking(False)
    myselect.register(new_connection, selectors.EVENT_READ, read)


if len(sys.argv) != 2:
    print("please input <port number> ")
    sys.exit(0)

port = int(sys.argv[1])
server_address = (socket.gethostname(), port)
print('starting up on {} port {}'.format(*server_address))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
#server.settimeout(15)
server.bind(server_address)
server.listen(5)
conn = 0
n = 0
avg = 0.0

current_milli_time = lambda: int(round(time.time() * 1000000))
start = current_milli_time() 
# for selectors 
myselect.register(server, selectors.EVENT_READ, accept)

old = 0
while keep_running:
    print('waiting for I/O ..............heart beat')
    for key, mask in myselect.select(timeout=1):
        start = current_milli_time() 
        callback = key.data
        callback(key.fileobj, mask)

    if lost != old:
        old = lost
        print("lost %d connections from beginning" % lost)
        logging.warn("lost %d connections from beginning" % lost)

print('shutting down')
myselect.close()
