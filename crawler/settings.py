# Scrapy settings for carinfo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36"

ITEM_PIPELINES = ['crawler.pipelines.CrawlerPipeline', ]

SCHEDULER_DOMAIN_CLASS = "crawler.lib.models.Domain"
SCHEDULER_FLOW_CLASS = "crawler.lib.models.Flow"

DUPEFILTER_CLASS = "crawler.extensions.dupefilter.RFPDupeFilter"

SPIDER_MIDDLEWARES = {
    "crawler.middlewares.spidermiddleware.FlowMiddleware": 543,
    "crawler.middlewares.spidermiddleware.SpiderMiddleware": 544
}
DOWNLOADER_MIDDLEWARES = {
    "crawler.middlewares.downloadmiddleware.ResponseTransfer": 543, 
    "crawler.middlewares.downloadmiddleware.DownloadMiddleware": 544
}
EXTENSIONS = {
    "crawler.extensions.scheduler_ext.SchedulerExtension": 500,
    "crawler.extensions.pushworker.PushWorkerExtension": 543
}
SCHEDULER = "crawler.extensions.scheduler.Scheduler"

# Fingerprint url expire time
FP_EXPIRE = 90 * 24 * 3600

FURTHER_REQUEST_MODULE = "crawler.spiders.further_request"

# Redis config
REDIS_HOST = '192.168.2.228'
REDIS_PORT = 6381
MAIN_REDIS_DB = 0
LOG_REDIS_DB = 15
# Fingerprint DB
FP_REDIS_DB = 14
SLICE_REDIS_DB = 13

# Mysql config
MYSQL_HOST = '192.168.2.228'
MYSQL_PORT = 3306
MYSQL_DB = 'spider'
MYSQL_USER = 'crawler'
MYSQL_PASS = 'crawler'

# Mongodb config
MONGO_SERVER = '192.168.2.228'
MONGO_PORT = 2281
MONGO_DB = 'dcrawler'
MONGO_COLL = 'car_info'

# RabbitMQ config
RABBITMQ_SERVER = "192.168.2.229"
RABBITMQ_PORT = 5672
RABBITMQ_VHOST = '/dcrawler-pro'
RABBITMQ_USER = 'dcrawler'
RABBITMQ_PASS = '123'
MQ_EXCHANGE = 'processing_exchange'
MQ_INKEY = ''
MQ_INQUEUE = ''
MQ_OUTKEY = 'enroll'
MQ_OUTQUEUE = 'enroll_queue'
