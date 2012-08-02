import os
import sys
import csv
import codecs
import logging

DELIM    = ','
QUOTING  = csv.QUOTE_NONNUMERIC
ENCODING = 'utf-8'
ENCODINGS = [
    'utf-8',
    'cp1250'
    ]
UNIQUE_COLS = [
    'date',
    'query',
    ]
logger = logging.getLogger()

def read_csv(fn, delim=DELIM, encoding=ENCODING):
    """ read the csv file, if it exists """
    # read csv
    logger.info("Reading CSV file: %s" % fn)
    try:
        reader = csv.DictReader(open(fn, 'rb', ENCODING), delimiter=delim)
    except Exception, err:
        raise err
    # read existing data
    data = []
    for row in reader:
        data.append(row)
    return data

def write_csv(fn, data, quoting=QUOTING, delim=DELIM, encoding=ENCODING, encodings=ENCODINGS):
    # set the file options
    mode = 'wb'
    write_header = True
    existing_data = []
    if os.path.isfile(fn):
        # since the file exists, we just append and make
        # sure that we write the headers
        mode = 'ab'
        write_header = False
        existing_data = read_csv(fn, delim, encoding)
    # since the data is from a generator, get the first
    # row and the headers
    first_row = data.next()
    headers   = get_headers(first_row)

    csv_writer = csv.DictWriter(
        open(fn, mode, encoding=encoding),
        fieldnames=headers,
        delimiter=delim,
        quoting=quoting
        )

    if write_header:
        csv_writer.writeheader()
    # be sure to add the first row
    # check that the first row does not match existing data
    if do_write_row(first_row, existing_data):
        csv_writer.writerow(first_row)

    count = 1
    headers = []
    for r in data:
        if not do_write_row(r, existing_data): continue
        row = csv_writer.writerow(r)
        count += 1
        sys.stdout.write('.')
    print ''
    return count

def do_write_row(current_row, existing_data, unique_cols=UNIQUE_COLS):
    """ very brute force approach to make sure existing
        data will not be written to csv
    """
    current = []
    for c in unique_cols:
        current.append(current_row[c])
    write_row = True
    for e in existing_data:
        existing = []
        for c in unique_cols:
            existing.append(e[c])
        if existing == current: write_row = False
    return write_row


def get_headers(row):
    headers = row.keys()
    headers.sort()
    # if date exists in headers, make sure that it is the
    # the first column
    if 'date' in headers:
        d = headers.pop(headers.index('date'))
        headers.insert(0,d)
    return headers

def open(fn, mode, encoding=ENCODING):
    return codecs.open(fn, mode, encoding=encoding)