# -*- coding: utf-8 -*-
'''Read the documentation'''


import base64
import uuid
import threading
# https://pymotw.com/2/socket/tcp.html
# https://docs.python.org/3/howto/sockets.html

# Messaging Server v0.1.0
import socket
import sys


class SimpleMailServerProtocol():
    def __init__(self):
        self.IMQ = []  # incoming_message_queue
        self.MBX = {}  # user_mailboxes
        self.login = {} #registered accounts and passwords
        self.ID = {}  #session ids and usernames
        self.assigned_cookies=[] #to check which session cookies has already been assigned




    def moduli_list_generator(self, string):
        moduli_list=[]
        print "Moduli_list:", moduli_list
        count = 0
        for character in string:
            count += ord(character)
        moduli = count % 13
        moduli_list.append(moduli)
        count = 0
        return moduli_list



    def checksum(self, input_list):
        count1 = 0
        for x in input_list:
            count1 += x
        print "The sum of each moduli in the list:", count1
        result = count1 % 17
        return result

    def checksum_output(self, string):
        return self.checksum(self.moduli_list_generator(string))

    # CONTRACT
    # start_server : string number -> socket
    # Takes a hostname and port number, and returns a socket
    # that is ready to listen for requests
    def start_server (self, host, port):
      server_address = (host, port)
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.bind(server_address)
      sock.listen(1)
      return sock


      # CONTRACT
      # socket -> boolean
      # Shuts down the socket we're listening on.
    def stop_server(self, sock):
      return sock.close()
    #<------------------------------------------------------------------------------------------------------------>
    def get_message(self, sock):
      chars = []
      connection, client_address = sock.accept()
      print ("Connection from [{0}]".format(client_address))
      try:
          while True:
              char = connection.recv(1)
              if char == b'\0':
                  break
              if char == b'':
                  break
              else:
                  # print("Appending {0}".format(char))
                  chars.append(char.decode("utf-8"))
      finally:
          return (''.join(chars), connection)

    #This is get_message() method I implemented in Matt Jadud's server code file - Sher Sanginov
    # CONTRACT
    # get_message : socket -> Tuple(string, socket)
    # Takes a socket and loops until it receives a complete message
    # from a client. Returns the string we were sent.
    # No error handling whatsoever.
    #def get_message (self, sock):
     # connection, client_address = sock.accept() # accept client connection , returns a tuple of two values
      #print "Client address: [{0}]".format(client_address)
      #message=connection.recv(5000)
      #tup=(message, connection)
      #return tup
      #char=''
      #while char != b'\0': #this loop stops when received character is equal to \0 (delimitor)
      #	char=connection.recv(1)  #receives one character at a time
       #     if char.isalpha()==True or char.isspace()== True or char.isdigit()==True:  #checks validity of a character
        #    	string= str(char) #append char to string
         #   	print "Received byte:", string   #print each string character
    #now if you think about that a bit, you'll come to realize : reading ; message must be fixed length
    #what must i do to send complete message? you can user delimeters: every message with be delimited with period
    # message is not done until the period is sent
    #bytes are not strings some_byte=b'x'
      #connection.send("connected\0")


#< ----------------------------------------------------------------------------------------------------------->


