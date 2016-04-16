import re
import csv
from time import sleep
from cStringIO import StringIO
from os import environ
from IPython import embed
from pytrends.pyGTrends import pyGTrends, _clean_subtable, _parse_rows

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

def get_trend_score(query):
    try:
        connector = pyGTrends(environ.get('gname'), environ.get('gpass'))
        connector.request_report(query)
        sleep(5)

        stock_data = parse_data(connector.decode_data)
        popularity = stock_data['interest_over_time'][-1].values()[-1]
        return popularity
    except Exception as e:
        print(e)
        return "N/A"
