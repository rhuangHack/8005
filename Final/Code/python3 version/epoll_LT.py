# Selectors_echo server
import signal
import selectors
import socket
import sys
import logging
import os

logging.basicConfig(filename='./proxy.log', filemode='w', level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S')

myselect = selectors.EpollSelector()
keep_running = True
lost = 0
conn = 0
total_conn = 0
sock_pairs = {}
ports_setting = {}


# read configure file to a dictionary for searching the route
def readPortsList():
    global ports_setting
    f = open('ports.conf', 'r')
    for line in f:
        link = line[:-1]
        lport, rhost = link.split(' ')
        lport = int(lport)
        ports_setting.update({lport:rhost})
    print("\n[+] finish reading ports setting from file...\n")


# according to the requesting port to check dictionary to find the destination address and connect it, return the socket
def rSock(conn):
    global myselect
    global ports_setting
    local_port = conn.getsockname()[1]
    print("[+] visitor request for port : %d" % local_port)
    rhost = ports_setting.get(local_port)
    rserver_addr, rserver_port = rhost.split(':')
    rserver_port = int(rserver_port)
    rserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        rserver.connect((rserver_addr, rserver_port))
    except OSError as e:
        return
    return rserver


# disconnect the link and delete all the socket related objects
def disconn(local, remote):
    global myselect
    global sock_pairs
    try:
        myselect.unregister(local)
        myselect.unregister(remote)
        del sock_pairs[local]
        del sock_pairs[remote]
        local.close()
        print("[-] close local socket ")
        remote.close()
        print("[-] close remote socket ")
    except:
        print("[*] ******************  there is some trouble *********************")
        pass


# main business logic: receving data from one socket and sending data from another socket
def datatrans(sock, mask):
    global sock_pairs
    global myselect

   # while keep_running:
        #print('[.] waiting for events ..............heart beat')

    for key, mask in myselect.select(timeout=1):
        connection = key.fileobj

        try:
            client_address = connection.getpeername()
        except:
            accept(connection, mask)
            return
        remote = sock_pairs.get(connection)

        l_addr = connection.getsockname()[0]
        l_port = connection.getsockname()[1]
        r_addr = remote.getsockname()[0]
        r_port = remote.getsockname()[1]

        data = connection.recv(1024)
        if len(data) == 0:
            print( "[-] No data received! Breaking...")
            disconn(connection, remote)
            continue

        print("[+] %s ---------> %s:%d >>>>>> %s:%d data length [%d]" % (client_address, l_addr, l_port, r_addr, r_port, len(data)))
        remote.sendall(data)


# accept the new connection, and register these new socket to selector
def accept(sock, mask):
    "Callback for new connections"
    global sock_pairs
    local, addr = sock.accept()
    print('[+] accept({})'.format(addr))
    global total_conn
    total_conn += 1
    remote = rSock(local)
    if remote is None:
        print('\n[-] OSError: [Errno 113] No route to host ...')
        local.close()
    else:
        sock_pairs.update({local:remote, remote:local})
        print("[+] updated socket pairs to %d : %s" % (len(sock_pairs), sock_pairs))
        myselect.register(local, selectors.EVENT_READ, datatrans)
        myselect.register(remote, selectors.EVENT_READ, datatrans)


# listening for the Ctrl + C interrupt and stop the server
def signal_handler(signal, frame):
    global total_conn
    global myselect
    myselect.close()
    print("\n[-] Proxy Server stoped ... after serving %d connections " % total_conn)
    sys.exit(0)


# initiate all the ports the server will listen and forwarding data
def initServer():
    global ports_setting
    readPortsList()
    keys = ports_setting.keys()
    sockets = []

    index = 0
    for port in keys:
        server_address = (socket.gethostname(), port)
        sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        sockets[index].setblocking(False)
        sockets[index].bind(server_address)
        sockets[index].listen(5)
        myselect.register(sockets[index], selectors.EVENT_READ, accept)
        index += 1
        print('[+] Starting up on {} port {}'.format(*server_address))
        print("[+] port %d will forward to %s ...\n" % (port, ports_setting.get(port)))


# register the signal to a function...
signal.signal(signal.SIGINT, signal_handler)

initServer()

old = 0
while keep_running:
    print('[*] waiting for I/O ..............heart beat')
    for key, mask in myselect.select(timeout=1):
        callback = key.data
        callback(key.fileobj, mask)

    if lost != old:
        old = lost
        print("[-] lost %d connections from beginning" % lost)
        logging.warn("lost %d connections from beginning" % lost)

