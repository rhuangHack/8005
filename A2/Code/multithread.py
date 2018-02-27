import threading
import socketserver
import socket
from sys import argv
from sys import getsizeof

import logging
logging.basicConfig(filename='./mthread.log', filemode='w', level=logging.INFO, format='%(asctime)s %(relativeCreated)6d %(threadName)s %(message)s', datefmt='%m-%d %H:%M:%S')

SERVER_HOST = socket.gethostname()
SERVER_PORT = int(argv[1])
BUF_SIZE = 1024
peers={}

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = str(self.request.recv(BUF_SIZE), 'ascii')
            if data:
                th = threading.current_thread()
                peers[th]=getsizeof(data)
                
		#total_data.append(getsizeof(data))
                response = "%s: %s" %(th.name, data)
                print('echoing', 'to', self.client_address)    
                try:
                    self.request.sendall(response.encode())
                except:
                    logging.error("error happened")
                    pass
            
                
                self.finish()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.
TCPServer):
    pass

if __name__ == "__main__":
    server = ThreadedTCPServer((SERVER_HOST, SERVER_PORT), ThreadedTCPRequestHandler)
    print("Listening on", server.server_address)
    server.timeout = None
    try:
        server.serve_forever()
    except KeyboardInterrupt:       
        pass
    print("Accepted clients:", str(len(peers)),"clients")
    #print("Total data received:",str(sum(total_data)))
