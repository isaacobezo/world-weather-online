""" utilities """
import os
import codecs
import datetime
import yaml
import logging
import csv

DEFAULT_ENCODING = 'utf-8'
APIS_KEY = 'apis'
logger = logging.getLogger()

def load_yaml(fs):
    """ load the filestream as a YAML """
    return yaml.load(fs)

def open(fn, mode, encoding=DEFAULT_ENCODING):
    """ override open with codecs.open """
    return codecs.open(fn, mode, encoding=encoding)

def build_url_string(configs, mode, api, apis_key=APIS_KEY):
    """ get the url string to the correct path for the
        right API and API level (or mode)
    """
    mode_configs = configs[mode]
    if not mode_configs.has_key(api):
        mode_configs[api] = configs[apis_key][api]
    # we should now have both the base and the api
    # portion of the URL
    return mode_configs['base'] + mode_configs[api]

def clean_queries(queries):
    """ make sure to remove all items that are None """
    for q,v in queries.items():
        if not v == None: continue
        del queries[q]
    return queries

def merge_dicts(base_dict, merged_dict, key=None):
    """ merge two dictionaries, one is the default and the second
        one is the new settings or values
    """
    m = merged_dict
    b = base_dict
    if key is not None:
        # sometimes they are the same key (or they should be)
        m = m[key]
        b = b[key]
    for k,v in m.items():
        b[k] = v
    return b

def merge_lists(base_list, merge_list):
    """ merge lists, using the base list as the default """
    for i in merge_list:
        if i in base_list: continue
        base_list.append(i)
    return base_list

def collect_query_keyvals(keys, available_vals):
    """ collect all of the remaining keys/val pairs
        and combine into a single dict
    """
    out = {}
    for k in keys:
        v = None
        if available_vals.has_key(k): v = available_vals[k]
        out[k] = v
    return out

def set_date_span(dates):
    """ convert the dates (to and from) into actual dates,
        using the format (or setting to now)
    """
    now = datetime.datetime.today()
    now_keywords = ['now', 'today']
    dt_format = dates['format']
    del dates['format']
    date_span = []
    for k,v in dates.items():
        # if today or now is defined, then set to None, which
        # will define the date as today
        if v is None:
            v = now
        elif v in now_keywords:
            v = now
        else:
            v = datetime.datetime.strptime(v, dt_format)
        # now add back to dates
        if not v in date_span: date_span.append(v)
        dates[k] = v
    # get dates between the dates
    date_span.sort()
    date_span.reverse()

    # return date spans
    return date_span

def create_date_span(date_span):
    """ create a span of datetimes """
    days = 1
    start_date = date_span.pop()
    out = []
    if len(date_span) == 1:
        end_date = date_span.pop()
        date_diffs = start_date - end_date
        days = abs(date_diffs.days)
    for day in xrange(0,days):
        this_date = start_date + datetime.timedelta(days=day)
        if this_date in out: continue
        out.append(this_date)
    return out

def create_queries(queries, date_span, columns, keys, use_num_of_days=False, dt_format='%m-%d-%Y'):
    """ build the queries to be used, if the num_of_days is specified to use,
        break the generator after the first pass (since it will start with
        the oldest date and the number of days in the span)
    """
    num_of_days = len(date_span) -1
    for i,date in enumerate(date_span):
        date = date.strftime(dt_format)
        for q in queries:
            c = columns
            c['q'] = q
            c['date'] = date
            # if we use number of days, then add it here
            if use_num_of_days: c['num_of_days'] = num_of_days
            # add keys
            for k,v in keys.items(): c[k] = v
            # remove None values
            for k,v in c.items():
                if v is None or not v: del c[k]
            yield c
        if use_num_of_days: break

def flatten_results(results, api, ignores=['current_condition'], value_key='value'):
    for data in results:
        # just shift to the actual data
        data = data['data']
        # if there is an error skip
        if 'error' in data.keys():
            msg = data['error'][0]['msg']
            logger.debug('World Weather Error Message: %s' % msg)
            continue

        # clean the data of the ignored elements
        for i in ignores:
            if not data.has_key(i): continue
            del data[i]

        # combine and flatten the rest of the data
        data = combine_results(data)
        data = flatten_list_items(data, value_key)
        # yeild the results
        yield data

def combine_results(results):
    """ take the remaining data elements and create a single dictionary """
    out = {}
    for values in results.values():
        for value in values:
            for k,v in value.items():
                if out.has_key(k):
                    raise results
                out[k] = v
    return out

def flatten_list_items(results, value_key='value'):
    for key, vals in results.items():
        if not type(vals) is list: continue
        row = []
        for v in vals:
            row.append(v[value_key])
        results[key] = ','.join(row)
    return results

def setup_csv_name(output_options, query_name):
    """ determine what the csv name """
    if output_options.has_key('name'):
        query_name = output_options['name']
    # make sure we are only dealing with only the
    # actual name
    query_name,_ = os.path.splitext(query_name)
    return '%s.csv' % query_name