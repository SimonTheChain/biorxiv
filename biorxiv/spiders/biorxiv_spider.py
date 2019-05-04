# -*- coding: utf-8 -*-


from scrapy.spiders import SitemapSpider

from selenium.webdriver.common.action_chains import ActionChains
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

        authors = []
        names = response.xpath('//*[@class="highwire-citation-authors"]')

        for n in names:
            author = AuthorItem()
            # first_name = n.xpath('.//*[@class="nlm-given-names"]/text()').extract_first()
            # last_name = n.xpath('.//*[@class="nlm-surname"]/text()').extract_first()
            # author["name"] = "{first} {last}".format(first=first_name, last=last_name)
            # author["orcid"] = str(n.xpath('./span/a/@href')).split(sep="/")[-1]

            # reference: https://stackoverflow.com/a/29052586/5242366
            main_window_handle = None

            while not main_window_handle:
                main_window_handle = self.driver.current_window_handle

            # hover to enable popup
            actions = ActionChains(self.driver)
            author_element = self.driver.find_element_by_xpath(
                '//*[contains(@class, "highwire-citation-author")]'
            )
            actions.move_to_element(author_element).perform()

            popup_window_handle = None

            while not popup_window_handle:
                for handle in self.driver.window_handles:
                    if handle != main_window_handle:
                        popup_window_handle = handle
                        break

            # parse popup contents
            self.driver.switch_to.window(popup_window_handle)

            # author name
            author["name"] = self.driver.find_element_by_xpath(
                '//*[@class="author-tooltip-name"]/text()'
            )

            # addresses
            affiliations_element = self.driver.find_element_by_xpath(
                '//*[@class="author-tooltip-text"]'
            )
            affiliations = []

            for a in affiliations_element:
                aff = a.xpath(
                    './span/span/text()'
                )
                affiliations.append(aff)

            author["address"] = affiliations

            # orcid
            orcid = self.driver.find_element_by_xpath(
                '//*[@class="author-orcid-link"]/a/@href'
            )
            author["orcid"] = str(orcid).split(sep="/")[-1]

            self.driver.switch_to.window(main_window_handle)

            # popup = WebDriverWait(
            #     driver=self.driver,
            #     timeout=10,
            #     # poll_frequency=500,
            # ).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "author-popup-hover"))
            # )

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
