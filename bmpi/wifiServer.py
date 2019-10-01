#!/usr/bin/python3
import socket
import struct
from queue import Queue, Empty
from bmpi import serialDriver, logger
import time



interface = "wlan0"

class wifiServer():
 
    def __init__(self, logger):
        self.logger = logger
        self.input_queue = Queue()
        self.output_queue = Queue()

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


    #removes null bytes and formats for SSE
    #returns string
    def format_for_sse(payload):
        payload = payload.replace('\x00', '')
        payload = "data: "+payload+"\n\n"
        return payload

    #takes a string with escapebytes and replaces it with \r\n
    def byteUnstuff(self, payload):
        payload = payload.replace(b'\xdb\xdc', b'\r\n')
        return payload.replace(b'\x00', b'')
    
    # read line from queue as bytes
    def receiveFromSerial(self):
    
        try:  payload = self.output_queue.get_nowait()
        except Empty:
            print('no output yet')
        else:
            #remove escape and null bytes
            payload = self.byteUnstuff(payload)
            #remove line feed
            payload = payload.splitlines()[0]
            
            self.command(payload.decode())()
            logger.log('Recv: ', payload.decode('iso-8859-1'))

    
    def sendToSerial(self, payload):
        self.input_queue.put(payload)
        #remove line feed
        payload = payload.splitlines()[0]
        #send to logger
        logger.log('Send: ', payload.decode('iso-8859-1'))
