# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class TrueloveItem(scrapy.Item):
    # define the fields for your item here like:
    nick = scrapy.Field()
    age = scrapy.Field()
    crawled = scrapy.Field()
    spider = scrapy.Field()
    url = scrapy.Field()