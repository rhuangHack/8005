import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;

import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 2018-03-03: adding AvgTime( print avg every 1000 in Nanos), supress other
 * output. 2018-02-24:@0224 calling tasks ( CPUTask and IOTask) 2018-01-12
 * PollServer should be branched from EPoll every time EPoll update Provide the
 * PollServer, which is pretty much same as EPollServer. But due to
 * unfortunately the lower layer issue at PollSelectProvider, which caused for
 * java.util.ConcurrentModificationException by Poll SelectProvider
 * 
 * 
 * ******** Java NIO uses multiplexing to server multiple clients from the same
 * thread. Before NIO, a server had to open a thread for each client.
 * 
 * @author john @2018-01-31
 * 
 * @@todo: 1) hashmap could be bottleneck, is it thread-safe? Not Need as only
 *         one thread to read/write 2) JVM tunning 3) ip stack tuning for linux
 *         kernel
 * 
 *
 *         Howto: 1) Epoll java
 *         -Djava.nio.channels.spi.SelectorProvider=sun.nio.ch.EPollSelectorProvider
 *         2) Poll java
 *         -Djava.nio.channels.spi.SelectorProvider=sun.nio.ch.PollSelectorProvider
 * 
 */
public class PollServer implements Runnable {

	static String ADDRESS = "192.168.0.15";// should be useless
	static int PORT = 8511;
	public final static long SELECT_TIMEOUT = 10000;

	static int BUFFER_SIZE = 1024;
	static int THREADNUM = 1;

	static int CPUTASK_TRUE = 0; // ignore CPU task
	static int IOTASK_TRUE = 0; // ignore IO task

	static int counter;
	static int conCounter; // counter of connection

	private ServerSocketChannel serverChannel;
	private Selector selector;

	private ConcurrentHashMap<SocketChannel, byte[]> mesgCache = new ConcurrentHashMap<SocketChannel, byte[]>();

	PrintWriter pwr;

	public PollServer() {

	}

	public static void main(String[] args) {

		if (args.length == 4) {

			PORT = new Integer(args[0]);
			BUFFER_SIZE = Integer.parseInt(args[1]);
			CPUTASK_TRUE = Integer.parseInt(args[2]);
			IOTASK_TRUE = Integer.parseInt(args[3]);

		} else {
			Util.loger(" Usage: {PORT} {BUFFER_SIZE(B)} {CPU (0|1)} {IO(0|1)}");
			Util.loger("Current port :" + " " + PORT);

			return;
		}

		execute(ADDRESS, PORT, BUFFER_SIZE, THREADNUM);

	}

