from scrapy import cmdline
# cmdline.execute('scrapy crawl love'.split())

import os
os.chdir('truelove/spiders')
cmdline.execute('scrapy runspider love.py'.split())