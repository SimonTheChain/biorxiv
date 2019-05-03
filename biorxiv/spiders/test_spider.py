# -*- coding: utf-8 -*-


from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from biorxiv.items import ArticleItem
from biorxiv.items import AuthorItem
from biorxiv.items import ArticleItemLoader
from biorxiv.items import AuthorItemLoader


class TestSpider(CrawlSpider):
    """
    Crawls Plos to gather various informations
    """
    name = "test_crawler"
    allowed_domains = ["journals.plos.org"]
    start_urls = [
        "https://journals.plos.org/plosone/browse/physics",
    ]

    rules = (
        Rule(LinkExtractor(
            allow=r'^https://journals.plos.org/plosone/article(.*)'),
            callback='parse_item',
        ),
        Rule(LinkExtractor(
            allow=r'^https://journals.plos.org/plosone/browse/physics?page(.*)'),
            follow=True
        ),
        Rule(LinkExtractor(
            allow=r'^https://journals.plos.org/plosone/article/authors(.*)'),
            callback='parse_authors',
        ),
    )

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.driver = None

    def parse_start_url(self, response):
        """
        Initial parsing before extracting links
        """
        self.logger.info("Crawling initial page: {}".format(response.url))

        # sort by popularity
        popular = self.driver.find_element_by_xpath('//*[@class="sort"]/a[text()="Popular"]')
        popular.click()

    def parse_item(self, response):
        """
        Parses each article page
        """
        self.logger.info("Crawling page: {}".format(response.url))

        # create item instance
        article_loader = ArticleItemLoader(item=ArticleItem(), response=response)

        # populate item
        self.logger.debug(
            "Title: {}".format(
                response.xpath('//*[@id="artTitle"]/text()').extract_first()
            )
        )
        article_loader.add_xpath(
            "title",
            '//*[@id="artTitle"]/text()'
        )

        self.logger.debug(
            "PDF Link: {}".format(
                response.xpath('//*[@id="downloadPdf"]/@href').extract_first()
            )
        )
        article_loader.add_xpath(
            "pdf_link",
            '//*[@id="downloadPdf"]/@href'
        )

        self.logger.debug(
            "Abstract: {}".format(
                response.xpath('//*[@class="abstract toc-section"]/div/p/text()').extract_first()
            )
        )
        article_loader.add_xpath(
            "abstract",
            '//*[@class="abstract toc-section"]/div/p/text()'
        )

        # click the authors tab
        # authors_tab = self.driver.find_element_by_xpath(
        #     '//*[@id="tabAuthors"]/a'
        # )
        # authors_tab.click()
        #
        # authors = []
        # names = response.xpath('//h1[text()="About the Authors"]/dl')
        #
        # for n in names:
        #     author = AuthorItem()
        #     author["name"] = n.xpath('./dt/text()')
        #     author["address"] = n.xpath('[@id="authCorresponding-0"]/a/@href')  # to extract
        #     author["orcid"] = n.xpath('./[@id="authOrcid-0"]/span/a/@href')  # to extract
        #
        #     authors.append(dict(author))
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
                response.xpath('//*[@class="articleinfo"]/p[4]/text()').extract_first()
            )
        )
        article_loader.add_xpath(
            "copyright_info",
            '//*[@class="articleinfo"]/p[4]/text()'
        )

        self.logger.debug(
            "Date history: {}".format(
                response.xpath('//*[@class="articleinfo"]/p[3]/text()').extract_first()
            )
        )
        article_loader.add_xpath(
            "date_history",
            '//*[@class="articleinfo"]/p[3]/text()'
        )

        return article_loader.load_item()

    def parse_authors(self, response):
        """
        Gathers info about authors
        :param response: Response object
        :return: Item object
        """
        self.logger.info("Crawling authors page: {}".format(response.url))
        names = response.xpath('//h1[text()="About the Authors"]/dl')

        for n in names:
            self.logger.debug("Author: {}".format(n))

            # create item instance
            author_loader = AuthorItemLoader(item=AuthorItem(), selector=n)

            # populate item loader
            author_loader.add_xpath("name", './dt/text()')
            author_loader.add_xpath("address", '[@id="authCorresponding-0"]/a/@href')
            author_loader.add_xpath("orcid", './[@id="authOrcid-0"]/span/a/@href')

            yield author_loader.load_item()
