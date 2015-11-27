'''
Created on Jul 20, 2015

@author: ionut
'''

import csv
import json
import logging
import signal
import tornado.web

import settings
import utils

_ADDRESSES = []
_DETAILS = {}


logging.basicConfig(level=settings.LOG_LEVEL, #filename='ip2loc.log',
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
        
        pos = find_ip(ip)
        if pos is None:
            return self.response('error', 'could not find address')
        
        start_addr = _ADDRESSES[pos]
        data = utils.sh2rec(start_addr, _DETAILS[start_addr])
        self.response(data=data)
            

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/find/?", IPHandler, {}),
])

if __name__ == "__main__":
    
    configure_signals()
    logging.info('starting iplocpy application')
    logging.info('loading database in memory from: %s' % settings.CSV_PATH)
    load_data(settings.CSV_PATH)
    logging.info('ready, listening on %d' % settings.PORT)
    application.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()