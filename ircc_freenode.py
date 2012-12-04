# test locally using netcat
# usage: nc 127.0.0.1 4567

# To Do:
# 1. Add ability to join a channel.
# 2. Add 'bot-like' ability to generate responses.  Perhaps they mashup literature? or google news articles?    
# 3. messages seem to end with "\n"
import socket
import threading
import pdb
import time

# rather than if use dict. to turn user-supplied command into IRC command

SERVER = "irc.freenode.net"
PORT = 6667
CHANNEL = '#HACKERSCHOOL'
NICK = 'testmatt'

IRC_CMDS = {'m':'PRIVMSG','n':'NICK', 'j':'JOIN','q':'QUIT'}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create IPv4, TCP socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse port quickly

def read(sock): #listens for and prints out the received message
    while True:
        msg = sock.recv(1024)
        if msg:
            print msg #not sure why the quotes are required
            msgtuple = (msg,'server')
            (validmsg, (prefix,command,args,trailer),errormsg, source) = parse_msg(*msgtuple)
            if command == 'PING':
                sock.sendall('PONG '+trailer)
            #print 'Server message was parsed as ',parse_servermsg(msg)

def parse_msg(msg,source): #returns (validmsg, (prefix,command,args,trailer),errormsg, source)
    #validmsg = False #better way to construct valid-message checking?
    if msg[0] == '/': #user command
       user_cmd, args_and_trailer = msg[1:].split(' ',1)
       args, trailer = args_and_trailer.split(' ',1) #for now, only one-argument functions can be handled
       args = args.strip()
       #args = args.split(' ') #Q: will whitespace get in the way?  
       #args = ' '.join(args) #joins the elements of list in 'args' with spaces
       return (True,(None,IRC_CMDS[user_cmd], args, trailer), None, source)    
    elif msg[0] == ':':
        prefix, not_prefix = msg[1:].split(' ',1) #splits message into pre-space and post-space
        command_and_args, trailer = not_prefix.split(':',1)
        command, args = command_and_args.split(' ',1) #returns '' for args if no args exist
        args = args.rstrip() #remove trailing whitespace
        return (True,(prefix, command, args, trailer), None, source)
    else:
       return (False,None,"Sorry, parse_msg couldn't handle the message")

#DEBUGGING STATEMENTS
print parse_msg('/m testmatt testmsg','user')
assert parse_msg('/m testmatt testmsg','user') == (True,(None,'PRIVMSG','testmatt','testmsg'),None,'user')

print parse_msg(':rajaniemi.freenode.net 433 * mattwieler :Nickname is already in use.','server')
assert parse_msg(':rajaniemi.freenode.net 433 * mattwieler :Nickname is already in use.','server')

def parsed_to_irc(validmsg,(prefix,IRC_command,args,trailer),errormsg, source):
    if validmsg:
        return (True,IRC_command+" "+args+" :"+trailer+"\n",None) #the \n is necessary for the IRC server
    if not validmsg: #if not a valid 
        return (False,None,"Usage: /command arg trailer2")

#debugging
# a = parse_servermsg(':rajaniemi.freenode.net 433 * mattwieler :Nickname is already in use.')
# b = parse_servermsg('PING :gibson.freenode.net')

def write(sock): #blocks on raw_msg, returns any msg from user
    while True:
        msg = raw_input("What to send to server?")
        msgtuple = (msg,'user') #(message,source)
        parsed_msg = parse_msg(*msgtuple)
        validmsg,IRC_msg,errormsg = parsed_to_irc(*parsed_msg)
        if validmsg:
            print "Sending",IRC_msg
            sock.sendall(IRC_msg)
        else:
            print errormsg

read_thread = threading.Thread(target=read, args=(sock,)) #starts read thread by passing
# read function and its arguments
read_thread.daemon = True #if only daemon threads are still running, they'll die.

def main(): 
    print "test to see if main function is run"
    print "2"
    print "Connecting to",SERVER,"Port",PORT,"as",NICK
    sock.connect((SERVER,PORT))
    print "Waiting 3 seconds..." #this should only be sent once the server replies with stuff
    time.sleep(3)
    print "Sending nickname request to server..."
    sock.send("NICK "+NICK+"\nUSER "+NICK+" 0 * "+NICK+"\n")
    read_thread.start()
    write(sock) #enters a while loop. If the loop is broken, only the thread remains, and it dies


if __name__ == '__main__':
     main()

     # while True:
    #     msg = raw_msg("thoughts?")
    #     if msg == 'quit':
    #             break
    #     validmsg, msg_IRC, errormsg = parse(msg)
    #     if validmsg:
    #         sock.sendall(msg_IRC)
    #     elif not validmsg:
    #         print errormsg
    #     else:
    #         print "Unanticipated exception encountered."


#sockob = handle_new_connection(lsock) #creates a sockob that can .sendall and .recv





#sock.bind(('0.0.0.0', 4567)) #make socket available on local port 4567

#sock.listen(1) #transforms socket into 'listening' socket -- now functions
    # as a switchboard operator that can accept new connection requests

# def handle_new_connection(lsock):
#     sockob, addr = lsock.accept() #returns socket obecty, address (IP, PORT)
#     lsock.setblocking(False) #makes the socket nonblocking
#     print 'Connection accepted from ', addr #debug stmt
#     print 'Socket connects', sockob.getsockname(), 'with peer', sockob.getpeername() #debug stmt
#     return sockob #returns a socket obect that can send via sockob.sendall and receive via sockob.recv
