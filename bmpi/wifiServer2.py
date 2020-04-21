#!/usr/bin/python3
import socket
import struct
import time
import json
#import threading
from email.parser import BytesParser
#from queue import Queue, Empty
from bmpi import serialDriver, htmlParse
from flask import request
import chardet
import io
from io import StringIO
from multiporcessing import Process, Pipe


debug = True
interface = "wlan0"

class wifiServer():
 
    def __init__(self):
        #self.serial_input_queue = Queue()
        #self.serial_output_queue = Queue()
        self.parent_p, self.child_p = Pipe()
        
        #self.log_input_queue = Queue()
        self.htmlData = ""
        self.requestUri = str()
        self.recipeCount = int()

        #self.serial_bg = serialDriver.SerialThread(self, self.serial_input_queue, self.serial_output_queue)
        #self.serial_bg.daemon = True
        #self.serial_bg.start()
        self.Process(target=serialDriver2.SerialProcess, args=((self, self.child_p),)).start()
        self.ipaddr =  self.getIp()
        self.parser = htmlParse.parser()

        #self.t = threading.Timer(10.0, self.pollStatus)
        #self.t.start()

    
    #read line from serial queue as bytes
    def receiveFromSerial(self):
        while True:
            if parent_p.poll():
        try:  serialData = self.parent_p.recv()

            print('no output yet')
        else:
            #takes bytes with escapebytes and replaces it with \r\n
            serialData = serialData.replace(b'\xdb\xdc', b'\r\n')
            serialData = serialData.decode('ISO-8859-1')
            cmd = serialData.rstrip('\r\n')

            #'switch' case for what command we need to send to BM 
            if '=' in cmd: # can have a = in the params. need to fix that
                cmd, params = serialData.split('=', 1)
                func = self.command(cmd)
                func(params)
            else:
                #select function based on AT command
                func = self.command(cmd)
                func()


    #TODO receive params and send them to the functions too
    #selects the command taht needs to be sent to BM
    def command(self, command):
        return {
            'at+rsi_mac?': self.send_mac,
            'at+rsi_fwversion?': self.send_fw,
            'at+rsi_reset': self.send_ok,
            'at+rsi_band': self.select_band,
            'at+rsi_init': self.init,
            'at+rsi_scan': self.ssid_scan,
            'at+rsi_network': self.infra_mode,
            'at+rsi_authmode': self.auth_mode,
            'at+rsi_join': self.join_ssid,
            'at+rsi_ipconf': self.config_ip,
            'at+rsi_rssi?': self.rssi,
            'at+rsi_ltcp': self.open_socket,
            'at+rsi_cls': self.close_socket,
            'at+rsi_snd': self.save_data
            #'AT+RSI_READ': self.send_data,
        }.get(command, lambda: "Invalid command")
  
    #save html data from BM
    def save_data(self, data):
        #remove unwanted data and headers
        data = data.replace('1,0,0,0,', '')
        #save html data to string
        self.htmlData += data
        #send OK to BM to ack the request
        self.sendToSerial(b'OK\r\n')

    #parse saved data when we get a close socket from BM
    #TODO html data might not have headers. need to handle that
    def close_socket(self, params):
        if self.htmlData:
            #parse headers
            val = ""
            headers, body = self.htmlData.split('\r\n\r\n', 1)
            code, headers = headers.split('\r\n', 1) 
            headers = headers.encode()
            headers = BytesParser().parsebytes(headers)
            val = headers['Content-Type']
            #if headers contain text/html send to uiQueue
            if 'text/html' in val:
                #parse with html parser so we can remove the doc type?
                self.sendToLogQueue(body)
            self.htmlData = ""
        self.sendToSerial(b'OK\r\n')

    def pollStatus(self):
        t = threading.Timer(15.0, self.pollStatus)
        t.start()
        self.send_data("/bm.html")
        print("poll")




    #sends json data to log queue
    def sendToLogQueue(self, data):
        #remove newline and tab
        data = data.replace('\r\n', '')
        #data = data.replace('\t', '')
        self.log_input_queue.put(data)

    ##functions to setup the wifi of the bmpi
    #192.168.11.140: \xc0\xa8\x01\x8c

    #get ip address
    def getIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255",1))
        ip = s.getsockname()[0]
        s.close()
        print("ip is :" + ip)
        return ip

    #Read the default gateway from /proc
    def get_gw():
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
                
                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
    

    #sends OK to the BM
    def send_ok(self):
        self.sendToSerial(b'OK\r\n')
    
    def send_mac(self):
        self.sendToSerial(b'OK b8 27 eb bd 63 18 \r\n')
    
    def send_fw(self):
        self.sendToSerial(b'OK 4.8.4\r\n')
    
    #first command to configure band. 0 = 2.4Ghz. 1 = 5 GHz
    def select_band(self, band):
        self.sendToSerial(b'OK\r\n')

    #executed after selecting the band
    def init(self):
        self.sendToSerial(b'OK\r\n')
    
    #SSID of the Access Point, returned in ASCII. 32 byte stream, filler bytes
    #(0x00) are put to complete 32 bytes, if actual SSID length is not 32 bytes.
    
    #Security Mode of the scanned Access Point, returned in hexadecimal, 1 byte.
    #0x00 – Open (No Security)
    #0x01 – WPA 1
    #0x02 – WPA2
    #0x03 – WEP

    #return the SSID list
    def ssid_scan(self, params):
        #found a sid
        if ',' in params:
            channel, ssid = params.split(',')
            ssid = ssid.lstrip()
            #TODO send correct ssid
        self.ssid = b'OK Data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x14\r\n'
        self.sendToSerial(self.ssid)
    
    #configures infrastructure mode
    def infra_mode(self, params):
        self.sendToSerial(b'OK\r\n')
    
    #configures the auth mode
    def auth_mode(self, params):
        self.sendToSerial(b'OK\r\n')
    
    #SSID name, TxRate, TxPower
    def join_ssid(self, params):
        ssid, txRate, txPower = params.split(',')
        ssid = ssid.lstrip()
        self.sendToSerial(b'OK\r\n')
    
    #DHCP_MODE, IP address, SUBNET, GATEWAY
    def config_ip(self, params):
        #params dont matter. just send it back the rpi ip address, subnet and gateway
        self.dhcp = b'OK\xb8\x27\xeb\xbd\x63\x18\xac\x10\x14.\xff\xff\xff\x00\xac\x10\x14\xfe\r\n'
        self.sendToSerial(self.dhcp)
    
    #Absolute value of the RSSI information, returned in hexadecimal, 1 byte. 
    #RSSI information indicates the signal strength of the Access Point.
    def rssi(self):
        rssi = b'OK\x1f\r\n' #iwlist scan
        self.sendToSerial(rssi)
    
    def open_socket(self, params):
        #params should always be 80
        socket = b'OK\x01\r\n'
        self.sendToSerial(socket)

    #send keypress to BM
    def send_data(self, data):
        value = b'AT+RSI_READ\x01\x27\x00GET '+ data.encode('ascii') + b' HTTP/1.1 Host: 172.16.20.48\r\n'
        self.sendToSerial(value)        

    def sendToSerial(self, payload):
        #print(b'send to BM: ' + payload)
        self.parent_p.send(payload)
















    #TODO clean up the list > dict > json.
    #TODO do we need the if /bmtxt? we should be able to just receeive anything and depending on the AT command, parse it properly. when the stream is finished, it will close. fill up a list and when we get close, parse the list
    def parse_response(self, serialData):
        if "/bm.txt?" in self.requestUri and 'at+rsi_snd' in serialData:
            bmpi = {}
            print('parsing: ' + serialData)
            headers, body = serialData.split('\r\n\r\n', 1)
            versionDate, serialNum, state = body.split(';', 2)
            version,month,day,year = versionDate.split(" ")
            request_line, headers_alone = headers.split('\r\n', 1) #request_line will have 200OK
            #encode to bytes so we can parse the headers_alone
            headers_alone = headers_alone.encode()
            headers = BytesParser().parsebytes(headers_alone)

            bmpi['ipaddr'] = self.ipaddr
            bmpi['version'] = version
            bmpi["date"] = (day + " " + month + " " + year)
            bmpi['serialnum'] = serialNum
            items = state.split("X")
            bmpi["clock"] = items[1]
            bmpi["unit"] = items[2]
            bmpi["unknown"] = items[3]
            bmpi["target_temp"] = items[4]
            bmpi["actual_temp"] = items[5]
            bmpi["target_time"] = items[6]
            bmpi["elapsed_time"] = items[7] 
            jsonData = json.dumps(bmpi)
            #print(jsonData)
            self.sendToLogQueue(jsonData)
            #clean up
            self.requestUri = ""
        #recipe url. This will come in 2 seperate responses from the BM
        elif "/rz.txt" in self.requestUri and 'at+rsi_snd' in serialData:
            #http list is empty so it must be the first response from BM
            if not self.http_list:
                print("1st response for rz")
                headers, body = serialData.split('\r\n\r\n', 1)
                versionDate, serialNum, self.recipeCount = body.split(';') 
                self.http_list.extend((headers, versionDate, serialNum))
                request_line, headers_alone = self.http_list[0].split('\r\n', 1) #request_line will have 200OK
                #encode to bytes so we can parse the headers_alone
                headers_alone = headers_alone.encode()
                headers = BytesParser().parsebytes(headers_alone)

            #first response has been added to list
            else:
                bmpi = {}
                print("2nd response for rz")
                recipes = serialData.split('\r\n', int(self.recipeCount))
                #remove at+rsi_snd=1,0,0,0
                recipes = recipes[1:]
                self.http_list.append(recipes)
                bmpi['version'] = self.http_list[1]
                bmpi['serialnum'] = self.http_list[2]
                bmpi['rz'] = self.http_list[3]
                jsonData = json.dumps(bmpi)
                self.sendToLogQueue(jsonData)
                #clean up
                self.requestUri = ""
                self.recipeCount = None
                self.http_list.clear()
        #AT command

        #TODO fix this with the new function format
        else:
            #remove EOL characters
            serialData.rstrip()
            data = {"at_command": serialData}
            jsonData = json.dumps(data)
            #self.sendToLogQueue(jsonData)




