# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from scrapy.exporters import JsonLinesItemExporter,JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline

class SiderScrapyPipeline(object):
    def __init__(self):
        self.fp = open('music.json','wb')
        self.exporters = JsonLinesItemExporter(self.fp,ensure_ascii=False)
        self.fp.write(b"[")
        pass

    # 打开爬虫的时候
    def open_spider(self,spider):
        print('爬虫开始。。。。。')
        pass

    # 有值传过来的时候
    def process_item(self, item, spider):
        self.exporters.export_item(item)
        self.fp.write(b',')
        return item

    # 爬虫关闭的时候
    def close_spider(self,spider):
        print('爬虫结束。。。。。')
        self.fp.write(b"]")
        self.fp.close()
        pass