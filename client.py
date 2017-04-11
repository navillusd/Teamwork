# -*- coding: utf-8 -*-
'''There are still some bugs that need to be fixed. The client and server about 90% done'''
# Messaging Client
import socket
import sys

MSGLEN = 1

# CONTRACT
# get_message : socket -> string
# Takes a socket and loops until it receives a complete message
# from a client. Returns the string we were sent.
# No error handling whatsoever.
def send (msg, HOST, PORT):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))
  length = sock.send(bytes(msg + "\0"))
  print ("SENT MSG: '{0}'".format(msg))
  print ("CHARACTERS SENT: [{0}]".format(length))
  return sock

def receive_message (sock):
  print "im about to receive message"
  chars = []
  try:
    while True:
      char = sock.recv(1)
      if char == bytearray('\0'):
        break
      if not char:
        break
      else:
        #print("Appending {0}".format(char))
        chars.append(char.decode("utf-8") )
  finally:
    print "finally"
    return ''.join(chars)


moduli_list=[]
def moduli_list_generator(string):
  count = 0
  for character in string:
    count += ord(character)
  moduli = count % 13
  moduli_list.append(moduli)
  count = 0
  print "The moduli list:", moduli_list
  return moduli_list


def checksum(input_list):
  count1 = 0
  for x in input_list:
    count1 += x
  print "The sum of each moduli in the list:", count1
  result = count1 % 17
  print "Checksum:", result
  return result



def checksum_output(string):
  return checksum(moduli_list_generator(string))

if __name__ == "__main__":
  # Check if the user provided all of the 
  # arguments. The script name counts
  # as one of the elements, so we need at 
  # least three, not fewer.
  '''
  if len(sys.argv) < 3:
    print ("Usage:")
    print (" python client.py <host> <port>")
    print (" For example:")
    print (" python client.py localhost 8888")
    print 
    sys.exit()
'''
  #host = sys.argv[1]
  #port = int(sys.argv[2])
  host="localhost"
  port= 8884
  Running = True
  while Running:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    #sock.connect((sys.argv[1], int(sys.argv[2])))
    input=int(raw_input("Press 1 for login, 2 for register:"))
    if input==1:
      username=raw_input("Username:")
      password=raw_input("Password")
      user_input= " ".join(["LOGIN", username, password])
      print user_input
      li=[]
      li.append(user_input)
      print li
      crc_number=checksum_output(user_input)
      number=str(crc_number)
      message=" ".join([user_input, number, "\0"])
      message1=bytearray(message, encoding="utf-8")
      length=sock.send(message1)
      #length=send(message1)
      print "Number of bytes sent:", length
      session_cookie=receive_message(sock)
      if session_cookie.startswith("Cookie"):
        input=int(raw_input("Press:\n 1: Message \n 2: Store \n3: Count \n4: Delete Message \n5 Get Message  \n 6: Dump \n7:Log Out")) #get message, dump.
        if input==1:
          sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          sock.connect((host, port))
          content=raw_input("What is your message?")
          user_input = " ".join(["MESSAGE", content, session_cookie])
          user_in=bytearray(user_input, encoding="utf-8")
          sock.send(user_in)
          print "your message sent"
          message1=receive_message(sock)
          print message1
          sock.close()









      else:
        print session_cookie
      #print("RESPONSE: [{0}]".format(cookie_id))
      sock.close()
      #run=True
      #while run:
       # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.connect((host, port))
        #user_input=int(raw_input("Press: \n 1 to Log Out \n 2 to Message"))
    elif input==2:
      username = raw_input(b"Username:")
      password = raw_input(b"Password")
      user_input = " ".join([b"REGISTER", username, password])
      crc_number = checksum_output(user_input)
      number = str(crc_number)
      message = " ".join([user_input, number, "\0"])
      message1=bytearray(message, encoding="utf-8")
      print message1
      length = sock.send(message)
      session_cookie = receive_message(sock)
      sock.close()
      if session_cookie.startswith("Cookie"):
        if session_cookie.startswith("Cookie"):
          input = int(raw_input("Press:\n 1: Message \n 2: Store \n3: Count \n4: Delete Message \n5 Get Message  \n 6: Dump "))  # get message, dump.
          if input == 1:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            content = raw_input("What is your message?")
            user_input = " ".join(["MESSAGE", content, session_cookie])
            user_in = bytearray(user_input, encoding="utf-8")
            sock.send(user_in)
            print "your message sent"
            message1 = receive_message(sock)
            print message1
            sock.close()
        elif input==2:

      else:
        print session_cookie







# length=sock.send(b"REGISTER sher 123")
# print ("CHARACTERS SENT: [{0}]".format(length))







"""

message goes into the IMQ queue
then we say store and the message moved from queue to mailbox
extend what it look like to extent protocol with session identifier
Use:
Cookies http
Sesion Identifier
Asymmetric keys
User Identification Protocols
"""
