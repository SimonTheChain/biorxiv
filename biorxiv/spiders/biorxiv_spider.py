# -*- coding: utf-8 -*-


import os
import time  # DEBUG

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from biorxiv.items import ArticleItem
from biorxiv.items import AuthorItem
from biorxiv.items import ArticleItemLoader


class BioRxivSpider(CrawlSpider):
    """

    """
    name = "biorxiv_crawler"
    allowed_domains = ["www.biorxiv.org"]
    start_urls = [
        "https://www.biorxiv.org/search/%252A",
    ]

    rules = (
        Rule(LinkExtractor(
            allow=r'^https://www.biorxiv.org/content/(.*)'),
            callback='parse_item',
        ),
        Rule(LinkExtractor(
            allow=r'^https://www.biorxiv.org/search/(.*)page(.*)'),
            follow=True
        ),
        # to check: it feels like the following would be more efficient
        # Rule(LinkExtractor(
        #     allow=r'^https://www.biorxiv.org/content/(.*)article-info(.*)'),
        #     follow=True,
        #     callback="parse_history"
        # ),
    )

    def parse_start_url(self, response):
        self.logger.info("Crawling initial page: {}".format(response.url))

        # sort by date
        newest_first = response.xpath('//select[@id="edit-sort"]/option[@value="publication-date-descending"]')
        newest_first.click()
        time.sleep(10)  # DEBUG

        # show 100 results per page (to check: this might not be necessary)
        number_of_results = response.xpath('//select[@id="edit-numresults"]/option[@value="100"]')
        number_of_results.click()
        time.sleep(10)  # DEBUG

    def parse_item(self, response):
        self.logger.info("Crawling page: {}".format(response.url))

        # create item instance
        article_loader = ArticleItemLoader(item=ArticleItem(), response=response)

        # populate item
        self.logger.debug(
            "Title: {}".format(
                response.xpath('//*[@id="page-title"]/text()')
            )
        )
        article_loader.add_xpath(
            "title",
            '//*[@id="page-title"]/text()'
        )

        self.logger.debug(
            "PDF Link: {}".format(
                response.xpath('//*[@id="mini-panel-biorxiv_art_tools"]/div/div[1]/div/div/div/div/a/@href')
            )
        )
        article_loader.add_xpath(
            "pdf_link",
            '//*[@id="mini-panel-biorxiv_art_tools"]/div/div[1]/div/div/div/div/a/@href'
        )

        self.logger.debug(
            "Abstract: {}".format(
                response.xpath('//*[@id="abstract-1"]/p/text()')
            )
        )
        article_loader.add_xpath(
            "abstract",
            '//*[@id="abstract-1"]/p/text()'
        )

        info_tab = response.xpath(
            '//*[@id="block-system-main"]/div/div/div/div/div[1]/div/div/div[3]/div/div/ul/li[3]/a[1]/@href'
        ).extract_first()
        info_tab.click()

        authors = []
        names = response.xpath('//*[@class="highwire-citation-authors"]')

        for n in names:
            author = AuthorItem()
            first_name = n.xpath('./span/a/[@class="nlm-given-names"]/text()').extract_first()
            last_name = n.xpath('./span/a/[@class="nlm-surname"]/text()').extract_first()
            author["name"] = "{first} {last}".format(first=first_name, last=last_name)
            author["orcid"] = n.xpath('./span/a/@href')  # to extract

            authors.append(author)

        addresses = response.xpath('//*[@id="contrib-group-1]')

        for a in addresses:
            author["address"] = a.xpath('')

        self.logger.debug(
            "Copyright Info: {}".format(
                response.xpath('//*[@class="panel-pane pane-biorxiv-copyright"]/div/div/div/text()')
            )
        )
        article_loader.add_xpath(
            "copyright_info",
            '//*[@class="panel-pane pane-biorxiv-copyright"]/div/div/div/text()'
        )

        self.logger.debug(
            "Date history: {}".format(
                response.xpath('//*[@class="published-label"]/text()')
            )
        )
        article_loader.add_xpath(
            "date_history",
            '//*[@class="published-label"]/text()'
        )

        return article_loader.load_item()

