# test locally using netcat
# usage: nc 127.0.0.1 4567

# To Do:
# 1. make trailers are OPTIONAL -- DONE
# 2. add interactive pygame interface to learn about control structures, user interface


# 1. Add ability to join a channel.
# 2. Add 'bot-like' ability to generate responses.  Perhaps they mashup literature? or google news articles?    
# 3. messages seem to end with "\n"
import socket
import threading
import pdb
import time
import select

#for pygame
import sys
import pygame
from pygame.locals import *

# rather than if use dict. to turn user-supplied command into IRC command

SERVER = "irc.freenode.net"
PORT = 6667
CHANNEL = '#HACKERSCHOOL'
NICK = 'testmatt'
FONTSIZE = 24
NUM_LINES_ON_SCREEN = 25


IRC_CMDS = {'m':'PRIVMSG','n':'NICK', 'j':'JOIN','q':'QUIT','o':'NOTICE'}

def print_dict():
    print "User command   |IRC Command\n-----------------------------"
    for k,v in IRC_CMDS.items():
        print k,"\t\t",v

def makenew_pyg_textsurface(msg,fontsize):
    fontobject = pygame.font.Font(None,fontsize) #makes a font object
    textsurface = fontobject.render(msg,1,(255,255,255))
    return textsurface

class Message:
    def __init__(self,(msg,source)): #remember init takes arguments, NOT the class
        self.original_msg = msg #pygame may not recognize / so for now add it in manually if you have to using "/"+msg
        self.source = source
        self.parsed_msg = None
        self.valid_msgtuple = (None,"Message has not yet been parsed by parse_message")
        self.IRC_formatted_msg = None
    
    def is_msg_in_expected_structure(self):
        if len(self.original_msg.split(' ')) < 2:
            self.valid_msgtuple = (False, "usage: /command argument trailer")
        elif not IRC_CMDS.get(self.original_msg[1:].split(' ')[0],None): #returns None if user_cmd key not found in IRC_CMDS dict
            self.valid_msgtuple = (False,"User command not recognized. Valid IRC commands include:",print_dict())
        else:
            self.valid_msgtuple = (True, None)

    def parse_msg(self): #returns ((prefix,command,args,trailer),(parseable_msg,why_unparseable)
        if self.source == 'user' and self.valid_msgtuple[0]:
            user_cmd, args_and_trailer = self.original_msg[1:].split(' ',1)
            if len(args_and_trailer.split(' ')) > 1:
                args, trailer = args_and_trailer.split(' ',1) #for now, only one-argument functions can be handled
            elif len(args_and_trailer.split(' ')) == 1:
                args, trailer = args_and_trailer, '' #must be '', can't be None, bc later trailer is concatenated
            args = args.strip()
            self.parsed_msg = (None, user_cmd, args, trailer)
    
        elif self.source == 'server':
            if self.original_msg[0] == ':': 
                prefix, not_prefix = self.original_msg[1:].split(' ',1) #splits message into pre-space and post-space
            elif self.original_msg[0] != ':': #this statement is redundantly explicit, for clarity
                prefix, not_prefix = None, self.original_msg
            command_and_args, trailer = not_prefix.split(':',1)
            print "original_msg: ", self.original_msg
            print "parsed_msg: ", self.parsed_msg
            print "\nParsed message:\n", self.parsed_msg #placeholder. eventually display properly formatted message
            print "command and args\n",command_and_args,"\nend of command and args" #debug stmt
            if ' ' in command_and_args:
                command, args = command_and_args.split(' ',1) #returns '' for args if no args exist
                args = args.rstrip() #remove trailing whitespace. Should args be a space-delimited string or a list?
            else:
                command = command_and_args
                args = ''
            self.parsed_msg = (prefix, command, args, trailer)
            self.valid_msgtuple = (True, None)
        else:
           self.parsed_msg = None
           #self.valid_msgtuple = (False, "Sorry, parse_msg couldn't handle the message")

    def format_as_IRC(self): #check message is valid prior to running
        (prefix, user_cmd, args, trailer) = self.parsed_msg #factor this out of format_as_IRC; this part just separates
        #the message into its constituent parts (as defined by the IRC protocol)
        if prefix:
            self.IRC_formatted_msg = ":"+prefix+" "+IRC_CMDS[user_cmd]+" "+args+" :"+trailer+"\n" #the \n is necessary for the IRC server
        if not prefix:
            self.IRC_formatted_msg = IRC_CMDS[user_cmd]+" "+args+" :"+trailer+"\n" #the \n is necessary for the IRC server


