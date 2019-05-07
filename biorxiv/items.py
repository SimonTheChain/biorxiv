# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.loader.processors import MapCompose


def strip_newlines(text):
    """
    Strips newline characters from a string
    :param text: String to process
    :return: Cleaned string
    """
    if not isinstance(text, str):
        raise TypeError("The argument for 'strip_newlines' must be a string")

    return text.strip("\n")


class ArticleItem(scrapy.Item):
    """
    Structures data found in articles
    """
    title = scrapy.Field()
    pdf_link = scrapy.Field()
    abstract = scrapy.Field(
        input_processor=MapCompose(strip_newlines)
    )
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
