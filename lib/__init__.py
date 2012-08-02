import os
import datetime
import logging
import logging.handlers
import codecs
#
# global (to this module) variables
#
time_format     = "%Y-%m-%d"
log_time_format = "%Y-%m-%d %H:%M:%S"

now      = datetime.datetime.now().strftime(log_time_format)
today    = datetime.datetime.now().strftime(time_format)
hostname = os.getenv("COMPUTERNAME")
cwd      = os.getcwd()
encoding = 'utf-8'
test_results = os.path.join('logs','test-files')


# log formatter
formatter       = "%(asctime)s - [%(levelname)s] - %(funcName)s - %(message)s"
#formatter       = "%(asctime)s - [%(levelname)s] - %(module)s.%(funcName)s - %(message)s"
min_formatter   = "%(asctime)s - [%(levelname)s] - %(message)s"
extra_formatter = "%(asctime)s - [%(thread)d] - %(levelname)s - %(module)s.%(funcName)s - %(message)s"

# file log rotation constants
max_size    =  20*1024*1024  # in Bytes (5 MB)
keep_count  = 5 # how many do we keep

# Logger
#   basic logger configuration.
def Logger(logfile_name, log_level=logging.INFO, time_format=log_time_format, extra_info = False, **kw):
    logger = logging.getLogger()
    #
    # default settings
    #
    log_logging_level       = log_level
    console_logging_level   = log_level
    log_formatter           = formatter
    console_formatter       = min_formatter

    # if the debug option is used, be very verbose
    if extra_info: log_formatter = extra_formatter
    if log_level == logging.DEBUG:
        console_formatter = log_formatter
    #
    # check the if any args have been passed in via kw
    #
    # -- logging levels --
    if kw.has_key("console_level"):
        console_logging_level = kw["console_level"]
    # -- formatters --
    if kw.has_key("log_formatter"):
        log_formatter = kw["log_formatter"]
    if kw.has_key("console_formatter"):
        console_formatter = kw["console_formatter"]
    if kw.has_key("format"):
        log_formatter = kw["format"]
        console_formatter = log_formatter
    # set up the logging instance

    #
    # make sure the logdir exists
    #
    logdir = os.path.dirname(logfile_name)
    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    #
    # setup the formatters
    #
    log_formatter     = logging.Formatter(log_formatter, datefmt=time_format)
    console_formatter = logging.Formatter(console_formatter, datefmt=time_format)

    # log time formatter


    #
    # set the levels
    #
    logger.setLevel(log_logging_level)
    # add handlers
    # Handler: Log File Handler
    log_handler = logging.handlers.RotatingFileHandler(
        logfile_name,
        maxBytes=max_size,
        backupCount=keep_count
        )
    log_handler.setFormatter(log_formatter)

    # Handler: Console Output Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_logging_level)
    console_handler.setFormatter(console_formatter)

    # add handlers to the logger
    logger.addHandler(log_handler)
    logger.addHandler(console_handler)
    return logger

# QuickSetup for Logger
#   Passes in the progname and creates the logger which will
#   log to the 'logs' directory.
def LoggerQuickSetup(log_file, log_level=logging.INFO, extra_info = False, **kw):
    if log_file.find('logs') == -1:
        log_file = os.path.join('logs', log_file)
    if os.path.splitext(log_file)[-1] == '': log_file += '.log'
    logger  = Logger(log_file, log_level=log_level, extra_info=extra_info, **kw)
    return logger


