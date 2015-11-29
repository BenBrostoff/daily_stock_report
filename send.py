from os import environ
from datetime import datetime
import json

from oauth2client.client import SignedJwtAssertionCredentials
import gspread
import mandrill

from stocks import *

EMAIL_CLIENT = mandrill.Mandrill(environ.get('MANDRILL_KEY'))

def get_spreadsheet_client():
    json_key = json.load(open(environ.get('KEY_LOCATION')))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], 
        json_key['private_key'].encode(), scope)

    return gspread.authorize(credentials)

def get_favorites(gc):
    favorites = gc.open("Favorites") \
                  .worksheet("Favorites") \
                  .get_all_values()

    return [item for sublist in favorites for item in sublist]

def build_email(favs):
    message_body = ''
    for x in favs:
        message_body += Stock(x, Share(x)).convert_to_html()
        message_body += '<br>' * 2

    return {
        'to': [{'email': 'ben.brostoff@gmail.com'}],
        'from_email': 'ben.brostoff@gmail.com',
        'html': message_body,
        'subject': datetime.now().strftime("%B %d, %Y") + ' Stock Report'
    }

gc = get_spreadsheet_client()
favs = get_favorites(gc)

EMAIL_CLIENT.messages.send(message=build_email(favs))
