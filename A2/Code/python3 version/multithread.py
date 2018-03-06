import threading
import socketserver
import socket
from sys import argv
from sys import getsizeof
from sys import exit
import time
import logging

logging.basicConfig(filename='./mthread.log', filemode='w', level=logging.INFO, format='%(asctime)s %(relativeCreated)6d %(threadName)s %(message)s', datefmt='%m-%d %H:%M:%S')

if len(argv) != 2:
    print("please input <port number> ")
    exit(0)

SERVER_HOST = socket.gethostname()
SERVER_PORT = int(argv[1])
BUF_SIZE = 1024
peers={}

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("new client connected")
        while True:
            try:
                data = str(self.request.recv(BUF_SIZE), 'ascii')
            except:
                logging.error("connection reset by peer")
                self.finish()

            if data:
                current_milli_time = lambda: int(round(time.time() * 1000000))
                start = current_milli_time()
                th = threading.current_thread()
                peers[th]=getsizeof(data)
                
		#total_data.append(getsizeof(data))
                response = "%s: %s" %(th.name, data)
                print('echoing', 'to', self.client_address)    
                try:
                    self.request.sendall(response.encode())
                    end = current_milli_time()
                    print("***** response time is %.3f ms" % float((end - start)/1000))
                    logging.info("***** response time is %.3f ms" % float((end - start)/1000))
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
