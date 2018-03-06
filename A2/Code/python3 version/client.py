# Select echo client

import selectors
import socket
import time
import sys

from threading import Thread
import multiprocessing
import os

import logging
logging.basicConfig(filename='./client.log', filemode='w', level=logging.INFO, format='%(asctime)s %(relativeCreated)6d %(threadName)s %(message)s', datefmt='%m-%d %H:%M:%S')


def conn(server):
    # connction is a blocking operation, so call setblocking()
    # after it returns
    
    #server_address = ('localhost', 10000)
    port = int(sys.argv[2])
    server_address = (server, port)
    print('connecting to {} port {}'.format(*server_address))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    sock.setblocking(False)
    return sock

def nio(sock):
    myselect = selectors.DefaultSelector()
    # Set up the selector to watch for when the socket is ready 
    # to send data as well as when there is data to read.
    myselect.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, )
    return myselect

def enlarge():
    outgoing = b'This s the message.hello,server!'
    for i in range(5):
        outgoing = outgoing + outgoing
    return outgoing

def datatrans(keep_running, sock, myselect, alive, times):
    if times == 0:
        return sock

    st = enlarge()
    outgoing = []
    outgoing.append(st)
    
    bytes_sent = 0
    bytes_received = 0
    first = True
    while keep_running:
        print('waiting for I/O...')

        for key, mask in myselect.select(timeout=1):
            if first:
                connection = key.fileobj
                client_address = connection.getpeername()
                first = False

            print('client({})'.format(client_address))

            if mask & selectors.EVENT_READ:
                print('%d ready to read' % os.getpid())
                try:
                    data = connection.recv(1024)
                except socket.error as e:
                    if e.errno != 104:
                        print("*************** NOT ERR 104 *************")
                        logging.error(e)
                    # reconnection for this thread
                    print("**************************** CONNECTION LOST *************************")
                    logging.error('******** connection lost *******')
#test
                    first = True
                    myselect.unregister(connection)
                    connection.close()
                    continue 
                    
                    #doSomething()
                    #return connection
                    
                    
                if data:
                    # A readable client socket has data
                    bytes_received += len(data)
                    print('received {!r}'.format(len(data)))
                    logging.info('received {!r}'.format(len(data)))

                # interpret empty result as closed connection,
                # and also close when we have received a copy
                # of all of the data sent.
                keep_running = not ( data or (bytes_received and (bytes_received == bytes_sent)))

                if keep_running == False and times > 1:
                    times -= 1
                    keep_running = True
                    time.sleep(alive)
                    myselect.modify(sock, selectors.EVENT_WRITE)
                    outgoing.append(data)


            if mask & selectors.EVENT_WRITE:
                if not outgoing:

                    # we are out messeges, so we are no longer need to write anythins
                    # change our registration to let us keep reading responses from the 
                    # server.
                    myselect.modify(sock, selectors.EVENT_READ)

                else:
                    #send the naxt message
                    next_msg = outgoing.pop()
                    print('sending {!r}'.format(len(next_msg)))
                    logging.info('sending {!r}'.format(len(next_msg)))
                    try:
                        sock.sendall(next_msg)
                    except BrokenPipeError:
                        pass
                    bytes_sent += len(next_msg)
           
    return connection

def generater():
    thpool = []
    tnum = int(sys.argv[5])
    for x in range(tnum):
        thread = Thread(target=doSomething)
        thpool.append(thread)
        thread.start()
        time.sleep(0.02)

    for th in thpool:
        th.join()

# do business logic
def doSomething():
    
    # get arguments from user input
    server = sys.argv[1]
    times = int(sys.argv[3])
    alive = int(sys.argv[4])

    time.sleep(1)
    keep_running = True
    pid = os.getpid()
    sock = conn(server)
    myselect = nio(sock)
    con = datatrans(keep_running, sock, myselect, alive, times)
    print("PID %d done ..." % pid)
    exit(myselect, con)

def exit(myselect, connection):
    print('shutting down')
    myselect.unregister(connection)
    connection.close()
    myselect.close()

if len(sys.argv) != 6:
    print("please input: <ip> <port> <packets> <sleep> <conn> ")
    sys.exit(0)

t = time.time()
print("start at %s" % t)
amount = multiprocessing.cpu_count()
proc = []

for x in range(amount):
    process = multiprocessing.Process(target=generater)
    proc.append(process)
    print("let's go...", process.name)
    process.start()


for pr in proc:
    pr.join()

end = time.time()
print("end at %s" % end)
print("using %s" % (end - t))
logging.info("using %s seconds to finish %s connections per core" % ((end-t),sys.argv[5]))
print("%d : The main process done ... " % os.getpid())
