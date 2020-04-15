import markovify
import json
from dotenv import load_dotenv
from os import environ
from expiringdict import ExpiringDict
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

load_dotenv()

# store Twitter specific credentials
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
ACCOUNT_SCREEN_NAME = environ['ACCOUNT_SCREEN_NAME']
ACCOUNT_USER_ID = environ['ACCOUNT_USER_ID']
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
TRACK = environ['TRACK']

tweets_filename = "./tweets/%s-replies.txt" % ACCOUNT_SCREEN_NAME

auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
twitterApi = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


class ReplyToTweet(StreamListener):

    def __init__(self):
        self.__max_per_user = 5 # max replies per user within an hour
        self.__rate_limits_per_user = ExpiringDict(max_len=1000, max_age_seconds=(1 * 60))
        self.initialize_model()

    def initialize_model(self):
        with open(tweets_filename) as f:
            text = f.read()
            self.__text_model = markovify.Text(text)

    def response(self, text):
        return str(self.__text_model.make_short_sentence(80, tries=10).lower() or '')

    def on_data(self, data):
        if not data:
            return

        tweet = json.loads(str(data).strip())
        retweeted = tweet.get('retweeted')
        from_self = tweet.get('user', {}).get('id_str','') == ACCOUNT_USER_ID

        # if retweeted is not None and not retweeted and not from_self:
        if retweeted is not None and not from_self:

            tweetId = tweet.get('id_str')
            screenName = tweet.get('user', {}).get('screen_name')
            tweetText = tweet.get('text')

            # check if we already replied to this user and when
            # rate limit replies per user
            # update rate for this user
            existing_rate = int(0 if self.__rate_limits_per_user.get(screenName) is None else self.__rate_limits_per_user.get(screenName))
            self.__rate_limits_per_user[screenName] = existing_rate + 1

            # check rate limit, and reply accordingly
            if (existing_rate == self.__max_per_user):
                replyText = '@' + screenName + ' no te voy a responder. Esperá sentado una hora.'
                twitterApi.update_status(status=replyText, in_reply_to_status_id=tweetId)
                print("replied to this user, saying he/she should wait for an hour.")
                return
            elif (existing_rate > self.__max_per_user):
                print("*already* replied to this user, he/she should wait for an hour, ignoring.")
                return

            replyText = '@' + screenName +" "+ self.response("")
            print("%s | %s" % (replyText, "https://twitter.com/%s/status/%s" % (screenName, tweetId)))
            twitterApi.update_status(status=replyText, in_reply_to_status_id=tweetId)
            return

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    streamListener = ReplyToTweet()
    twitterStream = Stream(auth, streamListener)
    twitterStream.filter(track=[TRACK])

