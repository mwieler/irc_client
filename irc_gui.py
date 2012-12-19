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
NUM_LINES_ON_SCREEN = 21
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
        self.valid_msgtuple = (None,"Message has not yet been parsed by parse_message")
        self.IRC_formatted_msg = None
    
    def parse_msg(self): #returns ((prefix,command,args,trailer),(parseable_msg,why_unparseable)
        if self.source == 'user':
            if len(self.original_msg.split(' ')) < 2:
                self.valid_msgtuple = (False, "usage: /command argument trailer")
            elif not IRC_CMDS.get(self.original_msg.split(' ')[0],None): #returns None if command key not found in IRC_CMDS dict
                self.valid_msgtuple = (False,"User command not recognized. Valid IRC commands include:",print_dict())
            else:
                self.valid_msgtuple = (True, None) #assume that if I haven't caught an error in the if stmts above, it's valid
                command, args_and_trailer = self.original_msg.split(' ',1)
                if len(args_and_trailer.split(' ')) > 1:
                    args, trailer = args_and_trailer.split(' ',1) #for now, only one-argument functions can be handled
                elif len(args_and_trailer.split(' ')) == 1:
                    args, trailer = args_and_trailer, '' #must be '', can't be None, bc later trailer is concatenated
                #this is wher eyou clean up user messages
                args = args.strip()
                self.valid_msgtuple = (True, None)
                self.prefix = ''
                self.command = command
                self.args = args
                self.trailer = trailer

        elif self.source == 'server':
            if self.original_msg[0] == ':': 
                prefix, not_prefix = self.original_msg[1:].split(' ',1) #splits message into pre first-space and post first-space
            elif self.original_msg[0] != ':': #this statement is redundantly explicit, for clarity
                prefix, not_prefix = None, self.original_msg
            command_and_args, trailer = not_prefix.split(':',1)
            if ' ' in command_and_args:
                command, args = command_and_args.split(' ',1) #returns '' for args if no args exist
                args = args.rstrip() #remove trailing whitespace. Should args be a space-delimited string or a list?
            else:
                command = command_and_args
                args = ''
            #this is where you clean up server messages
            if prefix: #kind of a hack. Resolve the prefix/no prefix issue
                if '!' in prefix: #if there's an exclamation point in the prefix...
                    prefix = prefix[:prefix.index('!')] #truncate it beginning with the exclamation point
            trailer = trailer.replace('\r','')
            trailer = trailer.replace('\n','')
            self.valid_msgtuple = (True, None)
            self.prefix = prefix
            self.command = command
            self.args = args
            self.trailer = trailer
        else:
           self.valid_msgtuple = (False, "Sorry, parse_msg couldn't parse the message")

    def add_IRC_msg_attr(self): #check message is valid prior to running
        #the message into its constituent parts (as defined by the IRC protocol)
        if self.prefix:
            self.IRC_formatted_msg = ":"+self.prefix+" "+IRC_CMDS[self.command]+" "+self.args+" :"+self.trailer+"\n" #the \n is necessary for the IRC server
        if not self.prefix:
            self.IRC_formatted_msg = IRC_CMDS[self.command]+" "+self.args+" :"+self.trailer+"\n" #the \n is necessary for the IRC server

def read(sock): #listens for and prints out the received message
    while True:
        msg = sock.recv(1024)

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
    unsent_string = "" #this is the object the user builds up before hitting 'return.'
    # After user hits 'return', the unsent_string is converted into a Message_object
    server_message = ""
    sock = setup_sock()

    #set up pygame interface
    screen = pygame.display.set_mode((1080,640)) #width, height of canvas
   
    #initialize the rectangles
    rect = pygame.draw.rect(screen,(255,155,55),(0,0,10,10)) #initializes rectangle (horiz,vert,width,heigh)
    rect.bottomleft = (0,550) #moves bottom-left corner of rectangle to new coordinate (horiz, vert)

    #rect2 = pygame.draw.rect(screen,(153,33,255),(0,0,10,10))
    #rect2.bottomleft = (0,90)

    trueloopcounter = 0
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN: #if the user depresses a key
                if event.key == K_RETURN: #if the enter key is depressed (event.key == 13) 
                    unsent_string = str(unsent_string) #not sure if this line is necessary
                    user_message_object = Message((unsent_string,'user'))
                    user_message_object.parse_msg()
                    if user_message_object.valid_msgtuple[0] == True: #if message is valid
                        user_message_object.add_IRC_msg_attr() #add a .IRC_formatted_msg attribute, the message formatted as IRC message....
                        write(sock,user_message_object.IRC_formatted_msg)
                        pyg_textsurfaces.append(makenew_pyg_textsurface(str("(to "+user_message_object.args+"): "+user_message_object.trailer),FONTSIZE))
                        unsent_string = '' #this line leaves a one-character artifact, not sure why
                    if user_message_object.valid_msgtuple[0] == False:
                        pyg_textsurfaces.append(makenew_pyg_textsurface('Error: '+str(user_message_object.valid_msgtuple[1]),FONTSIZE))
                elif event.key == K_BACKSPACE:
                    unsent_string = unsent_string[:-1]
                else:
                    unsent_string += event.unicode

        readable, writeable, error = select.select([sock], [sock], [sock], 0)
        
        screen.fill((0,0,0)) #puts in a black background, so that you only see the most recently drawn objects
        
        unsent_user_message = makenew_pyg_textsurface(str(unsent_string),FONTSIZE) #coerce user_message to string earlier?
                
        if readable:
            server_message = sock.recv(1024)
            server_message = Message((server_message,'server')) #makes server message string a Message object
            server_message.parse_msg()
            try: #try to print the prefix & trailer
                pyg_textsurfaces.append(makenew_pyg_textsurface(server_message.prefix+": "+server_message.trailer,FONTSIZE)) #just the new message
            except: #if that doesn't work, print just the trailer
                pyg_textsurfaces.append(makenew_pyg_textsurface(server_message.trailer,FONTSIZE))
            # this will need to be tweaked
        rect = pygame.draw.rect(screen,(255,155,55),rect) #this re-draws the rectangle (now that it's been moved)
        
        offset = 10
        for block in pyg_textsurfaces[-NUM_LINES_ON_SCREEN:]:
            offset += FONTSIZE
            screen.blit(block,(0,offset))

        screen.blit(unsent_user_message,(0,550))

        pygame.display.flip() #updates display
        print 'TICK '+str(trueloopcounter)
        trueloopcounter += 1

if __name__ == '__main__':
    pygame.init()
    main()