# multi-thread echo server 

import socket
import time
import sys

from threading import Thread
import multiprocessing
import os

import logging
logging.basicConfig(filename='./mthread.log', filemode='w', level=logging.INFO, format='%(asctime)s %(relativeCreated)6d %(threadName)s %(message)s', datefmt='%m-%d %H:%M:%S')


def generater(sock):
    
    sock.settimeout(30)
    thread = Thread(target=read, args=(sock,))
    thread.start()
    time.sleep(0.02)

# do business logic
def read(connection):
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
        logging.info("received data is : %s" % data)
        connection.sendall(data)
        #connection.send(data)
        logging.info("sent data length is : %d" % len(data))
    else:
        # interpret empty result as closed connection
        print(' closing')
        myselect.unregister(connection)
        connection.close()
        # Tell the main loop to stop
        ##keep_running = False



def exit(connection):
    print('shutting down')
    connection.close()

t = time.time()
print("Multi-thread server start at %s" % t)
amount = multiprocessing.cpu_count()
proc = []

port = int(sys.argv[1])
server_address = (socket.gethostname(), port)
print('starting up on {} port {}'.format(*server_address))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#server.settimeout(15)
server.bind(server_address)
server.listen(5)

#use pool to deal with it
pool = multiprocessing.Pool(processes = amount)

while True:
    print ('Waiting for connection ......')
    sock, addr = server.accept()
    print ('Connected by ', addr)
    pool.apply_async(generater, args=(sock,))
