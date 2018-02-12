
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.net.ServerSocket;
import java.net.Socket;

public class MTServer implements Runnable {

	private static int SERVER_PORT = 8899;

	Socket csocket;
	int tid;

	MTServer(Socket csocket, int threadId) {
		this.csocket = csocket;
		tid = threadId;
	}

	public static void main(String args[]) throws Exception {
		
		
		execute(SERVER_PORT);
	}

	
	
	 static void execute (int port) {
		 
		ServerSocket ssock;
		try {
			ssock = new ServerSocket(port);
		
		Util.loger("Listening on port:"+port);

			for (int i = 1;; i++) {
				Socket sock = ssock.accept();
				Util.loger("Connected");
				Thread mts = new Thread(new MTServer(sock, i));
				mts.setName("MTServer-" + i);
				mts.start();
			}
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	 }
	public void run() {
		Util.loger(Thread.currentThread().getName()+" running...");
		try {
			PrintStream pstream = new PrintStream(csocket.getOutputStream());

			Util.logd("I got the data:" + pstream);
			for (int i = 10; i >= 0; i--) {
				pstream.println(i + " piles of GOLD  in the CAVE");				
			}
			Util.logd(" I've sent back GOLD to you attached with you sent to me");
			
			BufferedReader in = new BufferedReader(new InputStreamReader(csocket.getInputStream()));
			String inputLine;
			while ((inputLine = in.readLine()) != null) {
				pstream.println(inputLine);				
				Util.logd(inputLine);
			}
			pstream.close();
			csocket.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}