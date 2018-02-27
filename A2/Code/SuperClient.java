
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;

import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Scanner;
import java.util.regex.Pattern;

/**
 *
 * 2018-02-25 
 * a)Optimize the exception to overwrite the broken pipe: 
 * b)Split the
 * loopSend with SuperClientls 
 * 2018-02-24; 
 * a) adding loopsending inside thread;
 * b) add args support in cli c) add finite loop for create threads to workaround
 * client socket (ip_v4_port_range) MAX_CONN
 *
 * @author john
 *
 */
public class SuperClient implements Runnable {

	private static String IP = "localhost";
	private static int PORT = 8511;

	static int BUFFER_SIZE = 1024;
	static int INTERVAL = 100; // in the span of the connection creation, control the speed (Milli-Sec)
	static int TTL = 1000 * 30; // The duration of one connection (Milli-Sec)

	// For each thread
	static int MESGLOOP = 1;
	static int FakeNaos = 1000 * 1; // in Ms actually
	static int MAX_CONN = 65000; // due to the port(binding) limitation ( can not assign port...)

	SocketChannel socketChannel;

	private static int tid = 0; // thread_id

	private static final String IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
			+ "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."
			+ "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$";

	SuperClient(int threadId) {

		tid = threadId;

	}

	public static void main(String[] args) {

		if (args.length == 6) {
			IP = args[0];

			// on purpose to demo different ways to transfer Str to Int
			PORT = new Integer(args[1]);
			INTERVAL = Integer.parseInt(args[2]);
			// TTL=Integer.parseInt(args[3]);
			MESGLOOP = Integer.parseInt(args[3]);
			FakeNaos = Integer.parseInt(args[4]);
			BUFFER_SIZE = Integer.parseInt(args[5]);

		} else {
			Util.loger(" Usage: {IP} {PORT} {INTERVAL} {MESGLOOP} {FakeNaos} (Buffer Size(byte))");
			Util.loger("Current ip and port :" + IP + " " + PORT);

			return;
		}

		Pattern pattern = Pattern.compile(IPADDRESS_PATTERN); // seems complex pattern should compile first;
		boolean validatedIP = pattern.matcher(IP).matches();
		// or another way
		validatedIP = Pattern.matches(IPADDRESS_PATTERN, IP);

		if (!validatedIP && !IP.equals("localhost")) {
			Util.loger("Invalidate IP format...");
			System.exit(-1);
		}

		for (int i = 0; i < MAX_CONN; i++) {
			SuperClient tc = new SuperClient(i);
			Thread t = new Thread(tc);
			t.setName("SuperClient-" + i);
			t.start();

			// Give interval for next threads in milli-seconds
			Util.setTimer(INTERVAL);
			Util.logd("Interval is:" + INTERVAL);
		}

	}

	void connect() throws UnknownHostException, IOException {

		if (null == IP || 0 == PORT) {
			Util.loger(" Need ip and/or port to connect");
			System.exit(-1);
			;
		}

		socketChannel = SocketChannel.open();
		socketChannel.connect(new InetSocketAddress(IP, PORT));

		Util.loger("Connected to: \t" + IP);

	}

	@Override
	public void run() {

		String tName = Thread.currentThread().getName();
		Util.loger(tName + " started...");
		try {
			this.connect();

			String mesgToSend = " Send from " + tName + Util.bigMsg(BUFFER_SIZE - 32);

			// add here for loop sending
//			for (int j = 0; j < MESGLOOP; j++) 
			{
				this.send("Length:" + mesgToSend.length() + mesgToSend);
//				Util.setTimer(FakeNaos);

			}

			Util.setTimer(TTL); // keep it here , not such important if loop Sending

		} catch (IOException e) {
			// TODO Auto-generated catch block
			Util.loger(e.getMessage());
		}

	}

	void send(String msg) {

		try {
			// BUFFER_SIZE = msg.length();
			Util.loger("The packet length to be sent is:" + msg.length());
			ByteBuffer writeBuffer = ByteBuffer.allocate(BUFFER_SIZE);
			ByteBuffer readBuffer = ByteBuffer.allocate(BUFFER_SIZE);

			writeBuffer.put(msg.getBytes(), 0, BUFFER_SIZE);
			writeBuffer.flip();

			// while (true)
			{
				long startPoint = System.currentTimeMillis();
				writeBuffer.rewind();
				socketChannel.write(writeBuffer);

				// check return
				readBuffer.clear();
				socketChannel.read(readBuffer);
				Util.loger(startPoint, "Intervial_of_echo time");
				Util.logd(" I got reply:" + Util.byteBuffer2String(readBuffer));

			}
		} catch (IOException e) {
			Util.loger(e.getMessage());
		}
	}

}
