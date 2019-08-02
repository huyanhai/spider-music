# -*- coding: utf-8 -*-
import scrapy
import requests
import json
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from sider_scrapy.items import QqmusicItem


class MusicSpider(CrawlSpider):
    name = 'music'
    allowed_domains = ['y.qq.com']
    start_urls = ['https://y.qq.com/n/yqq/album/003L8BAv3UNXWx.html']

    # def __init__(self):
    #     self.song_data = []

    rules = (
        Rule(LinkExtractor(allow=r'album/.+\.html'),callback='parse_item', follow=False),
    )


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
        for item in range(1,5):
            item = item*20
            for ids in range(1,7):
                formdata['data'] = '{"new_album":{"module":"newalbum.NewAlbumServer","method":"get_new_album_info","param":{"area":%d,"start":0,"num":%d}},"new_album_tag":{"module":"newalbum.NewAlbumServer","method":"get_new_album_area","param":{}},"comm":{"ct":24,"cv":0}}' %(ids,item)
                result = requests.get(URL,params=formdata)
                datas = json.loads(result.text)
                for id in datas['new_album']['data']['albums']:
                    url = 'https://y.qq.com/n/yqq/album/%s.html' %id['mid']
                    self.start_urls.append(url)
                    yield self.make_requests_from_url(url)

    def parse_item(self, response):
        URL_LINK = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        URL_LYR = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
        result = response
        song_mid = result.xpath("//span[@class='songlist__songname_txt']/a/@href").get().split('/')[-1].split('.')[0]
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
        qq_pages = 'https://y.qq.com/n/yqq/album/%s.html' %song_mid
        formdata_link = {
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
        formdata_lry = {
            '-':'MusicJsonCallback_lrc',
            'g_tk':'155229945',
            'songmid':song_mid,
            'format':'json',
            'inCharset':'utf8',
            'outCharset':'utf-8',
            'notice':'0',
            'platform':'yqq.json',
            'needNewCode':'0',
        }
        headers = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Referer':'https://y.qq.com/portal/player.html'
        }
        if len(more_data) > 4:
            song_type = more_data[4]
        print('正在爬取歌曲%s' %song_name)
        res_link = requests.get(URL_LINK,params=formdata_link) # 获取歌曲地址
        res_lyr = requests.get(URL_LYR,params=formdata_lry,headers=headers) # 获取歌词
        datas_link = json.loads(res_link.text)['req_0']['data']
        datas_lyr = json.loads(res_lyr.text)['lyric']
        song_link = 'http://isure.stream.qqmusic.qq.com/' + datas_link['midurlinfo'][0]['purl']
        item = QqmusicItem(singer_name=singer_name,song_name=song_name,schools=schools,language=language,send_time=send_time,song_type=song_type,company=company,post=post,song_mid=song_mid,song_link=song_link,qq_pages=qq_pages,lyric=datas_lyr)
        yield item