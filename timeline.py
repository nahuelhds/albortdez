import configparser
import GetOldTweets3 as got

config = configparser.ConfigParser()
config.read('.twitter')

tweetCriteria = got.manager.TweetCriteria().setUsername(config['source']['account_screen_name'])\
    .setEmoji("unicode")

tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]
print(tweet.text)
