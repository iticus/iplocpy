'''
Created on Jul 24, 2015

@author: ionut
'''

import csv
import psycopg2

import settings
import utils

create_query = '''CREATE TABLE addresses(id bigserial PRIMARY KEY,
        x bigint,
        y bigint,
        country text,
        county text,
        city text
    );'''
index_query = 'CREATE INDEX ON addresses(x);'
    
dbconn = psycopg2.connect(settings.POSTGRES_CONN)
dbconn.autocommit = True
cursor = dbconn.cursor()

print('creating PostgreSQL table')
cursor.execute(create_query)

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
        data = (
            start_address,
            stop_address,
            row[2],
            row[3],
            row[4]
        )
        cursor.execute("INSERT INTO addresses(x, y, country, county, city) VALUES(%s, %s, %s, %s, %s)", data)

print('creating index')
cursor.execute(index_query)
print('finished')