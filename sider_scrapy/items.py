# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SiderScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    post = scrapy.Field()
    sing_name = scrapy.Field()
    singer = scrapy.Field()
    link = scrapy.Field()
    pass

class QqmusicItem(scrapy.Item):
    singer_name = scrapy.Field()
    song_name = scrapy.Field()
    issue = scrapy.Field()
    song_type = scrapy.Field()
    language = scrapy.Field()
    send_time = scrapy.Field()
    schools = scrapy.Field()
    company = scrapy.Field()
    post = scrapy.Field()
    song_mid = scrapy.Field()
    lyric = scrapy.Field()
    song_link = scrapy.Field()
    qq_pages = scrapy.Field()