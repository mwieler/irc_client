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

IRC_CMDS = {'m':'PRIVMSG','n':'NICK', 'j':'JOIN','q':'QUIT','NOTICE':'notice'}

# Create 'sock', a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create IPv4, TCP socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse port quickly

class message:
    def __init__(self,(msg,source)): #remember init takes arguments, NOT the class
        self.original_msg = msg
        self.source = source
        self.parsed_msg = None
        self.error_attributes = (None,"Message has not yet been parsed by parse_message")
        self.IRC_formatted_msg = None
    
    def is_msg_in_expected_structure(self):
        #pdb.set_trace()
        if self.original_msg[0] != '/':
            self.error_attributes = (False, "string must begin with a '/'")
        elif len(self.original_msg.split(' ')) < 3:
            self.error_attributes = (False, "usage: /command argument trailer")
        elif not IRC_CMDS.get(self.original_msg[1:].split(' ')[0],None): #returns None if user_cmd key not found in IRC_CMDS dict
            self.error_attributes = (False,"User command not recognized")
        else:
            self.error_attributes = (True, None)

    def parse_msg(self): #returns ((prefix,command,args,trailer),(parseable_msg,why_unparseable)
        if self.original_msg[0] == '/' and self.source == 'user' and self.error_attributes[0]: #/ indicates a user command
            user_cmd, args_and_trailer = self.original_msg[1:].split(' ',1)
            args, trailer = args_and_trailer.split(' ',1) #for now, only one-argument functions can be handled
            args = args.strip()
            self.parsed_msg = (None, user_cmd, args, trailer)
    
        elif self.source == 'server':
            if self.original_msg[0] == ':': 
                prefix, not_prefix = self.original_msg[1:].split(' ',1) #splits message into pre-space and post-space
            elif self.original_msg[0] != ':': #this statement is redundantly explicit, for clarity
                prefix, not_prefix = None, self.original_msg
            command_and_args, trailer = not_prefix.split(':',1)
            print "original_msg: ",msg_object.original_msg
            print "parsed_msg: ",msg_object.parsed_msg
            print "\nParsed message:\n", msg_object.parsed_msg #placeholder. eventually display properly formatted message
            print "command and args\n",command_and_args,"\nend of command and args" #debug stmt
            #pdb.set_trace() #debug statement
            command, args = command_and_args.split(' ',1) #returns '' for args if no args exist
            args = args.rstrip() #remove trailing whitespace. Should args be a space-delimited string or a list?
            self.parsed_msg = (prefix, command, args, trailer)
            self.error_attributes = (True, None)
        else:
           self.parsed_msg = None
           #self.error_attributes = (False, "Sorry, parse_msg couldn't handle the message")
           #pdb.set_trace()

    def format_as_IRC(self): #check message is valid prior to running
        #pdb.set_trace()
        (prefix, user_cmd, args, trailer) = self.parsed_msg
        if prefix:
            self.IRC_formatted_msg = ":"+prefix+" "+IRC_CMDS[user_cmd]+" "+args+" :"+trailer+"\n" #the \n is necessary for the IRC server
        if not prefix:
            self.IRC_formatted_msg = IRC_CMDS[user_cmd]+" "+args+" :"+trailer+"\n" #the \n is necessary for the IRC server


def read(sock): #listens for and prints out the received message
    while True:
        msg = sock.recv(1024)
        #msg_object = message((msg,'server'))
        print msg #for now, all the client does with servers messages is print them: eventually, it should make sense of them, too, and pong the server
        #pdb.set_trace()
        #msg_object.parse_msg() #we should be able to combine these two lines, or automatically call them
        #msg_object.format_as_IRC() #we should be able to combine these two lines, or automatically call them
        # parseable_msg, why_unparseable = msg_object.error_attributes
        # if parseable_msg:
        #     if msg_object.parsed_msg[1] == 'PING': #clean up - indexing refers to IRC command. make this clear
        #         sock.sendall('PONG '+trailer)
        # if not parseable_msg:
        #     print msg_object.original_msg, "was not parseable. Reason:\n", why_unparseable

def write(sock): #blocks on raw_msg, returns any msg from user
    while True:
        msg = raw_input("What to send to server?")
        msgtuple = (msg,'user') #(message,source)
        msg_object2 = message(msgtuple)
        msg_object2.is_msg_in_expected_structure()
        msg_object2.parse_msg() #these two fcns should be run automatically?
        #these two fcns should be run automatically?
        #pdb.set_trace()
        if msg_object2.error_attributes[0]: #if the message has been parsed...
            msg_object2.format_as_IRC() #format it as an IRC message....
            print "Sending",msg_object2.IRC_formatted_msg #and send it
            sock.sendall(msg_object2.IRC_formatted_msg)
        else:
            print msg_object2.error_attributes[1] #make this clearer

read_thread = threading.Thread(target=read, args=(sock,)) #starts read thread by passing read function and its arguments
read_thread.daemon = True #if only daemon threads are still running, they'll die. So if you kill the main loop

def main(): 
    print "test to see if main function is run"
    print "Connecting to",SERVER,"Port",PORT,"as",NICK
    sock.connect((SERVER,PORT))
    print "Waiting 2 seconds..." #this should only be sent once the server replies with stuff
    time.sleep(2)
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


#DEBUGGING STATEMENTS
#print parse_msg('/m testmatt testmsg','user')
#assert parse_msg('/m testmatt testmsg','user') == ((None,'PRIVMSG','testmatt','testmsg'),None,'user')

#print parse_msg(':rajaniemi.freenode.net 433 * mattwieler :Nickname is already in use.','server')
#assert parse_msg(':rajaniemi.freenode.net 433 * mattwieler :Nickname is already in use.','server')

# a = parse_servermsg(':rajaniemi.freenode.net 433 * mattwieler :Nickname is already in use.')
# b = parse_servermsg('PING :gibson.freenode.net')
#------------------------------------------------------

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
