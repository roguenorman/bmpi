#!/usr/bin/python3
import socket
import struct
from queue import Queue, Empty
from bmpi import serialDriver, logger
import time
import json



interface = "wlan0"

class wifiServer():
 
    def __init__(self, logger):
        #dont need self.logger?
        #self.logger = logger
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.http_list = list()

        self.serial_bg = serialDriver.SerialThread(self, self.input_queue, self.output_queue)
        self.serial_bg.daemon = True
        self.serial_bg.start()

    ##functions to setup the wifi of the bmpi
    ##send all data to the serial port in binary
    
    #ipaddr =  socket.inet_aton("172.16.20.48")
    #ipaddr =  socket.inet_aton(get_ip())
    #gw = get_gw()
    #192.168.11.140: \xc0\xa8\x01\x8c
    
    #get ip address
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255",1))
        ip = s.getsockname()[0]
        s.close()
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
        #input_queue.put(b'OK\r\n')
    
    def send_mac(self):
        self.sendToSerial(b'OK b8 27 eb bd 63 18 \r\n')
        #input_queue.put(b'OK b8 27 eb bd 63 18 \r\n')
    
    def send_fw(self):
        self.sendToSerial(b'OK 4.8.4\r\n')
        #input_queue.put(b'OK 4.8.4\r\n')
    
    #first command to configure band. 0 = 2.4Ghz
    def select_band(self):
        self.sendToSerial(b'OK\r\n')
        #send_ok()
    
    #executed after selecting the band
    def init(self):
        self.sendToSerial(b'OK\r\n')
        #send_ok()
    
    
    #SSID of the Access Point, returned in ASCII. 32 byte stream, filler bytes
    #(0x00) are put to complete 32 bytes, if actual SSID length is not 32 bytes.
    
    #Security Mode of the scanned Access Point, returned in hexadecimal, 1 byte.
    #0x00 – Open (No Security)
    #0x01 – WPA 1
    #0x02 – WPA2
    #0x03 – WEP
        
    def ssid_scan(self):
        self.ssid = b'OK Data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x14\r\n'
        self.sendToSerial(self.ssid)

    def data_scan(self):
        self.ssid_scan()
    
    #configures infrastructure mode
    def infra_mode(self):
        self.sendToSerial(b'OK\r\n')
    
    #configures the auth mode
    def auth_mode(self):
        self.sendToSerial(b'OK\r\n')
    
    #SSID name, TxRate, TxPower
    def join_ssid(self):
        self.sendToSerial(b'OK\r\n')
    
    #DHCP_MODE, IP address, SUBNET, GATEWAY
    def config_ip(self):
        self.dhcp = b'OK\xb8\x27\xeb\xbd\x63\x18\xac\x10\x14.\xff\xff\xff\x00\xac\x10\x14\xfe\r\n'
        self.sendToSerial(self.dhcp)
    
    #Absolute value of the RSSI information, returned in hexadecimal, 1 byte. 
    #RSSI information indicates the signal strength of the Access Point.
    def rssi(self):
        rssi = b'OK\x1f\r\n' #iwlist scan
        self.sendToSerial(rssi)
    
    def open_socket(self):
        socket = b'OK\x01\r\n'
        self.sendToSerial(socket)

    def close_socket(self):
        self.sendToSerial(b'OK\r\n')
    
    # TODO split command at '='
    def command(self, command):
        return {
            'at+rsi_mac?': self.send_mac,
            'at+rsi_fwversion?': self.send_fw,
            'at+rsi_reset': self.send_ok,
            'at+rsi_band=0': self.select_band,
            'at+rsi_init': self.init,
            'at+rsi_scan=0': self.ssid_scan,
            'at+rsi_scan=0, Data': self.data_scan,
            'at+rsi_network=INFRASTRUCTURE': self.infra_mode,
            'at+rsi_authmode=4': self.auth_mode,
            'at+rsi_join= Data,0,2': self.join_ssid,
            'at+rsi_ipconf=1,0,0': self.config_ip,
            'at+rsi_rssi?': self.rssi,
            'at+rsi_ltcp=80': self.open_socket,
            'at+rsi_cls=1': self.close_socket
        }.get(command, lambda: "Invalid command")

    #decodes http response from BM. There are 2 types of responses, receipes and status of BM
    def decode_response(self, payload):
        headers = {}
        bmpi = {}
        for i in self.http_list:
            resp = i.split("\r\n\r\n")
           
            body = resp[-1:]
            fields = resp[:-1]
            #contains headers it means its the status
            if len(fields) > 0:

                fields = fields[0].split("\r\n")
                fields = fields[1:] #ignore the HTTP/1.1 200 OK
                for field in fields:
                    key,value = field.split(':')#split each line by http field name and value     
                    headers[key] = value
                #extract serialnumber date and status. last entry is bmpi status
                body = body[0].split("\r\n")
                body = body[:-1]           
                date, serialnum, state = body[0].split(";")

                bmpi["date"] = date
                bmpi["serialnum"] = serialnum
                print(state)

                items = state.split("X")

                bmpi["clock"] = items[1]
                bmpi["unit"] = items[2]
                bmpi["unknown3"] = items[3]
                bmpi["target_temp"] = items[4]
                bmpi["actual_temp"] = items[5]
                bmpi["target_time"] = items[6]
                bmpi["elapsed_time"] = items[7] 

            #recipes
            else:
                recipes = {}
                body = body[0].split("\r\n")
                body = body[1:-1]
                for i in range(len(body)):
                    d = {}
                    value,key = body[i].split('.')
                    d[key] = value
                    recipes[i] = d
                data['recipes'] = recipes

            
        #print(bmpi)
        return(bmpi)

    #removes null bytes and formats for SSE
    #returns string
    def format_for_sse(payload):
        payload = payload.replace('\x00', '')
        payload = "data: "+payload+"\n\n"
        return payload

    #takes bytes with escapebytes and replaces it with \r\n
    def byteUnstuff(self, payload):
        return payload.replace(b'\xdb\xdc', b'\r\n')

    def removeNullBytes():
        return payload.replace(b'\x00', b'')

    
    # read line from queue as bytes
    def receiveFromSerial(self):

        try:  payload = self.output_queue.get_nowait()
        except Empty:
            print('no output yet')
        else:
            #remove escapte bytes
            payload = self.byteUnstuff(payload)
            #decode response
            payload = payload.decode()

            #if http response add it to list (need to destoy list after all http response is delt with)
            if 'at+rsi_snd' in payload:
                self.http_list.append(payload)
            else:
                if not self.http_list:
                    #list is empty
                    pass
                else:
                    #list is full
                    self.decode_response(self.http_list)
                    self.http_list.clear()


            self.command(payload.rstrip('\r\n'))()

            #send to logger
            #logger.log('Recv: ', payload.rstrip('\r\n'))

    
    def sendToSerial(self, payload):
        self.input_queue.put(payload)
        #remove line feed
        payload = payload.splitlines()[0]
        #send to logger
        #logger.log('Send: ', payload.decode('latin-1'))

