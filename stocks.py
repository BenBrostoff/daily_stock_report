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

    def diff_per(self, comp):
        if not self.price:
            return 'Price not available'
        per = 100 * (float(self.price) - float(comp)) / float(self.price)
        return "%.2f" % per + '%'

    @staticmethod
    def style(change):
        if '+' in change:
            return 'green'
        else:
            return 'red'

    def convert_to_html(self):
        return self.STOCK_HTML % (
            self.ticker,
            self.mcap,
            self.price,
            self.style(self.day_change),
            self.day_change,
            self.year_low,
            self.off_low,
            self.year_high,
            self.off_high
        )
