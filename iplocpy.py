'''
Created on Jul 20, 2015

@author: ionut
'''

import csv
import json
import logging
import psycopg2
import pymongo
import signal
import tornado.web

import settings
import utils

_ADDRESSES = []
_DETAILS = {}


logging.basicConfig(level=settings.LOG_LEVEL, #filename='iplocpy.log',
    format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def configure_signals():
    
    def stopping_handler(signum, frame):
        logging.info('interrupt signal %s received, shutting down' % signum)
        tornado.ioloop.IOLoop.instance().stop()
        
    signal.signal(signal.SIGINT, stopping_handler)
    signal.signal(signal.SIGTERM, stopping_handler)


def load_data(path):
    with open(path, 'rb') as csvfile:
        ip_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        #"0.0.0.0","0.255.255.255","US","California","Los Angeles"
        for row in ip_reader:
            if row[0] == '::':
                break
            start_address = utils.ip2int(row[0])
            stop_address = utils.ip2int(row[1])
            
            _ADDRESSES.append(start_address)
            _DETAILS[start_address] = (stop_address, row[2], row[3], row[4])


def find_ip(ipnum):
    lo = 0
    hi = len(_ADDRESSES)-1
    while (hi >= lo):
        
        mid = (lo+hi) / 2
        midval = _ADDRESSES[mid]
        
        if midval < ipnum:
            lo = mid+1
        elif midval > ipnum: 
            hi = mid-1
        else:
            return mid
    
    mid = min(lo, mid, hi)
    if _ADDRESSES[mid] <= ipnum:
        return mid
    
    return None


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.pgconn = self.settings['pgconn']
        self.mgconn = self.settings['mgconn']
        self.set_header("Content-Type", "application/json")
        tornado.web.RequestHandler.initialize(self)
    
    def response(self, status='OK', data=None):
        self.finish(json.dumps({'status': status, 'data': data}))    


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.response(data='iplocpy running here...')

    @tornado.web.asynchronous
    def post(self):
        self.response('error', 'POST not allowed for this URL')


class IPHandler(BaseHandler):
    
    @tornado.web.asynchronous
    def post(self):
        self.response('error', 'POST not allowed for this URL')
    
    @tornado.web.asynchronous
    def get(self):
        ip = self.get_argument('ip_addr', None)
        if not ip:
            return self.response('error', 'please input an IPv4 address')
        try:
            ip = utils.ip2int(ip)
        except:
            return self.response('error', 'please input a valid IPv4 address')
        
        if not (0 <= ip <= 4294967295):
            return self.response('error', 'please input a valid IPv4 address')
        
        response = None
        resolver = self.get_argument('resolver', 'mem')
        if resolver == 'postgres':
            cursor = self.pgconn.cursor()
            cursor.execute('select x, y, country, county, city from addresses where x <= %s and y >= %s', (ip, ip))
            records = cursor.fetchall()
            if records:
                record = records[0]
                response =  {'range': (utils.int2ip(record[0]), utils.int2ip(record[1])),
                    'country': record[2],
                    'county': record[3],
                    'city': record[4]
                }
            
        elif resolver == 'mongo':
            records = self.mgconn.ipdb.addresses.find({'x': {'$lte': ip}, 'y': {'$gte': ip}})
            if records:
                record = records[0]
                response =  {'range': (utils.int2ip(record['x']), utils.int2ip(record['y'])),
                    'country': record['country'],
                    'county': record['county'],
                    'city': record['city']
                }
            
        else:
            pos = find_ip(ip)
            if pos:
                start_addr = _ADDRESSES[pos]
                response = utils.sh2rec(start_addr, _DETAILS[start_addr])
        
        if response:    
            return self.response(data=response)
        
        self.response('error', 'could not find address')
            
pgconn = psycopg2.connect(settings.POSTGRES_CONN)
mgconn = pymongo.MongoClient(settings.MONGO_CONN)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/find/?", IPHandler, {}),
    ], pgconn=pgconn, mgconn=mgconn, debug=False, gzip=False
)

if __name__ == "__main__":
    
    configure_signals()
    logging.info('starting iplocpy application')
    logging.info('loading database in memory from: %s' % settings.CSV_PATH)
    load_data(settings.CSV_PATH)
    logging.info('ready, listening on %d' % settings.PORT)
    application.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()