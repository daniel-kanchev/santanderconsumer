import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from santanderconsumer.items import Article


class SantanderconsumerSpider(scrapy.Spider):
    name = 'santanderconsumer'
    start_urls = ['https://www.santanderconsumer.se/om-oss/press-och-media/']

    def parse(self, response):
        articles = response.xpath('//div[@class="Grid-cell  "]')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('.//span[@class="documents-block__date"]/text()[last()]').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()
        else:
            return

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
