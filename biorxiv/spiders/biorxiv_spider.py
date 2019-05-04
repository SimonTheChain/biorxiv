# -*- coding: utf-8 -*-


from scrapy.spiders import SitemapSpider

from biorxiv.items import ArticleItem
from biorxiv.items import AuthorItem
from biorxiv.items import ArticleItemLoader


class BioRxivSpider(SitemapSpider):
    """
    Crawls BioRxiv to gather various informations
    """
    name = "biorxiv_crawler"
    allowed_domains = ["www.biorxiv.org"]
    sitemap_urls = [
        "https://www.biorxiv.org/sitemap.xml",
    ]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.driver = None

    def parse(self, response):
        """
        Parses each article page
        """
        self.logger.info("Parsing page: {}".format(response.url))

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

        # click the info/history tab
        info_tab = self.driver.find_element_by_xpath(
            '//*[@class="tabs inline panels-ajax-tab"]/li/a'
        )
        info_tab.click()

        # authors = []
        # names = response.xpath('//*[@class="highwire-citation-authors"]')
        #
        # for n in names:
        #     author = AuthorItem()
        #     first_name = n.xpath('./span/a/[@class="nlm-given-names"]/text()').extract_first()
        #     last_name = n.xpath('./span/a/[@class="nlm-surname"]/text()').extract_first()
        #     author["name"] = "{first} {last}".format(first=first_name, last=last_name)
        #     author["orcid"] = n.xpath('./span/a/@href')  # to extract
        #
        #     authors.append(dict(author))
        #
        # addresses = response.xpath('//*[@id="contrib-group-1]')
        #
        # # for a in addresses:
        # #     author["address"] = a.xpath('')
        #
        # self.logger.debug(
        #     "Authors: {}".format(
        #         authors
        #     )
        # )
        # article_loader.add_value(
        #     "authors",
        #     authors
        # )

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

        yield article_loader.load_item()
