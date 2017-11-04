# coding:utf-8

import requests
import urllib
import json

searchURL = "https://y.qq.com/portal/search.html#page={}&searchid=1&w={}"
header = {
    'user-Agent': r'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
songsinfo_url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?&remoteplace=yqq.yqq.yqq&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p={}&n=20&w={}&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0"
songplayinfo_url = 'https://y.qq.com/n/yqq/song/{}.html'
download_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid={}&tpl=yqq_song_detail&format=jsonp&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'

def get_search_page(name, page):
    s_url = searchURL.format(page, urllib.parse.quote(name))
    print(s_url)
    respones = requests.get(s_url, header)
    return respones

def get_songsinfo(name , page):
    s_url = songsinfo_url.format(page, urllib.parse.quote(name.encode("utf-8")))
    responses = requests.get(s_url, header)
    return responses

def get_songsinfo_object(songsinfo:str):
    songsinfo = songsinfo[songsinfo.index("{"):-1]
    print(songsinfo)
    hjson = json.loads(songsinfo)
    return hjson

def get_download_addr(songid:str, mid):
    t_url = download_url.format(mid)
    songinfo = requests.get(t_url, header).content.decode('utf-8')

    hjson = json.loads(songinfo[1:-1])
    return hjson['url'][songid]



if __name__ == '__main__':
    #print(get_search_page("林俊杰".encode("utf-8"), 1).content.decode("utf-8"))
    hjson = get_songsinfo_object(get_songsinfo("汪苏泷", 1).content.decode("utf-8"))
    print(hjson["data"]['song']['list'][0])
    print()
    url = get_download_addr('201949261','001zBl7p3qluVR')
    urllib.request.urlretrieve('http://'+url, "1.m4a")
