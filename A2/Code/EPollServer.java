
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;

import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;



/**
 * Java NIO uses multiplexing to server multiple clients from the same thread.
 * Before NIO, a server had to open a thread for each client.
 * 
 * @author john @2018-01-31
 * 
 * @@todo: 1) hashmap could be bottleneck, is it thread-safe?  Not Need as only one thread to read/write
 * 		   2) JVM tunning 
 * 		   3) ip stack tuning for linux kernel
 * 
 *
 *Howto:
 *1) Epoll 
  	java -Djava.nio.channels.spi.SelectorProvider=sun.nio.ch.EPollSelectorProvider 
 *2) Poll
	java -Djava.nio.channels.spi.SelectorProvider=sun.nio.ch.PollSelectorProvider 

 */
public class EPollServer implements Runnable {

	 static String ADDRESS = "localhost";
	 static int PORT = 8511;
	public final static long SELECT_TIMEOUT = 10000;

	static int BUFFER_SIZE=1024*51;
	static int THREADNUM=1;

static int counter;

	private ServerSocketChannel serverChannel;
	private Selector selector;

	private Map<SocketChannel, byte[]> mesgCache = new HashMap<SocketChannel, byte[]>();
	
	public EPollServer() {
		
	}

	public static void main(String[] args) {
		
		execute(ADDRESS, PORT,BUFFER_SIZE,THREADNUM);
	}
	
	public static void execute(String ip, int port, int buffer,int threadNum) {
    	
    	EPollServer ss = new EPollServer(); 
    	ss.init(ip, port);
    	BUFFER_SIZE=buffer;
    	
    	Util.loger("The select server is starting on port:"+port);
    	Util.loger("The provier is \t"+getProvider());
    
    	
    	for ( int i=1; i<=threadNum; i++) {
			Thread sstt = new Thread (ss,"SelectServerThread-"+i);
	    	sstt.start();
		} 
    	
    
    		Util.loger("threadNum is "+threadNum);
    		
    		
    	   	
	}

	private void init(String ip, int port) {
		Util.loger("initializing server");

		if (selector != null)
			return;
		if (serverChannel != null)
			return;

		try {

			selector = Selector.open();

			serverChannel = ServerSocketChannel.open();

			serverChannel.configureBlocking(false);

			serverChannel.register(selector, SelectionKey.OP_ACCEPT);
			// bind to the address
			serverChannel.socket().bind(new InetSocketAddress(ADDRESS, PORT));

		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void run() {
		Util.loger("Now accepting connections by..."+ Thread.currentThread().getName() );

counter++;
Util.loger("Connection Counter is::"+ counter);
		try {

			while (!Thread.currentThread().isInterrupted()) {
				long startPoint = System.currentTimeMillis();
				selector.select(SELECT_TIMEOUT); // block
				Util.loger(startPoint, "seletor.select");

				Iterator<SelectionKey> keys = selector.selectedKeys().iterator();

				while (keys.hasNext()) {
					SelectionKey key = keys.next();
					// remove the key so that we don't process this OPERATION again.
					keys.remove();

					// key could be invalid if for example, the client closed the connection.
					if (!key.isValid()) {
						continue;
					}

					if (key.isAcceptable()) {
						Util.loger("Accepting connection");
						accept(key);

					}

					if (key.isWritable()) {
						Util.loger("Writing...");
						write(key);
					}

					if (key.isReadable()) {
						Util.loger("Reading connection");
						read(key);
					}
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			closeConnection();
		}

	}
	
	
	private void accept(SelectionKey key) throws IOException {
		ServerSocketChannel serverSocketChannel = (ServerSocketChannel) key.channel();
		SocketChannel socketChannel = serverSocketChannel.accept();
		socketChannel.configureBlocking(false);

		socketChannel.register(selector, SelectionKey.OP_WRITE);
		byte[] hello = new String("Hello from server").getBytes();
		mesgCache.put(socketChannel, hello);
	}

	/**
	 * SocketChannel receiving back from the key.channel() is the same channel that was
	 * used to register the selector in the accept() method.
	 *  later, we might register to write from the read() method (for  example).
	 */
	private void write(SelectionKey key) throws IOException {
		SocketChannel channel = (SocketChannel) key.channel();
		
		byte[] data = mesgCache.get(channel);
		mesgCache.remove(channel);

		
		channel.write(ByteBuffer.wrap(data));
 Util.loger("Data write out is:"+new String(data));
		
		key.interestOps(SelectionKey.OP_READ);

	}

	private void closeConnection() {
		Util.loger("Closing server down");
		if (selector != null) {
			try {
				selector.close();
				serverChannel.socket().close();
				serverChannel.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}


	private void read(SelectionKey key) throws IOException {
		SocketChannel channel = (SocketChannel) key.channel();
		ByteBuffer readBuffer = ByteBuffer.allocate(BUFFER_SIZE);
		readBuffer.clear();
		int read;
		try {
			read = channel.read(readBuffer);
		} catch (IOException e) {
			Util.loger("Reading problem, closing connection");
			key.cancel();
			channel.close();
			return;
		}
		if (read == -1) {
			Util.loger("Nothing was there to be read, closing connection");
			channel.close();
			key.cancel();
			return;
		}
	
		readBuffer.flip();

		byte[] data = new byte[BUFFER_SIZE];
		// read only length can accept, otherwise, out-of-bound exception for data..
		read = read < BUFFER_SIZE ? read : (BUFFER_SIZE - 1);

		readBuffer.get(data, 0, read);

//		Util.loger("Received: " + new String(data));

		echo(key, data);
	}

	/**
	 * Channel is a two way communication linked with Buffer .

	 */

	private void echo(SelectionKey key, byte[] data) {
		SocketChannel socketChannel = (SocketChannel) key.channel();
		mesgCache.put(socketChannel, data);
		key.interestOps(SelectionKey.OP_WRITE);
	}

	static String getProvider() {

		String rst;
		rst = java.nio.channels.spi.SelectorProvider.provider().getClass().getName();
		return rst;


	}

}