# Mail server methods:




    def assign_cookie(self, username, conn):
        '''assigns cookie to the user'''
        if username not in self.ID:  #checking if username doesn't already have a cookie and if cookie is not assigned
            session_id = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
            while session_id in self.assigned_cookies:
                session_id = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
            self.ID[username]=session_id
            self.assigned_cookies.append(session_id)
            cookie= " ".join([b"Cookie:", session_id])
            cooki=bytearray(cookie, encoding='utf-8')
            conn.sendall(cooki)
            conn.close()
        else:
            print username, "has session cookie already"
            message=bytearray("This username has a session cookie. Please, log in:", encoding="utf-8")
            conn.send(message)
            conn.close()


    def register(self, message, connection):
          '''Register with password.Only username is parsed.Password must be direct'''
          username = message.split(" ")[1]   #splitting username from message
          password= message.split(" ")[2]   #splitting password from message
          if username not in self.login:    #if user is not already registered
              self.login[username]=password #register him/her
              self.assign_cookie(username, connection)
              if username not in self.MBX:   #if user does not have a mailbox
                  self.MBX[username]=[]     #create mailbox
              return True
          else:
              connection.send(bytearray("KO. You are registered. You should login now.",encoding="utf-8"))
              connection.close()
              return False

    def log_out(self, message, connection):
        username = message.split(" ")[1]  # splitting username from message
        password = message.split(" ")[2]  # splitting password from message
        if username in self.login:      #if user is already registered
            if self.login[username]==password:      #if his accound and password match
                for i in self.assigned_cookies:
                    if i == self.ID[username]:
                        self.assigned_cookies.remove(i)     #delete user session from assigned session list
                del self.ID[username]           #delete user from [account_name:session]
                print "Removed session id of user:", username



    def log_in(self,message,connection):
        #content=message.split(" ")[:4] "LOGIN sher pass 4"
        log=message.split(" ")[0]
        username = message.split(" ")[1]  # splitting username from message "LOGIN daryl lo 4>
        password = message.split(" ")[2]  # splitting password from message
        checksum=message.split(" ")[3]
        content = " ".join([log, username, password])
        content=str(content)
        num=self.checksum_output(content)
        print num
        if num==num:
            print "good message"
            if username in self.login:          #if user is registered
                if self.login[username]==password:  #if user account match user password
                    print "Success.", username, "is logged in."
                    self.assign_cookie(username, connection)    #assign cookie to logged in user
                else:
                    print "Failure. Wrong password."
            else:
                print "he should register first"
                connection.send(bytearray('You should register first.',encoding="utf-8"))
                connection.close()
        else:
            print "Retry"
            connection.send(bytearray("Please, resend the message", encoding="utf-8"))
            connection.close()


    def add_message(self, content, connection):
      print content
      message = content.split(" ")[1]
      cookie=content.split(" ")[3]
      cookie2=str(cookie)
      for i in self.ID:
          if self.ID[i]==cookie2:
              self.IMQ.append(message)
              print "message appended"
              connection.send(bytearray("OK. You message was added.", encoding="utf-8"))
          else:
              print "not appended"
              connection.send(bytearray("KO"))


    def store(self, message, connection):

      user = message.split(" ")[1]
      if user in self.MBX:
        recent_message = self.IMQ.pop()
        self.MBX[user].append(recent_message)
        connection.send(b"OK. Your recent message has been stored in user's mailbox")
        return True
      else:
        connection.send("KO. Your message has not been stored")
        return False

    def count(self, username, connection):
      user = username.split(" ")[1]
      if user in self.MBX:
        count = len(self.MBX[user])
        connection.send("Your total messages COUNTED:", "<", count, ">")
        return True
      else:
        connection.send("KO. did not count error")
        return False

    def delete_message(self, username, connection):
      user = username.split(" ")[1]
      if user in self.MBX:
        self.MBX[user].pop(0)
        connection.send("OK. You first message was deleted from MBX.")
        return True
      else:
        connection.send("KO. was not deleted")
        return False

    def get_client_message(self, username, connection):
      user = username.split(" ")[1]
      if user in self.MBX:
        connection.send("Your message:", self.MBX[user].pop())
        return True
      else:
        connection.send("KO. did not get client message")
        return False

        # return the first message from the user's mailbox queue
        # return KO if no message or user not registered

    def dump(self, msg, conn):
      if "DUMP" in msg:
        print self.MBX
        print self.IMQ
        conn.sendall(b"OK\0")
        return True
      else:
        print("NO HANDLER FOR CLIENT MESSAGE: [{0}]".format(msg))
        conn.sendall(b"KO\0")
        return False



# CONTRACT
# handle_message : string socket -> boolean
# Handles the message, and returns True if the server
# should keep handling new messages, or False if the 
# server should shut down the connection and quit.
    def handle_message (self, msg, conn):
      if msg.startswith("REGISTER"):
        self.register(msg, connection)
      elif msg.startswith("LOGIN"):
        self.log_in(message, conn)
      elif msg.startswith("MESSAGE"):
        self.add_message(msg, conn)
      elif msg.startswith("STORE"):
        self.store(msg, conn)
      elif msg.startswith("COUNT"):
        self.count(msg, conn)
      elif msg.startswith("DELMSG"):
        self.delete_message(msg, conn)
      elif msg.startswith("GETMSG"):
        self.get_client_message(msg, conn)
      elif msg.startswith("DUMP"):
        self.dump(msg, conn)

  
if __name__ == "__main__":
  # Check if the user provided all of the 
  # arguments. The script name counts
  # as one of the elements, so we need at 
  # least three, not fewer.
  '''
  if len(sys.argv) < 3:
    print ("Usage: ")
    print (" python server.py <host> <port>")
    print (" e.g. python server.py localhost 8888")'''
    #sys.exit()

  #host = sys.argv[1]
  #port = int(sys.argv[2])
  host = "localhost"
  port = 8884
  mail_server=SimpleMailServerProtocol()
  sock = mail_server.start_server(host, port)
  print("Running server on host [{0}] and port [{1}]".format(host, port))
  
  RUNNING = True
  while RUNNING:
    message, connection = mail_server.get_message(sock)

    print("MESSAGE: [{0}]".format(message))
    print "got the message"
    t= threading.Thread(target=mail_server.handle_message, args=(message, connection,)).start()




    #handle_message(message, connection)

    #handle_message(message, connection, MessageServer())
    # This 'if' probably should not be in production.
    # Our template/test code returns "None" for the connection...


  #mail_server.stop_server(sock)



