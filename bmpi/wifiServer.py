#!/usr/bin/python3
import socket
import struct
import time
import json
import threading
from email.parser import BytesParser
from queue import Queue, Empty
from bmpi import serialDriver, htmlParse
from flask import request
import chardet
import io
from io import StringIO

debug = True
interface = "wlan0"

class wifiServer():
 
    def __init__(self):
        threading.Thread.__init__(self)
        self.i_queue = Queue()
        self.o_queue = Queue()

        self.log_input_queue = Queue()
        self.htmlData = ""
        self.requestUri = str()
        self.recipeCount = int()

        self.serial_bg = serialDriver.SerialThread(self, self.i_queue, self.o_queue)
        self.serial_bg.daemon = True
        self.serial_bg.start()
        self.ipaddr =  self.getIp()
        self.parser = htmlParse.parser()
        
        self.wifi_bg = threading.Thread(target=self.receiveFromSerial, args=(self.i_queue, self.o_queue))
        self.wifi_bg.daemon = True
        self.wifi_bg.start()

        #self.t = threading.Timer(10.0, self.pollStatus)
        #self.t.start()

    
    #read line from serial queue as bytes
    def receiveFromSerial(self, i_queue, o_queue):
        while True:
            try:  
                #serialData = self.o_queue.get_nowait()
                serialData = self.o_queue.get()
                print(serialData)
                serialData = serialData.replace(b'\xdb\xdc', b'\r\n')
                serialData = serialData.decode('ISO-8859-1')
                cmd = serialData.rstrip('\r\n')
                #print('output received')
                #'switch' case for what command we need to send to BM 
                if '=' in cmd: # can have a = in the params. need to fix that
                    cmd, params = serialData.split('=', 1)
                    func = self.command(cmd)
                    func(params)
                    #self.sendToSerial(b'OK\r\n')
                else:
                    #select function based on AT command
                    func = self.command(cmd)
                    func()
            except Empty:
                continue


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
        print(b'send to BM: ' + payload)
        self.i_queue.put(payload)






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

