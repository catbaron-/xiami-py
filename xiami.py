# -*- coding: utf-8 -*-

import urllib2,urllib
import xml.dom.minidom
import json,sys

reload(sys) 
sys.setdefaultencoding( "utf-8" ) 

SONGDP1="http://www.xiami.com/app/iphone/song/id/"
SONGDP2="http://www.xiami.com/widget/xml-multi/sid/"
SONGSP = "http://www.xiami.com/app/iphone/search/key/"
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'} 
HOST_M = ["http://m1.file.xiami.com/","http://m4.file.xiami.com/","http://m5.file.xiami.com/"]
TRY_TIME = 5

## Function: get song url by song_id
## Argument: (int)song_id
## Return: 
##     return (list)url_list if sucessfully
def getXiamiByKey(k):
    songsp = SONGSP + urllib. quote(str(k))
    song_dict = {"result":0,"music_info":[]}
    req = urllib2.Request(songsp,headers=HEADERS)
    try_time = 0
    while try_time < TRY_TIME:
        try:
            song_json = json.loads(urllib2.urlopen(req).read())
            for song in song_json["songs"]:
                song_dict["music_info"].append(readMusicInfoFromJson(song))
            print song_dict
            return song_dict
        except Exception,e:
            print "ERR-- Err in getXiamiByKey() :",e
            try_time = try_time+1
    #print song_dict
    return {"result":1}


## Function: get song url by song_id
## Argument: (int)song_id
## Return: 
##     return (list)url_list if sucessfully
##    return (Bool)False  if failed
def getMusicInfoFromXiami(song_id):
    url_list = []
    try:
        songdp1 = SONGDP1 + str(song_id)
        songdp2 = SONGDP2 + str(song_id)
    except Exception,e:
        print "ERR--song id Err in getMusicInfoFromXiami():",e
        return False
    req1 = urllib2.Request(songdp1,headers = HEADERS)
    req2 = urllib2.Request(songdp2,headers = HEADERS)

    ## try to get json from a api
    try_time = 0
    while try_time < TRY_TIME:
        try:
            song1_json = json.loads(urllib2.urlopen(req1).read())
            music_info = readMusicInfoFromJson(song1_json)
            music_info["result"]=0
            return music_info
        except Exception,e:
            print "ERR--Get json From xiami Err in getMusicInfoFromXiami():",e
            try_time = try_time+1
    
    ## if get json failed, then try to get xml from another api
    print "get xiami JSON failed"
    try_time = 0
    while  try_time < TRY_TIME:
        try:
            song2_xml = xml.dom.minidom.parseString(urllib2.urlopen(req2).read())
            music_info = readMusicInfoFromXml(song2_xml)
            music_info["result"]=0
            return music_info
        except Exception,e:
            print "ERR--Get XML From xiami Err in getMusicInfoFromXiami():",e
            try_time = try_time+1

    ## both xml and json is failed
    print "get song info from xiami failed"
    return {"result":1}

## Function: decode from xml data to get the song url
## Argument: (string)string_url
## Return: 
##     return (string)url with auth key
##    return (Bool)False  if failed
def readMusicInfoFromJson(song_json):
    music_info = {"name":"","artist":"","singer":"","album":"","url_list":[]}
    music_info["url_list"] = readXiamiUrlFromJson(song_json)
    music_info["cover"] = song_json["album_logo"].replace("_3.jpg",".jpg")
    music_info["name"] = song_json["name"]
    music_info["artist"] = song_json["artist_name"]
    music_info["singer"] = song_json["singers"]
    music_info["album"] = song_json["title"]
    music_info["src_id"] = song_json["song_id"]
    return music_info
def readMusicInfoFromXml(song_xml):
    music_info = {"name":"","artist":"","singer":"","album":"","url_list":[]}
    music_info["url_list"] = readXiamiUrlFromXml(song_xml)
    nodes = song_xml.getElementsByTagName("song_name")
    music_info["name"] = nodes[0].childNodes[0].data
    nodes = song_xml.getElementsByTagName("artist_name")
    music_info["artist"] = nodes[0].childNodes[0].data
    music_info["singer"] = music_info["artist"]
    nodes = song_xml.getElementsByTagName("album_name")
    music_info["album"] = nodes[0].childNodes[0].data
    nodes = song_xml.getElementsByTagName("album_cover")
    music_info["cover"] = nodes[0].childNodes[0].data.replace("_3.jpg",".jpg")
    nodes = song_xml.getElementsByTagName("song_id")
    music_info["src_id"] = nodes[0].data
    return music_info



## Function: decode from xml data to get the song url
## Argument: (string)string_url
## Return: 
##     return (string)url with auth key
##    return (Bool)False  if failed
def decodeXiamiXmlUrl(string_url):
    try:
        line = int(string_url[0])
    except Exception,e:
        print "ERR--XML data ERR in decodeXiamiXmlUrl:",e
        return False

    encode_url = string_url[1:]
    url_len = len(encode_url)
    col_0 = url_len/line
    col_1 = col_0+1
    col_1_c = url_len%line

    decode_url = ""
    count = 0
    start = 0
    decode_list = [""]*line

    while count < line:
        if count < col_1_c :
            decode_list[count] = encode_url[start:start+col_1]
        else:
            decode_list[count] = encode_url[start:start+col_0]
        start = start + len(decode_list[count])
        count = count+1
    count = 0
    while count < col_0:
        for ch in decode_list:
            decode_url = decode_url + ch[count]
        count = count+1

    count = 0
    while count < col_1_c:
        decode_url = decode_url + decode_list[count][-1]
        count = count + 1
    return urllib.unquote(decode_url).replace("^","0")

## Function: read url and decode from xml 
## Argument: (XML Obj)song_xml
## Return: 
##     return (string)url list
##    return (Bool)False  if failed
def readXiamiUrlFromXml(song_xml):
    song_urls = []
    try:
        nodes = song_xml.getElementsByTagName("location")
    except Exception,e:
        print "ERR--initial nodes failed in readXiamiUrlFromXml():",e
    for n in nodes:
        try:
            data = n.childNodes[0].data
        except Exception,e:
            print "ERR--get data from nodes failed in readXiamiUrlFromXml():",e
        url = decodeXiamiXmlUrl(data)
        if url:
            song_urls.append(url)
    if len(song_urls)>0:
        song_uri = song_urls[0]
        return createUrlList(song_uri)


## Function: read url from json
## Argument: (json Obj)song_json
## Return: 
##     return (string)url list
##    return (Bool)False  if failed
def readXiamiUrlFromJson(song_json):
    song_uri = song_json["location"]
    #song_uri = (song_url.split("xiami.com/")[-1]).split("?")[0]
    song_urls = createUrlList(song_uri)
    return song_urls

## Function: create a url list from uri and HOST
## Argument: (string)song_url with auth key and host
## Return: 
##     return (string)url list
##    return (Bool)False  if failed    
def createUrlList(song_url):
    song_urls = []
    song_uri = (song_url.split("xiami.com/")[-1]).split("?")[0]
    for host in HOST_M:
            if host[-1] != "/":
                host = host+"/"
            song_urls.append(host + song_uri)
    return song_urls

def main():
    #getMusicInfoFromXiami("1769402049")
    getXiamiByKey("周杰伦")
if __name__ == '__main__':
    main()