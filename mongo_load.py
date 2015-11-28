'''
Created on Jul 20, 2015

@author: ionut
'''

import csv
import pymongo

import settings
import utils

client = pymongo.MongoClient(settings.MONGO_CONN)

print('importing CSV file')
with open(settings.CSV_PATH, 'rb') as csvfile:
    ip_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    k = 0
    for row in ip_reader:
        k += 1
        if k % 200000 == 0:
            print('loaded %d addresses' % k)
        
        if row[0] == '::':
            break
        start_address = utils.ip2int(row[0])
        stop_address = utils.ip2int(row[1])
        doc = {
            'x': start_address,
            'y': stop_address,
            'country': row[2],
            'county': row[3],
            'city': row[4]
        }
        client.ipdb.addresses.insert_one(doc)

print('creating index')
client.ipdb.addresses.ensure_index([('x', 1)])
print('finished')