def read(sock): #listens for and prints out the received message
    while True:
        msg = sock.recv(1024)

def parse(msg): #blocks on raw_msg, returns any msg from user
    msgtuple = (msg,'user') #(message,source)
    user_msg = Message(msgtuple)
    user_msg.is_msg_in_expected_structure()
    user_msg.parse_msg()
    if user_msg.valid_msgtuple[0]: #if the message has been parsed successfully...
        return user_msg #hope this returns a "Message" object, as I've defined it
    else:
        print user_msg.valid_msgtuple[1] #prints an error message

def write(sock, msg):
    print "Sending",msg #and send it
    sock.sendall(msg)

def setup_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create IPv4, TCP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse port quickly 
    print "Connecting to",SERVER,"Port",PORT,"as",NICK
    sock.connect((SERVER,PORT))
    sock.setblocking(False)
#    print "Waiting a few seconds..." #this should only be sent once the server replies with stuff
#    time.sleep(5)
    print "Sending nickname request to server..."
    sock.send("NICK "+NICK+"\nUSER "+NICK+" 0 * "+NICK+"\n")
    return sock

def main(): 
    # Create 'sock', a socket object
    pyg_textsurfaces = []
    user_message = ""
    server_message = ""
    sock = setup_sock()

    #set up pygame interface
    screen = pygame.display.set_mode((1080,640)) #width, height of canvas
   
    #initialize the rectangles
    rect = pygame.draw.rect(screen,(255,155,55),(0,0,10,10)) #initializes rectangle (horiz,vert,width,heigh)
    rect.bottomleft = (0,550) #moves bottom-left corner of rectangle to new coordinate (horiz, vert)

    #rect2 = pygame.draw.rect(screen,(153,33,255),(0,0,10,10))
    #rect2.bottomleft = (0,90)

    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN: #if the user depresses a key
                if event.key == K_RETURN: #if the enter key is depressed (event.key == 13) 
                    user_message = str(user_message) #not sure if this line is necessary
                    parsed_message = parse(user_message)                
                    if parsed_message.valid_msgtuple[0] == True: #if message is valid
                        parsed_message.format_as_IRC() #add a .IRC_formatted_msg attribute, the message formatted as IRC message....
                        write(sock,parsed_message.IRC_formatted_msg)
                        pyg_textsurfaces.append(makenew_pyg_textsurface(str(NICK+": "+parsed_message.parsed_msg[2]+" "+parsed_message.parsed_msg[3]),FONTSIZE))
                        user_message = "" #this line leaves a one-character artifact, not sure why
                    if parsed_message.valid_msgtuple[0] == False:
                        pyg_textsurfaces.append(makenew_pyg_textsurface('Error: '+str(parsed_message.valid_msgtuple[1]),FONTSIZE))
                    event.unicode = None #will this fix the problem???    
                elif event.key == K_BACKSPACE:
                    user_message = user_message[:-1]
                else:
                    user_message += event.unicode

        readable, writeable, error = select.select([sock], [sock], [sock], 0)
        
        screen.fill((0,0,0)) #puts in a black background, so that you only see the most recently drawn objects
        
        unsent_user_message = makenew_pyg_textsurface(user_message,FONTSIZE)
                
        if readable:
            server_message = sock.recv(1024)
            server_message = Message((server_message,'server')) #makes server message string a Message object
            server_message.parse_msg()
            pyg_textsurfaces.append(makenew_pyg_textsurface(server_message.parsed_msg[2]+": "+server_message.parsed_msg[3],FONTSIZE)) #just the new message

        rect = pygame.draw.rect(screen,(255,155,55),rect) #this re-draws the rectangle (now that it's been moved)

        screen.blit(unsent_user_message,(0,540)) #screen has method blit, which can put, in this case, textsurface onto rect
        
        offset = 10
        for block in pyg_textsurfaces[-NUM_LINES_ON_SCREEN:]:
            offset += FONTSIZE
            screen.blit(block,(0,offset))

        screen.blit(unsent_user_message,(0,540))

        pygame.display.flip() #updates display

if __name__ == '__main__':
    pygame.init()
    main()