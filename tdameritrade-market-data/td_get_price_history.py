#!/usr/bin/env python
#
# Visit TD Ameritrade's developer website for more information.
# https://developer.tdameritrade.com/content/getting-started
#

import argparse
import time
from datetime import datetime
import sys, os, time, json
import requests
import logging.config

def init_logger(logger_name, log_file=None, **kwargs):
    global LOG_LEVEL
    LOG_LEVEL = logging.DEBUG
    LOGFORMAT = "%(log_color)s %(asctime)s - %(levelname)s - %(message)s %(reset)s"
    
    from colorlog import ColoredFormatter
    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOGFORMAT)
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(stream)

    # Create file handler and set level to debug
    if log_file:
        fh = logging.FileHandler(log_file, mode='a', encoding=None, delay=False, **kwargs)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # Create formatter
        fh.setFormatter(formatter) # Add formatter to handlers
        logger.addHandler(fh) # Add handlers to logger
    return logger

def parse_arguments():
    global args
    parser = argparse.ArgumentParser(description='TDAmeritrade')
    parser.add_argument('-c', '--config', default='config.json', type=str, required=False, help='config file [default: config.json]')
    parser.add_argument('-e', '--extended-hours', default=False, type=bool, required=False, help='with extended hour data')
    parser.add_argument('-s', '--symbol', default='QQQ', type=str, required=False, help='symbol')
    parser.add_argument('-S', '--start', default="2020-01-01 00:00:00", type=str, required=False, help='start time in EDT timezone')
    parser.add_argument('-E', '--end', default=None, type=str, required=False, help='end time in EDT timezone')
    parser.add_argument('-F', '--frequency', default="1", type=int, required=False, help='frequency in minutes')
    parser.add_argument('-k', '--api-key', default="DORAEMON001", type=str, required=True, help='TD Ameritrade api key, c.f. https://developer.tdameritrade.com/price-history/apis')
    args  = parser.parse_args()

def td_get_price_history(fp, symbol, extended, start, end, frequency = 1): 
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    data = { 'apikey':'DORAEMON001'}
    params = {
        'frequencyType': 'minute',
        'frequency': frequency,
        'startDate': start,
        'endDate': end,
        'needExtendedHoursData': extended
    }              
    time.sleep(1)
    priceHistoryReply = requests.get('https://api.tdameritrade.com/v1/marketdata/{}/pricehistory?apikey={}'.format(symbol, args.api_key), params = params) 
    chart = priceHistoryReply.json()

    if fp:    
        for line in chart.get("candles", []):
            #It's funny that data received may contain data point out of range that we ask for
            if not int(line['datetime']) in range(start, end):
                logger.warn(f'INVALID ==================== {start} - {end} symbol:{symbol} line:{line}')
            else:    
                fp.write(json.dumps(line) + '\n')
    return chart

if __name__ == "__main__":
    init_logger(__name__, None)
    logger = logging.getLogger(__name__)    
  
    parse_arguments()
    start_ms = int(1000*datetime.strptime(args.start + " EDT",  "%Y-%m-%d %H:%M:%S %Z").timestamp())
    end_ms = int(1000*datetime.strptime(args.end + " EDT",  "%Y-%m-%d %H:%M:%S %Z").timestamp()) if args.end is not None else int(1000*time.time())
    duration_ms = 24*3600*1000

    logger.info(f"Retrieving TD Ameritrade Market Data from {args.start} ({start_ms}) to {args.end} ({end_ms})...")
    os.makedirs("charts", exist_ok=True)
    fp = open('charts/' + args.symbol + '.jsonl', 'w')
    for t in range(start_ms, end_ms, duration_ms):
        td_get_price_history(fp, args.symbol, args.extended_hours, t, t + duration_ms - 1, args.frequency)
    fp.close()
    logger.info("done")

