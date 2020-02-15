#!/usr/bin/python3

payload = ""


class logger():
 
    def __init__(self):
        self.payload = ""
        #self.input_queue = Queue()
        #self.output_queue = Queue()
        #self.http_list = list()

        #self.serial_bg = serialDriver.SerialThread(self, self.input_queue, self.output_queue)
        #self.serial_bg.daemon = True
        #self.serial_bg.start()

    def log(self, action, message):
        global payload
        print('message')
        print(message)
        message = message.replace('\x00', '')
        message = "data: "+message+"\n\n"
        message = message.replace('\x00', '')
        payload = message

    def sse_event(self):
        global payload
        yield payload



#def format_for_sse(payload):
    #global payload = payload.replace('\x00', '')
    #payload = "data: "+payload+"\n\n"
    #yield payload


# logger will send to the terminal and ui pages for sse

#both pages have a function that calls a fucntion here
#the function here yields

