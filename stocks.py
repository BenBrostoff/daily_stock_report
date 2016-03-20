import requests
from yahoo_finance import *
from bs4 import BeautifulSoup as BS

class Article():

    def __init__(self, title, link):
        self.title = title
        self.link = link

    def convert_to_html(self):
        return '<a href={}>{}</a>'.format(
            self.link, self.title)

    def __repr__(self):
        return "Title: {} || Link: {}".format(
            self.title, self.link)

class Stock():

    STOCK_HTML = "<strong>%s</strong> \
                <br>CAP: %s \
                <br>PRICE: %s <span style='color:%s'>(%s)</span> \
                <br>YLOW: %s (%s) <br>YHIGH: %s (%s)"

    def __init__(self, ticker, share):
        self.articles = []
        self.ticker = ticker
        self.price = share.get_price()
        self.day_change = share.get_percent_change()
        self.mcap = share.get_market_cap()
        self.year_low = share.get_year_low()
        self.year_high = share.get_year_high()

        self.off_high = self.diff_per(self.year_high)
        self.off_low = self.diff_per(self.year_low)

        self.gather_headlines()

    def diff_per(self, comp):
        per = 100 * (float(self.price) - float(comp)) / float(self.price)
        return "%.2f" % per + '%'

    def gather_headlines(self):
        base = 'https://finance.yahoo.com/q/h?s={}+Headlines'.format(self.ticker)
        r = requests.get(base)
        soup = BS(r.text)

        try:
            headlines = soup.find('div', class_='yfi_quote_headline')
            for x in headlines.select('a'):
                self.articles.append(
                    Article(x.text, x['href']).convert_to_html()
                )
        except:
            print 'Error converting articles'

    @staticmethod
    def style(change):
        if '+' in change:
            return 'green'
        else:
            return 'red'

    def convert_to_html(self):
        base = self.STOCK_HTML % (
            self.ticker, self.mcap, self.price,
            self.style(self.day_change),
            self.day_change,
            self.year_low, self.off_low,
            self.year_high, self.off_high)

        articles = ''
        for x in self.articles[:2]:
            articles += '<br>' + x

        return base + articles