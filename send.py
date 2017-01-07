from time import sleep
from os import environ
from datetime import datetime
import requests as r
import json

from oauth2client.client import SignedJwtAssertionCredentials
import gspread
import sendgrid
from yahoo_finance import Share, YQLQueryError

from stocks import Stock

_MARKIT_API = 'http://dev.markitondemand.com/Api/v2/Quote/json?symbol={}'
_SGRID_KEY = environ.get('SGRID_KEY')

if not _SGRID_KEY:
    raise Exception('Sendgrid API key required!')

_EMAIL_CLIENT = sendgrid.SendGridClient(_SGRID_KEY)
_my_email = 'ben.brostoff@gmail.com'

def run():
    gc = _get_spreadsheet_client()
    queries = _get_favorites(gc, "Queries")
    favs = _get_favorites(gc, 'Stocks')
    _EMAIL_CLIENT.send(_build_email(queries, favs))

def _build_email(favs):
    message = sendgrid.Mail()

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
                    message_body += Stock.STOCK_HTML %  (
                    fav, s_data['MarketCap'], s_data['LastPrice'],
                    'green' if s_data['ChangePercent'] >= 0 else 'red',
                    s_data['ChangePercent'],
                    'Unavailable', 'Unavailable',
                    'Unavailable', 'Unavailable')
        message_body += '<br>' * 2

    message.add_to(_my_email)
    message.set_from(_my_email)
    message.set_subject(datetime.now().strftime("%B %d, %Y") + ' Stock Report')
    message.set_html(message_body)
    return message

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
