from time import sleep
from os import environ
from datetime import datetime
import requests as r
import json

from oauth2client.client import SignedJwtAssertionCredentials
import gspread
import mandrill
from yahoo_finance import Share, YQLQueryError

from stocks import Stock, Article
from stock_tweets import DailyTweets, StockTweet

_MARKIT_API = 'http://dev.markitondemand.com/Api/v2/Quote/json?symbol={}'
EMAIL_CLIENT = mandrill.Mandrill(environ.get('MANDRILL_KEY'))

def build_email(favs, tweets):
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

    for tweet in tweets:
        message_body += tweet.convert_to_html()

    return {
        'to': [{'email': 'ben.brostoff@gmail.com'}],
        'from_email': 'ben.brostoff@gmail.com',
        'html': message_body,
        'subject': datetime.now().strftime("%B %d, %Y") + ' Stock Report'
    }

def __get_spreadsheet_client():
    json_key = json.load(open(environ.get('KEY_LOCATION')))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], 
        json_key['private_key'].encode(), scope)

    return gspread.authorize(credentials)

def __get_favorites(gc):
    favorites = gc.open("Favorites") \
                  .worksheet("Favorites") \
                  .get_all_values()

    return [item for sublist in favorites for item in sublist]

def __get_tweets():
    tweets = []
    for tweet in DailyTweets.get_tweets():
        tweets.append(StockTweet(tweet))

    return tweets

gc = __get_spreadsheet_client()
favs = __get_favorites(gc)
tweets = __get_tweets()

EMAIL_CLIENT.messages.send(message=build_email(favs, tweets))
