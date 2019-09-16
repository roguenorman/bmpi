#!/usr/bin/python3
from bmpi import input_queue, output_queue
import socket
import struct


##functions to setup the wifi of the bmpi
##send all data to the serial port in binary

interface = "wlan0"

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
def send_ok():
    global input_queue
    input_queue.put(b'OK\r\n')
 
#first command to configure band. 0 = 2.4Ghz
def select_band():
    send_ok()

#executed after selecting the band
def init():
    send_ok()


#SSID of the Access Point, returned in ASCII. 32 byte stream, filler bytes
#(0x00) are put to complete 32 bytes, if actual SSID length is not 32 bytes.

#Security Mode of the scanned Access Point, returned in hexadecimal, 1 byte.
#0x00 – Open (No Security)
#0x01 – WPA 1
#0x02 – WPA2
#0x03 – WEP

#Absolute value of the RSSI information, returned in hexadecimal, 1 byte. 
#RSSI information indicates the signal strength of the Access Point.

def ssid_scan():
    global input_queue
    ssid = b'OK Data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x14\r\n'
    input_queue.put(ssid)

def data_scan():
    ssid_scan()

#configures infrastructure mode
def infra_mode():
    send_ok()

#configures the auth mode
def auth_mode():
    send_ok()

#SSID name, TxRate, TxPower
def join_ssid():
    send_ok()


#ipaddr =  socket.inet_aton("172.16.20.48")
ipaddr =  socket.inet_aton(get_ip())
gw = get_gw()
#192.168.11.140: \xc0\xa8\x01\x8c

#DHCP_MODE, IP address, SUBNET, GATEWAY
def config_ip():
    global input_queue
    dhcp = b'OK\xb8\x27\xeb\xbd\x63\x18\xac\x10\x14.\xff\xff\xff\x00\xac\x10\x14\xfe\r\n'
    input_queue.put(dhcp)

#report wifi signal strength to BM
def rssi():
    global input_queue
    rssi = b'OK\x1f\r\n' #iwlist scan
    input_queue.put(rssi)

def open_socket():
    global input_queue
    socket = b'OK\x01\r\n'
    input_queue.put(socket)

def close_socket():
    send_ok()

#ui = b'AT+RSI_READ\x01\x27\x00GET /ui.txt HTTP/1.1 Host: 172.16.20.46\r\n'


# TODO split command at '='
def chooseCommand(command):
    return {
        'at+rsi_reset': send_ok,
        'at+rsi_band=0': select_band,
        'at+rsi_init': init,
        'at+rsi_scan=0': ssid_scan,
        'at+rsi_scan=0, Data': data_scan,
        'at+rsi_network=INFRASTRUCTURE': infra_mode,
        'at+rsi_authmode=4': auth_mode,
        'at+rsi_join= Data,0,2': join_ssid,
        'at+rsi_ipconf=1,0,0': config_ip,
        'at+rsi_rssi?': rssi,
        'at+rsi_ltcp=80': open_socket,
        'at+rsi_cls=1': close_socket
    }.get(command, lambda: "Invalid command")

def sendCommand(data_stream):
    global input_queue
    ui = b'AT+RSI_READ\x01\x27\x00GET /ui.txt HTTP/1.1 Host: 172.16.20.48\r\n'
    start = b'AT+RSI_READ\x01\x2a\x00GET /start.bmp HTTP/1.1 Host: 172.16.20.48\r\n'
    index = b'AT+RSI_READ\x01\x2a\x00GET /index.html HTTP/1.1 Host: 172.16.20.48\r\n'
    recipe = b'AT+RSI_READ\x01\x27\x00GET /rz.txt HTTP/1.1 Host: 172.16.20.48\r\n'
    bm_txt = b'AT+RSI_READ\x01\x27\x00GET /bm.txt HTTP/1.1 Host: 172.16.20.48\r\n'
    bm_html = b'AT+RSI_READ\x01\x27\x00GET /bm.html HTTP/1.1 Host: 172.16.20.48\r\n'
    key1 = b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=1 HTTP/1.1 Host: 172.16.20.48\r\n'

    if data_stream == "ui":
        input_queue.put(ui)
    if data_stream == "start":
        input_queue.put(start)
    if data_stream == "recipe":
        input_queue.put(recipe)
    if data_stream == "bm.txt":
        input_queue.put(bm_txt)
    if data_stream == "bm.html":
        input_queue.put(bm_html)
    if data_stream == "index":
        input_queue.put(index)
    if data_stream == "key1":
        input_queue.put(key1)