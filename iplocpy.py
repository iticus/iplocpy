'''
Created on Jul 20, 2015

@author: ionut
'''

import logging
import psycopg2
import pymongo
import signal
import redis
import tornado.web

import settings

def configure_signals():
    
    def stopping_handler(signum, frame):
        logging.info('interrupt signal %s received, shutting down' % signum)
        tornado.ioloop.IOLoop.instance().stop()
        
    signal.signal(signal.SIGINT, stopping_handler)
    signal.signal(signal.SIGTERM, stopping_handler)


configure_signals()
logging.info('starting iplocpy application')

import handlers
pgconn = psycopg2.connect(settings.POSTGRES_CONN)
mgconn = pymongo.MongoClient(settings.MONGO_CONN)
rdconn = redis.StrictRedis(settings.REDIS_CONN)

application = tornado.web.Application([
    (r"/", handlers.MainHandler),
    (r"/find/?", handlers.IPHandler, {}),
    ], pgconn=pgconn, mgconn=mgconn, rdconn=rdconn, debug=False, gzip=False
)

logging.info('ready, listening on %d' % settings.PORT)
application.listen(settings.PORT)
tornado.ioloop.IOLoop.instance().start()