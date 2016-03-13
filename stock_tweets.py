from __future__ import unicode_literals

import requests as r

class DailyTweets():
    _TWEET_API =  'http://somanycolors.org:9911/tweets'

    @classmethod
    def get_tweets(cls):
        return r.get(cls._TWEET_API).json()

class StockTweet():    
    _TWEET_MAPPINGS = {
        u'Text': 'text',
        u'RetweetCount': 'retweet_count',
        u'User': 'user',
        u'CreatedAt': 'created_at'
    }

    def __init__(self, tweet):
        for field, mapping in self._TWEET_MAPPINGS.items():
            setattr(self, mapping, 
                tweet[field])

    def convert_to_html(self):
        return "<strong>{}</strong> <br> {} ({} rts) - {} <br><br>".format(
            self.user,
            self.text, self.retweet_count, 
            self.created_at
        )
  