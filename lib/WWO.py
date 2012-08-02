#!/usr/bin/env python
""" get_wwo
    Collect Results from the BASE URL provided and the query list
    from the World Weather Online API.
"""
import logging
import simplejson
import sys
from time import sleep
from urllib import urlencode
from urllib2 import Request, build_opener, URLError
from urlparse import parse_qs

logger = logging.getLogger()
AVAILABLE_FORMATS = [ 'json' ]

class WorldWeatherOnline(object):


    def __init__(self, base_url, **kw):
        self.url = base_url
        for k,v in kw.items(): setattr(self, k, v)
        self._opener = build_opener()

    def run(self, queries, api='weather'):
        for q in queries:
            date  = q['date']
            query = q['q']
            format_type = q['format']
            q = urlencode(q)
            q = '%s?%s' % (self.url, q)
            r = self._connect_to_url(q)
            r = self._open_url(r)
            r = self.load(format_type, r)
            # check for error messages
            if 'error' in r['data'].keys():
                error_msg = ["Query failed: '%s'" % query]
                for e in r['data']['error']:
                    e = e['msg']
                    error_msg.append(e)
                # just fail on all error messages
                error_msg = '\n'.join(error_msg)
                logger.debug(error_msg)
                raise Exception(error_msg)

            # for some reason, we need to make sure we have the request date
            # and the actual data point date fixed.
            r['data']['request'][0]['request_date'] = r['data'][api][0]['date']
            r['data'][api][0]['date'] = date
            yield r

    def load(self, format_type, data):
        """ load the data object correctly """
        f = FormatHandler(format_type)
        return f.load(data)

    def _open_url(self, r):
        count = 0
        attempts = 10
        while True:
            try:
                return self._opener.open(r)
            except URLError, urerr:
                # sometimes we need to wait for the connection
                sleep(1)
            except Exception, err:
                raise err
            count += 1
            if count >= attempts: break
        raise URLError('Connection timed out')

    def _connect_to_url(self, url):
        try:
            r = Request(url)
        except Exception, err:
            raise err
        return r


class FormatHandler(object):
    """ wrapper for the different types of formats that the
        data can back as.
    """

    def __init__(self, format_type, available_formats=AVAILABLE_FORMATS):
        self.format = format_type.lower()
        if not self.format in available_formats:
            raise Exception("Unable to process format type '%s'" % self.format)

    def load(self, data):
        format_loader = 'self._load_%s(data)' % self.format
        return eval(format_loader)

    def _load_json(self, data):
        return simplejson.load(data)


# wrapper for GetWWO
def get_wwo(base_url, queries):
    g = WorldWeatherOnline(base_url)
    results = g.run(queries)
    return results
