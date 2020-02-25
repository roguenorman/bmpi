#!/usr/bin/python3
import json
from queue import Queue, Empty

#logger reads from the logger queue and yields
#ui and terminal receives messages from the logger

logger_input_queue = Queue()
logger_output_queue = Queue()
http_list = list()
request = ""

#decodes http response from wifiServer recives as string
def decode_response(payload):
    global http_list
    global request
    headers = {}
    bmpi = {}
    print("3")
    print(payload) 
    #if http response add it to list (destroy list after all http responses are delt with)

    #request will be the url that was requested. if its rz.txt we need http_list to be 2 if its bm.txt?key http_list will be 1


    if 'at+rsi_snd' in payload:
        print("http response")
        print(request)
        http_list.append(payload)
    else:
        if not http_list:
            #list is empty
            pass
        else:
            #list is full so decode response
            print("http_list")
            print(http_list)
            for i in http_list:
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

    http_list.clear()
    return json.dumps(bmpi)




#def removeNullBytes():
#    return payload.replace(b'\x00', b'')

# read line from queue as bytes
#def receiveFromWifiServer():
#    global http_list
#    #remove escapte bytes
#    payload = byteUnstuff(payload)
#    #decode response
#    payload = payload.decode()
#    #if http response add it to list (need to destroy list after all http response is delt with)
#    if 'at+rsi_snd' in payload:
#        http_list.append(payload)
#    else:
#        if not http_list:
#            #list is empty
#            pass
#        else:
#            #list is full so decode response
#            #decode_response returns json
#            payload = decode_response(http_list)
#            sendToLogger(payload)
#            http_list.clear()
#            return
#    sendToLogger(payload)



def decode__response(payload):
    global http_list
    headers = {}
    bmpi = {}
    print("3")
    print(payload) 
    #if http response add it to list (destroy list after all http responses are delt with)
    if 'at+rsi_snd' in payload:
        print("http response")
        http_list.append(payload)




    #message is AT command
    else:
        if not http_list:
            #list is empty
            pass
        else:
            #list is full so decode response
            for i in http_list:
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

    http_list.clear()
    return json.dumps(bmpi)


    # #decodes http response from BM.
    # def decode_response(self, payload):
    #     headers = {}
    #     bmpi = {}
    #     for i in self.http_list:
    #         resp = i.split("\r\n\r\n")
           
    #         body = resp[-1:]
    #         fields = resp[:-1]
    #         #contains headers it means its the status
    #         if len(fields) > 0:

    #             fields = fields[0].split("\r\n")
    #             fields = fields[1:] #ignore the HTTP/1.1 200 OK
    #             for field in fields:
    #                 key,value = field.split(':')#split each line by http field name and value     
    #                 headers[key] = value
    #             #extract serialnumber date and status. last entry is bmpi status
    #             body = body[0].split("\r\n")
    #             body = body[:-1]           
    #             version_date, serialnum, state = body[0].split(";")
    #             version,month,day,year = version_date.split(" ")


    #             items = state.split("X")
    #             bmpi['version'] = version
    #             bmpi["date"] = (day + " " + month + " " + year)
    #             bmpi["serialnum"] = serialnum
    #             bmpi["clock"] = items[1]
    #             bmpi["unit"] = items[2]
    #             bmpi["unknown3"] = items[3]
    #             bmpi["target_temp"] = items[4]
    #             bmpi["actual_temp"] = items[5]
    #             bmpi["target_time"] = items[6]
    #             bmpi["elapsed_time"] = items[7]

    #     return json.dumps(bmpi)


    # #takes bytes with escapebytes and replaces it with \r\n
    # def byteUnstuff(self, payload):
    #     return payload.replace(b'\xdb\xdc', b'\r\n')

    # def removeNullBytes():
    #     return payload.replace(b'\x00', b'')