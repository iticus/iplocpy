'''
Created on Nov 27, 2015

@author: ionut
'''


def ip2int(ip):
    o = map(int, ip.split('.'))
    if len(o) > 4:
        raise Exception('invalid input')
    for d in o:
        if d < 0:
            raise Exception('invalid input')
        if d > 255:
            raise Exception('invalid input')
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res


def int2ip(ipnum):
    o1 = int(ipnum / 16777216) % 256
    o2 = int(ipnum / 65536) % 256
    o3 = int(ipnum / 256) % 256
    o4 = int(ipnum) % 256
    return '%s.%s.%s.%s' % (o1, o2, o3, o4)


def sh2rec(start_addr, doc):
    return {
            'range': (int2ip(start_addr), int2ip(doc[0])),
            'country': doc[1],
            'county': doc[2],
            'city': doc[3]
        }
