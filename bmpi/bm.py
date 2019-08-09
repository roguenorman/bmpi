#!/usr/bin/python3
import serial
import io
import base64
import socket


ser = serial.Serial('/dev/ttyAMA0', baudrate=115200, parity='N', stopbits=1, bytesize=8, rtscts=0, dsrdtr=0)
ser_text = io.TextIOWrapper(ser, newline='\r\n')

def readFromSerial:
    data = ser_text.readline()
    if len(data) >= 1:
        print(data)


print(ser.name)

ok = 'OK\r\n'
ipaddr =  socket.inet_aton("172.16.20.46")
#192.168.11.140: \xc0\xa8\x01\x8c


def sendToSerial(data):
    print(data)
    ser.write(data.encode())
    #sio.flush()

#def encode(ip):
#    return ascii85_encode(ipaddress.ip_address(ip).packed)[0]

while True:
    #data = ser.readline()
    data = ser_text.readline()
    if len(data) >= 1:
        print(data)


    if 'at+rsi_snd' in data.decode('latin-1'):
        data = b'OK424\r\n'
        d = 'OK\x00\r\n'
        sendToSerial(d)
    #first command to configure band. 0 = 2.4Ghz
    if 'hg?' in data.decode():
        sendToSerial(ok)

    #first command to configure band. 0 = 2.4Ghz
    if 'at+rsi_band=0' in data.decode():
        sendToSerial(ok)
    #get AP mac
    if 'at+rsi_mac?' in data.decode():
        mac = "OK b8 27 eb bd 63 18 \r\n"
        sendToSerial(mac)
    #get wifi module FW version
    if 'at+rsi_fwversion?' in data.decode():
        fwversion = "OK 4.8.4\r\n"
        sendToSerial(fwversion)
    # manual ssid entry for 'Data'
    if 'at+rsi_scan=0,Data' in data.decode():
        ssid = 'OK Data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x14\r\n'
        sendToSerial(ssid)
    #ssid scan all channels
    if 'at+rsi_scan=0' in data.decode():
        ssid = 'OK Data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x14\r\n'
        sendToSerial(ssid)
    #reset wifi module   
    if 'at+rsi_reset' in data.decode():
        sendToSerial(ok)
    if 'at+rsi_disassoc' in data.decode():
        sendToSerial(ok)
    if 'at+rsi_init' in data.decode():
        sendToSerial(ok)
    #get AP bssid
    if 'at+rsi_bssid?' in data.decode():
        bssid = 'OK Data\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 0C 8D DB 94 2E E9\r\n' #sudo iwlist wlan0 scanning
        sendToSerial(bssid)
    #close tcp socket
    if 'at+rsi_cls' in data.decode():
        sendToSerial(ok)
    #close tcp socket
    if 'at+rsi_network=INFRASTRUCTURE' in data.decode():
        sendToSerial(ok)
    #set wifi module password
    if 'at+rsi_psk' in data.decode():
        sendToSerial(ok)
    #request to join network (ssid,txrate,txpower)
    if 'at+rsi_join' in data.decode():
        sendToSerial(ok)

    #set auth mode 1 = PSK
    if 'at+rsi_authmode' in data.decode():
        sendToSerial(ok)
    if 'at+rsi_pwmode' in data.decode():
        sendToSerial(ok)
    if 'at+rsi_sleeptimer' in data.decode():
        sendToSerial(ok)

    #set wifi module IP (dhcp mode,ip address,subnet,gateway) in hex
    if 'at+rsi_ipconf=1' in data.decode():
        dhcp = b'OK\xb8\x27\xeb\xbd\x63\x18\xac\x10\x14.\xff\xff\xff\x00\xac\x10\x14\xfe\r\n'
        print(dhcp)
        ser.write(dhcp)

    #get wifi module rssi. 1 byte hexidecimal
    if 'at+rsi_rssi?' in data.decode():
        rssi = b'OK\x1f\r\n' #iwlist scan
        print(rssi)
        ser.write(rssi)

    #set wifi module dns server
    if 'at+rsi_dnsserver' in data.decode():
        sendToSerial(ok)

    #open port 80 on wifi module. socket returned in hexidecimal
    if 'at+rsi_ltcp=80' in data.decode():
        socket = b'OK\x01\r\n'
        print(socket)
        ser.write(socket)

    #get dns:
    if 'at+rsi_dnsget=api2.myspeidel.com' in data.decode():
        dns = socket.inet_aton(socket.gethostbyname('api2.myspeidel.com'))
        ip = "OK" + socket.inet_ntoa(dns)
        data = b'OK1\x7f\x00\x00\x01'
        print(ip)
        #ser.write(ip)
        sendToSerial(ip)  
    if 'at+rsi_tcp' in data.decode():
        tcp = b'OK\x01\r\n'
        print(tcp)
        ser.write(tcp)


#takes a string with escapebytes. if replaces the escape bytes with \r\n
def byteUnstuff(payload):
    x = payload.replace(b'\xdb\xdc', b'\r\n')
    return x


#http://172.16.20.46/ui.txt


"""
POST /braumeister/connect HTTP/1.1ÛÜHost: api2.myspeidel.comÛÜAuthorization: Basic c3BlaWRlbDptYWlzY2hldGF1Y2hlcgÛÜUser-Agent: Mozilla/4.0ÛÜAccept: text/plain; text/html,*/*ÛÜConnection: closeÛÜContent-Type: application/x-www-form-urlencodedÛÜContent-Length:84 ÛÜÛÜcode=V1.1.27%20Sep%2012%202018;0000000000000000;265161600;b@b.c;2a2bad8d;3fb6adc5ÛÜ 
POST /rz.txt HTTP/1.1ÛÜHost: 172.16.20.46ÛÜAuthorization: Basic c3BlaWRlbDptYWlzY2hldGF1Y2hlcgÛÜUser-Agent: Mozilla/4.0ÛÜAccept: text/plain; text/html,*/*ÛÜConnection: closeÛÜContent-Type: application/x-www-form-urlencodedÛÜContent-Length:85 ÛÜÛÜ
