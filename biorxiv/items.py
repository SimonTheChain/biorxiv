# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class ArticleItem(scrapy.Item):
    """
    Structures data found in articles
    """
    title = scrapy.Field()
    pdf_link = scrapy.Field()
    abstract = scrapy.Field()
    copyright_info = scrapy.Field()
    authors = scrapy.Field()
    date_history = scrapy.Field()


class AuthorItem(scrapy.Item):
    """
    Structures data about authors
    """
    name = scrapy.Field()
    address = scrapy.Field()
    orcid = scrapy.Field()


class ArticleItemLoader(ItemLoader):
    """
    Applies TakeFirst to all item outputs
    """
    default_output_processor = TakeFirst()


class AuthorItemLoader(ItemLoader):
    """
    Applies TakeFirst to all item outputs
    """
    default_output_processor = TakeFirst()
