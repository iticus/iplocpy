'''
Created on Aug 9, 2016

@author: ionut
'''

import csv
import logging

import utils
import settings

_ADDRESSES = []
_DETAILS = {}

def _load_data():
    logging.info('loading database in memory from: %s' % settings.CSV_PATH)
    with open(settings.CSV_PATH, 'rb') as csvfile:
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
            return _ADDRESSES[mid]
    
    mid = min(lo, mid, hi)
    if _ADDRESSES[mid] <= ipnum:
        return _ADDRESSES[mid]
    
    return None


def get_address_details(start_addr):
    return _DETAILS.get(start_addr, None)
    
    
_load_data()