#ui.txt - returns headers and serial number
#bm.html
#bm.txt?k=1 presses key and returns some data such as SN and recipe
#index.html - retuns a JS redirect to speidel
#start.bmp
#https://www.myspeidel.com/steuerung/index.php?l=1&i=172.16.20.96

#settings does not work on wifi module
#recipe does not work on wifi module
#recipe upload on wifi module
# recipe sync removes all and adds all



#bm.txt
#[b'at+rsi_snd=1,0,0,0,HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Type: text/plain\r\nCache-Control: no-cache\r\nAccess-Control-Allow-Origin: *
# \r\n\r\n
# 
# V1.1.26-4 Feb 19 2018; version_date
# 0004A30B003F56EB; serial_num
# 1X
# 12:50X
# CX
# 8101X
# 630X
# 999.5X
# 1800X
# 22164X
# 0X0X0X0XADUSXphX000X0X78X10X60X100X60X20X0X0X0X0.Recipe 4\r\n'] state

#rz.txt
#b'at+rsi_snd=1,0,0,0,HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Type: text/plain\r\nCache-Control: no-cache\r\nAccess-Control-Allow-Origin: *
# \r\n\r\n
# 
# V1.1.26-4 Feb 19 2018;
# 0004A30B003F56EB;4\r\n'


#b'at+rsi_snd=1,0,0,0,\r\n
# 0X52X63X30X70X30X78X15X81X0X85X0X60X100X60X10X0X0X0X0.Pale ale\r\n
# 1X65X65X60X75X10X75X0X78X0X78X0X60X100X40X25X10X0X0X0.IPA     \r\n
# 2X60X65X60X75X10X78X5X78X0X78X0X60X100X40X0X0X0X0X0.Blck IPA\r\n
# 3X65X66X60X66X0X73X0X78X0X78X10X60X100X60X20X0X0X0X0.Recipe 4\r\n'

