#coding: utf-8
from flask import Flask,jsonify,request,make_response
import hashlib
import time
import xml.etree.ElementTree as ET
import os
import glob
import pygame
import re
import pexpect
from threading import Thread
import serial
import time
import urllib
import urllib2
import json
import requests
import threading

accesstoken=''
accesstoken_time=0
ser=serial.Serial('/dev/ttyUSB0',9600,timeout=5)
time.sleep(1)
app=Flask(__name__)
@app.route("/",methods=['GET','POST'])
def hello():
    if request.method == 'GET':
        echostr=request.args.get('echostr')
        if checkSignature():           
            return echostr
        else:
            return 'hello'
    else:
        xmldata=request.data
        xml_recv = ET.fromstring(xmldata)
        MsgType = xml_recv.find('MsgType').text
        if MsgType == 'text':
            return textCmd()
        elif MsgType == 'event':
            return clickevent()

        
def checkSignature():
    try:
        signature=request.args.get('signature')
        timestamp=request.args.get('timestamp')
        nonce=request.args.get('nonce')
        token='upcnicxialy86981386'
        tmpArr=[token,timestamp,nonce]
        tmpArr.sort()
        tmpStr = ''.join(tmpArr)
        tmpStr = hashlib.sha1(tmpStr).hexdigest()
    except:
        return False
    else:   
        if signature == tmpStr:
            return True
        else:
            return False

def getaccesstoken():
    global accesstoken_time
    global accesstoken
    if int(time.time())-accesstoken_time>7200:
        url="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx8815c9d6a17b991c&secret=8b0b4e08eb495dfda3371a7a838044f2"
        req=urllib2.Request(url)
        res_data=urllib2.urlopen(req).read()
        print res_data
        json_data=json.loads(res_data)
        accesstoken=json_data["access_token"]
        accesstoken_time=int(time.time())
    print accesstoken
    return accesstoken

def sendtempwarning(temp):
    accesstoken=getaccesstoken()
    datas='{"touser":"oQlMXwGxxQn63balF2ZxJMfP7wpg","template_id":"6iqGBIRQIBUf0tQNkghD6oTwMOKm_2hESTJ5UoCQnkI","data":{"temp":{"value":"'+temp+'","color":"#173177"}}}'
    urls='https://api.weixin.qq.com/cgi-bin/message/template/send?access_token='+accesstoken
    print datas
    r=requests.post(urls, data=datas)
    print r.text

def sendgaswarning(gas):
    accesstoken=getaccesstoken()
    datas='{"touser":"oQlMXwGxxQn63balF2ZxJMfP7wpg","template_id":"3D3FMMz4zD8CekdKbrpdjSiRxa-EbqAbeFG_6mYSOqU","data":{"gas":{"value":"'+gas+'","color":"#173177"}}}'
    urls='https://api.weixin.qq.com/cgi-bin/message/template/send?access_token='+accesstoken
    print datas
    r=requests.post(urls, data=datas)
    print r.text

def sendsoilwarning():
    accesstoken=getaccesstoken()
    datas='{"touser":"oQlMXwGxxQn63balF2ZxJMfP7wpg","template_id":"iOUuXXOf4FYcLd6-7gcatsvLkUqtH6np8GcdCMG4KyE","data":{}}'
    urls='https://api.weixin.qq.com/cgi-bin/message/template/send?access_token='+accesstoken
    r=requests.post(urls, data=datas)
    print r.text

def analyzeSerial(data):
    jsondata=json.loads(data)
    humidity=jsondata["humidity"]
    temperature=jsondata["temperature"]
    mq5warning=jsondata["mq5warning"]
    gas_density=jsondata["gas density"]
    indoor=jsondata["indoor"]
    light_intensity=jsondata["light_intensity"]
    ledstate=jsondata["ledstate"]
    PWM=jsondata["PWM"]
    soil_state=jsondata["soil_state"]
    soilHydropenia=jsondata["soilHydropenia"]
    sensor_data=u'湿度：'+humidity+u' \n温度:'+temperature+u' \n烟雾警告:'+mq5warning
    sensor_data=sensor_data+u' \n甲烷浓度：'+gas_density+u' \n室内光照：'+indoor+u' \n光照强度：'+light_intensity
    sensor_data=sensor_data+u' \nled状态：'+ledstate+u' \n风扇转速：'+PWM+u' \n土壤状态：'+soil_state+u' \n土壤湿度：'+soilHydropenia
    print sensor_data
    return sensor_data

