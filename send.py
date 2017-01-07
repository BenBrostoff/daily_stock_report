from time import sleep
from os import environ
from datetime import datetime
import requests as r
import json

from oauth2client.client import SignedJwtAssertionCredentials
import gspread
from yahoo_finance import Share, YQLQueryError

from stocks import Stock

_MARKIT_API = 'http://dev.markitondemand.com/Api/v2/Quote/json?symbol={}'
_EMAIL = environ.get('EMAIL')

def run():
    gc = _get_spreadsheet_client()
    favs = _get_favorites(gc, 'Stocks')
    return r.post(
        'https://api.mailgun.net/v3/{}.mailgun.org/messages'.format(
            environ.get('MAILGUN_DOMAIN')),
        auth=('api', environ.get('MAILGUN_KEY')),
        data={
            'from': _EMAIL,
            'to': _EMAIL,
            'subject': 'Stock Report {}'.format(datetime.now()),
            'html': _build_email(favs)
        }
    )

def _build_email(favs):
    message_body = ''
    for fav in favs:
        try:
            message_body += Stock(fav, Share(fav)).convert_to_html() 
        except YQLQueryError:
            # the Markit API seems to throw a 501 for ETFs
            if fav != 'SPY':
                sleep(5) # Markit request limit
                s_res = r.get(_MARKIT_API.format(fav))
                if s_res.status_code == 200:
                    s_data = s_res.json()
                    message_body += Stock.STOCK_HTML % (
                        fav,
                        s_data['MarketCap'],
                        s_data['LastPrice'],
                        'green' if s_data['ChangePercent'] >= 0 else 'red',
                        s_data['ChangePercent'],
                        'Unavailable', 'Unavailable', 'Unavailable', 'Unavailable')
        message_body += '<br>' * 2

    return message_body

def _get_spreadsheet_client():
    json_key = json.load(open(environ.get('KEY_LOCATION')))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(
        json_key['client_email'],
        json_key['private_key'].encode(),
        scope
    )

    return gspread.authorize(credentials)

def _get_favorites(gc, sheet):
    favorites = gc.open("Favorites") \
                  .worksheet(sheet) \
                  .get_all_values()

    return [item for sublist in favorites for item in sublist]

run()