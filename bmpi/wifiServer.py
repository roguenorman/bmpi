#!/usr/bin/python3
import socket
import struct
import time
import json
from email.parser import BytesParser
from queue import Queue, Empty
from bmpi import serialDriver
from flask import request
import chardet

import numpy as np
import binascii
from PIL import Image
import io
from io import StringIO

debug = True
interface = "wlan0"
http_list = list()

class wifiServer():
 
    def __init__(self):
        self.serial_input_queue = Queue()
        self.serial_output_queue = Queue()

        self.log_input_queue = Queue()
        self.http_list = list()
        self.requestUri = str()
        self.recipeCount = int()

        self.serial_bg = serialDriver.SerialThread(self, self.serial_input_queue, self.serial_output_queue)
        self.serial_bg.daemon = True
        self.serial_bg.start()
        self.ipaddr =  self.getIp()


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
        #serial_input_queue.put(b'OK\r\n')
    
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
        
#    def ssid_scan(self):
#        self.ssid = b'OK Data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x14\r\n'
#        self.sendToSerial(self.ssid)

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

    
    #TODO receive params and send them to the functions too
    def command(self, command):
        return {
            'at+rsi_mac?': self.send_mac,
            'at+rsi_fwversion?': self.send_fw,
            'at+rsi_reset': self.send_ok,
            'at+rsi_band': self.select_band,
            'at+rsi_init': self.init,
            'at+rsi_scan': self.ssid_scan,
            #'at+rsi_scan': self.data_scan,
            'at+rsi_network': self.infra_mode,
            'at+rsi_authmode': self.auth_mode,
            'at+rsi_join': self.join_ssid,
            'at+rsi_ipconf': self.config_ip,
            'at+rsi_rssi?': self.rssi,
            'at+rsi_ltcp': self.open_socket,
            'at+rsi_cls': self.close_socket,
            'at+rsi_snd': self.save_data,
        }.get(command, lambda: "Invalid command")

    def sendToSerial(self, payload):
        self.serial_input_queue.put(payload)

    #sends json data to log queue
    def sendToLogQueue(self, jsonData):
        self.log_input_queue.put(jsonData)

    #read line from queue as bytes
    def receiveFromSerial(self):
        try:  serialData = self.serial_output_queue.get_nowait()
        except Empty:
            print('no output yet')
        else:
            #takes bytes with escapebytes and replaces it with \r\n
            serialData = serialData.replace(b'\xdb\xdc', b'\r\n')
            serialData = serialData.decode('iso-8859-1')
            cmd = serialData.rstrip('\r\n')
            #command has parameters
            if '=' in cmd: # can have a = in the params. need ot fix that
                cmd, params = serialData.split('=', 1)
                func = self.command(cmd)
                func(params)
            else:
                #select function based on AT command
                func = self.command(cmd)
                func()


    #save data from BM
    def save_data(self, data):
        #remove unwanted 
        data = data.replace('1,0,0,0,', '')
        #save the data into a list
        self.http_list.append(data)
        self.sendToSerial(b'OK\r\n')
        

    #parse saved data when we get a close socket
    def close_socket(self, params):
        #parse list can we ues html parser?
        #another command has caused a close socket
        if self.http_list:
            html = ''
            html = html.join(self.http_list)
            html = html
            print(html)
            #print(self.http_list)
            self.http_list.clear()
        self.sendToSerial(b'OK\r\n')


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

    def parse_bmp(self, serialData):
        print("bmp")
        if "bmp" in self.requestUri:
            if b'at+rsi_snd' in serialData:
                #serialData.decode('iso-8859-1')
                #print(serialData)
                header, bmp = serialData.split(b'\r\n\r\n', 1)
                #print(bmp)
                bmp = bmp.rstrip()
                #print('smallhex')
                hex = bmp.hex()
                print(bmp)
                #Image.frombytes()


                #img = Image.open(io.BytesIO(bytearray.fromhex(hex)), 'r') # 1 L P RGB
                #img.save('base.bmp')
                #print(img)
                #num_array = np.asarray(bmp)
                #print(num_array)
                #binascii.unhexlify(bmp) # return binary data

                #is it base64 encoded???

            
            #else:
            #    if b'at+rsi_snd' in serialData:
            #        print("2nd response for bmp")
            #        bmp = serialData.split('\r\n')
            #        print("bmp")
            #        print(serialData)
            #        first, bmp = serialData.split('\r\n\r\n', 1)
            #        self.http_list.extend((first, bmp))
            #        array2 = np.asarray(bmp)
            #        self.requestUri = ""
        #return jsonData


