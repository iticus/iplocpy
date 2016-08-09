'''
Created on Nov 27, 2015

@author: ionut
'''

import logging

PORT = 8080

logging.basicConfig(level=logging.INFO,
    format='[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger('tornado').setLevel(logging.WARNING)

CSV_PATH = 'dbip-city.csv'

POSTGRES_CONN = 'dbname=ipdb user=user password=password host=127.0.0.1'
MONGO_CONN = 'mongodb://127.0.0.1:27017/'
REDIS_CONN = '127.0.0.1'