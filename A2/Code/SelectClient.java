package ca.bcit.comp8005.ass2.abacus;

	import java.io.IOException;
	import java.net.InetSocketAddress;
	import java.nio.ByteBuffer;
	import java.nio.channels.SelectionKey;
	import java.nio.channels.Selector;
	import java.nio.channels.SocketChannel;
	import java.util.Iterator;

import ca.bcit.comp8005.utilities.Util;
	 
	 
public class SelectClient {	 
	    /**
	     * @param args
	     */
	    public static void main(String[] args) {
	        String string1 = "Sending a first message";
	       
	        SocketTest test1 = new SocketTest(string1);
	        Thread thread = new Thread(test1);
	        thread.start();
	        
	        String string2 = "Sending a Second message";
	        SocketTest test2 = new SocketTest(string2);
	        Thread thread2 = new Thread(test2);
	        thread2.start();
	      
	    }
	 
	    static class SocketTest implements Runnable {
	 
	        private String message = "";
	        private Selector selector;
	 	 
	        public SocketTest(String message){
	            this.message = message;
	        }
	 
	        @Override
	        public void run() {
	            SocketChannel channel;
	            try {
	                selector = Selector.open();
	                channel = SocketChannel.open();
	                channel.configureBlocking(false);
	 
	                channel.register(selector, SelectionKey.OP_CONNECT);
//	                channel.connect(new InetSocketAddress("47.104.73.117", 8511));
	                channel.connect(new InetSocketAddress("localhost", 8511));
	 
	                while (!Thread.interrupted()){
	 
	                    selector.select(1000); //1000 means TIMEOUT (s)
	                     
	                    Iterator<SelectionKey> keys = selector.selectedKeys().iterator();
	 
	                    while (keys.hasNext()){
	                        SelectionKey key = keys.next();
	                        keys.remove();
	 
	                        if (!key.isValid()) continue;
	 
	                        if (key.isConnectable()){
	                            System.out.println("I am connecting to the server");
	                            connect(key);
	                        }   
	                        if (key.isWritable()){
	                            write(key);
	                        }
	                        if (key.isReadable()){
	                            read(key);
	                        }
	                    }  
	                    
	                    /**
	                     *  How to inter-action? for instance, a robot backend to provide dialog as QA session.
	                     *  Or simply saying: how to write again?
	                     */
	                    
	                    Util.loger("will close the connection in 30 sec");
	                    Util.setTimer(30);
	                    close();
	                }
	            } catch (IOException e1) {
	                // TODO Auto-generated catch block
	                e1.printStackTrace();
	            } finally {
	                close();
	            }
	        }
	         
	        private void close(){
	            try {
	                selector.close();
	            } catch (IOException e) {
	                // TODO Auto-generated catch block
	                e.printStackTrace();
	            }
	        }
	 
	        private void read (SelectionKey key) throws IOException {
	            SocketChannel channel = (SocketChannel) key.channel();
	            ByteBuffer readBuffer = ByteBuffer.allocate(1000);
	            readBuffer.clear();
	            int length;
	            try{
	            length = channel.read(readBuffer);
	            } catch (IOException e){
	                System.out.println("Reading problem, closing connection");
	                key.cancel();
	                channel.close();
	                return;
	            }
	            if (length == -1){
	                System.out.println("Nothing was read from server");
	                channel.close();
	                key.cancel();
	                return;
	            }
	            readBuffer.flip();
	            byte[] buff = new byte[1024];
	            length=length<1024?length:1024;
	            readBuffer.get(buff, 0, length);  
	            System.out.println("Server said: "+new String(buff));
	        }
	 
	        private void write(SelectionKey key) throws IOException {
	            SocketChannel channel = (SocketChannel) key.channel();
	            channel.write(ByteBuffer.wrap(message.getBytes()));
	 
	            // lets get ready to read.
	            key.interestOps(SelectionKey.OP_READ);
	        }
	 
	        private void connect(SelectionKey key) throws IOException {
	            SocketChannel channel = (SocketChannel) key.channel();
	            if (channel.isConnectionPending()){
	                channel.finishConnect();
	            }
	            channel.configureBlocking(false);
	            channel.register(selector, SelectionKey.OP_WRITE);
	        }
	    }
	

}
