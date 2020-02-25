#!/usr/bin/python3
import socket
import struct
import time
import json
from queue import Queue, Empty
from bmpi import serialDriver
from flask import request



debug = True
interface = "wlan0"
#log_input_queue = Queue()
http_list = list()
#requestUri = None

class wifiServer():
 
    def __init__(self):
        self.serial_input_queue = Queue()
        self.serial_output_queue = Queue()

        self.log_input_queue = Queue()
        self.http_list = list()
        self.requestUri = str()

        self.serial_bg = serialDriver.SerialThread(self, self.serial_input_queue, self.serial_output_queue)
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
        #serial_input_queue.put(b'OK\r\n')
    
    def send_mac(self):
        self.sendToSerial(b'OK b8 27 eb bd 63 18 \r\n')
        #serial_input_queue.put(b'OK b8 27 eb bd 63 18 \r\n')
    
    def send_fw(self):
        self.sendToSerial(b'OK 4.8.4\r\n')
        #serial_input_queue.put(b'OK 4.8.4\r\n')
    
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


    def sendToSerial(self, payload):
        self.serial_input_queue.put(payload)

    #sends json data to log queue
    def sendToLogQueue(self, jsonData):
        print("sending json to log queue:")
        print(jsonData)
        self.log_input_queue.put(jsonData)

    #read line from queue as bytes
    def receiveFromSerial(self):
        try:  serialData = self.serial_output_queue.get_nowait()
        except Empty:
            print('no output yet')
        else:
            #takes bytes with escapebytes and replaces it with \r\n
            serialData = serialData.replace(b'\xdb\xdc', b'\r\n')
            #decode from bytes to str
            serialData = serialData.decode()
            #send AT command back to BM
            self.command(serialData.rstrip('\r\n'))()
            #process message and send to log queue
            jsonData = self.decode_response2(serialData)
            #send to log queue as json
            self.sendToLogQueue(jsonData)

    #creates a list from the serial data so we can process it and return json
    #if its a AT command return json
    #TODO clean up the list > dict > json
    def decode_response2(self, serialData):
        print ("requestUri is: " + self.requestUri)
        #button push 
        if  "/bm.txt?" in self.requestUri and 'at+rsi_snd' in serialData:
            self.http_list.append(serialData)
            self.requestUri = ""
            # process list into json
            jsonData = self.decode(self.http_list)
            return jsonData
        #recipe url
        if "/rz.txt" in self.requestUri and 'at+rsi_snd' in serialData:
            #need to have 2 entries in http_list
            if len(self.http_list) < 2:
                self.http_list.append(serialData)
            else:
                self.requestUri = ""
                jsonData = decode(self.http_list)
                return jsonData
        #AT command
        else:
            #remove EOL characters
            serialData.rstrip()
            data = {"at_command": serialData}
            return json.dumps(data)

    #dont need to pass httplist since its global
    def decode2(self, httpList):
        #recipe
        if len(httpList) == 2:
            pass
        #bm.txt
        else:
            pass
        self.http_list.clear()
        return json.dumps(bmpi)

    #extracts the status from the list
    #accepts list, returns json
    def decode(self, httpList):
        bmpi = {}
        headers = {}
        for i in httpList:
            resp = i.split("\r\n\r\n")
            body = resp[-1:]
            fields = resp[:-1]
            #contains headers it means its the /bm.txt
            if len(fields) > 0:
                fields = fields[0].split("\r\n")
                fields = fields[1:] #ignore the HTTP/1.1 200 OK
                for field in fields:
                    key,value = field.split(':')#split each line by http field name and value     
                    headers[key] = value
                #extract serialnumber date and status. last entry is bmpi status
                body = body[0].split("\r\n")
                body = body[:-1]           
                version_date, serialnum, state = body[0].split(";")
                version,month,day,year = version_date.split(" ")
                items = state.split("X")
                bmpi['version'] = version
                bmpi["date"] = (day + " " + month + " " + year)
                bmpi["serialnum"] = serialnum
                bmpi["clock"] = items[1]
                bmpi["unit"] = items[2]
                bmpi["unknown3"] = items[3]
                bmpi["target_temp"] = items[4]
                bmpi["actual_temp"] = items[5]
                bmpi["target_time"] = items[6]
                bmpi["elapsed_time"] = items[7] 

            self.http_list.clear()
            return json.dumps(bmpi)

    #def decode_response(self, payload):
    #    #print("decoding: " + payload)
    #    headers = {}
    #    bmpi = {}
    #    #if http response add it to list (destroy list after all http responses are delt with)
    #    #is a http response so append it to the list
    #    if 'at+rsi_snd' in payload:
    #        print("http response")
    #        print(payload)      
    #        http_list.append(payload)
    #    #payload is not a http response (end of the http responses and list is full)
    #    else:
    #        #if list is empty it means the previous payload was not http response
    #        #we should decode this response as an AT command
    #        if not http_list:
    #            print("AT Command")
    #            print(payload)
    #            payload.rstrip('\r\n')
    #            bmpi['at_command'] = payload
#
    #        #if the list is not empty, it means previous payload was a http response
    #        #we need to handle the http list
    #        else:
    #            #list is full so decode response
    #            print("http_list")
    #            print(http_list)
    #            for i in http_list:
    #                resp = i.split("\r\n\r\n")
    #                body = resp[-1:]
    #                fields = resp[:-1]
    #                #contains headers it means its the status
    #                if len(fields) > 0:
    #                    fields = fields[0].split("\r\n")
    #                    fields = fields[1:] #ignore the HTTP/1.1 200 OK
    #                    for field in fields:
    #                        key,value = field.split(':')#split each line by http field name and value     
    #                        headers[key] = value
    #                    #extract serialnumber date and status. last entry is bmpi status
    #                    body = body[0].split("\r\n")
    #                    body = body[:-1]           
    #                    version_date, serialnum, state = body[0].split(";")
    #                    version,month,day,year = version_date.split(" ")
    #                    items = state.split("X")
    #                    bmpi['version'] = version
    #                    bmpi["date"] = (day + " " + month + " " + year)
    #                    bmpi["serialnum"] = serialnum
    #                    bmpi["clock"] = items[1]
    #                    bmpi["unit"] = items[2]
    #                    bmpi["unknown3"] = items[3]
    #                    bmpi["target_temp"] = items[4]
    #                    bmpi["actual_temp"] = items[5]
    #                    bmpi["target_time"] = items[6]
    #                    bmpi["elapsed_time"] = items[7]
#
    #    http_list.clear()
    #    return json.dumps(bmpi)