#!/usr/bin/python
""""""
__version__ = '0.1'
import os
import sys
import codecs
import logging
import datetime
from argparse import ArgumentParser, FileType

import lib
import lib.Utils
import lib.WWO
import lib.WriteCSV

CONFIGS_DIR = 'configs'
SETTINGS = os.path.join(CONFIGS_DIR, 'settings.yaml')
API_KEY  = os.path.join(CONFIGS_DIR, 'key.yaml')

DEFAULT_TIME_MASK = '%Y-%m-%d'

logger = logging.getLogger()

def main(query, query_name, default_settings, keys):
    # set the defaults
    default_results = settings['results']
    all_columns     = settings['columns']

    # query specific settings
    query_settings = lib.Utils.merge_dicts(default_settings, query, 'settings')
    query_outputs  = lib.Utils.merge_dicts(default_settings, query, 'output')
    query_dates    = lib.Utils.merge_dicts(default_settings['settings'], query['settings'], 'dates')
    queries = query['q']

    # for now, we are only writing to csv files.
    output_name = lib.Utils.setup_csv_name(query_outputs, query_name)
    logger.info('Output filename is: %s' % output_name)

    # just get the api and mode
    api  = query_settings['api']
    mode = query_settings['mode']
    keys =  keys[mode]

    # setup the columns
    columns = all_columns['default'][api]
    if all_columns.has_key(mode):
        columns = lib.Utils.merge_lists(columns, all_columns[mode][api])

    # convert the columns into keyval pairs (set to None)
    logger.info("Create the query columns")
    query_columns = lib.Utils.collect_query_keyvals(columns, query_settings)

    # create the API url
    base_url = lib.Utils.build_url_string(settings['urls'], mode, api)
    logger.info("Url Base Path: '%s'" % (base_url))

    # setup the dates, there might be a to and from date
    query_dates = lib.Utils.set_date_span(query_dates)
    query_date_span = lib.Utils.create_date_span(query_dates)


    # create the queries to use
    logger.info("Creating the query generator")
    queries = lib.Utils.create_queries(
        queries,
        query_date_span,
        query_columns,
        keys,
        query_settings['num_of_days'],
        query_settings['date format']
        )

    # get results
    results = lib.WWO.get_wwo(base_url, queries)

    # flatten results:
    results = lib.Utils.flatten_results(results, api)

    # write to csv file
    count = lib.WriteCSV.write_csv(output_name, results)

    logger.info("Wrote %d items to %s" % (count, output_name))

def usage(argv=sys.argv, prog=os.path.basename(__file__), description=__doc__, version=__version__):
    argv = argv[1:]
    parser = ArgumentParser(prog=prog,description=description, version=version)
    parser.add_argument(dest='query', metavar='QUERY.YAML', type=FileType('rb'),
                        help="Query Yaml for Weather data"
                       )
    optionals = parser.add_argument_group('Optional Arguments')
    optionals.add_argument('-k', '--key', dest='keys', default=API_KEY,
                           metavar='KEY.YAML', type=FileType('rb'),
                           help='The YAML that contains the API key to use, currently %s' % API_KEY
                          )
    optionals.add_argument('-s', '--settings', dest='settings', default=SETTINGS,
                           metavar='SETTINGS.YAML', type=FileType('rb'),
                           help="Settings YAML, which defines the configuration settings " +\
                                "for this script, these settings should not be changed"
                          )

    parser.add_argument_group(optionals)
    opts = parser.parse_args()
    return opts


# launch main
if __name__ == '__main__':
    opts = usage()
    query_name = os.path.basename(opts.query.name)
    settings = lib.Utils.load_yaml(opts.settings)
    keys     = lib.Utils.load_yaml(opts.keys)
    query    = lib.Utils.load_yaml(opts.query)
    # setup logger
    log_file = os.path.join('logs', 'get-wwo.log')
    logger = lib.LoggerQuickSetup(log_file)
    logger.info("***** STARTING %s *****" % datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S'))

    # get the wwo data
    main(query, query_name, settings, keys)