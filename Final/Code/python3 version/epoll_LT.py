# Selectors_echo server 
import time
import selectors
import socket
import sys
import logging
import os

logging.basicConfig(filename='./select.log', filemode='w', level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S')

myselect = selectors.EpollSelector()
keep_running = True
lost = 0

def rSock(conn):
    local_port = conn.getsockname()[1]
    print(local_port)
    rserver_addr = "192.168.0.26"
    rserver_port = 22
    rserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rserver.connect((rserver_addr, rserver_port))
    return rserver



def datatrans(local, remote, myselect):
    
    l_addr = local.getsockname()[0]
    l_port = local.getsockname()[1]
    r_addr = remote.getsockname()[0]
    r_port = remote.getsockname()[1]
    
    print("[+] %s:%d --------- %s:%d" % (l_addr, l_port, r_addr, r_port))
    while keep_running:

        for key, mask in myselect.select(timeout=1):
            connection = key.fileobj
            
            try: 
                client_address = connection.getpeername()
            except:
                accept(connection, mask)
                return


            print('client({})'.format(client_address))
            
            data = connection.recv(1024)
            if len(data) == 0:
                print( "[-] No data received! Breaking...")
                myselect.unregister(connection)
                try:
                    myselect.unregister(local)
                    myselect.unregister(remote)
                    local.close()
                    remote.close()
                except:
                    pass

                connection.close() 
                #break
                return 

            if connection == local:
                print("[+] %s:%d >>>>>> %s:%d data length [%d]" % (l_addr, l_port, r_addr, r_port, len(data)))
                remote.sendall(data)


            if connection == remote:
                print("[+] %s:%d <<<<<< %s:%d data length [%d]" % (l_addr, l_port, r_addr, r_port, len(data)))
                local.sendall(data)
           



def accept(sock, mask):
    "Callback for new connections"
    local, addr = sock.accept()
    print('accept({})'.format(addr))
    global conn
    conn += 1
    remote = rSock(local)

    myselect.register(local, selectors.EVENT_READ,)
    myselect.register(remote, selectors.EVENT_READ,)
    datatrans(local, remote, myselect)

if len(sys.argv) != 2:
    print("please input <port number> ")
    sys.exit(0)

port = int(sys.argv[1])
server_address = (socket.gethostname(), port)
print('starting up on {} port {}'.format(*server_address))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.settimeout(15)
server.bind(server_address)
server.listen(5)
conn = 0
n = 0
avg = float(0)

server_address1 = (socket.gethostname(), 10000)
server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server1.setblocking(False)
server1.bind(server_address1)
server1.listen(5)

current_milli_time = lambda: int(round(time.time() * 1000000))
start = current_milli_time()
myselect.register(server, selectors.EVENT_READ, accept)

myselect.register(server1, selectors.EVENT_READ, accept)

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
