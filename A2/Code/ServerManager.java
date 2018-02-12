import java.nio.channels.spi.SelectorProvider;

public class ServerManager {

	final static String POLL = "sun.nio.ch.PollSelectorProvider";
	final static String EPOLL = "sun.nio.ch.EPollSelectorProvider";

	// Configurable Arguments
	public static int ULIMIT_SIZE=100*1000;

	static String ServerIP = "localhost";
	static int ServerPort = 8088;
	static String Mode = "EPOLL";
	static int BUFFER_SIZE = 1024 * 50;
	static int ThreadNum = 1;

	public static void main(String[] args) {
		
		prepArgs(args);
		setupEnv();

	}

	static void prepArgs(String[] args) {

		if (args.length >= 4) {

			Util.loger("<ServerIP> <ServerPort> <EPOLL|POLL|MT> <BUFFER_SIZE> <ThreadNumber> ");
				ServerIP = args[0];
			ServerPort = Integer.parseInt(args[1]);
			Mode = args[2];
			BUFFER_SIZE = Integer.parseInt(args[3]);
			ThreadNum = Integer.parseInt(args[4]);
			
			if (Mode =="POLL") {
				Util.loger(" MUST-DO: -f POLL, MUST HAVE!! -Djava.nio.channels.spi.SelectorProvider=sun.nio.ch.PollSelectorProvider");
			//@todo further check...	
			}
		}

	}

	static void setupEnv() {

		// put it in a shell
		Util.runCmd("ulimit -n " + ULIMIT_SIZE);

	}

	void initServer() {

		Util.loger("The High Perform Server is starting on port:" + ServerPort);
		

		if (Mode == "EPOLL") {
			EPollServer.execute(ServerIP, ServerPort, BUFFER_SIZE, ThreadNum);
			Util.loger("The provier is \t" + getProvider());
		} else if (Mode == "POLL") {
			PollServer.execute(ServerIP, ServerPort, BUFFER_SIZE, ThreadNum);
			Util.loger("The provier is \t" + getProvider());
		} else {
			MTServer.execute(ServerPort);
		}

	}

	static String getProvider() {

		// Util.loger(System.getProperties());
		String rst;
		rst = SelectorProvider.provider().getClass().getName();
		return rst;


	}

	static void setProvider(Boolean isPoll) {

		String providerName = isPoll ? POLL : EPOLL;

		try {
			// hack to work around compiler complaints about sun.nio.ch.PollSelectorProvider
			// being proprietary
			Class.forName(providerName).newInstance();
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		System.setProperty("java.nio.channels.spi.SelectorProvider", SelectorProvider.class.getName());
	}

}
