from tkinter import *
from tkinter import ttk
import time
import sys

LOG_LINE_NUM = 0

p1 = int(1000)
p2 = int(2000)
#content={p1:'192.168.0.33:22', p2:'192.168.0.33:80'}
content={}

class MY_GUI():
    
    def __init__(self,init_window_name):
        self.init_window_name = init_window_name


    # set window 
    def set_init_window(self):
        self.init_window_name.title("port forwarding tool")           #窗口名
        #self.init_window_name.geometry('320x160+10+10')                         #290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.init_window_name.geometry('1068x681+10+10')
        #self.init_window_name["bg"] = "pink"                                    #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
        #self.init_window_name.attributes("-alpha",0.9)                          #虚化，值越小虚化程度越高
        
        #Label
        self.log_label = Label(self.init_window_name, text="Service Log")
        self.log_label.grid(row=0, column=0)
        self.init_data_label = Label(self.init_window_name, text="Program Monitor")
        self.init_data_label.grid(row=0, column=12)
        self.port_forward_label = Label(self.init_window_name, text="Port forward table")
        self.port_forward_label.grid(row=10, column=12)
        self.lport_label = Label(self.init_window_name, text="local port : ")
        self.lport_label.grid(row=12, column=12, sticky=(W))
        self.rhost_label = Label(self.init_window_name, text="remote host : ")
        self.rhost_label.grid(row=12, column=14, sticky=(W))
        
        #Frame
        self.init_data_Text = Text(self.init_window_name, width=60, height=10)  #status monitor
        self.init_data_Text.grid(row=1, column=12, rowspan=12, columnspan=10, sticky=(N, W, E))
        
        self.log_data_Text = Text(self.init_window_name, width=60, height=35)  #log tracer
        self.log_data_Text.grid(row=1, column=0, rowspan=12, columnspan=10)
        scroll = ttk.Scrollbar(self.init_window_name, orient=VERTICAL, command=self.log_data_Text)
        self.log_data_Text.configure(yscrollcommand=scroll.set)
        
        self.port_forward_table = ttk.Treeview(self.init_window_name, selectmode="extended", columns=("local port","remote host"))  #port configure
        self.port_forward_table.grid(row=11, column=12, columnspan=10, sticky=(N, W, E))

        #Fill the table

        self.port_forward_table["columns"]=("local port","remote host")
        self.port_forward_table.column("#0", width=50, stretch=NO)
        self.port_forward_table.column("local port", width=100 )
        self.port_forward_table.column("remote host", width=200)
        self.port_forward_table.heading("#0", text="No")
        self.port_forward_table.heading("local port", text="local port")
        self.port_forward_table.heading("remote host", text="remote host")

        for k,v in content.items():
            self.port_forward_table.insert('', 'end',  values=(k, v))

        self.port_forward_table.bind('<ButtonRelease-1>', self.select_item)
        
        ttk.Style().configure("Treeview", font=('', 11), background="#383838", foreground="white", fieldbackground="yellow")

        #Entry part
        self.lport = StringVar()
        self.rhost = StringVar()
        self.lport_entry = ttk.Entry(self.init_window_name, width=10, textvariable=self.lport)
        self.lport_entry.grid(row=12, column=13, sticky=(W))
        self.rhost_entry = ttk.Entry(self.init_window_name, width=20, textvariable=self.rhost)
        self.rhost_entry.grid(row=12, column=15, sticky=(W))

        #Buttons
        self.update_button = Button(self.init_window_name, text="Update", bg="lightblue", width=10,command=self.update_item)  # 调用内部方法
        self.update_button.grid(row=13, column=12)

        self.add_button = Button(self.init_window_name, text="Add", bg="lightblue", width=10,command=self.add_item)  # 调用内部方法
        self.add_button.grid(row=13, column=13)

        self.del_button = Button(self.init_window_name, text="Delet", bg="lightblue", width=10,command=self.del_item)  # 调用内部方法
        self.del_button.grid(row=13, column=14)

        self.writefile_button = Button(self.init_window_name, text="Save", bg="lightblue", width=10,command=self.write_file)  # 调用内部方法
        self.writefile_button.grid(row=13, column=15, sticky=(W))

        self.run_button = Button(self.init_window_name, text="Run", bg="lightblue", width=10,command=self.run)  # 调用内部方法
        self.run_button.grid(row=13, column=16)
    
    # func
    def select_item(self, evt):
        try:
            # gets all values of the row
            row = self.port_forward_table.selection()[0]
            print(self.port_forward_table.item(row)['values'][0])
            #self.lport = self.port_forward_table.item(row)['values'][0]
            self.clear_entry()
            self.lport_entry.insert(0, self.port_forward_table.item(row)['values'][0])
            self.rhost_entry.insert(0, self.port_forward_table.item(row)['values'][1])
        except:
            print("click on the wild area...")
            pass

    def add_item(self):
        global content
        print("click add button")
        port = int(self.lport.get())
        host = self.rhost.get()
        self.port_forward_table.insert('', 'end',  values=(port, host))
        content.update({port:host})
        print(content)
        self.clear_entry()

    def update_item(self):
        print("click update button")
        global content
        try:
            row = self.port_forward_table.selection()[0]
            print(self.port_forward_table.item(row)['values'][0])
            port_old = self.port_forward_table.item(row)['values'][0]
            port = int(self.lport.get())
            host = self.rhost.get()
            self.port_forward_table.item(row, values=(port, host))
            if port_old != port:
                del content[port_old]
            content.update({port:host})
            
            print(content)
            self.clear_entry()
        except:
            pass

    def del_item(self):
        print("click delete button")
        global content
        try:
            row = self.port_forward_table.selection()[0]
            print(self.port_forward_table.item(row)['values'][0])
            key = self.port_forward_table.item(row)['values'][0]
            del content[key]
            self.port_forward_table.delete(row)
            print(content)
            self.clear_entry()
        except:
            print("please choose a piece of data first...")
            pass

    # write back the dictionary to conf file
    def write_file(self):
        print("click write file button")
        global content
        with open('ports.conf', 'w') as f:
            for k, v in content.items():
                line = str(k) + ' ' + v + '\n'
                f.write(line)


    def run(self):
        print("click run button")

    # clear entry modulee
    def clear_entry(self):
        self.lport_entry.delete(0, END)
        self.rhost_entry.delete(0, END)

    # get current timestamp
    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        return current_time


    # print log
    def write_log_to_Text(self,logmsg):
        global LOG_LINE_NUM
        current_time = self.get_current_time()
        logmsg_in = str(current_time) +" " + str(logmsg) + "\n" 
        if LOG_LINE_NUM <= 7:
            self.log_data_Text.insert(END, logmsg_in)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_data_Text.delete(1.0,2.0)
            self.log_data_Text.insert(END, logmsg_in)


# read configure file to a dictionary for searching the route
def readPortsList():
    global content 
    f = open('ports.conf', 'r')
    for line in f:
        link = line[:-1]
        lport, rhost = link.split(' ')
        lport = int(lport)
        content.update({lport:rhost})
    print("\n[+] finish reading ports setting from file...\n")

def gui_start():

    readPortsList()
    init_window = Tk()              #实例化出一个父窗口
    ZMJ_PORTAL = MY_GUI(init_window)
    # 设置根窗口默认属性
    ZMJ_PORTAL.set_init_window()

    init_window.mainloop()          #父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示


gui_start()