#ui.txt - returns headers and serial number
#bm.html
#bm.txt?k=1 presses key and returns some data such as SN and recipe
#index.html - retuns a JS redirect to spidel
#start.bmp
#https://www.myspeidel.com/steuerung/index.php?l=1&i=172.16.20.96

#settings doesn work on wifi module
#recipe does not work on wifi module
#recipe uoload on wifi module
# recipe sync removes all and adds all

    #decode the http response into json and send to log queue
    #list will have 4 entires
#    def decode_http(self):
#        bmpi = {}
#        #print(self.http_list)
#        request_line, headers_alone = self.http_list[0].split('\r\n', 1) #request_line will have 200OK
#        #encode to bytes so we can parse the headers_alone
#        headers_alone = headers_alone.encode()
#        headers = BytesParser().parsebytes(headers_alone)
#        bmpi['version'] = self.http_list[1]
#        bmpi['serialnum'] = self.http_list[2]
#        if "/bm.txt?" in self.requestUri:
#            bmpi['state'] = self.http_list[3]
#        elif "/rz.txt" in self.requestUri:
#            bmpi['rz'] = self.http_list[3]
#        #print(bmpi)
#        #clean up 
#        self.requestUri = ""
#        self.http_list.clear()
#        return json.dumps(bmpi)

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



#    #extracts the status from the list
#    #accepts list, returns json
#    def decode(self, httpList):
#        bmpi = {}
#        headers = {}
#        for i in httpList:
#            resp = i.split("\r\n\r\n")
#            body = resp[-1:]
#            fields = resp[:-1]
#            #contains headers it means its the /bm.txt
#            if len(fields) > 0:
#                fields = fields[0].split("\r\n")
#                fields = fields[1:] #ignore the HTTP/1.1 200 OK
#                for field in fields:
#                    key,value = field.split(':')#split each line by http field name and value     
#                    headers[key] = value
#                #extract serialnumber date and status. last entry is bmpi status
#                body = body[0].split("\r\n")
#                body = body[:-1]           
#                version_date, serialnum, state = body[0].split(";")
#                version,month,day,year = version_date.split(" ")
#                items = state.split("X")
#                bmpi['version'] = version
#                bmpi["date"] = (day + " " + month + " " + year)
#                bmpi["serialnum"] = serialnum
#                bmpi["clock"] = items[1]
#                bmpi["unit"] = items[2]
#                bmpi["unknown3"] = items[3]
#                bmpi["target_temp"] = items[4]
#                bmpi["actual_temp"] = items[5]
#                bmpi["target_time"] = items[6]
#                bmpi["elapsed_time"] = items[7] 
#
#            self.http_list.clear()
#            return json.dumps(bmpi)
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


#        def command(self, command):
#        return {
#            'at+rsi_mac?': self.send_mac,
#            'at+rsi_fwversion?': self.send_fw,
#            'at+rsi_reset': self.send_ok,
#            'at+rsi_band=0': self.select_band,
#            'at+rsi_init': self.init,
#            'at+rsi_scan=0': self.ssid_scan,
#            'at+rsi_scan=0, Data': self.data_scan,
#            'at+rsi_network=INFRASTRUCTURE': self.infra_mode,
#            'at+rsi_authmode=4': self.auth_mode,
#            'at+rsi_join= Data,0,2': self.join_ssid,
#            'at+rsi_ipconf=1,0,0': self.config_ip,
#            'at+rsi_rssi?': self.rssi,
#            'at+rsi_ltcp=80': self.open_socket,
#            'at+rsi_cls=1': self.close_socket,
#            'at+rsi_snd=1': self.send_ok
#        }.get(command, lambda: "Invalid command")