def textCmd():
    xmldata=request.data
    xml_recv = ET.fromstring(xmldata)
    Content = xml_recv.find('Content').text
    ToUserName = xml_recv.find('ToUserName').text
    FromUserName = xml_recv.find('FromUserName').text
    MsgType = xml_recv.find('MsgType').text
    if Content=='motion':
        os.system('motion')
        Content='motion start http://192.168.253.2:8081'
    elif Content=='kill motion':
        os.system('killall motion')
        Content='motion stop'
    elif Content=='music list':
        Content=music_list()
    elif Content[0:1]=='M':
        num=int(Content[1])
        Content=music_play(num)
    elif Content=='music stop':
        Content=music_stop()
    elif Content=='music pause':
        Content=music_pause()
    elif Content=='music unpause':
        Content=music_unpause()
    elif Content=='video list':
        Content=video_list()
    elif Content[0:1]=='V':
        num=int(Content[1])
        Content=video_play(num)
    elif Content=='video stop':
        Content=video_stop()
    elif Content=='video pause':
        Content=video_pause()
    elif Content=='O':
        Content=serialdo('o')
    elif Content=='A':
        Content=serialdo('a')
        Content=analyzeSerial(Content[:-2])
    elif Content=='C':
        Content=serialdo('c')
    elif Content[0:1]=='P':
        num=Content[1:3]
        Content=serialdo('p'+num)
    return xmlResponse(Content,ToUserName,FromUserName,MsgType)

def clickevent():
    xmldata=request.data
    xml_recv = ET.fromstring(xmldata)
    ToUserName = xml_recv.find('ToUserName').text
    FromUserName = xml_recv.find('FromUserName').text
    MsgType = xml_recv.find('MsgType').text
    eventkey =xml_recv.find('EventKey').text
    event =xml_recv.find('Event').text
    if eventkey=='motion':
        os.system('motion')
        Content='motion start http://192.168.253.2:8081'
    elif eventkey=='kill motion':
        os.system('killall motion')
        Content='motion stop'
    elif eventkey=='music list':
        print 'music list'
        Content=music_list()
    elif eventkey=='music stop':
        Content=music_stop()
    elif eventkey=='music pause':
        Content=music_pause()
    elif eventkey=='music unpause':
        Content=music_unpause()
    elif eventkey=='video list':
        Content=video_list()
    elif eventkey=='video stop':
        Content=video_stop()
    elif eventkey=='video pause':
        Content=video_pause()
    elif eventkey=='open_led':
        Content=serialdo('o')
    elif eventkey=='close_led':
        Content=serialdo('c')
    elif eventkey=='info':
        Content=serialdo('a')
        Content=analyzeSerial(Content[:-2])
    elif eventkey=='help':
        Content=u'使用说明\n 开灯:o \n 关灯:c \n 设备信息:a \n 风扇转速:px(x=000-254)\n 播放音乐:mx(x=0-9) \n 播放视频:vx(x=0-9)'
    return xmlResponse(Content,ToUserName,FromUserName,MsgType)
    
def serialdo(cmd):
    if ser.isOpen():
        print 'connect'
        ser.write(cmd)
        print 'cmd:'+cmd
        data=ser.readline()
        data=data.replace("@"," \n")
    else:
        data = 'not connect'
    print data
    return data

def xmlResponse(Content,ToUserName,FromUserName,MsgType):
    reply="<xml><ToUserName><![CDATA["+FromUserName+"]]></ToUserName><FromUserName><![CDATA["+ToUserName+"]]></FromUserName><CreateTime>"+str(int(time.time()))+"</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA["+Content+"]]></Content><FuncFlag>0</FuncFlag></xml>"
    responses=make_response(reply)
    responses.content_type='application/xml'
    return responses

playlist={}
def music_list():
    global playlist
    playlist={}
    num=1
    for mp3file in glob.glob('/home/pi/Music/*.mp3'):
        playlist[num]=mp3file
        num=num+1
    return str(playlist)

