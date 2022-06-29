import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import os

PORT = 9999
HOST= socket.gethostbyname(socket.gethostname())

class Client:

  def __init__(self,host,port):
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.sock.connect((host,port))
    msg=tkinter.Tk()
    msg.withdraw()
    self.username=simpledialog.askstring("Username", "Please enter the username", parent=msg)
    if self.username== "Admin":
      self.password=simpledialog.askstring("Password","Please enter the admin password",parent=msg)

    self.gui_done=False
    self.running= True

    gui_thread=threading.Thread(target=self.gui_loop)
    receive_thread=threading.Thread(target=self.receiving)
    gui_thread.start()
    receive_thread.start()

    

  #build the gui
  def gui_loop(self):
    self.win= tkinter.Tk()
    self.win.configure(bg="lightgray")

    #chat label
    self.chat_label=tkinter.Label(self.win,text= "Chat:", bg="lightgray")
    self.chat_label.config(font=("Arial",12))
    self.chat_label.pack(padx=20,pady=5)

    self.text_area=tkinter.scrolledtext.ScrolledText(self.win)
    self.text_area.pack(padx=20,pady=5)
    #can't be modified
    self.text_area.config(state="disabled")

    self.msg_label=tkinter.Label(self.win,text="Messsage",bg="lightgray")
    self.msg_label.pack(padx=20,pady=5)
    self.msg_label.config(font=("Arial",12))

    #input area
    self.input_area=tkinter.Text(self.win,height=3)
    self.input_area.pack(padx=20,pady=5)

    self.send_button=tkinter.Button(self.win, text= "Send", command= self.sending)
    self.send_button.config(font=("Arial",12))
    self.send_button.pack(padx=20,pady=5)

    self.gui_done = True
    self.win.protocol("WM_DELETE_WINDOW",self.stop)
    self.win.mainloop()


  def sending(self):
    message=f"{self.username}: {self.input_area.get('1.0','end')}"
    self.input_area.delete('1.0','end')
    if message[len(self.username)+2:].startswith("/"):
      if self.username=="Admin":
        if message[len(self.username)+2:].startswith("/kick"):
          self.sock.send(f"KICK{message.rstrip()[len(self.username)+7:]}".encode("utf-8"))
        elif message[len(self.username)+2:].startswith("/ban"):
          self.sock.send(f"BAN{message.rstrip()[len(self.username)+6:]}".encode("utf-8"))
          print(f"BAN {message[len(self.username)+6:]}")
        else:
          print("Error","This command doesn't exist")
      else:
        print("Permissions","This command can only be executed by admin")
    elif message[len(self.username)+2:].startswith("\FILE"):
      try:
        filepath=message.strip('\n')[len(self.username)+8:]
        filesize=os.path.getsize(filepath)
        filename=filepath.split(os.sep)[-1]
        data=f"FILE_{filename}_{filesize}"
        self.sock.send(data.encode("utf-8"))
        with open(filename, "rb") as f:
          while True:
            data=f.read(1024)
            #if it sent all part of the files, break
            if not data:
              self.send("FINISHED".encode("utf-8")) 	 
              break
            #if there's data send it
            self.sock.send(data)
      except:
        print(f"There's no actual {filepath}\n")
    else:
      if self.running:
        self.sock.send(message.encode("utf-8"))
    

  def stop(self):
    self.running= False
    self.win.destroy()
    self.sock.close()
    exit(0)

  def receiving(self):
    while self.running:
      try:
        #if client receives username from server, it sends it
        message=self.sock.recv(1024).decode("utf-8")
        if message== "Username":
          self.sock.send(self.username.encode("utf-8"))
          next_message= self.sock.recv(1024).decode("utf-8")
          if next_message== "Password":
            self.sock.send(self.password.encode("utf-8"))
            if self.sock.recv(1024).decode("utf-8") == "REJECTED":
              print("ERROR Not Admin Connection was rejected. Wrong password")
              self.running=False
          elif next_message== "BAN":
            print("ERROR Banned Connection was refused. You have been banned")
            self.running= False
        else:
          if self.gui_done:
            self.text_area.config(state="normal")
            self.text_area.insert('end',message)
            self.text_area.yview('end')
            self.text_area.config(state='disabled')
      except ConnectionAbortedError:
        break
      except:
        self.sock.close()
        break


client=Client(HOST,PORT)