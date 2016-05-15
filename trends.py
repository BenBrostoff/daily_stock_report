import logging
import re
import csv
from time import sleep
from cStringIO import StringIO
from os import environ
from IPython import embed
from pytrends.pyGTrends import pyGTrends, _clean_subtable, _parse_rows

logging.basicConfig()

_GNAME, _GPASS = environ.get('gname'), environ.get('gpass')
_log = logging.getLogger(__name__)

def parse_data(data):
    """
    Mostly copy of https://github.com/GeneralMills/pytrends, 
    error handles some parsing issues
    """
    parsed_data = {}
    for i, chunk in enumerate(re.split(r'\n{2,}', data)):
        if i == 0:
            match = re.search(r'^(.*?) interest: (.*)\n(.*?); (.*?)$', chunk)
            if match:
                source, query, geo, period = match.groups()
                parsed_data['info'] = {'source': source, 'query': query,
                                       'geo': geo, 'period': period}
        else:
            chunk = _clean_subtable(chunk)
            rows = [row for row in csv.reader(StringIO(chunk)) if row]
            if not rows:
                continue
            try:  
                label, parsed_rows = _parse_rows(rows)
            except ValueError:
                pass
            if label in parsed_data:
                parsed_data[label+'_1'] = parsed_data.pop(label)
                parsed_data[label+'_2'] = parsed_rows
            else:
                parsed_data[label] = parsed_rows

    return parsed_data

class TrendAnalysis(object):
    def __init__(self, query, res):
        self.query = query
        self.res = res

    def set_stats(self, trail=52, recent=3):
        trailing_pop = [x[self.query.lower()] for x
                        in self.res['interest_over_time'][(trail * -1):]
                        if x[self.query.lower()] is not None]
        self.trailing_avg = sum(trailing_pop) / trail
        self.trailing_weeks = trail
        self.recent_avg = sum(trailing_pop[(recent * -1):]) / recent

def get_trend_score(query, horizon=52, trail=3):
    try:
        connector = pyGTrends(_GNAME, _GPASS)
        connector.request_report(query)
        sleep(5)

        stock_data = parse_data(connector.decode_data)
        trend = TrendAnalysis(query, stock_data)
        trend.set_stats()
        return trend
    except Exception as e:
        _log.error(e)
        return "N/A"
