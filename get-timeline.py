import tweepy
import configparser

config = configparser.ConfigParser()
config.read('.twitter')
twitter_account = config['source']['account_screen_name']

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(config['consumer']['key'], config['consumer']['secret'])
auth.set_access_token(config['access']['token'], config['access']['token_secret'])

# Creation of the actual interface, using authentication
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
saveFile = open('./tweets/%s.txt' % twitter_account, 'w')

for status in tweepy.Cursor(api.user_timeline, id=twitter_account, tweet_mode="extended").items():
    print(status.full_text)
    saveFile.write("%s\n" % status.full_text)

saveFile.close()

print("")
print("====================")
print("Extraction finished!")
print("====================")
