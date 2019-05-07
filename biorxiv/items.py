# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


import datetime

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


def convert_to_datetime(publish_string):
    """
    Converts a date string into datetime
    :param publish_string: Date in the form of a string
    :return: Date in datetime
    """
    if not isinstance(publish_string, str):
        raise TypeError("The argument for 'convert_to_datetime' should be a string")

    publish_datetime = datetime.datetime.strptime(
        publish_string,
        "%B %d, %Y."
    )

    return publish_datetime


class ArticleItem(scrapy.Item):
    """
    Structures data found in articles
    """
    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    pdf_link = scrapy.Field(
        output_processor=TakeFirst()
    )
    abstract = scrapy.Field(
        input_processor=MapCompose(strip_newlines),
        output_processor=TakeFirst()
    )
    copyright_info = scrapy.Field(
        output_processor=TakeFirst()
    )
    authors = scrapy.Field()
    date_history = scrapy.Field(
        input_processor=MapCompose(convert_to_datetime),
        output_processor=TakeFirst()
    )


class AuthorItem(scrapy.Item):
    """
    Structures data about authors
    """
    name = scrapy.Field()
    address = scrapy.Field()
    orcid = scrapy.Field()
