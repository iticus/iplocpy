##iplocpy

***iplocpy*** (IP location Python) is a simple Tornado based web application to determine the location for an IP address. It is based on the free data (city level) available from [DB-IP](https://db-ip.com/).

###Example
Request:
``` curl http://127.0.0.1:8080/find/?ip_addr=123.123.123.123```

Response:
```{
  "status": "OK",
  "data": {
    "county": "Beijing",
    "country": "CN",
    "range": [
      "123.112.0.0",
      "123.124.127.255"
    ],
    "city": "Beijing"
  }
}```


###Requirements
The application is written in Python and uses the [Tornado](http://www.tornadoweb.org/en/stable/) web framework, *csv* and *json* modules.

###Data source
You need to download the db-ip city database from https://db-ip.com/db/download/city and unpack it.
As of November 2015 the database size is  around 50 MB (400 MB unpacked). 

###Performance
The application can use multiple data stores to balance memory consumption, CPU usage and disk space. Some stats for the November 2015 data set on my Asus UX52VS notebook (10 GB RAM, i7-3517U CPU): 

* in-memory
	* startup time: **60 seconds** (loading the entire CSV data file)
	* memory usage: **1940 MB**
	* lookup time: **~1ms** 
	* throughput: **~1000 requests/second** (measured with Tornado's AsyncHTTPClient and [httperf](https://github.com/httperf/httperf))
* PostgreSQL
    * import time: **720 seconds** (inserting records + creating indexes)
    * table size: **427 MB**
    * index size: **360 MB**
    * lookup time: **3 ms**, **279 ms**, **4 ms** (start, middle, end address)
* MongoDB (wt+snappy)
	* import time: **1916 seconds** (inserting documents + creating indexes)
	* table size: **165 MB**
	* index size: **161 MB**
	* lookup time: **8 ms**, **7.5 s**, **9.7 s** (start, middle, end address)
* Redis - *to be implemented*

###Notes
1) For now the search function is only implemented for IPv4 addresses.
2) PostgreSQL is about 3x faster at loading the data compared to MongoDB
3) MongoDB table and index size are about 2.5x - 3x smaller than PostgreSQL (due to using snappy compression)
4) Using two separate indexes (x and y) PostgreSQL seems to be performing much better than MongoDB (to be analyzed)