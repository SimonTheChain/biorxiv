# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.loader.processors import TakeFirst


def extract_link(text):
    """
    Extracts a link from a string
    :param text: String containing a url
    :return: Link as string
    """
    # reference: https://daringfireball.net/2009/11/liberal_regex_for_matching_urls
    pattern = re.compile(r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/)))')
    link = pattern.match(text)

    if link:
        return link.group(0)


class ArticleItem(scrapy.Item):
    """
    Structures data found in articles
    """
    title = scrapy.Field()
    pdf_link = scrapy.Field(
        input_processor=MapCompose(extract_link)
    )
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

    """
    default_output_processor = TakeFirst()
