# -*- coding: utf-8 -*-


from scrapy.spiders import SitemapSpider

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
    sitemap_rules = [
        ('/content/', 'parse_article')
    ]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.driver = None

    def parse(self, response):
        pass

    def parse_article(self, response):
        """
        Parses each article page
        """
        self.logger.info("Parsing page: {}".format(response.url))
        print("Parsing article: {}".format(response.url))  # DEBUG

        # create item instance
        article_loader = ArticleItemLoader(
            item=ArticleItem(),
            response=response
        )

        # populate item
        self.logger.debug(
            "Title: {}".format(
                response.xpath('//*[@id="page-title"]/text()').get()
            )
        )
        article_loader.add_xpath(
            "title",
            '//*[@id="page-title"]/text()'
        )

        # TODO: Rewrite pdf link xpath
        self.logger.debug(
            "PDF Link: {}".format(
                response.xpath('//*[@id="mini-panel-biorxiv_art_tools"]/div/div[1]/div/div/div/div/a/@href').get()
            )
        )
        article_loader.add_xpath(
            "pdf_link",
            '//*[@id="mini-panel-biorxiv_art_tools"]/div/div[1]/div/div/div/div/a/@href'
        )

        self.logger.debug(
            "Abstract: {}".format(
                response.xpath('//*[@id="abstract-1"]/p/text()').get()
            )
        )
        article_loader.add_xpath(
            "abstract",
            '//*[@id="abstract-1"]/p/text()'
        )

        names = response.xpath('//div[contains(@id, "hw-article-author-popups")]/div')
        authors = []

        for n in names:
            # initialize AuthorItem object
            author = AuthorItem()

            # author name
            name = n.xpath('./*[@class="author-tooltip-name"]/text()').get()
            self.logger.debug("Author name: {}".format(name))
            author["name"] = name

            # addresses
            affiliations_elements = n.xpath(
                '//*[@class="nlm-institution"]'
            )
            affiliations = []

            for a in affiliations_elements:
                affiliations.append(a.xpath('./text()').get())

            author["address"] = affiliations

            # orcid
            orcid = n.xpath(
                '//*[@class="author-orcid-link"]/a/@href'
            ).get()
            author["orcid"] = str(orcid).split(sep="/")[-1]

            authors.append(author)

        self.logger.debug(
            "Authors: {}".format(
                authors
            )
        )
        article_loader.add_value(
            "authors",
            authors
        )

        # click the info/history tab
        try:
            self.driver.get(response.url)

        except TimeoutException as e:
            self.logger.warning("Skipping article: {}\n{}".format(response.url, e))
            return

        info_tab = self.driver.find_element_by_xpath(
            '//*[@class="tabs inline panels-ajax-tab"]/*/a[contains(@href, "article-info")]'
        )
        info_tab.click()

        # wait for elements to be visible
        try:
            WebDriverWait(
                driver=self.driver,
                timeout=30,
                # poll_frequency=500,
            ).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="panel-pane pane-biorxiv-copyright"]/div/div/div')
                )
            )

        except TimeoutException as e:
            self.logger.warning("Skipping article: {}\n{}".format(response.url, e))
            print("Skipping article: {}".format(response.url))  # DEBUG
            return

        self.logger.debug(
            "Copyright Info: {}".format(
                response.xpath('//*[@class="panel-pane pane-biorxiv-copyright"]/div/div/div/text()').get()
            )
        )
        article_loader.add_xpath(
            "copyright_info",
            '//*[@class="panel-pane pane-biorxiv-copyright"]/div/div/div/text()'
        )

        self.logger.debug(
            "Date history: {}".format(
                response.xpath('//*[@class="published-label"]/text()').get()
            )
        )
        article_loader.add_xpath(
            "date_history",
            '//*[@class="published-label"]/text()'
        )

        return article_loader.load_item()
