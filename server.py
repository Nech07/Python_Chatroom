import socket
import threading


PORT = 9999

#take local ip address
SERVER= socket.gethostbyname(socket.gethostname())

#specify type of address family and socket type AF_INET is the internet address family of IPv4
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#bind port to ther server
ADDR= (SERVER,PORT)
server.bind(ADDR)


#lists for clients and their nicknames
clients=[]
usernames=[]

#sending message for each user
def send_message(message):
  for client in clients:
    client.send(message)


def kick(user):
  if user in usernames:
    indexx=usernames.index(user)
    client=clients[indexx]
    clients.remove(client)
    client.send("You were kicked\n".encode("utf-8"))
    usernames.pop(indexx)
    send_message(f"{user} was kicked\n".encode("utf-8"))
    client.close()

def handle_client(conn):
  while True:
    try:
      message=conn.recv(1024)
      msg= message.decode("utf-8")
      if msg.startswith("FILE"):
        data=conn.recv(1024).decode("utf-8")
        
      elif msg.startswith("KICK"):
        if usernames[clients.index(conn)]== "Admin":
          user_kick=msg[5:]
          kick(user_kick)
        else:
          conn.send("You dan't have permission to user this command")
      elif msg.startswith("BAN"):
        if usernames[clients.index(conn)]== "Admin":
          user_ban=msg[4:]
          kick(user_ban)
          with open("bans.txt","a") as f:
            f.write(f"{user_ban}\n")
          print(f"{user_ban} banned")
          send_message(f"{user_ban} banned")
        else:
          print("You don't have permission to user this command")
      else:
        send_message(message)
    except:
      #removing and closing clients
      if conn in clients:
        indexx=clients.index(conn)
        clients.remove(conn)
        send_message(f"{usernames[indexx]} left the chat\n".encode("ascii"))
        usernames.remove(usernames[indexx])
        conn.close()
        break
  

#start socket and listen for new connections
def start():
  server.listen()
  PASSWORD=input("admin password: ")
  print(f"SERVER IS LISTENING on {SERVER}")
  while True:
    #store address of a new conection
    conn,addr=server.accept()
    print(f"Connected with {str(addr)}")
    #request and record the username in the list
    conn.send("Username".encode("utf-8"))

    username=conn.recv(1024).decode("utf-8")
    print("Username is {}".format(username))
    with open("bans.txt", "r") as f:
      bans=f.readlines()
    if username+"\n" in bans:
      conn.send("BAN".encode("utf-8"))
      conn.close
      continue

    if username== "Admin":
      conn.send("Password".encode("utf-8"))
      password=conn.recv(1024).decode("ascii")

      if password !=PASSWORD:
        conn.send("REJECTED".encode("utf-8"))
        conn.close()
        continue
    usernames.append(username)
    clients.append(conn)


    #print in the chatroom a new user joined
    send_message(f"{username} joined the chat\n".encode("utf-8"))

    #starting a new thread
    thread = threading.Thread(target=handle_client, args=(conn,))
    thread.start()




print("SERVER is starting")
start()