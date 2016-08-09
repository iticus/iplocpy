'''
Created on Aug 9, 2016

@author: ionut
'''

import json
import tornado.web

import memback
import utils

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.pgconn = self.settings['pgconn']
        self.mgconn = self.settings['mgconn']
        self.rdconn = self.settings['rdconn']
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
        
        start_addr = memback.find_ip(ip)
        if not start_addr:
            return self.response('error', 'could not find address')
            
        if resolver == 'postgres':
            cursor = self.pgconn.cursor()
            #cursor.execute('select x, y, country, county, city from addresses where x <= %s and y >= %s', (ip, ip))
            cursor.execute('select x, y, country, county, city from addresses where x = %s', (start_addr, ))
            records = cursor.fetchall()
            if records:
                record = records[0]
                response =  {'range': (utils.int2ip(record[0]), utils.int2ip(record[1])),
                    'country': record[2],
                    'county': record[3],
                    'city': record[4]
                }
                cursor.close()
            
        elif resolver == 'mongo':
            #records = self.mgconn.ipdb.addresses.find({'x': {'$lte': ip}, 'y': {'$gte': ip}})
            records = self.mgconn.ipdb.addresses.find({'x': start_addr})
            if records:
                record = records[0]
                response =  {'range': (utils.int2ip(record['x']), utils.int2ip(record['y'])),
                    'country': record['country'],
                    'county': record['county'],
                    'city': record['city']
                }
                records.close()
            
        else:
            #details = self.rdconn.get(start_addr)
            #response = utils.sh2rec(start_addr, json.loads(details))
            response = utils.sh2rec(start_addr, memback.get_address_details(start_addr))
        
        if response:    
            return self.response(data=response)
        
        self.response('error', 'could not find address')