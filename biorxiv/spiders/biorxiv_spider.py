# -*- coding: utf-8 -*-


from urllib.parse import urlparse

from scrapy.spiders import SitemapSpider
from scrapy.loader import ItemLoader

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import lxml.html

from biorxiv.items import ArticleItem
from biorxiv.items import AuthorItem


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
        self.item_count = 0
        self.item_limit = 1000

    def parse(self, response):
        pass

    def parse_article(self, response):
        """
        Parses each article page
        """
        # limit the number of items scraped
        if self.item_count >= self.item_limit:
            self.logger.info("The maximum number of items allowed has been reached")
            return

        self.logger.info("Parsing page: {}".format(response.url))

        if response.status == 404:
            self.logger.warning("The request resulted in a 404 status")
            return

        # create item instance
        article_loader = ItemLoader(
            item=ArticleItem(),
            response=response
        )

        # title
        self.logger.debug(
            "Title: {}".format(
                response.xpath('//*[@id="page-title"]/text()').get()
            )
        )
        article_loader.add_xpath(
            "title",
            '//*[@id="page-title"]/text()'
        )

        # pdf link
        parsed_uri = urlparse(response.url)
        domain = "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)
        pdf = response.xpath('//a[contains(@class, "article-dl-pdf-link")]/@href').get()
        pdf_link = domain + pdf

        self.logger.debug(
            "PDF Link: {}".format(
                pdf_link
            )
        )
        article_loader.add_value(
            "pdf_link",
            pdf_link
        )

        # abstract
        root = lxml.html.fromstring(response.body)
        abstract_parts = root.xpath('//div[@id="abstract-1"]//p')
        abstract_text = [str(i.text_content()) for i in abstract_parts]
        abstract = " ".join(abstract_text)

        self.logger.debug("Abstract: {}".format(abstract))
        article_loader.add_value(
            "abstract",
            abstract
        )

        names = response.xpath('//div[contains(@id, "hw-article-author-popups")]/div')
        authors = []

        for n in names:
            # initialize AuthorItem object
            author = AuthorItem()

            # author name
            name = n.xpath(
                './*[@class="author-tooltip-name"]/text()'
            ).get()
            self.logger.debug("Author name: {}".format(name))
            author["name"] = name

            # address
            affiliation = n.xpath(
                '//span[@class="nlm-institution"]/text()'
            ).get()
            self.logger.debug("Address: {}".format(affiliation))
            author["address"] = affiliation

            # orcid
            orcid_link = n.xpath(
                '//*[@class="author-orcid-link"]/a/@href'
            ).get()
            orcid = str(orcid_link).split(sep="/")[-1]
            self.logger.debug("Orcid: {}".format(orcid))
            author["orcid"] = orcid

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
            info_tab = self.driver.find_element_by_xpath(
                '//*[@class="tabs inline panels-ajax-tab"]/*/a[contains(@href, "article-info")]'
            )
            info_tab.click()

        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning("Skipping article: {}\n{}".format(response.url, e))
            return

        # wait for elements to be visible
        try:
            WebDriverWait(
                driver=self.driver,
                timeout=30,
                # poll_frequency=500,
            ).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="panel-pane pane-biorxiv-copyright"]')
                )
            )

        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning("Skipping article: {}\n{}".format(response.url, e))
            return

        # copyright
        copyright_info = response.xpath(
            '//*[@class="panel-pane pane-biorxiv-copyright"]//*/div[@class="field-item even"]/text()'
        )
        self.logger.debug(
            "Copyright Info: {}".format(
                copyright_info.get()
            )
        )
        article_loader.add_value(
            "copyright_info",
            copyright_info.get()
        )

        # date
        try:
            date_history = WebDriverWait(
                driver=self.driver,
                timeout=30,
                # poll_frequency=500,
            ).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//li[@class="published"]')
                )
            )

            self.logger.debug(
                "Date history: {}".format(
                    date_history.text
                )
            )
            article_loader.add_value(
                "date_history",
                date_history.text
            )

        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning("Skipping article: {}\n{}".format(response.url, e))
            return

        self.item_count += 1
        return article_loader.load_item()
