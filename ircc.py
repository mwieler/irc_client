# To Do:
# 1. Add ability to join a channel.
# 2. Add 'bot-like' ability to generate responses.  Perhaps they mashup literature? or NYT articles?    

import socket
import threading
import pdb

# rather than if use dict. to turn user-supplied command into IRC command

CHANNEL = '#HACKERSCHOOL'

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create IPv4, TCP socket
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse port quickly
lsock.bind(('0.0.0.0', 4567)) #make socket available on local port 4567
lsock.listen(1) #transforms socket into 'listening' socket -- now functions
    # as a switchboard operator that can accept new connection requests

def handle_new_connection(lsock):
    sockob, addr = lsock.accept() #returns socket obecty, address (IP, PORT)
    lsock.setblocking(False) #makes the socket nonblocking
    print 'Connection accepted from ', addr #debug stmt
    print 'Socket connects', sockob.getsockname(), 'with peer', sockob.getpeername() #debug stmt
    return sockob #returns a socket obect that can send via sockob.sendall and receive via sockob.recv

def read(sockob): #listens for and prints out the received message
    while True:
        msg = sockob.recv(1024)
        print "\n server says:", msg,

def parse(input): #returns (validmsgflag,msg,errormsg)
    validmsg = False #better way to construct valid-message checking?
    if input.startswith("/"):
        #print "commands include: [none yet]"
        input1=input[1:].split(' ') #separate 
        if input1.pop(0) == 'p': #"private message to", input1[0], "that says", input1[1]
            return (True,"PRIVMSG "+CHANNEL+" :"+input1[0]+": "+" ".join(input1[1:]),None)
    else:
        return (0,None,"Usage: /p [addressee, if applicable] msg")

def write(sockob): #blocks on raw_input, returns any input from user
    while True:
        input = raw_input("thoughts?")
        if input == 'quit':
                break
        validmsg, input_IRC, errormsg = parse(input)
        if validmsg:
            sockob.sendall(input_IRC)
        elif not validmsg:
            print errormsg
        else:
            print "Unanticipated exception encountered."


sockob = handle_new_connection(lsock) #creates a sockob that can .sendall and .recv

read_thread = threading.Thread(target=read, args=(sockob,)) #starts read thread by passing
# read function and its arguments
read_thread.daemon = True #if only daemon threads are still running, they'll die.
read_thread.start()

write(sockob) #enters a while loop. If the loop is broken, only the thread remains, and it dies