def music_play(listnum):
    global playlist
    if playlist=={}:
        num=1
        for mp3file in glob.glob('/home/pi/Music/*.mp3'):
            playlist[num]=mp3file
            num=num+1
    if os.path.exists(playlist[listnum])==True:
        pygame.mixer.init()
        track=pygame.mixer.music.load(playlist[listnum])
        pygame.mixer.music.play()
        return 'Now Play '+playlist[listnum]
    else:
        return 'No this Song'

def music_stop():
    pygame.mixer.init()
    pygame.mixer.music.stop()
    return 'music_stop'

def music_pause():
    pygame.mixer.init()
    pygame.mixer.music.pause()
    return 'music_pause'

def music_unpause():
    pygame.mixer.init()
    pygame.mixer.music.unpause()
    return 'music_unpause'



class OMXPlayer(object):

    _FILEPROP_REXP = re.compile(r".*audio streams (\d+) video streams (\d+) chapters (\d+) subtitles (\d+).*")
    _VIDEOPROP_REXP = re.compile(r".*Video codec ([\w-]+) width (\d+) height (\d+) profile (\d+) fps ([\d.]+).*")
    _AUDIOPROP_REXP = re.compile(r"Audio codec (\w+) channels (\d+) samplerate (\d+) bitspersample (\d+).*")
    _STATUS_REXP = re.compile(r"V :\s*([\d.]+).*")
    _DONE_REXP = re.compile(r"have a nice day.*")

    _LAUNCH_CMD = '/usr/bin/omxplayer -s %s %s'
    _PAUSE_CMD = 'p'
    _TOGGLE_SUB_CMD = 's'
    _QUIT_CMD = 'q'

    paused = False
    subtitles_visible = True

    def __init__(self, mediafile, args=None):
        if not args:
            args = ""
        cmd = self._LAUNCH_CMD % (mediafile, args)
        self._process = pexpect.spawn(cmd)

        self._position_thread = Thread(target=self._get_position)
        self._position_thread.start()


    def _get_position(self):
        while True:
            index = self._process.expect([self._STATUS_REXP,
                                            pexpect.TIMEOUT,
                                            pexpect.EOF,
                                            self._DONE_REXP])
            if index == 1: continue
            elif index in (2, 3): break
            else:
                self.position = float(self._process.match.group(1))
            time.sleep(0.05)

    def toggle_pause(self):
        if self._process.send(self._PAUSE_CMD):
            self.paused = not self.paused

    def toggle_subtitles(self):
        if self._process.send(self._TOGGLE_SUB_CMD):
            self.subtitles_visible = not self.subtitles_visible
            
    def stop(self):
        self._process.send(self._QUIT_CMD)
        self._process.terminate(force=True)

videolist={}
omx=None
nowvideo=None
def video_list():
    global videolist
    videolist={}
    num=1
    for mp4file in glob.glob('/home/pi/Videos/*.mp4'):
        videolist[num]=mp4file
        num=num+1
    return str(videolist)

def video_play(listnum):
    global nowvideo
    global videolist
    global omx
    if videolist=={}:
        num=1
        for mp4file in glob.glob('/home/pi/Videos/*.mp4'):
            videolist[num]=mp4file
            num=num+1
    if os.path.exists(videolist[listnum])==True:
        if nowvideo!=None:
            omx.stop()
        omx=OMXPlayer(videolist[listnum])
        nowvideo=videolist[listnum]
        return  'video play '+videolist[listnum]
    else:
        return 'No This video'

def video_stop():
    global omx
    global nowvideo
    omx.stop()
    nowvideo=None
    return 'video stop'

def video_pause():
    global omx
    omx.toggle_pause()
    return 'video pause'

def scanport():
    while(True):
        content=serialdo('a')
        content=content[:-2]
        jsondata=json.loads(content)
        temperature=jsondata["temperature"]
        mq5warning=jsondata["mq5warning"]
        gas_density=jsondata["gas density"]
        soil_state=jsondata["soil_state"]
        temp=float(temperature)
        if temp>20.0:
            sendtempwarning(temperature)
        if mq5warning=='Y':
            sendgaswarning(gas_density)
        if soil_state=='Soil Dry':
            sendsoilwarning()
        time.sleep(3600)
    print 'hello world!'

if __name__=='__main__':
    t=threading.Thread(target=scanport)
    t.setDaemon(True)
    t.start()
    app.run(host='0.0.0.0',port=80,threaded=True)
    
    

