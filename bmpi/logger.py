#!/usr/bin/python3
import json
from queue import Queue, Empty

#logger reads from the logger queue and yields
#ui and terminal receives messages from the logger

logger_input_queue = Queue()
logger_output_queue = Queue()
#class logger():
 
    #def __init__(self):
        #self.logger_input_queue = Queue()
        #self.logger_output_queue = Queue()

def log_message(self, action, message):
    logger_output_queue.put(message)
    #message = message.replace('\x00', '')
    message = "data: "+message+"\n\n"
    print(message)
    payload = message




