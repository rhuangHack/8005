# Selectors_echo server 

import selectors
import socket
import sys
import logging

logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S')

myselect = selectors.EpollSelector()
keep_running = True
lost = 0


def create():
    port = int(sys.argv[1])
    server_address = (socket.gethostname(), port)
    print('starting up on {} port {}'.format(*server_address))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.settimeout(15)
    server.bind(server_address)
    server.listen(5)
    return server

def accept(sock):

    #"Callback for new connections"
    f = Future()
    new_connection, addr = sock.accept()
    print('accept({})'.format(addr))
    new_connection.setblocking(False)
    
    def on_accept():
        f.set_result(None)
   
    myselect.register(sock.fileno(), selectors.EVENT_READ, on_accept)
    yield from f
    myselect.unregister(sock.fileno())
    return new_connection

def read(connection):
    f = Future()

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
    #data = connection.recv(1024)
    
    def on_readable():
        f.set_result(connection.recv(1024))
    
    myselect.register(connection.fileno(), selectors.EVENT_READ, on_readable)
    data = yield from f
    myselect.unregister(connection.fileno())
    
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


class Future:
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)

    def __iter__(self):
        yield self
        return self.result


class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:

            next_future = self.coro.send(future.result)
        except StopIteration:
            return
        next_future.add_done_callback(self.step)


class TestServer:
    def __init__(self):
        self.sock = create()
        #self.connection 

    def service(self):
        connection = yield from accept(self.sock)
        yield from read(connection)



def loop():
    global old
    while keep_running:
        print('waiting for I/O ..............heart beat')
        for key, mask in myselect.select(timeout=1):
            callback = key.data
            callback()

        if lost != old:
            old = lost
            print("lost %d connections from beginning" % lost)
            logging.warn("lost %d connections from beginning" % lost)


old = 0
ser = TestServer()
Task(ser.service())
loop()
print('shutting down')
myselect.close()
