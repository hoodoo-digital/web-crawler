import scrapy
from dynaconf import settings

REPORT_ID=settings.REPORT_IF
INCLUDE_CHILDREN=settings.INCLUDE_CHILDREN
unique_urls = []
unique_items = []


class MyItems(scrapy.Item):
    original_page =scrapy.Field()
    original_request = scrapy.Field()
    response_page = scrapy.Field()
    response_status= scrapy.Field()


class MySpider(scrapy.Spider):
    name = settings.NAME
    start_urls = settings.START_URLS
    handle_httpstatus_list = [200,400,403,404,500,503]
    handle_httpstatus_all = True
    custom_settings = {
        'CONCURRENT_REQUESTS': settings.CONCURRENT_REQUESTS_PER_DOMAIN,
        # Delay in seconds between requests
        'DOWNLOAD_DELAY': settings.DOWNLOAD_DELAY,
        'FEED_URI' : settings.OUTPUT_FILE,
        'FEED_FORMAT': settings.OUTPUT_FORMAT,
    }

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, dont_filter=True, meta={'referer': u})

    def parse(self, response):
        # parse after login verification
        if response.status == 301:
            yield scrapy.Request(response.url, self.parse, dont_filter=False, meta={'referer': response.meta['referer']})
        if self.isAllowedUrl(response.url):
            # fetch all links
            for href in self.getLinks(response):
                try:
                    # handle relative URLs
                    url = response.urljoin(href)
                    # filter unique and valid
                    if self.isUniqueUrl(url) and self.shouldFollow(url) and self.isAllowed(url):               
                        yield scrapy.Request(url, self.parse, dont_filter=False, meta={'referer': response.url})
                except:
                    self.log(f'Something bad happen with {response}')
                    continue

        # pass the item to the writter
        # Note: Implement influxdb
        if response.status in settings.REPORT_IF:
            item = MyItems()
            if response.request.meta.get('redirect_urls'):
                item['original_request'] = response.request.meta["redirect_urls"][0]
            item['original_page'] = response.meta['referer']
            item['response_status'] = response.status
            item['response_page'] = response.url
            yield item  

    @staticmethod
    def getLinks(response):
        # this avoids an error trying to fetch links from non html links
        try: 
            return response.xpath('//a/@href').getall()
        except:
            return []

    def isAllowedUrl(self, url):
        if not INCLUDE_CHILDREN:
            return url in self.start_urls
        
        for s in settings.START_URLS:
            if url.startswith(s.replace('.html','')):
                return True
        return False

    @staticmethod
    def isAllowed(url):
        return not(url.startswith('mailto:') 
                    or url.startswith('tel:') 
                    or url.endswith('.pdf')
                    or url.startswith('javascript:')
                    or url.endswith('.jpg')
                    or url.endswith('.png')
                    or url.endswith('.gif')
                )
    
    @staticmethod
    def shouldFollow(url):
        ''' filter non allowed domains '''
        result = next((st for st in settings.DISALLOWED_DOMAINS if st in url), None)
        if result is None:
            return True
        return False
    
    @staticmethod
    def isUniqueUrl(url):
        if url in unique_urls:
            return False
        unique_urls.append(url)
        return True
        