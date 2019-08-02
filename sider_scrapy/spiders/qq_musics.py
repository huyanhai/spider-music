# -*- coding: utf-8 -*-
# scrapy genspider -t crawl Music_lyr 'y.qq.com' 创建命令
import scrapy
import time
import json
import requests
import ssl
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from urllib.parse import urlencode,quote

from sider_scrapy.items import QqmusicItem

ssl._create_default_https_context = ssl._create_unverified_context


class QqMusicsSpider(CrawlSpider):
    name = 'qq_musics'
    allowed_domains = ['y.qq.com']
    start_urls = ['https://u.y.qq.com/cgi-bin/musicu.fcg']

    def __init__(self):
        self.song_data = {}

    # rules = (
    #     Rule(LinkExtractor(allow=r'.+n/yqq/toplist/.+\.html'),callback="parse_url",follow=True),
    #     Rule(LinkExtractor(allow=r'.+n/yqq/song/.+\.html'),callback="parse_song", follow=False)
    # )

    # 开始请求执行
    def start_requests(self):
        URL = 'https://u.y.qq.com/cgi-bin/musicu.fcg'

        formdata = {
            '-':'getUCGI12417882050721563',
            'g_tk':'155229945',
            'format':'json',
            'inCharset':'utf8',
            'outCharset':'utf-8',
            'notice':'0',
            'platform':'yqq.json',
            'needNewCode':'0',
        }
        for item in range(1,10):
            item = item*20
            for ids in range(1,7):
                formdata['data'] = '{"new_album":{"module":"newalbum.NewAlbumServer","method":"get_new_album_info","param":{"area":%d,"start":0,"num":%d}},"new_album_tag":{"module":"newalbum.NewAlbumServer","method":"get_new_album_area","param":{}},"comm":{"ct":24,"cv":0}}' %(ids,item)
                yield scrapy.FormRequest(URL,callback=self.parse_url,formdata=formdata,method='GET')

    def parse_url(self, response):
        # response.urljoin(url) 链接转换
        result = json.loads(response.text)
        datas = result['new_album']['data']['albums']
        for li in datas:
            song_id = li['mid']
            URL = 'https://y.qq.com/n/yqq/album/%s.html' %song_id
            print('正在爬取歌曲id是：%s' %song_id)
            yield scrapy.FormRequest(URL,callback=self.parse_song,method='GET')

    def parse_song(self,response):
        # URL = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
        URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        result = response
        song_mid = result.xpath("//span[@class='songlist__songname_txt']/a/@href").get().split('/')[-1].split('.')[0]
        # formdata = {
        #     '-':'MusicJsonCallback_lrc',
        #     'g_tk':'155229945',
        #     'songmid':song_mid,
        #     'format':'json',
        #     'inCharset':'utf8',
        #     'outCharset':'utf-8',
        #     'notice':'0',
        #     'platform':'yqq.json',
        #     'needNewCode':'0',
        # }
        formdata = {
            '-':'getplaysongvkey',
            'g_tk':'155229945',
            'loginUin': '810839700',
            'hostUin':'0',
            'format':'json',
            'inCharset':'utf8',
            'outCharset':'utf-8',
            'notice':'0',
            'platform':'yqq.json',
            'needNewCode':'0',
            'data':'{"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"986239112","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"986239112","songmid":["%s"],"songtype":[0],"uin":"810839700","loginflag":1,"platform":"20"}},"comm":{"uin":810839700,"format":"json","ct":24,"cv":0}}' %song_mid
        }
        singer_name = result.xpath("//div[@class='data__cont']/div[@class='data__singer']/a/text()").get()
        song_name = result.xpath("//div[@class='data__cont']//h1/text()").get()
        more_data = result.xpath("//div[@class='data__cont']//li/text()").getall()
        company = result.xpath("//div[@class='data__cont']//li/a/text()").get()
        post = response.urljoin(result.xpath("//span[@class='data__cover']/img/@src").get())
        more_data = list(map(lambda x:x.split('：')[1],more_data))
        schools = more_data[0]
        language = more_data[1]
        send_time = more_data[2]
        song_type = None
        if len(more_data) > 4:
            song_type = more_data[4]
        self.song_data = {
            "singer_name":singer_name,
            "song_name":song_name,
            "company":company,
            "post":post,
            "schools":schools,
            "language":language,
            "send_time":send_time,
            "song_type":song_type,
            "song_mid":song_mid,
            'lyric':None
        }
        try:
            yield scrapy.FormRequest(URL,method='GET',formdata=formdata,callback=self.get_song_src)    
        except requests.ConnectionError as e:
            yield None

    def song_lyric(self, response):
        URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        formdata = {
            '-':'getplaysongvkey',
            'g_tk':'155229945',
            'loginUin': '810839700',
            'hostUin':'0',
            'format':'json',
            'inCharset':'utf8',
            'outCharset':'utf-8',
            'notice':'0',
            'platform':'yqq.json',
            'needNewCode':'0',
            'data':'{"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"986239112","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"986239112","songmid":["%s"],"songtype":[0],"uin":"810839700","loginflag":1,"platform":"20"}},"comm":{"uin":810839700,"format":"json","ct":24,"cv":0}}' %self.song_data['song_mid']
        }
        result = json.loads(response.text)
        if 'lyric' in result:
            self.song_data['lyric'] = result['lyric']
        try:
            yield scrapy.FormRequest(URL,formdata=formdata,method='GET',callback=self.get_song_src)
        except requests.ConnectionError as e:
            yield None
    
    def get_song_src(self, response):
        print('-'*40)
        print(response.url)
        print('-'*40)
        datas = self.song_data
        if 'data' in json.loads(response.text)['req_0']:
            data = json.loads(response.text)['req_0']['data']
            song_link = 'http://isure.stream.qqmusic.qq.com/' + data['midurlinfo'][0]['purl']
            item = QqmusicItem(singer_name=datas['singer_name'],song_name=datas['song_name'],schools=datas['schools'],language=datas['language'],send_time=datas['send_time'],song_type=datas['song_type'],company=datas['company'],post=datas['post'],song_mid=datas['song_mid'],lyric=datas['lyric'],song_link=song_link)
            yield item
        else:
            yield None