	public static void execute(String ip, int port, int buffer, int threadNum) {

		PollServer ss = new PollServer();
		ss.init(ip, port);
		BUFFER_SIZE = buffer;

		Util.loger("The EPoll server is starting on port:" + port);
		Util.loger("The provier is \t" + getProvider());

		for (int i = 1; i <= threadNum; i++) {
			Thread sstt = new Thread(ss, "SelectServerThread-" + i);
			sstt.start();
		}

		Util.loger("threadNum is " + threadNum);

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
			serverChannel.socket().bind(new InetSocketAddress(PORT));

		} catch (IOException e) {
			Util.loger(e.getMessage());
		}
	}

	@Override
	/**
	 * ServerSocketChannel is selectable and good for a stream-oriented listening
	 * socket.
	 * 
	 */
	public void run() {
		Util.loger("Now accepting connections by..." + Thread.currentThread().getName());

		long singleTime, subSumTime = 0;
		try {

			while (!Thread.currentThread().isInterrupted()) {
				long startPoint = System.nanoTime();
				selector.select(SELECT_TIMEOUT); // block here in the system to retrieve the events interested
				// Util.loger(startPoint, "seletor.select");

				// response time ... output every 1000 packets.

				singleTime = System.nanoTime() - startPoint;
				singleTime = counter == 0 ? 0 : singleTime;
				subSumTime += singleTime;
				// resTimeArray[i]=singleTime;

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
						conCounter++;

					}

					if (key.isWritable()) {
						Util.loger("Writing...");
						// startPoint = System.currentTimeMillis();
						write(key);
						counter++;
						Util.loger("Connection Counter is::" + counter);

						if ((counter % 1000) == 0) {
							double d2l = subSumTime / 1000 / 1000;
							d2l = d2l / 1000;
							System.out.println(
									"\n\n\nConnection " + conCounter + " ---- Average Respone Time---" + d2l + " (ms)");
							// IOTasks( new byte[subSumTime/1000));
							// saveFile(subSumTime/1000);
							subSumTime = 0;
						}

					}

					if (key.isReadable()) {
						Util.loger("Reading connection");

						read(key);

					}
				}
			}
		} catch (IOException e) {
			Util.loger(e.getMessage());
		} finally {
			closeConnection();
			Util.loger("Server-End in finally");
		}

	}

	private void accept(SelectionKey key) throws IOException {
		ServerSocketChannel serverSocketChannel = (ServerSocketChannel) key.channel();
		SocketChannel socketChannel = serverSocketChannel.accept();
		socketChannel.configureBlocking(false);

		socketChannel.register(selector, SelectionKey.OP_READ);
		// byte[] hello = new String("Hello from server").getBytes();
		// mesgCache.put(socketChannel, hello);

	}

	/**
	 * SocketChannel receiving back from the key.channel() is the same channel that
	 * was used to register the selector in the accept() method. later, we might
	 * register to write from the read() method (for example).
	 */
	private void write(SelectionKey key) throws IOException {
		SocketChannel channel = (SocketChannel) key.channel();

		byte[] data = mesgCache.get(channel);
		mesgCache.remove(channel);

		channel.write(ByteBuffer.wrap(data));
		Util.logd("Data write out length is:" + data.length);

		key.interestOps(SelectionKey.OP_READ);

	}

	private void closeConnection() {
		Util.loger("Closing server down");

		pwr.close();
		if (selector != null) {
			try {
				selector.close();
				serverChannel.socket().close();
				serverChannel.close();

			} catch (IOException e) {
				Util.loger(e.getMessage());
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

		// Util.loger("Received: " + new String(data));

		echo(key, data);
	}

	/**
	 * Channel is a two way communication linked with Buffer .
	 * 
	 */

	private void echo(SelectionKey key, byte[] data) {
		SocketChannel socketChannel = (SocketChannel) key.channel();
		mesgCache.put(socketChannel, data);
		key.interestOps(SelectionKey.OP_WRITE);

		if (CPUTASK_TRUE == 1)
			cpuTasks();
		if (IOTASK_TRUE == 1)
			IOTasks(data);

	}

	static private void cpuTasks() {

		String key = "aiyan&albert@bcit4comp8505&8506";
		// String key = "aiyanma123456";
		String clean = "fengqingyundan, shan'gaoshuichang";

		byte[] encrypted;
		try {
			encrypted = Util_Task.encrypt(clean, key);

			Util.loger("The encrypted data is:" + new String(encrypted));
			String decrypted = Util_Task.decrypt(encrypted, key);
			Util.loger("The decrypted data is:" + decrypted);

		} catch (Exception e) {
			// TODO Auto-generated catch block
			Util.loger(e.getMessage());
		}
	}

	static private void IOTasks(byte[] data) {

		File f = new File("./EPOLL-IO");
		try {
			if (!f.exists())
				f.createNewFile();

			Files.write(Paths.get("./EPOLL-IO"), data);

		} catch (IOException e) {
			// TODO Auto-generated catch block
			Util.loger(e.getMessage());
		}
	}

	static private void saveFile(long ll) {

		try {

			String fileName = "./time-log";

			FileWriter fileWriter = new FileWriter(fileName);

			PrintWriter pwr = new PrintWriter(fileWriter);
			pwr.print("AvgTime");
			pwr.print(ll);

			pwr.close();

		} catch (IOException e) {
			// TODO Auto-generated catch block
			Util.loger(e.getMessage());
		}
	}

	static String getProvider() {

		String rst;
		rst = java.nio.channels.spi.SelectorProvider.provider().getClass().getName();
		return rst;

	}

}