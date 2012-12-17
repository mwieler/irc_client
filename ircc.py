# test locally using netcat
# usage: nc 127.0.0.1 4567

# To Do:
# 1. Add ability to join a channel.
# 2. Add 'bot-like' ability to generate responses.  Perhaps they mashup literature? or google news articles?    

import socket
import threading
import pdb

# rather than if use dict. to turn user-supplied command into IRC command

CHANNEL = '#HACKERSCHOOL'
COMMANDS = {'p':'PRIVMSG','n':'NICK', 'j':'JOIN'}

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

def parse(input):
    validmsg = False #better way to construct valid-message checking?
    if input[0] == '/':
       user_cmd, addressee, msg = input[1:].split(' ',2)
       return (True,COMMANDS[user_cmd]+" "+CHANNEL+" :"+addressee+": "+msg, None)    
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

def parse_usermsg(msg): #returns (validmsgflag, (prefix,command,args,trailer),errormsg)
    validmsg = False #better way to construct valid-message checking?
    if msg[0] == '/':
       user_cmd, args, trailer = msg[1:].split(' ',2)
       return (True,(None,IRC_CMDS[user_cmd],args,trailer), None)    
    else:
      return (False,None,"Usage: /p [addressee, if applicable] msg")

def parsed_to_irc(validmsg,(prefix,IRC_command,args,trailer),errormsg):
    if validmsg:
        return IRC_command+" "+args+" :"+trailer
    if not validmsg:
        print errormsg

def parse_servermsg(msg):
    if msg[0] == ':':
        prefix, not_prefix = msg[1:].split(' ',1) #splits message into pre-space and post-space
    else:
        prefix = None
        not_prefix = msg   
    command_and_args, trailer = not_prefix.split(':',1)
    command, args = command_and_args.split(' ',1) #returns '' for args if no args exist
    return prefix, command, args, trailer


sockob = handle_new_connection(lsock) #creates a sockob that can .sendall and .recv

read_thread = threading.Thread(target=read, args=(sockob,)) #starts read thread by passing
# read function and its arguments
read_thread.daemon = True #if only daemon threads are still running, they'll die.
read_thread.start()

write(sockob) #enters a while loop. If the loop is broken, only the thread remains, and it dies