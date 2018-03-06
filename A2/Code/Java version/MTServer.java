
import java.io.BufferedReader;


import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.Executor;

/**2018-0303- add port as args 
 *  2018-02-24
 * to run it, simply run
 * #java MTServer 
 * Details see end of the file.
 * 
 *
 */
public class MTServer implements Runnable {

	private static int SERVER_PORT = 8899;

	Socket csocket;
	int tid;

	static boolean poolMode = false;
	 static final int      MIN_THREAD_POOL_SIZE=2;
	 static final int      MAX_THREAD_POOL_SIZE=1024; // for processing requests
	
	MTServer(Socket csocket, int threadId) {
		this.csocket = csocket;
		tid = threadId;
	}

	public static void main(String args[]) {
		SERVER_PORT = Integer.parseInt(args[0]);
		if(args.length ==2 && (args[1].indexOf("pool")!=-1))
			poolMode = true;
		
		execute(SERVER_PORT);
	}

	
	
	 static void execute (int port) {
		 
		ServerSocket ssock;
		
	    // Create a thread pool (Executor)
		// 3000: KeepAlive Time
	  Executor  executor=new ThreadPoolExecutor(MIN_THREAD_POOL_SIZE, MAX_THREAD_POOL_SIZE, 30000, TimeUnit.MILLISECONDS,
	                                    new LinkedBlockingQueue(1000));
		
	  int counter =0;
	  long startPoint =0;
		try {
			ssock = new ServerSocket(port);
		
			Util.loger("Listening on port:" + port);

			for (int i = 1;; i++) {
				Socket sock = ssock.accept();

				startPoint = System.currentTimeMillis();
				Util.loger("Connected");

				Thread mts = new Thread(new MTServer(sock, i));
				mts.setName("MTServer-" + i);
				
							
				
				if (!poolMode)
					mts.start();
				else
					executor.execute(mts);

				counter++;
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			Util.loger(e.getMessage());
			
		} finally	{
			
			showStats(startPoint,counter);
		
		}
		
	 }
	private static void showStats(long startPoint,int counter) {
		// TODO Auto-generated method stub
		Util.loger(startPoint, "Here is the connections handled:\t"+ counter);
		
	}

	public void run() {
		Util.loger(Thread.currentThread().getName()+" running...");
		long startPoint = System.nanoTime();
		try {
			PrintStream pstream = new PrintStream(csocket.getOutputStream());

			Util.logd("I got the data:" );
			for (int i = 10; i >= 0; i--) {
				pstream.println(i + " piles of GOLD  in the CAVE");				
			}
			Util.logd(" I've sent back GOLD to you  PLUS those you sent me");
			
			BufferedReader in = new BufferedReader(new InputStreamReader(csocket.getInputStream()));
			String inputLine;
			while ((inputLine = in.readLine()) != null) {
				pstream.println(inputLine);				
				Util.logd(inputLine);
			}
			
		long responseTime = System.nanoTime()-startPoint;
		double d2l = responseTime/1000/1000;
		System.out.println("\n\n\n----The responseTime is:"+d2l/1000+"(ms)");
			pstream.close();
			csocket.close();
			
			
			
		} catch (IOException e) {
			Util.loger(e.getMessage());
		}
	}
}



/**
 * @@@ Test capture....
C:\Users\john\eclipse-workspace\COMP8005\bin>java SuperClient localhost 8899 100  1000 1000000 1024
Timer set for 100 milsecs, starting ....
SuperClient-0 started...
Connected to:   localhost
The packet length to be sent is:1043
Intervial_of_echo time time used:0
 I got reply:10 piles of GOLD  in the CAVE
 .......
 * 
 * @@@@Test at Server
C:\Users\john\eclipse-workspace\COMP8005\bin>java MTServer
Listening on port:8899
Connected
MTServer-1 running...
I got the data:java.io.PrintStream@1a31a8d0
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-2 running...
I got the data:java.io.PrintStream@69656e74
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-3 running...
I got the data:java.io.PrintStream@34c05d0e
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-4 running...
I got the data:java.io.PrintStream@56489592
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-5 running...
I got the data:java.io.PrintStream@26af6bb1
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-6 running...
I got the data:java.io.PrintStream@40d974e1
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-7 running...
I got the data:java.io.PrintStream@5fd08fc5
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-8 running...
I got the data:java.io.PrintStream@27dca26d
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-9 running...
I got the data:java.io.PrintStream@43a3a747
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-10 running...
I got the data:java.io.PrintStream@4521d907
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-11 running...
I got the data:java.io.PrintStream@4f114b68
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-12 running...
I got the data:java.io.PrintStream@28979470
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-13 running...
I got the data:java.io.PrintStream@131c736d
 I've sent back GOLD to you  PLUS those you sent me
Connected
MTServer-14 running...
 * 
 * 
 */
