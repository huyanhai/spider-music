# -*- coding: utf-8 -*-
import scrapy
from sider_scrapy.items import SiderScrapyItem


class QqMusicSpider(scrapy.Spider):
    name = 'qq_music'
    allowed_domains = ['y.qq.com']
    start_urls = ['http://y.qq.com/']
    
    def parse(self, response):
        list = response.css(".songlist__list .songlist__item_box")
        print('='*20)
        for li in list:
            post = li.css('.songlist__pic::attr(src)').get()
            sing_name = li.css('.songlist__song a::text').get()
            singer = li.css('.songlist__author a::text').get()
            link = li.css('.album_name::attr(href)').get()
            item = SiderScrapyItem(post=post,sing_name=sing_name,singer=singer,link=link)
            yield item

        print('='*20)
        pass
