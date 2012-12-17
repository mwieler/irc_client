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
        self.original_msg = '/'+msg #pygame may not recognize / so for now add it in manually
        self.source = source
        self.parsed_msg = None
        self.valid_msgtuple = (None,"Message has not yet been parsed by parse_message")
        self.IRC_formatted_msg = None
    
    def is_msg_in_expected_structure(self):
        #pdb.set_trace()
        if self.original_msg[0] != '/':
            self.valid_msgtuple = (False, "commands must begin with a '/'")
        elif len(self.original_msg.split(' ')) < 2:
            self.valid_msgtuple = (False, "usage: /command argument trailer")
        elif not IRC_CMDS.get(self.original_msg[1:].split(' ')[0],None): #returns None if user_cmd key not found in IRC_CMDS dict
            self.valid_msgtuple = (False,"User command not recognized. Valid IRC commands include:",print_dict())
        else:
            self.valid_msgtuple = (True, None)

    def parse_msg(self): #returns ((prefix,command,args,trailer),(parseable_msg,why_unparseable)
        if self.original_msg[0] == '/' and self.source == 'user' and self.valid_msgtuple[0]: #/ indicates a user command
            user_cmd, args_and_trailer = self.original_msg[1:].split(' ',1)
            #pdb.set_trace()
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
            print "original_msg: ",msg_object.original_msg
            print "parsed_msg: ",msg_object.parsed_msg
            print "\nParsed message:\n", msg_object.parsed_msg #placeholder. eventually display properly formatted message
            print "command and args\n",command_and_args,"\nend of command and args" #debug stmt
            #pdb.set_trace() #debug statement
            command, args = command_and_args.split(' ',1) #returns '' for args if no args exist
            args = args.rstrip() #remove trailing whitespace. Should args be a space-delimited string or a list?
            self.parsed_msg = (prefix, command, args, trailer)
            self.valid_msgtuple = (True, None)
        else:
           self.parsed_msg = None
           #self.valid_msgtuple = (False, "Sorry, parse_msg couldn't handle the message")
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
        #msg_object = Message((msg,'server'))
        print msg #for now, all the client does with servers messages is print them: eventually, it should make sense of them, too, and pong the server
        #pdb.set_trace()
        #msg_object.parse_msg() #we should be able to combine these two lines, or automatically call them
        #msg_object.format_as_IRC() #we should be able to combine these two lines, or automatically call them
        # parseable_msg, why_unparseable = msg_object.valid_msgtuple
        # if parseable_msg:
        #     if msg_object.parsed_msg[1] == 'PING': #clean up - indexing refers to IRC command. make this clear
        #         sock.sendall('PONG '+trailer)
        # if not parseable_msg:
        #     print msg_object.original_msg, "was not parseable. Reason:\n", why_unparseable

def write(sock,msg): #blocks on raw_msg, returns any msg from user
    msgtuple = (msg,'user') #(message,source)
    user_msg = Message(msgtuple)
    user_msg.is_msg_in_expected_structure()
    user_msg.parse_msg()
    if user_msg.valid_msgtuple[0]: #if the message has been parsed successfully...
        user_msg.format_as_IRC() #format it as an IRC message....
        print "Sending",user_msg.IRC_formatted_msg #and send it
        sock.sendall(user_msg.IRC_formatted_msg)
    else:
        print user_msg.valid_msgtuple[1] #make this clearer

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
                    write(sock,user_message)
                    #pdb.set_trace()
                    pyg_textsurfaces.append(makenew_pyg_textsurface(user_message,FONTSIZE))
                    user_message = '' #this line leaves a one-character artifact, not sure why

                if event.key == K_BACKSPACE:
                    user_message = user_message[:-1]
                else:
                    user_message += event.unicode
        
        readable, writeable, error = select.select([sock], [sock], [sock], 0)
        
        screen.fill((0,0,0)) #puts in a black background, so that you only see the most recently drawn objects
        
        unsent_user_message = makenew_pyg_textsurface(user_message,FONTSIZE)
                
        if readable:
            server_message = sock.recv(1024)
            pyg_textsurfaces.append(makenew_pyg_textsurface(server_message,FONTSIZE))

        rect = pygame.draw.rect(screen,(255,155,55),rect) #this re-draws the rectangle (now that it's been moved)

        screen.blit(unsent_user_message,(0,540)) #screen has method blit, which can put, in this case, textsurface onto rect
        
        offset = 10
        for block in pyg_textsurfaces[-10:]:
            offset += FONTSIZE
            screen.blit(block,(0,offset))

        screen.blit(unsent_user_message,(0,540))

        pygame.display.flip() #updates display

if __name__ == '__main__':
    pygame.init()
    main()
    # import inputbox2 as ibox
    # screen = ibox.pygame.display.set_mode((1080,240))
    # if ibox.ask(screen, "input>  "):
    #     print "'%s' was entered." % ibox.ask(screen, "input>  ")